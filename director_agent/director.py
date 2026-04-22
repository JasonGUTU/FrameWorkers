"""Upfront-plan Director.

Each user turn:
  1. Project current Plan Stack into a slim memory list.
  2. Merge the new user line with prior chat lines + stack memory.
  3. Planner LLM produces the **full pipeline** (list of ``PlanStepSpec``).
  4. One ``POST /api/plan-stack/modify`` batch persists the plan (create steps
     + ensure a PENDING layer + add steps to that layer + initial execution
     pointer).
  5. Loop: ``get_next_step`` → ``execute_agent`` → ``update_step_status`` →
     ``advance_execution_pointer``. On failure the replanner rewrites the
     remaining PENDING tail (replan); if it can't, the executor advances past
     the failed step.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Dict, List, Optional

from . import config
from .api_client import BackendAPIClient, BackendAPIError
from .router import LlmSubAgentPlanner, PlanStepSpec, ReplanDecision

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Content extraction + small utilities
# ---------------------------------------------------------------------------


def chat_content_as_user_text(raw: Any) -> str:
    """Normalize chat ``content`` into one string for the merge / planner LLM."""
    if raw is None:
        return ""
    if isinstance(raw, str):
        return raw.strip()
    if isinstance(raw, (dict, list)):
        return json.dumps(raw, ensure_ascii=False)
    return str(raw).strip()


def _post_director_quiet(client: BackendAPIClient, content: str) -> None:
    try:
        client.create_message(content, sender_type="director")
    except Exception:
        pass


def _prior_user_chat_lines(
    client: BackendAPIClient,
    *,
    current_user_message_id: Optional[str],
    max_lines: int,
) -> List[str]:
    if not current_user_message_id or max_lines <= 0:
        return []
    try:
        rows = client.list_messages()
    except Exception as exc:
        logger.warning("list_messages for merge failed: %s", exc)
        return []
    if not isinstance(rows, list):
        return []
    cur = str(current_user_message_id)
    tuples: List[tuple[str, str, str]] = []
    for m in rows:
        if not isinstance(m, dict):
            continue
        if str(m.get("sender_type") or "").lower() != "user":
            continue
        mid = str(m.get("id") or "")
        if mid == cur:
            continue
        txt = chat_content_as_user_text(m.get("content", ""))
        if not txt:
            continue
        ts = str(m.get("timestamp") or "")
        tuples.append((ts, mid, txt))
    tuples.sort(key=lambda x: x[0])
    texts = [t[2] for t in tuples]
    if len(texts) > max_lines:
        texts = texts[-max_lines:]
    return texts


# ---------------------------------------------------------------------------
# Stack projection / memory
# ---------------------------------------------------------------------------


def _slim_stack_row(step_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Project one full PlanStep dict into a memory-slim row."""
    description = step_payload.get("description") or {}
    agent_id = None
    intent = None
    if isinstance(description, dict):
        agent_id = description.get("agent_id")
        intent = description.get("intent")
    return {
        "step_id": step_payload.get("id"),
        "agent_id": agent_id,
        "status": step_payload.get("status"),
        "intent": intent,
        "results_summary": _trim_results(step_payload.get("results")),
    }


def _trim_results(results: Any, *, max_chars: int = 400) -> Any:
    """Keep results compact — LLM doesn't need full blobs in memory."""
    if results is None:
        return None
    try:
        text = json.dumps(results, ensure_ascii=False, default=str)
    except Exception:
        text = str(results)
    if len(text) > max_chars:
        return text[: max_chars - 3] + "..."
    return text


