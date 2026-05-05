"""Upfront planner + replanner built on ``inference.clients.LLMClient.chat_json``.

``LlmSubAgentPlanner.plan_pipeline_upfront`` returns a list of
:class:`PlanStepSpec` (one ``{agent_id, intent}`` per planned step) — the director
then batch-writes them into the Plan Stack.

``merge_session_goal`` retains its prior shape; planner/replanner use JSON mode.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .config import (
    DIRECTOR_MEMORY_MODEL,
    DIRECTOR_ROUTING_MODEL,
    MAX_PIPELINE_STEPS,
)
from . import prompts

logger = logging.getLogger(__name__)


def _env_int(name: str, default: int, *, lo: int, hi: int) -> int:
    try:
        n = int(os.getenv(name, str(default)).strip())
        return max(lo, min(n, hi))
    except ValueError:
        return default


_ROUTING_CHAT_JSON_MAX_TOKENS = _env_int(
    "DIRECTOR_ROUTING_CHAT_JSON_MAX_TOKENS", 32768, lo=256, hi=256_000
)


@dataclass(frozen=True)
class PlanStepSpec:
    """One step the planner wants on the Plan Stack.

    ``agent_id`` must be a registered sub-agent id; ``intent`` is a short
    natural-language description of what this step should do. The director
    stores ``{agent_id, intent}`` on ``PlanStep.description`` so subsequent
    stack reads can recover both without a separate lookup.
    """

    agent_id: str
    intent: str = ""


@dataclass(frozen=True)
class ReplanDecision:
    """Output of ``replan_on_failure``.

    ``new_tail`` holds the replacement for the PENDING tail. When empty, the
    director has no actionable tail and simply advances past the failed step.
    """

    new_tail: List[PlanStepSpec] = field(default_factory=list)
    rationale: str = ""


def _agents_catalog_for_prompt(agents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Director-owned routing topology (see director_agent/topology.py). Injected
    # into each agent's catalog entry so sub-agent descriptors stay free of
    # cross-agent naming per the "Sub-agent 解耦" principle.
    # FW_TOPOLOGY=0 ablates the injection (eval-only escape hatch). Default ON.
    enable_topo = os.getenv("FW_TOPOLOGY", "1") != "0"
    if enable_topo:
        from .topology import get_topology_block

    out: List[Dict[str, Any]] = []
    for a in agents:
        if not isinstance(a, dict):
            continue
        aid = str(a.get("id") or "").strip()
        if not aid:
            continue
        base_desc = str(a.get("description") or "")
        if not enable_topo:
            full_desc = base_desc
        else:
            topo_block = get_topology_block(aid)
            full_desc = base_desc + "\n\n" + topo_block if topo_block else base_desc
        out.append(
            {
                "id": aid,
                "description": full_desc,
            }
        )
    return out


def _allowed_ids(agents: List[Dict[str, Any]]) -> List[str]:
    return [x["id"] for x in _agents_catalog_for_prompt(agents)]


def _memory_blob(memory: List[Dict[str, Any]]) -> str:
    return json.dumps(memory or [], ensure_ascii=False, default=str)


class LlmSubAgentPlanner:
    """LiteLLM via ``inference.clients.LLMClient`` — merge + upfront plan + replan."""

    def __init__(
        self,
        model: Optional[str] = None,
        llm_client: Any = None,
        *,
        fewshots: bool = True,
        policies: bool = True,
        schema_variant: str = "with_rationale",
        chat_extra_body: Optional[Dict[str, Any]] = None,
    ) -> None:
        raw = (model or DIRECTOR_ROUTING_MODEL or DIRECTOR_MEMORY_MODEL or "").strip()
        self._model = raw or "gpt-3.5-turbo"
        self._llm = llm_client
        # Two independent scaffold flags (topology is the third — env var
        # FW_TOPOLOGY, handled inside _agents_catalog_for_prompt):
        #   fewshots=True  → append 7 worked-pattern examples
        #   policies=True  → append 4 semantic routing rules
        # fewshots=True implicitly requires policies=True (the worked patterns
        # embody the policies). LoRA training typically uses
        # (fewshots=False, policies=True) to keep routing rules as runtime
        # hints rather than baking them into weights.
        # schema_variant="no_rationale" overrides scaffold and uses the minimal
        # CORE that drops top-level rationale + per-step intent (matches the
        # LoRA *_no_rationale training prompt byte-for-byte).
        if schema_variant == "no_rationale":
            self._core = prompts.PLAN_UPFRONT_CORE_NO_RATIONALE
        elif fewshots:
            self._core = prompts.PLAN_UPFRONT_CORE_WITH_FEWSHOTS
        elif policies:
            self._core = prompts.PLAN_UPFRONT_CORE_WITH_POLICIES
        else:
            self._core = prompts.PLAN_UPFRONT_CORE
        self._chat_extra_body: Optional[Dict[str, Any]] = (
            dict(chat_extra_body) if chat_extra_body else None
        )

    # ------------------------------------------------------------------
    # LLM client plumbing
    # ------------------------------------------------------------------

    def _client(self):
        if self._llm is not None:
            return self._llm
        try:
            from inference.clients import LLMClient
        except ImportError as exc:
            raise ImportError(
                "Router requires the `inference` package on PYTHONPATH "
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
        import asyncio

        return asyncio.run(
            self._acomplete_json_dict(system, user, max_tokens=max_tokens)
        )

    async def _acomplete_json_dict(
        self,
        system: str,
        user: str,
        *,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Async leaf — drives chat_json directly so callers under
        asyncio.gather share one event loop (avoids cross-loop Future bug
        that ThreadPoolExecutor + asyncio.run hits with google.genai SDK).
        """
        client = self._client()
        chat_json_fn = getattr(client, "chat_json", None)
        if not callable(chat_json_fn):
            raise TypeError(
                "director_agent routing requires an LLM client with async chat_json(...) "
                "(e.g. inference.clients.LLMClient)."
            )
        cap = _ROUTING_CHAT_JSON_MAX_TOKENS if max_tokens is None else max_tokens
        kwargs: Dict[str, Any] = dict(
            system_prompt=system,
            user_prompt=user,
            model=self._model,
            max_tokens=cap,
        )
        if self._chat_extra_body:
            kwargs["extra_body"] = self._chat_extra_body
        out = await chat_json_fn(**kwargs)
        if not isinstance(out, dict):
            raise ValueError(f"chat_json returned non-dict: {type(out)}")
        return out

    # ------------------------------------------------------------------
    # merge_session_goal
    # ------------------------------------------------------------------

    def merge_session_goal(
        self,
        *,
        latest_user_message: str,
        stack_memory: List[Dict[str, Any]],
        prior_user_chat_lines: Optional[List[str]] = None,
    ) -> str:
        """Merge prior context + latest line into one string; no prior → return latest."""
        line = (latest_user_message or "").strip()
        if not line:
            return ""
        prior = [p.strip() for p in (prior_user_chat_lines or []) if isinstance(p, str) and p.strip()]
        if not stack_memory and not prior:
            return line

        user = prompts.build_merge_user_prompt(
            prior_user_lines=prior,
            latest_line=line,
            mem_blob=_memory_blob(stack_memory),
        )
        try:
            data = self._complete_json_dict(prompts.MERGE_SESSION_GOAL_SYSTEM, user)
        except Exception as exc:
            logger.error("merge_session_goal LLM failed: %s", exc)
            return line
        if not isinstance(data, dict):
            return line
        merged = data.get("merged_goal")
        if not isinstance(merged, str) or not merged.strip():
            return line
        return merged.strip()

    # ------------------------------------------------------------------
    # Upfront planner
    # ------------------------------------------------------------------

    def plan_pipeline_upfront(
        self,
        *,
        user_goal: str,
        available_agents: List[Dict[str, Any]],
        stack_memory: Optional[List[Dict[str, Any]]] = None,
        max_steps: int = MAX_PIPELINE_STEPS,
    ) -> List[PlanStepSpec]:
        """Sync wrapper around :meth:`aplan_pipeline_upfront`.

        Returns ``[]`` on LLM / validation failure (caller should fall back or
        log-and-stop; director posts a chat error on empty plan).
        """
        import asyncio

        return asyncio.run(
            self.aplan_pipeline_upfront(
                user_goal=user_goal,
                available_agents=available_agents,
                stack_memory=stack_memory,
                max_steps=max_steps,
            )
        )

    async def aplan_pipeline_upfront(
        self,
        *,
        user_goal: str,
        available_agents: List[Dict[str, Any]],
        stack_memory: Optional[List[Dict[str, Any]]] = None,
        max_steps: int = MAX_PIPELINE_STEPS,
    ) -> List[PlanStepSpec]:
        """Plan the full pipeline ONCE for this user turn.

        Async canonical implementation. Use directly under ``asyncio.gather``
        / ``Semaphore`` for concurrent eval (single event loop avoids the
        cross-loop Future bug that ThreadPoolExecutor + ``asyncio.run`` hits
        with google.genai's async client). Sync callers go through
        :meth:`plan_pipeline_upfront`.
        """
        allowed = _allowed_ids(available_agents)
        if not allowed:
            return []
        catalog = _agents_catalog_for_prompt(available_agents)
        system = prompts.build_plan_system_prompt(
            core=self._core,
            allowed=allowed,
            catalog=catalog,
            max_plan_steps=max_steps,
        )
        user = prompts.build_plan_user_prompt(
            user_goal=user_goal,
            mem_blob=_memory_blob(stack_memory or []),
        )
        # Unified retry budget covering BOTH failure modes:
        #   (a) LLM samples `{"plan":[]}` despite the "never empty" prompt rule
        #   (b) LLM emits malformed JSON (missing `}` between array elements is a
        #       known gemini-2.5-flash flake under json_object mode), causing
        #       chat_json to raise ValueError. Earlier code returned [] on the
        #       initial exception without ever entering the retry loop.
        plan: List[PlanStepSpec] = []
        attempts = 3
        for attempt in range(attempts):
            try:
                data = await self._acomplete_json_dict(system, user)
                plan = _parse_plan(data, allowed, max_steps=max_steps)
            except Exception as exc:
                logger.error(
                    "aplan_pipeline_upfront attempt %d/%d failed: %s",
                    attempt + 1, attempts, exc,
                )
                plan = []
            if plan:
                break
            if attempt + 1 < attempts:
                logger.warning(
                    "aplan_pipeline_upfront attempt %d/%d empty/failed, retrying",
                    attempt + 1, attempts,
                )
        return plan

    # ------------------------------------------------------------------
    # Replanner
    # ------------------------------------------------------------------

    def replan_on_failure(
        self,
        *,
        user_goal: str,
        available_agents: List[Dict[str, Any]],
        failed_step: Dict[str, Any],
        pending_tail: List[Dict[str, Any]],
        completed_tail: List[Dict[str, Any]],
        max_steps: int = MAX_PIPELINE_STEPS,
    ) -> ReplanDecision:
        """Produce a replacement tail for a failed step.

        On LLM failure, malformed output, or empty plan, returns an empty
        ``new_tail`` — the director then advances past the failed step without
        replanning. ``MAX_REPLAN_ROUNDS`` caps total attempts.
        """
        allowed = _allowed_ids(available_agents)
        if not allowed:
            return ReplanDecision(rationale="empty catalog")
        catalog = _agents_catalog_for_prompt(available_agents)
        user = prompts.build_replan_user_prompt(
            allowed=allowed,
            catalog=catalog,
            user_goal=user_goal,
            failed_step_blob=_memory_blob([failed_step]),
            pending_tail_blob=_memory_blob(pending_tail),
            completed_blob=_memory_blob(completed_tail),
        )
        try:
            data = self._complete_json_dict(prompts.REPLAN_TAIL_SYSTEM, user)
        except Exception as exc:
            logger.error("replan_on_failure LLM failed: %s", exc)
            return ReplanDecision(rationale=f"replan LLM error: {exc}")
        if not isinstance(data, dict):
            return ReplanDecision(rationale="non-object replan JSON")
        new_tail = _parse_plan(data, allowed, max_steps=max_steps)
        rationale = str(data.get("rationale") or "").strip()
        if not new_tail:
            return ReplanDecision(rationale=rationale or "replan produced empty plan")
        return ReplanDecision(new_tail=new_tail, rationale=rationale)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_plan(
    data: Dict[str, Any],
    allowed: List[str],
    *,
    max_steps: int,
) -> List[PlanStepSpec]:
    plan_raw = data.get("plan")
    if not isinstance(plan_raw, list) or not plan_raw:
        logger.error("Plan JSON missing or empty `plan` list: %s", data)
        return []
    allowed_set = set(allowed)
    out: List[PlanStepSpec] = []
    for i, entry in enumerate(plan_raw):
        if not isinstance(entry, dict):
            logger.warning("Plan step %d not a dict, skipping: %r", i, entry)
            continue
        aid = entry.get("agent_id")
        if not isinstance(aid, str):
            logger.warning("Plan step %d missing agent_id, skipping", i)
            continue
        aid = aid.strip()
        if aid not in allowed_set:
            logger.warning("Plan step %d agent_id=%r not in catalog, skipping", i, aid)
            continue
        intent = str(entry.get("intent") or "").strip()
        out.append(PlanStepSpec(agent_id=aid, intent=intent))
        if len(out) >= max_steps:
            break
    return out
