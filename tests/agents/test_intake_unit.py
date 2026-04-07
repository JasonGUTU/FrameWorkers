"""Unit tests for IntakeTextAgent and IntakeImageAgent.

These tests cover the four intake-flow corner cases that the intake
sub-system promises to handle without crashing or losing data:

  * happy path (LLM call succeeds and returns the expected JSON)
  * fallback when the LLM call fails (network / parse / quota)
  * empty / missing input (no path, empty file, missing file on disk)
  * provenance preservation (``user_intent`` always reaches caption.why)

The tests use stub LLM clients so they run offline.
"""

from __future__ import annotations

import asyncio
import json
import sys
import tempfile
from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image

_repo_root = Path(__file__).resolve().parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from agents.intake.intake_text.agent import IntakeTextAgent, SHORT_TEXT_THRESHOLD
from agents.intake.intake_text.evaluator import IntakeTextEvaluator
from agents.intake.intake_text.schema import IntakeTextInput, IntakeTextOutput

from agents.intake.intake_image.agent import IntakeImageAgent
from agents.intake.intake_image.evaluator import IntakeImageEvaluator
from agents.intake.intake_image.schema import IntakeImageInput, IntakeImageOutput


# ---------------------------------------------------------------------------
# Stub LLM clients
# ---------------------------------------------------------------------------


class _StubTextLLM:
    """Stand-in for ``LLMClient.chat_json`` — records the call and returns
    a fixed JSON dict."""

    def __init__(self, payload: dict | None = None) -> None:
        self.payload = payload if payload is not None else {"summary": "stub summary"}
        self.calls: list[tuple[str, str]] = []

    async def chat_json(self, system_prompt: str, user_prompt: str, **_: object) -> dict:
        self.calls.append((system_prompt, user_prompt))
        return dict(self.payload)


class _RaisingTextLLM:
    """Always raises — exercises the long-text fallback caption."""

    async def chat_json(self, system_prompt: str, user_prompt: str, **_: object) -> dict:
        raise RuntimeError("simulated provider failure")


class _StubVisionLLM:
    """Stand-in for ``LLMClient.acall`` — records the multimodal payload
    and returns a canned chat-completions-style response."""

    def __init__(self, response_text: str | None = None) -> None:
        self.response_text = (
            response_text
            if response_text is not None
            else json.dumps({"visual_description": "stub vision description"})
        )
        self.last_messages: list | None = None
        self.last_kwargs: dict | None = None

    async def acall(self, messages, **kwargs):
        self.last_messages = messages
        self.last_kwargs = kwargs
        return {
            "choices": [
                {"message": {"content": self.response_text}},
            ]
        }


class _RaisingVisionLLM:
    async def acall(self, messages, **kwargs):
        raise RuntimeError("simulated vision endpoint failure")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_text(text: str) -> str:
    fh = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8")
    fh.write(text)
    fh.close()
    return fh.name


def _write_png(color: tuple[int, int, int] = (255, 0, 0)) -> str:
    img = Image.new("RGB", (8, 8), color=color)
    fh = tempfile.NamedTemporaryFile("wb", suffix=".png", delete=False)
    img.save(fh, format="PNG")
    fh.close()
    return fh.name


# ---------------------------------------------------------------------------
# IntakeTextAgent
# ---------------------------------------------------------------------------