def _project_plan_stack_as_memory(
    client: BackendAPIClient,
    *,
    window: int,
) -> List[Dict[str, Any]]:
    """Read the Plan Stack and turn its steps into a chronological slim list."""
    try:
        layers = client.get_plan_stack()
    except Exception as exc:
        logger.warning("get_plan_stack failed: %s", exc)
        return []
    if not isinstance(layers, list):
        return []

    all_step_ids: List[str] = []
    for layer in layers:
        if not isinstance(layer, dict):
            continue
        steps = layer.get("steps") or []
        for entry in steps:
            if not isinstance(entry, dict):
                continue
            sid = entry.get("step_id")
            if isinstance(sid, str) and sid:
                all_step_ids.append(sid)

    if not all_step_ids:
        return []

    # Last ``window`` steps preserve recency and cap the prompt size.
    if window > 0 and len(all_step_ids) > window:
        all_step_ids = all_step_ids[-window:]

    slim: List[Dict[str, Any]] = []
    for sid in all_step_ids:
        try:
            step = client.get_step(sid)
        except Exception as exc:
            logger.warning("get_step(%s) failed during memory projection: %s", sid, exc)
            continue
        if isinstance(step, dict):
            slim.append(_slim_stack_row(step))
    return slim


# ---------------------------------------------------------------------------
# Plan persistence — one batch write
# ---------------------------------------------------------------------------


def _ensure_pending_layer_index(plan_stack: List[Dict[str, Any]]) -> Optional[int]:
    """Return the layer index of the highest existing layer, or ``None`` if empty."""
    if not isinstance(plan_stack, list) or not plan_stack:
        return None
    idx = -1
    for layer in plan_stack:
        if isinstance(layer, dict):
            li = layer.get("layer_index")
            if isinstance(li, int) and li > idx:
                idx = li
    return idx if idx >= 0 else None


def _persist_plan(
    client: BackendAPIClient,
    *,
    plan: List[PlanStepSpec],
    rationale: str = "",
) -> List[str]:
    """Batch-write a plan to the stack.

    Strategy: always append a **new** layer at the end of the stack so the
    new plan is visually separated from any prior turn's steps. All new
    PlanSteps go into that new layer, in order.

    Returns the list of created step_ids (order matches ``plan``).
    """
    if not plan:
        return []

    try:
        existing_layers = client.get_plan_stack()
    except Exception as exc:
        logger.warning("get_plan_stack before plan persist failed: %s", exc)
        existing_layers = []
    if not isinstance(existing_layers, list):
        existing_layers = []
    highest = _ensure_pending_layer_index(existing_layers)
    new_layer_index = (highest + 1) if highest is not None else 0

    descriptions = [
        {
            "description": {
                "agent_id": spec.agent_id,
                "intent": spec.intent,
                "plan_rationale": rationale or None,
            }
        }
        for spec in plan
    ]

    # Step 1: batch create all PlanSteps + a new layer.
    ops: List[Dict[str, Any]] = [
        {"type": "create_steps", "params": {"steps": descriptions}},
        {"type": "create_layers", "params": {"layers": [{"layer_index": new_layer_index}]}},
    ]
    try:
        resp = client.modify_plan_stack(ops)
    except Exception as exc:
        logger.error("modify_plan_stack (create) failed: %s", exc)
        return []
    if not resp.get("success"):
        logger.error("modify_plan_stack (create) reported errors: %s", resp.get("errors"))
        return []
    created_step_ids = resp.get("created_step_ids") or []
    if len(created_step_ids) != len(plan):
        logger.error(
            "modify_plan_stack returned %d step ids, expected %d",
            len(created_step_ids),
            len(plan),
        )
        return []

    # Step 2: add each step to the new layer (order-preserving).
    add_ops: List[Dict[str, Any]] = [
        {
            "type": "add_steps_to_layers",
            "params": {
                "additions": [
                    {"layer_index": new_layer_index, "step_id": sid}
                    for sid in created_step_ids
                ]
            },
        }
    ]
    try:
        add_resp = client.modify_plan_stack(add_ops)
    except Exception as exc:
        logger.error("modify_plan_stack (add_steps_to_layers) failed: %s", exc)
        return []
    if not add_resp.get("success"):
        logger.error(
            "modify_plan_stack (add_steps_to_layers) errors: %s",
            add_resp.get("errors"),
        )
        return []

    # Step 3: ensure execution pointer is live on the first step we just added.
    try:
        pointer = client.get_execution_pointer()
    except Exception:
        pointer = None
    if pointer is None:
        try:
            client.set_execution_pointer(
                layer_index=new_layer_index,
                step_index=0,
            )
        except Exception as exc:
            logger.warning("set_execution_pointer on new layer failed: %s", exc)

    return created_step_ids


