"""No-stack Director routing: ``merge_session_goal`` + ``choose_pipeline_step`` (``run`` / ``done``)."""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from inference.clients.json_parse_diag import describe_json_decode_error, preview_text_for_log

from .config import DIRECTOR_MEMORY_MODEL, DIRECTOR_ROUTING_MODEL
from . import prompts

logger = logging.getLogger(__name__)


def _env_int(name: str, default: int, *, lo: int, hi: int) -> int:
    try:
        n = int(os.getenv(name, str(default)).strip())
        return max(lo, min(n, hi))
    except ValueError:
        return default


# Routing prompts: only recent rows (default 10) keeps context small; JSON blob cap is large by default.
_MAX_MEMORY_ROWS = _env_int("DIRECTOR_ROUTING_MEMORY_ROWS_MAX", 10, lo=1, hi=500)
_MAX_JSON_CHARS = _env_int("DIRECTOR_ROUTING_MEMORY_JSON_MAX_CHARS", 200_000, lo=5_000, hi=2_000_000)
# Provider still requires a completion budget; use a large default (override via env).
_ROUTING_CHAT_JSON_MAX_TOKENS = _env_int(
    "DIRECTOR_ROUTING_CHAT_JSON_MAX_TOKENS", 32768, lo=256, hi=256_000
)


@dataclass(frozen=True)
class PipelineRouteDecision:
    """Result of ``choose_pipeline_step`` (auto-chaining without Task Stack)."""

    agent_id: Optional[str]
    finished: bool
    rationale: str = ""

    @property
    def should_run(self) -> bool:
        return bool(self.agent_id) and not self.finished


