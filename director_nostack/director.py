"""
No-stack **Director** orchestration: frontend chat I/O, planning / replanning (LLM), Assistant execute.

**Responsibilities (this module + :class:`DirectorNoStack`):**

- **Frontend (HTTP):** poll user unread messages, mark director-read, post director replies
  (same message API as Vue ``ChatWindow``).
- **Plan / replan / reasoning:** each user turn runs :func:`run_nostack_pipeline` — merge prior
  context via ``planner.merge_session_goal``, then a loop of ``planner.choose_pipeline_step``
  (``run`` vs ``done``) using fresh memory / execution summaries — that *is* replanning after
  every Assistant step.
- **Assistant:** ``execute_agent`` (returns summary + ``global_memory_brief``, not inlined ``results``),
  ``memory/brief``, ``executions``, sub-agent catalog — all via :class:`NoStackAPIClient`.

Prompt text lives in ``prompts.py``; JSON shape + LLM calls in ``router.LlmSubAgentPlanner``.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Dict, List, Optional

from .api_client import BackendAPIError, NoStackAPIClient
from . import config as nostack_config
from .config import DIRECTOR_AGENT_NAME, POLLING_INTERVAL, STANDALONE_TASK_ID
from .router import LlmSubAgentPlanner

logger = logging.getLogger(__name__)


def chat_content_as_user_text(raw: Any) -> str:
    """
    Turn chat message ``content`` into one string for ``merge_session_goal`` / routing seed.

    Plain text: strip. Structured ``dict`` / ``list``: **full JSON** (no ``goal`` shortcut) so
    intent stays intact for the merge LLM to interpret; we do not assume a schema.
    """
    if raw is None:
        return ""
    if isinstance(raw, str):
        return raw.strip()
    if isinstance(raw, (dict, list)):
        return json.dumps(raw, ensure_ascii=False)
    return str(raw).strip()


def _post_director_quiet(client: NoStackAPIClient, content: str) -> None:
    try:
        client.create_message(content, sender_type="director")
    except Exception:
        pass


def _global_memory_rows(brief: Dict[str, Any]) -> List[Dict[str, Any]]:
    gm = brief.get("global_memory") if isinstance(brief, dict) else []
    return gm if isinstance(gm, list) else []


def _prior_user_chat_lines(
    client: NoStackAPIClient,
    *,
    current_user_message_id: Optional[str],
    max_lines: int,
) -> List[str]:
    """Older user texts from ``GET /api/messages/list``, excluding the current message id."""
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


def _latest_execution_summary(
    client: NoStackAPIClient, task_id: str
) -> Optional[Dict[str, Any]]:
    try:
        executions = client.get_executions_by_task(task_id)
    except Exception as exc:
        logger.warning("Failed to fetch executions for %s: %s", task_id, exc)
        return None
    if not executions:
        return None
    latest = executions[-1]
    return {
        "task_id": task_id,
        "execution_id": latest.get("id"),
        "status": latest.get("status"),
        "agent_id": latest.get("agent_id"),
        "results": latest.get("results"),
        "error": latest.get("error"),
    }


def _short_chat_reply(payload: Dict[str, Any], max_chars: int = 6000) -> str:
    status = payload.get("status")
    err = payload.get("error")
    lines = [
        f"[{DIRECTOR_AGENT_NAME}] Assistant status: {status}",
    ]
    if err:
        lines.append(f"error: {err}")
    brief = payload.get("global_memory_brief")
    if isinstance(brief, dict):
        gm = brief.get("global_memory")
        if isinstance(gm, list) and gm:
            rows_out: List[Dict[str, Any]] = []
            for row in gm[:40]:
                if isinstance(row, dict):
                    rows_out.append(dict(row))
            blob = json.dumps(rows_out, ensure_ascii=False, default=str)
            if len(blob) > max_chars:
                blob = blob[: max_chars - 20] + "\n…(truncated)"
            lines.append(
                f"global_memory_brief ({len(gm)} slim rows):\n" + blob
            )
    body = "\n".join(lines)
    if len(body) > 12000:
        return body[:12000] + "\n…(truncated)"
    return body


def run_nostack_pipeline(
    client: NoStackAPIClient,
    planner: LlmSubAgentPlanner,
    *,
    task_id: str,
    agents: List[Dict[str, Any]],
    user_goal: str,
    current_user_message_id: Optional[str] = None,
) -> None:
    """
    One user message → merge (if prior context) → loop: route (``run``/``done``) → Assistant
    execute until ``done`` or error. Full behavior: package ``README.md``.
    """
    latest_line = user_goal.strip()
    if not latest_line:
        return

    brief0 = client.get_workspace_memory_brief(task_id=task_id)
    gm0 = _global_memory_rows(brief0)
    summary0 = _latest_execution_summary(client, task_id)
    prior_lines = _prior_user_chat_lines(
        client,
        current_user_message_id=current_user_message_id,
        max_lines=nostack_config.MERGE_PRIOR_USER_LINES_MAX,
    )
    goal_text = planner.merge_session_goal(
        latest_user_message=latest_line,
        global_memory=gm0,
        execution_summary=summary0,
        prior_user_chat_lines=prior_lines or None,
    ).strip() or latest_line

    last_agent_id: Optional[str] = None
    step = 0

    while True:
        brief = client.get_workspace_memory_brief(task_id=task_id)
        gm = _global_memory_rows(brief)

        summary = _latest_execution_summary(client, task_id)

        decision = planner.choose_pipeline_step(
            original_user_goal=goal_text,
            after_frontend_user_message=(step == 0),
            step_index=step,
            last_agent_id=last_agent_id,
            available_agents=agents,
            global_memory=gm,
            execution_summary=summary,
        )

        if decision.finished:
            msg_done = (
                f"[{DIRECTOR_AGENT_NAME}] Pipeline complete."
                + (f" ({decision.rationale})" if decision.rationale else "")
            )
            _post_director_quiet(client, msg_done)
            break

        if not decision.should_run:
            logger.error("Router stopped without done: %s", decision.rationale)
            _post_director_quiet(
                client,
                f"[{DIRECTOR_AGENT_NAME}] Routing failed: {decision.rationale or 'no agent'}",
            )
            break

        agent_id = decision.agent_id
        assert agent_id is not None
        execute_fields: Dict[str, Any] = {"text": goal_text}
        logger.info(
            "Pipeline step %s agent_id=%s task_id=%s",
            step + 1,
            agent_id,
            task_id,
        )
        try:
            result = client.execute_agent(
                agent_id,
                task_id,
                execute_fields=execute_fields,
            )
        except Exception as e:
            logger.error("execute_agent failed: %s", e, exc_info=True)
            _post_director_quiet(
                client,
                f"[{DIRECTOR_AGENT_NAME}] Execute failed at step {step + 1}: {e}",
            )
            break

        status = str(result.get("status") or "")
        if status == "FAILED" or result.get("error"):
            _post_director_quiet(
                client,
                f"[{DIRECTOR_AGENT_NAME}] Step {step + 1} ({agent_id}) failed: "
                f"{result.get('error') or status}",
            )
            break

        try:
            header = f"[{DIRECTOR_AGENT_NAME}] Step {step + 1}: **{agent_id}** → {status}\n"
            reply = header + _short_chat_reply(result)
            client.create_message(reply, sender_type="director")
        except Exception as e:
            logger.warning("Could not post chat reply: %s", e)

        last_agent_id = agent_id
        step += 1


class DirectorNoStack:
    """
    Long-running process: poll chat → for each new user line, run :func:`run_nostack_pipeline`.

    Owns **frontend I/O** (``self.client``), **fixed** ``task_id``, and **planner** (merge + per-step
    route). Planning/replanning is not duplicated here — it is implemented inside
    ``run_nostack_pipeline`` + ``LlmSubAgentPlanner``.
    """

    def __init__(
        self,
        client: Optional[NoStackAPIClient] = None,
        planner: Optional[LlmSubAgentPlanner] = None,
    ) -> None:
        self.client = client or NoStackAPIClient()
        self.planner = planner or LlmSubAgentPlanner()
        self.running = False
        self.task_id = STANDALONE_TASK_ID

    def start(self) -> None:
        self.running = True
        logger.info("%s starting (task_id=%s)", DIRECTOR_AGENT_NAME, self.task_id)
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
            time.sleep(POLLING_INTERVAL)

    def stop(self) -> None:
        self.running = False

    def orchestrate_user_turn(
        self,
        *,
        user_goal: str,
        current_user_message_id: str,
        agents: List[Dict[str, Any]],
    ) -> None:
        """Run merge + multi-step Assistant loop for one consumed user message (test / embed hook)."""
        run_nostack_pipeline(
            self.client,
            self.planner,
            task_id=self.task_id,
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