# ---------------------------------------------------------------------------
# Execution loop
# ---------------------------------------------------------------------------


def _execute_planned_steps(
    client: BackendAPIClient,
    planner: LlmSubAgentPlanner,
    *,
    user_goal: str,
    agents: List[Dict[str, Any]],
) -> None:
    """Iterate the stack pointer until exhausted or safety budget hits."""
    budget_remaining = config.MAX_EXECUTIONS_PER_CYCLE
    replans_used = 0

    while budget_remaining > 0:
        budget_remaining -= 1
        try:
            next_step = client.get_next_step()
        except Exception as exc:
            logger.error("get_next_step failed: %s", exc)
            _post_director_quiet(
                client,
                f"[{config.DIRECTOR_AGENT_NAME}] get_next_step error, stopping: {exc}",
            )
            return
        if not next_step:
            # No more pending steps — plan fully executed.
            _post_director_quiet(
                client,
                f"[{config.DIRECTOR_AGENT_NAME}] Pipeline complete.",
            )
            return

        step_id = next_step.get("step_id")
        step_payload = next_step.get("step") or {}
        description = step_payload.get("description") if isinstance(step_payload, dict) else None
        agent_id = None
        if isinstance(description, dict):
            agent_id = description.get("agent_id")
        if not isinstance(agent_id, str) or not agent_id:
            logger.error("PlanStep %s has no agent_id in description; skipping", step_id)
            _safe_advance(client)
            continue

        existing_status = step_payload.get("status") if isinstance(step_payload, dict) else None
        if existing_status == "COMPLETED":
            # Stack advanced but pointer didn't. Just move on.
            _safe_advance(client)
            continue

        # Mark in-flight.
        try:
            client.update_step_status(step_id, "IN_PROGRESS")
        except Exception as exc:
            logger.warning("update_step_status(IN_PROGRESS) failed for %s: %s", step_id, exc)

        logger.info(
            "Executing plan step %s with agent %s (remaining budget %d)",
            step_id,
            agent_id,
            budget_remaining,
        )
        try:
            result = client.execute_agent(agent_id, step_id)
        except Exception as exc:
            logger.error("execute_agent failed for %s/%s: %s", step_id, agent_id, exc)
            _safe_mark(client, step_id, "FAILED")
            replans_used = _handle_failure(
                client,
                planner,
                agents=agents,
                user_goal=user_goal,
                failed_step_id=step_id,
                failed_agent_id=agent_id,
                failed_error=str(exc),
                replans_used=replans_used,
            )
            _safe_advance(client)
            continue

        status = str((result or {}).get("status") or "").upper()
        try:
            if status == "COMPLETED":
                client.update_step_status(step_id, "COMPLETED")
            else:
                # Assistant marks its own AgentExecution failure; propagate.
                client.update_step_status(step_id, "FAILED" if status == "FAILED" else "COMPLETED")
        except Exception as exc:
            logger.warning("update_step_status final state failed for %s: %s", step_id, exc)

        _announce_step(client, agent_id, status, result)

        if status == "FAILED":
            replans_used = _handle_failure(
                client,
                planner,
                agents=agents,
                user_goal=user_goal,
                failed_step_id=step_id,
                failed_agent_id=agent_id,
                failed_error=str((result or {}).get("error") or ""),
                replans_used=replans_used,
            )

        _safe_advance(client)

    _post_director_quiet(
        client,
        f"[{config.DIRECTOR_AGENT_NAME}] Pipeline reached per-cycle execution budget "
        f"({config.MAX_EXECUTIONS_PER_CYCLE}); stopping.",
    )


def _safe_advance(client: BackendAPIClient) -> None:
    try:
        client.advance_execution_pointer()
    except Exception as exc:
        logger.warning("advance_execution_pointer failed: %s", exc)


def _safe_mark(client: BackendAPIClient, step_id: str, status: str) -> None:
    try:
        client.update_step_status(step_id, status)
    except Exception as exc:
        logger.warning("update_step_status(%s, %s) failed: %s", step_id, status, exc)


