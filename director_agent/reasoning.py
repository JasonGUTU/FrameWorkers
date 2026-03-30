"""
Director reasoning: task-stack planning (``ReasoningEngine``) and LLM sub-agent routing
(``LlmSubAgentPlanner``) for ``POST /api/assistant/execute``.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Optional

from inference.clients.json_parse_diag import describe_json_decode_error, preview_text_for_log

from .config import DIRECTOR_MEMORY_MODEL, DIRECTOR_ROUTING_MODEL

logger = logging.getLogger(__name__)


def _env_int(name: str, default: int, *, lo: int, hi: int) -> int:
    try:
        n = int(os.getenv(name, str(default)).strip())
        return max(lo, min(n, hi))
    except ValueError:
        return default


_MAX_MEMORY_ROWS = _env_int("DIRECTOR_ROUTING_MEMORY_ROWS_MAX", 10, lo=1, hi=500)
_MAX_JSON_CHARS = _env_int("DIRECTOR_ROUTING_MEMORY_JSON_MAX_CHARS", 200_000, lo=5_000, hi=2_000_000)


class ReasoningEngine:
    """
    High-level planning for task stack updates (create vs execute vs wait).

    Concrete ``agent_id`` is chosen by ``LlmSubAgentPlanner`` in ``DirectorAgent``,
    not inside ``reason_and_plan``.
    """

    def reason_and_plan(
        self,
        user_message: Optional[Dict[str, Any]] = None,
        task_stack: Optional[List[Dict[str, Any]]] = None,
        task_summary: Optional[Dict[str, Any]] = None,
        reflection_summary: Optional[Dict[str, Any]] = None,
        global_memory: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        ``task_stack`` / ``task_summary`` / ``global_memory`` are kept for API
        compatibility with ``director._cycle`` but are unused here (may feed
        planning logic later).
        """
        _ = (task_stack, task_summary, global_memory)
        logger.info("Reasoning and planning...")

        if user_message:
            message_content = str(user_message.get("content", "") or "")
            explicit_task_id = user_message.get("task_id")
            parsed_content = self._parse_message_content_as_json(message_content)
            target_task_id = explicit_task_id or parsed_content.get("task_id")

            if target_task_id:
                return {
                    "action": "execute_task",
                    "task_updates": [],
                    "target_task_id": target_task_id,
                    "message_content": message_content,
                    "reasoning": (
                        "User message linked to existing task; sub-agent chosen via "
                        "LlmSubAgentPlanner (catalog + global_memory brief)"
                    ),
                }

            return {
                "action": "create_task",
                "task_updates": [
                    {
                        "description": {
                            "overall_description": user_message.get("content", ""),
                            "input": {},
                            "requirements": [],
                            "additional_notes": "",
                        }
                    }
                ],
                "reasoning": "User message received, creating task",
            }

        if reflection_summary:
            return {
                "action": "update_plan",
                "task_updates": [],
                "reasoning": "Reflection received, updating plan",
            }

        return {
            "action": "wait",
            "task_updates": [],
            "reasoning": "No action needed, waiting",
        }

    def should_trigger_reflection(
        self,
        execution_result: Dict[str, Any],
    ) -> bool:
        _ = execution_result
        return True

    @staticmethod
    def _parse_message_content_as_json(content: str) -> Dict[str, Any]:
        if not content:
            return {}
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as exc:
            logger.warning(
                "User message content is not valid JSON; skipping structured fields: %s",
                exc,
            )
            return {}
        if not isinstance(parsed, dict):
            logger.warning(
                "User message JSON root is not an object; skipping structured fields"
            )
            return {}
        return parsed


# --- LLM sub-agent routing (same module; used by ``DirectorAgent._delegate_to_assistant``) ---


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
                "capabilities": a.get("capabilities") if isinstance(a.get("capabilities"), list) else [],
            }
        )
    return out


def _allowed_ids(agents: List[Dict[str, Any]]) -> List[str]:
    return [x["id"] for x in _agents_catalog_for_prompt(agents)]