class TestIntakeTextAgent:
    def test_short_text_skips_llm_and_uses_static_caption(self):
        stub = _StubTextLLM()
        agent = IntakeTextAgent(llm_client=stub)
        path = _write_text("make a 30s film about a cat in a workshop")

        out = asyncio.run(agent._generate(
            IntakeTextInput(raw_text_path=path, user_intent="creative brief"),
        ))

        assert isinstance(out, IntakeTextOutput)
        assert stub.calls == [], "short text must NOT call the LLM"
        assert out.content.text.startswith("make a 30s film")
        assert out.content.summary == ""
        assert out.metrics.char_count == len(out.content.text)
        assert "natural-language brief from the user" in out.artifact_caption.what
        assert "make a 30s film" in out.artifact_caption.what
        # User intent must be preserved verbatim in caption.why
        assert out.artifact_caption.why == "creative brief"
        assert out.artifact_caption.scope == "global"

    def test_long_text_calls_llm_for_summary(self):
        stub = _StubTextLLM(payload={"summary": "a multi-page user story outline"})
        agent = IntakeTextAgent(llm_client=stub)
        long_text = "x" * (SHORT_TEXT_THRESHOLD + 200)
        path = _write_text(long_text)

        out = asyncio.run(agent._generate(
            IntakeTextInput(raw_text_path=path, user_intent="story outline"),
        ))

        assert len(stub.calls) == 1, "long text must call chat_json exactly once"
        assert out.content.summary == "a multi-page user story outline"
        assert out.content.text == long_text
        assert "a multi-page user story outline" in out.artifact_caption.what
        assert out.artifact_caption.why == "story outline"

    def test_long_text_llm_failure_falls_back_to_snippet_caption(self):
        agent = IntakeTextAgent(llm_client=_RaisingTextLLM())
        long_text = "the quick brown fox jumps over the lazy dog. " * 30
        path = _write_text(long_text)

        out = asyncio.run(agent._generate(
            IntakeTextInput(raw_text_path=path, user_intent="story"),
        ))

        # No LLM summary — but the agent must still emit a valid caption
        # so the artifact remains usable downstream.
        assert out.content.summary == ""
        assert "no LLM summary available" in out.artifact_caption.what
        assert "the quick brown fox" in out.artifact_caption.what
        assert out.artifact_caption.why == "story"

    def test_empty_path_returns_valid_artifact(self):
        agent = IntakeTextAgent(llm_client=_StubTextLLM())
        out = asyncio.run(agent._generate(
            IntakeTextInput(raw_text_path="", user_intent="nothing"),
        ))
        assert out.metrics.char_count == 0
        assert out.artifact_caption.what == "empty user text upload"
        assert out.artifact_caption.why == "nothing"

    def test_missing_file_treated_as_empty(self):
        agent = IntakeTextAgent(llm_client=_StubTextLLM())
        out = asyncio.run(agent._generate(
            IntakeTextInput(
                raw_text_path="/tmp/no_such_file_xyz.txt",
                user_intent="ghost",
            ),
        ))
        assert out.metrics.char_count == 0
        assert "empty" in out.artifact_caption.what

    def test_full_run_passes_evaluator(self):
        agent = IntakeTextAgent(llm_client=_StubTextLLM())
        agent.evaluator = IntakeTextEvaluator()
        path = _write_text("hello world creative brief")
        result = asyncio.run(agent.run(
            IntakeTextInput(raw_text_path=path, user_intent="brief"),
        ))
        assert result.passed is True
        assert result.attempts == 1


# ---------------------------------------------------------------------------
# IntakeImageAgent
# ---------------------------------------------------------------------------