def _announce_step(
    client: BackendAPIClient,
    agent_id: str,
    status: str,
    result: Optional[Dict[str, Any]],
) -> None:
    body = f"[{config.DIRECTOR_AGENT_NAME}] {agent_id} → {status or 'UNKNOWN'}"
    err = (result or {}).get("error")
    if err:
        body += f"\nerror: {err}"
    _post_director_quiet(client, body[:4000])


def _handle_failure(
    client: BackendAPIClient,
    planner: LlmSubAgentPlanner,
    *,
    agents: List[Dict[str, Any]],
    user_goal: str,
    failed_step_id: str,
    failed_agent_id: str,
    failed_error: str,
    replans_used: int,
) -> int:
    """Run the replanner if budget allows; rewrite the stack tail when asked.

    Returns the new ``replans_used`` counter.
    """
    if config.MAX_REPLAN_ROUNDS <= 0 or replans_used >= config.MAX_REPLAN_ROUNDS:
        return replans_used

    try:
        layers = client.get_plan_stack()
    except Exception:
        layers = []
    try:
        pointer = client.get_execution_pointer()
    except Exception:
        pointer = None

    completed_tail: List[Dict[str, Any]] = []
    pending_tail: List[Dict[str, Any]] = []
    for layer in layers if isinstance(layers, list) else []:
        if not isinstance(layer, dict):
            continue
        li = layer.get("layer_index")
        steps = layer.get("steps") or []
        for idx, entry in enumerate(steps):
            if not isinstance(entry, dict):
                continue
            sid = entry.get("step_id")
            if not sid:
                continue
            try:
                payload = client.get_step(sid)
            except Exception:
                continue
            slim = _slim_stack_row(payload if isinstance(payload, dict) else {})
            slim["layer_index"] = li
            slim["step_pos"] = idx
            status = (slim.get("status") or "").upper()
            if status in {"COMPLETED", "CANCELLED"}:
                completed_tail.append(slim)
            elif status == "PENDING":
                pending_tail.append(slim)

    failed_slim = {
        "step_id": failed_step_id,
        "agent_id": failed_agent_id,
        "status": "FAILED",
        "error": failed_error[:2000],
    }
    decision: ReplanDecision = planner.replan_on_failure(
        user_goal=user_goal,
        available_agents=agents,
        failed_step=failed_slim,
        pending_tail=pending_tail,
        completed_tail=completed_tail,
    )

    if decision.new_tail:
        # Remove all PENDING steps from the stack, then append a new layer with
        # the replanned tail so execution continues with the new plan.
        removals: List[Dict[str, Any]] = [
            {"layer_index": s.get("layer_index"), "step_id": s.get("step_id")}
            for s in pending_tail
            if s.get("step_id") and s.get("layer_index") is not None
        ]
        if removals:
            try:
                client.modify_plan_stack(
                    [{"type": "remove_steps_from_layers", "params": {"removals": removals}}]
                )
            except Exception as exc:
                logger.warning("replan: remove_steps_from_layers failed: %s", exc)
        _persist_plan(
            client,
            plan=decision.new_tail,
            rationale=f"replan after {failed_agent_id} FAILED: {decision.rationale[:300]}",
        )
        _post_director_quiet(
            client,
            f"[{config.DIRECTOR_AGENT_NAME}] Replanned tail ({len(decision.new_tail)} steps): "
            f"{decision.rationale}",
        )
        return replans_used + 1

    # No actionable decision (replan without a new tail after all retries).
    # Fall through — the executor will advance past the failed step on its own.
    if decision.rationale:
        _post_director_quiet(
            client,
            f"[{config.DIRECTOR_AGENT_NAME}] Replan produced no actionable tail ({decision.rationale}); advancing.",
        )
    return replans_used


# ---------------------------------------------------------------------------
# Top-level orchestration (one user turn)
# ---------------------------------------------------------------------------