def _extract_assistant_text(response: Dict[str, Any]) -> str:
    choices = response.get("choices") or []
    if not choices:
        return ""
    message = choices[0].get("message") or {}
    content = message.get("content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: List[str] = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(str(item.get("text", "")))
        return "".join(parts)
    return ""


def _parse_router_json(raw: str) -> Dict[str, Any]:
    """Strict parse: one JSON object — no markdown fence recovery (see project Maintenance Rules)."""
    text = (raw or "").strip()
    if not text:
        raise ValueError("empty router LLM response")
    try:
        obj = json.loads(text)
    except json.JSONDecodeError as exc:
        diag = describe_json_decode_error(text, exc)
        logger.error(
            "Director router JSON parse failed: %s | preview=%s",
            diag,
            preview_text_for_log(text),
        )
        raise ValueError(f"router JSON invalid: {exc}; {diag}") from exc
    if not isinstance(obj, dict):
        raise ValueError("router JSON root must be an object")
    return obj


class LlmSubAgentPlanner:
    """Call LiteLLM via ``inference.clients.LLMClient`` to choose one ``agent_id``."""

    def __init__(self, model: Optional[str] = None, llm_client: Any = None):
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
                "Director routing requires the `inference` package on PYTHONPATH "
                "(run from repo root or install merged requirements)."
            ) from exc
        self._llm = LLMClient()
        return self._llm

    def _complete(self, system: str, user: str) -> str:
        from inference.clients.base.base_client import Message, ModelConfig

        client = self._client()
        cfg = ModelConfig(model=self._model, temperature=0.2, max_tokens=1024)
        resp = client.call(
            [
                Message(role="system", content=system),
                Message(role="user", content=user),
            ],
            model=self._model,
            config=cfg,
        )
        return _extract_assistant_text(resp)

    def choose_for_stack_task(
        self,
        *,
        task_intent_text: str,
        available_agents: List[Dict[str, Any]],
    ) -> Optional[str]:
        """First-time (or stack-pulled) execution: user intent only + catalog."""
        allowed = _allowed_ids(available_agents)
        if not allowed:
            return None
        catalog = _agents_catalog_for_prompt(available_agents)
        system = (
            "You are the Director router. The user goal is described below. "
            "Choose exactly one pipeline agent id from the allowed list that best fits the next step. "
            "Respond with JSON only, no markdown: "
            '{"agent_id":"<id>","rationale":"<short reason>"}'
        )
        user = (
            "Allowed agent ids (you MUST copy one exactly):\n"
            + json.dumps(allowed, ensure_ascii=False)
            + "\n\nAgent catalog:\n"
            + json.dumps(catalog, ensure_ascii=False, default=str)
            + "\n\nUser / task intent:\n"
            + (task_intent_text or "").strip()[:_MAX_JSON_CHARS]
        )
        return self._choose_and_validate(system, user, allowed)

    def choose_for_followup(
        self,
        *,
        message_content: str,
        task_intent_text: str,
        available_agents: List[Dict[str, Any]],
        global_memory: List[Dict[str, Any]],
        execution_summary: Optional[Dict[str, Any]],
    ) -> Optional[str]:
        """Existing task: user follow-up + memory brief + last execution hint."""
        allowed = _allowed_ids(available_agents)
        if not allowed:
            return None
        catalog = _agents_catalog_for_prompt(available_agents)
        mem_rows = global_memory[:_MAX_MEMORY_ROWS] if global_memory else []
        summary_blob = (
            json.dumps(execution_summary, ensure_ascii=False, default=str)[:8000]
            if execution_summary
            else "null"
        )
        mem_blob = json.dumps(mem_rows, ensure_ascii=False, default=str)
        if len(mem_blob) > _MAX_JSON_CHARS:
            mem_blob = mem_blob[:_MAX_JSON_CHARS] + "\n…(truncated)"

        system = (
            "You are the Director router. The user is continuing an existing task. "
            "Use global_memory (newest first; slim rows: task_id, agent_id, created_at, execution_result only) "
            "and the latest execution summary "
            "to decide the single best next pipeline agent. "
            "Respond with JSON only, no markdown: "
            '{"agent_id":"<id>","rationale":"<short reason>"}'
        )
        user = (
            "Allowed agent ids (you MUST copy one exactly):\n"
            + json.dumps(allowed, ensure_ascii=False)
            + "\n\nAgent catalog:\n"
            + json.dumps(catalog, ensure_ascii=False, default=str)
            + "\n\nTask intent (structured goal / description):\n"
            + (task_intent_text or "").strip()[:12000]
            + "\n\nLatest execution summary (may be null):\n"
            + summary_blob
            + "\n\nglobal_memory (newest first):\n"
            + mem_blob
            + "\n\nUser follow-up message:\n"
            + (message_content or "").strip()[:12000]
        )
        return self._choose_and_validate(system, user, allowed)

    def _choose_and_validate(self, system: str, user: str, allowed: List[str]) -> Optional[str]:
        try:
            raw = self._complete(system, user)
            data = _parse_router_json(raw)
        except Exception as exc:
            logger.error("Director routing LLM failed or returned invalid JSON: %s", exc)
            return None
        if not isinstance(data, dict):
            return None
        aid = data.get("agent_id")
        if not isinstance(aid, str):
            return None
        aid = aid.strip()
        if aid not in allowed:
            logger.error("Director routing returned agent_id not in catalog: %s", aid)
            return None
        return aid