class TestIntakeImageAgent:
    def test_happy_path_carries_image_bytes_in_multimodal_message(self):
        stub = _StubVisionLLM()
        agent = IntakeImageAgent(llm_client=stub)
        path = _write_png()

        out = asyncio.run(agent._generate(
            IntakeImageInput(raw_image_path=path, user_intent="character ref"),
        ))

        assert isinstance(out, IntakeImageOutput)
        assert out.content.image_asset.uri == path
        assert out.content.visual_description == "stub vision description"
        assert "image showing stub vision description" in out.artifact_caption.what
        assert out.artifact_caption.why == "character ref"

        # Confirm the multimodal message actually carried the image bytes.
        assert stub.last_messages is not None
        assert len(stub.last_messages) == 2
        assert stub.last_messages[0]["role"] == "system"
        user_msg = stub.last_messages[1]
        assert user_msg["role"] == "user"
        assert isinstance(user_msg["content"], list)
        text_items = [c for c in user_msg["content"] if c.get("type") == "text"]
        image_items = [c for c in user_msg["content"] if c.get("type") == "image_url"]
        assert len(text_items) == 1
        assert len(image_items) == 1
        url = image_items[0]["image_url"]["url"]
        assert url.startswith("data:image/")
        assert "base64," in url

        # JSON mode flag must be forwarded so providers that honor it use it.
        assert stub.last_kwargs.get("response_format") == {"type": "json_object"}

    def test_plain_text_response_falls_back_to_raw_text(self):
        stub = _StubVisionLLM(response_text="a wide misty forest at dawn")
        agent = IntakeImageAgent(llm_client=stub)
        path = _write_png()
        out = asyncio.run(agent._generate(
            IntakeImageInput(raw_image_path=path, user_intent="style ref"),
        ))
        assert out.content.visual_description == "a wide misty forest at dawn"
        assert "image showing a wide misty forest at dawn" in out.artifact_caption.what

    def test_llm_failure_emits_fallback_caption(self):
        agent = IntakeImageAgent(llm_client=_RaisingVisionLLM())
        path = _write_png()
        out = asyncio.run(agent._generate(
            IntakeImageInput(raw_image_path=path, user_intent="ref"),
        ))
        assert out.content.visual_description == ""
        assert "vision LLM returned no description" in out.artifact_caption.what
        # Provenance still preserved
        assert out.artifact_caption.why == "ref"

    def test_empty_path_returns_valid_artifact(self):
        agent = IntakeImageAgent(llm_client=_StubVisionLLM())
        out = asyncio.run(agent._generate(
            IntakeImageInput(raw_image_path="", user_intent=""),
        ))
        assert out.content.visual_description == ""
        assert "no image path" in out.artifact_caption.what
        assert out.artifact_caption.why == "(no user intent provided)"

    def test_missing_file_emits_fallback_caption(self):
        agent = IntakeImageAgent(llm_client=_StubVisionLLM())
        out = asyncio.run(agent._generate(
            IntakeImageInput(
                raw_image_path="/tmp/no_such_image_xyz.png",
                user_intent="ghost",
            ),
        ))
        assert out.content.visual_description == ""
        assert "file missing on disk" in out.artifact_caption.what
        assert out.artifact_caption.why == "ghost"

    def test_invalid_json_in_strict_response_falls_back(self):
        # Provider returns broken JSON — agent should treat the raw text
        # as the description rather than crashing.
        stub = _StubVisionLLM(response_text="{not really json")
        agent = IntakeImageAgent(llm_client=stub)
        path = _write_png()
        out = asyncio.run(agent._generate(
            IntakeImageInput(raw_image_path=path, user_intent="ref"),
        ))
        assert out.content.visual_description == "{not really json"

    def test_full_run_passes_evaluator(self):
        agent = IntakeImageAgent(llm_client=_StubVisionLLM())
        agent.evaluator = IntakeImageEvaluator()
        path = _write_png()
        result = asyncio.run(agent.run(
            IntakeImageInput(raw_image_path=path, user_intent="ref"),
        ))
        assert result.passed is True
        assert result.attempts == 1


# ---------------------------------------------------------------------------
# Descriptor wiring
# ---------------------------------------------------------------------------


def test_intake_text_descriptor_extracts_path_from_resolved_entry():
    from agents.contracts import InputBundleV2
    from agents.intake.intake_text.descriptor import build_input as build_text_input
    from agents.intake.intake_text.labels import INPUT_LABEL_RAW_TEXT_UPLOAD

    bundle = InputBundleV2(
        task_id="task_xxx",
        context={
            "resolved_artifacts": {
                INPUT_LABEL_RAW_TEXT_UPLOAD: {
                    "what": "raw user upload, mime=text/plain, awaiting semantic analysis",
                    "why": "user wants to make a film about a cat",
                    "scope": "raw_pending",
                    "path": "/tmp/some/upload.txt",
                    "mime": "text/plain",
                }
            }
        },
    )
    inp = build_text_input("task_xxx", bundle)
    assert isinstance(inp, IntakeTextInput)
    assert inp.raw_text_path == "/tmp/some/upload.txt"
    assert inp.user_intent == "user wants to make a film about a cat"


def test_intake_image_descriptor_extracts_path_from_resolved_entry():
    from agents.contracts import InputBundleV2
    from agents.intake.intake_image.descriptor import build_input as build_image_input
    from agents.intake.intake_image.labels import INPUT_LABEL_RAW_IMAGE_UPLOAD

    bundle = InputBundleV2(
        task_id="task_yyy",
        context={
            "resolved_artifacts": {
                INPUT_LABEL_RAW_IMAGE_UPLOAD: {
                    "what": "raw user upload, mime=image/png, awaiting semantic analysis",
                    "why": "character reference for the protagonist",
                    "scope": "raw_pending",
                    "path": "/tmp/some/character.png",
                    "mime": "image/png",
                }
            }
        },
    )
    inp = build_image_input("task_yyy", bundle)
    assert isinstance(inp, IntakeImageInput)
    assert inp.raw_image_path == "/tmp/some/character.png"
    assert inp.user_intent == "character reference for the protagonist"