def run_plan_pipeline(
    client: BackendAPIClient,
    planner: LlmSubAgentPlanner,
    *,
    agents: List[Dict[str, Any]],
    user_goal: str,
    current_user_message_id: Optional[str] = None,
) -> None:
    """Drive one user turn end-to-end: merge → upfront plan → persist → execute."""
    latest_line = (user_goal or "").strip()
    if not latest_line:
        return

    stack_memory = _project_plan_stack_as_memory(client, window=config.DIRECTOR_MEMORY_WINDOW)
    prior_lines = _prior_user_chat_lines(
        client,
        current_user_message_id=current_user_message_id,
        max_lines=config.MERGE_PRIOR_USER_LINES_MAX,
    )
    merged_goal = (
        planner.merge_session_goal(
            latest_user_message=latest_line,
            stack_memory=stack_memory,
            prior_user_chat_lines=prior_lines or None,
        ).strip()
        or latest_line
    )

    plan = planner.plan_pipeline_upfront(
        user_goal=merged_goal,
        available_agents=agents,
        stack_memory=stack_memory,
        max_steps=config.MAX_PIPELINE_STEPS,
    )
    if not plan:
        _post_director_quiet(
            client,
            f"[{config.DIRECTOR_AGENT_NAME}] Planner returned no plan; nothing to do.",
        )
        return

    created_step_ids = _persist_plan(
        client,
        plan=plan,
        rationale=f"upfront plan for: {merged_goal[:200]}",
    )
    if not created_step_ids:
        _post_director_quiet(
            client,
            f"[{config.DIRECTOR_AGENT_NAME}] Failed to persist plan to Plan Stack.",
        )
        return

    _post_director_quiet(
        client,
        f"[{config.DIRECTOR_AGENT_NAME}] Plan persisted ({len(created_step_ids)} steps): "
        + ", ".join(f"{spec.agent_id}" for spec in plan),
    )

    _execute_planned_steps(
        client,
        planner,
        user_goal=merged_goal,
        agents=agents,
    )


# ---------------------------------------------------------------------------
# Director process
# ---------------------------------------------------------------------------


class DirectorAgent:
    """Long-running process: poll chat → for each new user line, run ``run_plan_pipeline``."""

    def __init__(
        self,
        client: Optional[BackendAPIClient] = None,
        planner: Optional[LlmSubAgentPlanner] = None,
    ) -> None:
        self.client = client or BackendAPIClient()
        self.planner = planner or LlmSubAgentPlanner()
        self.running = False

    def start(self) -> None:
        self.running = True
        logger.info("%s starting (Upfront + Plan Stack)", config.DIRECTOR_AGENT_NAME)
        try:
            health = self.client.health_check()
            logger.info("Backend health: %s", health)
        except Exception as e:
            logger.error("Backend health check failed: %s", e)
            return

        while self.running:
            try:
                self._cycle()
            except Exception as e:
                logger.error("Cycle error: %s", e, exc_info=True)
            time.sleep(config.POLLING_INTERVAL)

    def stop(self) -> None:
        self.running = False

    def orchestrate_user_turn(
        self,
        *,
        user_goal: str,
        current_user_message_id: str,
        agents: List[Dict[str, Any]],
    ) -> None:
        """Test / embed hook: run one user turn without the polling loop."""
        run_plan_pipeline(
            self.client,
            self.planner,
            agents=agents,
            user_goal=user_goal,
            current_user_message_id=current_user_message_id,
        )

    def _cycle(self) -> None:
        unread = self.client.get_unread_messages(
            sender_type="user",
            check_director_read=True,
            check_user_read=False,
        )
        if not unread:
            return

        msg = unread[0]
        msg_id = msg.get("id")
        if not msg_id:
            return

        try:
            self.client.update_message_read_status(
                str(msg_id), director_read_status="READ"
            )
        except Exception as e:
            logger.error("Failed to mark message read: %s", e)
            return

        user_text = chat_content_as_user_text(msg.get("content", ""))
        if not user_text:
            logger.warning("Empty user message %s, skipping", msg_id)
            return

        try:
            agents = self.client.get_all_agents()
        except BackendAPIError as e:
            logger.error("No agents: %s", e)
            return
        if not agents:
            logger.error("Sub-agent catalog empty")
            return

        self.orchestrate_user_turn(
            user_goal=user_text,
            current_user_message_id=str(msg_id),
            agents=agents,
        )
