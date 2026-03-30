"""
End-to-end: simulate the Vue chat path (``POST /api/messages/create`` as user) and run one
:class:`~director_nostack.director.DirectorNoStack` poll cycle against a real Flask app via
``test_client`` (no live port).

Router LLM is mocked; Assistant runs the stubbed ``NostackE2eAgent`` pipeline agent from
``conftest``.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from director_nostack.api_client import NoStackAPIClient
from director_nostack.director import DirectorNoStack
from director_nostack.router import PipelineRouteDecision

_ns_dir = Path(__file__).resolve().parent
if str(_ns_dir) not in sys.path:
    sys.path.insert(0, str(_ns_dir))
from flask_nostack_test_client import FlaskTestNoStackClient, post_user_chat_line


@pytest.mark.usefixtures("_stub_assistant_llm_hooks_for_nostack_e2e")
def test_e2e_user_message_triggers_assistant_and_director_chat(
    director_nostack_http_app,
    monkeypatch,
):
    """Frontend posts a user line → Director consumes unread → one execute → ``Pipeline complete``."""
    from director_nostack import director as director_mod

    task_id = "nostack_http_e2e_tid"
    monkeypatch.setattr(director_mod, "STANDALONE_TASK_ID", task_id)

    # User-facing goal (same shape as Vue ChatWindow): concrete brief for a short clip + story beat.
    user_brief = (
        "Generate about a 10-second video: a tiny paper boat drifts across a rainy puddle in an "
        "alley; a stray cat watches from a windowsill; the boat bumps a fallen leaf and spins—"
        "gentle, no dialogue, moody city twilight."
    )
    fc = director_nostack_http_app
    post_user_chat_line(fc, user_brief)

    planner = MagicMock()
    planner.merge_session_goal.return_value = user_brief
    planner.choose_pipeline_step.side_effect = [
        PipelineRouteDecision("NostackE2eAgent", False, "first agent"),
        PipelineRouteDecision(None, True, "goal met for test"),
    ]

    call_n = {"n": 0}

    def executions_side_effect(_tid: str):
        call_n["n"] += 1
        if call_n["n"] <= 1:
            return []
        return [
            {
                "id": "exec_e2e_1",
                "status": "COMPLETED",
                "agent_id": "NostackE2eAgent",
                "results": {"summary": "nostack e2e ok"},
                "error": None,
            }
        ]

    http = FlaskTestNoStackClient(fc)
    # Director cycle reads executions via the same client; second routing pass must see prior run.
    http.get_executions_by_task = MagicMock(side_effect=executions_side_effect)

    exec_calls: list[dict] = []

    def _trace_execute(agent_id, tid, execute_fields=None):
        exec_calls.append(
            {"agent_id": agent_id, "task_id": tid, "execute_fields": dict(execute_fields or {})}
        )
        return NoStackAPIClient.execute_agent(http, agent_id, tid, execute_fields=execute_fields)

    http.execute_agent = _trace_execute  # type: ignore[method-assign]

    d = DirectorNoStack(client=http, planner=planner)
    d._cycle()

    planner.merge_session_goal.assert_called_once()
    assert planner.choose_pipeline_step.call_count == 2
    assert len(exec_calls) == 1
    assert exec_calls[0]["agent_id"] == "NostackE2eAgent"
    assert exec_calls[0]["task_id"] == task_id
    assert "10-second" in (exec_calls[0]["execute_fields"].get("text") or "")

    ex = fc.get(f"/api/assistant/executions/task/{task_id}")
    assert ex.status_code == 200
    executions = ex.get_json()
    assert len(executions) == 1
    assert executions[0]["agent_id"] == "NostackE2eAgent"
    assert executions[0]["status"] == "COMPLETED"

    listed = fc.get("/api/messages/list").get_json()
    assert isinstance(listed, list)
    bodies = [str(m.get("content", "")) for m in listed if m.get("sender_type") == "director"]
    assert any("Step 1" in b and "NostackE2eAgent" in b for b in bodies)
    assert any("Pipeline complete" in b for b in bodies)


@pytest.mark.usefixtures("_stub_assistant_llm_hooks_for_nostack_e2e")
def test_e2e_run_nostack_pipeline_embed_hook_same_stack(
    director_nostack_http_app,
    monkeypatch,
):
    """Call :func:`director_nostack.director.run_nostack_pipeline` like an embedded host would."""
    from director_nostack import director as director_mod
    from director_nostack.director import run_nostack_pipeline

    task_id = "nostack_embed_e2e_tid"
    monkeypatch.setattr(director_mod, "STANDALONE_TASK_ID", task_id)

    embed_brief = (
        "Produce roughly 10 seconds of video: an old librarian closes the shop at blue hour, "
        "finds a bookmark tucked in a returned book with a note from someone they thought they'd "
        "never see again—quiet, emotional, one location."
    )
    fc = director_nostack_http_app
    msg_id = post_user_chat_line(fc, embed_brief)

    planner = MagicMock()
    planner.merge_session_goal.return_value = embed_brief
    planner.choose_pipeline_step.side_effect = [
        PipelineRouteDecision("NostackE2eAgent", False, ""),
        PipelineRouteDecision(None, True, ""),
    ]

    n = {"v": 0}

    def exec_se(_tid: str):
        n["v"] += 1
        if n["v"] == 1:
            return []
        return [
            {
                "id": "exec_emb",
                "status": "COMPLETED",
                "agent_id": "NostackE2eAgent",
                "results": {},
                "error": None,
            }
        ]

    http = FlaskTestNoStackClient(fc)
    http.get_executions_by_task = MagicMock(side_effect=exec_se)

    exec_calls: list[dict] = []

    def _trace_execute(agent_id, tid, execute_fields=None):
        exec_calls.append({"agent_id": agent_id, "task_id": tid})
        return NoStackAPIClient.execute_agent(http, agent_id, tid, execute_fields=execute_fields)

    http.execute_agent = _trace_execute  # type: ignore[method-assign]

    agents = http.get_all_agents()
    assert any(a.get("id") == "NostackE2eAgent" for a in agents)

    run_nostack_pipeline(
        http,
        planner,
        task_id=task_id,
        agents=agents,
        user_goal=embed_brief,
        current_user_message_id=msg_id,
    )

    assert len(exec_calls) == 1
    assert exec_calls[0]["agent_id"] == "NostackE2eAgent"
    brief = fc.get(f"/api/assistant/workspace/memory/brief?task_id={task_id}")
    assert brief.status_code == 200
    gm = brief.get_json().get("global_memory") or []
    assert len(gm) >= 1