def _agents_catalog_for_prompt(agents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for a in agents:
        if not isinstance(a, dict):
            continue
        aid = str(a.get("id") or "").strip()
        if not aid:
            continue
        out.append(
            {
                "id": aid,
                "description": str(a.get("description") or "")[:500],
                "asset_key": str(a.get("asset_key") or ""),
                "capabilities": a.get("capabilities")
                if isinstance(a.get("capabilities"), list)
                else [],
            }
        )
    return out


def _allowed_ids(agents: List[Dict[str, Any]]) -> List[str]:
    return [x["id"] for x in _agents_catalog_for_prompt(agents)]


def _parse_router_json(raw: str) -> Dict[str, Any]:
    """Strict parse: one JSON object, whole response body — no markdown fence recovery."""
    text = (raw or "").strip()
    if not text:
        raise ValueError("empty router LLM response")
    try:
        obj = json.loads(text)
    except json.JSONDecodeError as exc:
        diag = describe_json_decode_error(text, exc)
        logger.error(
            "router JSON parse failed: %s | preview=%s",
            diag,
            preview_text_for_log(text),
        )
        raise ValueError(f"router JSON invalid: {exc}; {diag}") from exc
    if not isinstance(obj, dict):
        raise ValueError("router JSON root must be an object")
    return obj


def _session_has_prior_context(
    global_memory: List[Dict[str, Any]],
    execution_summary: Optional[Dict[str, Any]],
) -> bool:
    if global_memory:
        return True
    if execution_summary is None:
        return False
    return bool(execution_summary.get("execution_id"))


def _memory_and_execution_blobs(
    global_memory: List[Dict[str, Any]],
    execution_summary: Optional[Dict[str, Any]],
) -> tuple[str, str]:
    mem_rows = global_memory[:_MAX_MEMORY_ROWS] if global_memory else []
    mem_blob = json.dumps(mem_rows, ensure_ascii=False, default=str)
    if len(mem_blob) > _MAX_JSON_CHARS:
        mem_blob = mem_blob[:_MAX_JSON_CHARS] + "\n…(truncated)"
    summary_blob = (
        json.dumps(execution_summary, ensure_ascii=False, default=str)[:8000]
        if execution_summary
        else "null"
    )
    return mem_blob, summary_blob


class LlmSubAgentPlanner:
    """LiteLLM via ``inference.clients.LLMClient`` — merge + per-step pipeline routing."""

    def __init__(self, model: Optional[str] = None, llm_client: Any = None) -> None:
        raw = (model or DIRECTOR_ROUTING_MODEL or DIRECTOR_MEMORY_MODEL or "").strip()
        self._model = raw or "gpt-3.5-turbo"
        self._llm = llm_client

    def _client(self):
        if self._llm is not None:
            return self._llm
        try:
            from inference.clients import LLMClient
        except ImportError as exc:
            raise ImportError(
                "Routing requires the `inference` package on PYTHONPATH "
                "(run from repo root or install merged requirements.txt)."
            ) from exc
        self._llm = LLMClient()
        return self._llm

    def _complete_json_dict(
        self,
        system: str,
        user: str,
        *,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        One JSON object via provider JSON mode (``chat_json`` / ``response_format``).

        Used for merge + pipeline routing so outputs are not free-form prose (avoids truncated
        pseudo-JSON from ``chat_text``).
        """
        client = self._client()
        chat_json_fn = getattr(client, "chat_json", None)
        if not callable(chat_json_fn):
            raise TypeError(
                "director_nostack routing requires an LLM client with async chat_json(...) "
                "(e.g. inference.clients.LLMClient)."
            )
        import asyncio

        cap = _ROUTING_CHAT_JSON_MAX_TOKENS if max_tokens is None else max_tokens

        async def _run() -> Dict[str, Any]:
            out = await chat_json_fn(
                system_prompt=system,
                user_prompt=user,
                model=self._model,
                max_tokens=cap,
            )
            if not isinstance(out, dict):
                raise ValueError(f"chat_json returned non-dict: {type(out)}")
            return out

        return asyncio.run(_run())

    def merge_session_goal(
        self,
        *,
        latest_user_message: str,
        global_memory: List[Dict[str, Any]],
        execution_summary: Optional[Dict[str, Any]],
        prior_user_chat_lines: Optional[List[str]] = None,
    ) -> str:
        """Merge prior context + latest line into one string; no prior → return latest (no LLM)."""
        line = (latest_user_message or "").strip()
        if not line:
            return ""
        prior = [p.strip() for p in (prior_user_chat_lines or []) if isinstance(p, str) and p.strip()]
        needs_llm = _session_has_prior_context(global_memory, execution_summary) or bool(prior)
        if not needs_llm:
            return line

        mem_blob, summary_blob = _memory_and_execution_blobs(global_memory, execution_summary)
        user = prompts.build_merge_user_prompt(
            prior_user_lines=prior,
            latest_line=line,
            summary_blob=summary_blob,
            mem_blob=mem_blob,
        )
        try:
            data = self._complete_json_dict(
                prompts.MERGE_SESSION_GOAL_SYSTEM,
                user,
            )
        except Exception as exc:
            logger.error("merge_session_goal LLM failed: %s", exc)
            return line
        if not isinstance(data, dict):
            logger.warning(
                "merge_session_goal: router JSON root is not an object; using latest user line"
            )
            return line
        merged = data.get("merged_goal")
        if not isinstance(merged, str):
            logger.warning(
                "merge_session_goal: missing or invalid merged_goal; using latest user line"
            )
            return line
        merged = merged.strip()
        if not merged:
            logger.warning(
                "merge_session_goal: merged_goal empty after strip; using latest user line"
            )
            return line
        return merged

    def choose_pipeline_step(
        self,
        *,
        original_user_goal: str,
        after_frontend_user_message: bool = True,
        step_index: int = 0,
        last_agent_id: Optional[str] = None,
        available_agents: Optional[List[Dict[str, Any]]] = None,
        global_memory: Optional[List[Dict[str, Any]]] = None,
        execution_summary: Optional[Dict[str, Any]] = None,
    ) -> PipelineRouteDecision:
        """
        Next ``agent_id`` or ``done``. ``after_frontend_user_message`` only on the first call of a run.
        ``done`` is LLM-judged only — see package README.
        """
        if available_agents is None:
            available_agents = []
        if global_memory is None:
            global_memory = []
        allowed = _allowed_ids(available_agents)
        if not allowed:
            return PipelineRouteDecision(None, True, "empty catalog")
        catalog = _agents_catalog_for_prompt(available_agents)
        mem_blob, summary_blob = _memory_and_execution_blobs(global_memory, execution_summary)

        continuation_note = (
            "Pipeline step index (0-based): "
            f"{step_index}. Last completed agent: {last_agent_id or 'none'}."
        )
        trigger_block = (
            prompts.ROUTING_TRIGGER_AFTER_USER_MESSAGE
            if after_frontend_user_message
            else prompts.ROUTING_TRIGGER_PIPELINE_CONTINUE
        )
        user = prompts.build_routing_user_prompt(
            allowed=allowed,
            catalog=catalog,
            original_user_goal=original_user_goal,
            trigger_block=trigger_block,
            continuation_note=continuation_note,
            summary_blob=summary_blob,
            mem_blob=mem_blob,
        )
        return self._choose_pipeline_json(
            prompts.ROUTING_PIPELINE_STEP_SYSTEM,
            user,
            allowed,
        )

    def _choose_pipeline_json(
        self, system: str, user: str, allowed: List[str]
    ) -> PipelineRouteDecision:
        try:
            data = self._complete_json_dict(system, user)
        except Exception as exc:
            logger.error("Pipeline routing LLM failed or invalid JSON: %s", exc)
            return PipelineRouteDecision(None, False, str(exc))
        if not isinstance(data, dict):
            return PipelineRouteDecision(None, False, "non-object JSON")
        action = str(data.get("action") or "").strip().lower()
        rationale = str(data.get("rationale") or "").strip()
        if action == "done":
            return PipelineRouteDecision(None, True, rationale)
        if action != "run":
            logger.error("Pipeline routing unknown action: %s", data.get("action"))
            return PipelineRouteDecision(None, False, "unknown action")
        aid = data.get("agent_id")
        if not isinstance(aid, str):
            return PipelineRouteDecision(None, False, "missing agent_id")
        aid = aid.strip()
        if aid not in allowed:
            logger.error("Pipeline routing agent_id not in catalog: %s", aid)
            return PipelineRouteDecision(None, False, "invalid agent_id")
        return PipelineRouteDecision(aid, False, rationale)
