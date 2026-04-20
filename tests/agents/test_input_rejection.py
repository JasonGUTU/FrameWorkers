"""Unit coverage for the upstream-input-rejection channel.

Covers three layers:

  * ``agents.common_schema`` — ``InputRejection`` / ``UpstreamInputRejected``
    plumbing + ``_maybe_parse_rejection`` heuristic.
  * ``agents.base_agent`` — ``BaseAgent.run()`` catches
    ``UpstreamInputRejected`` from ``generate()``, short-circuits (no
    retry — same input would yield the same rejection), and surfaces a
    structured ``eval_result`` with ``kind="upstream_input_rejected"``.
  * ``plan-stack-backend.src.assistant.service`` —
    ``AssistantService._format_failure_error`` branches on the ``kind``
    field to produce the ``[upstream_input_rejected] ...`` prefix that
    director's replan prompt keys on.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel

# Make plan-stack-backend importable for the service-layer test below.
_repo_root = Path(__file__).resolve().parents[2]
_pkg_root = _repo_root / "plan-stack-backend"
if str(_pkg_root) not in sys.path:
    sys.path.insert(0, str(_pkg_root))

from agents.base_agent import (
    BaseAgent,
    ExecutionResult,
    INPUT_REJECTION_RULE,
    _maybe_parse_rejection,
)
from agents.common_schema import InputRejection, UpstreamInputRejected


# ---------------------------------------------------------------------------
# Typed input/output stand-ins used by the minimal BaseAgent subclass below.
# ---------------------------------------------------------------------------


class _StubInput(BaseModel):
    story_json_text: str = ""


class _StubOutput(BaseModel):
    content: dict = {}


class _AgentThatRejects(BaseAgent[_StubInput, _StubOutput]):
    """Minimal BaseAgent subclass whose ``generate()`` always raises
    :class:`UpstreamInputRejected`. No LLM calls are made — we only exercise
    the exception handling in ``BaseAgent.run()``.
    """

    def __init__(self, rejection: InputRejection) -> None:
        super().__init__(llm_client=object())  # run() never calls the LLM here
        self._rejection = rejection
        self.call_count = 0

    async def generate(
        self,
        input_data: _StubInput,
        *,
        rework_notes: str = "",
    ) -> _StubOutput:
        self.call_count += 1
        raise UpstreamInputRejected(self._rejection)


# ---------------------------------------------------------------------------
# common_schema
# ---------------------------------------------------------------------------


class TestInputRejectionSchema:
    def test_defaults_are_empty(self) -> None:
        r = InputRejection()
        assert r.reason == ""
        assert r.missing_labels == []
        assert r.offending_fields == []
        assert r.upstream_agent_hint == ""

    def test_round_trip(self) -> None:
        r = InputRejection(
            reason="no characters",
            missing_labels=["story"],
            offending_fields=["content.cast"],
            upstream_agent_hint="StoryAgent",
        )
        dumped = r.model_dump()
        assert dumped["reason"] == "no characters"
        rebuilt = InputRejection.model_validate(dumped)
        assert rebuilt == r

    def test_exception_carries_structured_rejection(self) -> None:
        r = InputRejection(reason="empty blueprint")
        exc = UpstreamInputRejected(r)
        assert exc.rejection is r
        assert "empty blueprint" in str(exc)


# ---------------------------------------------------------------------------
# _maybe_parse_rejection — the gate used by _llm_fill_full / _llm_fill_creative
# ---------------------------------------------------------------------------


class TestMaybeParseRejection:
    def test_none_when_missing(self) -> None:
        assert _maybe_parse_rejection({"content": {"scenes": []}}) is None

    def test_parses_valid(self) -> None:
        parsed = _maybe_parse_rejection(
            {
                "input_rejection": {
                    "reason": "no cast",
                    "missing_labels": ["story"],
                    "upstream_agent_hint": "StoryAgent",
                }
            }
        )
        assert isinstance(parsed, InputRejection)
        assert parsed.reason == "no cast"
        assert parsed.missing_labels == ["story"]
        assert parsed.upstream_agent_hint == "StoryAgent"

    def test_returns_none_when_field_is_garbage(self) -> None:
        # Not a dict → treated as "no rejection" so normal Pydantic parsing
        # below produces the legible validation error instead.
        assert _maybe_parse_rejection({"input_rejection": "nope"}) is None
        assert _maybe_parse_rejection({"input_rejection": []}) is None


# ---------------------------------------------------------------------------
# BaseAgent.run() — catches UpstreamInputRejected, does NOT retry
# ---------------------------------------------------------------------------


class TestBaseAgentRunRejectionHandling:
    def _run(self, agent: BaseAgent, input_data: BaseModel, *, max_retries: int = 3):
        return asyncio.get_event_loop().run_until_complete(
            agent.run(input_data, max_retries=max_retries),
        )

    def test_rejection_short_circuits_without_retry(self) -> None:
        rejection = InputRejection(
            reason="story_json_text is empty",
            missing_labels=["story"],
            offending_fields=["content"],
            upstream_agent_hint="StoryAgent",
        )
        agent = _AgentThatRejects(rejection)

        result = asyncio.run(
            agent.run(_StubInput(story_json_text=""), max_retries=3),
        )

        assert isinstance(result, ExecutionResult)
        assert result.passed is False
        # No retry: generate() must have been called exactly once even though
        # max_retries=3 was allowed. Same input → same rejection; retry would
        # only waste an LLM call.
        assert agent.call_count == 1
        assert result.attempts == 1
        assert result.output is None

        er = result.eval_result
        assert er["kind"] == "upstream_input_rejected"
        assert er["overall_pass"] is False
        assert "story_json_text is empty" in er["summary"]
        assert er["input_rejection"]["reason"] == "story_json_text is empty"
        assert er["input_rejection"]["missing_labels"] == ["story"]
        assert er["input_rejection"]["upstream_agent_hint"] == "StoryAgent"

    def test_input_rejection_rule_block_is_non_empty(self) -> None:
        # Sanity: the rule constant actually exists, mentions the key the LLM
        # is expected to emit, and is non-trivial in length so a single
        # accidental deletion wouldn't silently disable the channel.
        assert "input_rejection" in INPUT_REJECTION_RULE
        assert "DO NOT fabricate" in INPUT_REJECTION_RULE
        assert len(INPUT_REJECTION_RULE) > 500


# ---------------------------------------------------------------------------
# AssistantService._format_failure_error — branches on kind
# ---------------------------------------------------------------------------


class TestFormatFailureError:
    @pytest.fixture(autouse=True)
    def _load_service(self):
        # Stub flask_cors so src.assistant.service is importable without
        # actually spinning up Flask.
        import types

        if "flask_cors" not in sys.modules:
            stub = types.ModuleType("flask_cors")
            stub.CORS = lambda *args, **kwargs: None
            sys.modules["flask_cors"] = stub

        import src.assistant.service as service_module

        self._fmt = service_module.AssistantService._format_failure_error

    def test_rejection_branch_emits_prefix_with_structured_fields(self) -> None:
        err = self._fmt(
            {
                "kind": "upstream_input_rejected",
                "input_rejection": {
                    "reason": "no characters",
                    "missing_labels": ["story"],
                    "offending_fields": ["content.cast"],
                    "upstream_agent_hint": "StoryAgent",
                },
            }
        )
        assert err.startswith("[upstream_input_rejected] ")
        assert "reason=no characters" in err
        assert "missing=[story]" in err
        assert "hint=StoryAgent" in err

    def test_rejection_branch_tolerates_missing_subfields(self) -> None:
        err = self._fmt(
            {
                "kind": "upstream_input_rejected",
                "input_rejection": {"reason": "bad"},
            }
        )
        assert err.startswith("[upstream_input_rejected] ")
        assert "reason=bad" in err
        assert "missing=[]" in err
        assert "hint=(none)" in err

    def test_quality_gate_branch_keeps_legacy_prefix(self) -> None:
        err = self._fmt(
            {
                "attempts": 3,
                "overall_pass": False,
                "eval_summary": "structural: shot_id format wrong",
            }
        )
        assert err.startswith("quality gate failed: ")
        assert "structural: shot_id format wrong" in err

    def test_empty_debug_emits_sentinel_string(self) -> None:
        # No debug dict at all (e.g. exception path where _execution_debug
        # was never populated) still yields a non-empty string.
        assert self._fmt(None) == "agent quality gate failed (no eval summary)"
        assert self._fmt("not a dict") == "agent quality gate failed (no eval summary)"
