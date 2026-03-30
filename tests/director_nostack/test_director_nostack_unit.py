"""Unit tests for ``director_nostack`` (no Task Stack, no live HTTP)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from director_nostack.director import DirectorNoStack
from director_nostack.director import (
    _latest_execution_summary,
    _prior_user_chat_lines,
    chat_content_as_user_text,
)
from director_nostack.router import LlmSubAgentPlanner, PipelineRouteDecision


@pytest.fixture
def mock_client() -> MagicMock:
    c = MagicMock()
    c.get_unread_messages.return_value = []
    c.get_all_agents.return_value = [
        {"id": "StoryAgent", "description": "story"},
        {"id": "ScreenplayAgent", "description": "screenplay"},
    ]
    c.get_workspace_memory_brief.return_value = {"global_memory": []}
    c.get_executions_by_task.return_value = []
    c.execute_agent.return_value = {
        "status": "COMPLETED",
        "error": None,
        "error_reasoning": None,
        "global_memory_brief": {
            "global_memory": [
                {
                    "task_id": "standalone_chat",
                    "agent_id": "StoryAgent",
                    "created_at": "2026-01-01T00:00:00",
                    "execution_result": {"status": "COMPLETED"},
                }
            ]
        },
    }
    return c


def test_cycle_no_unread_does_not_execute(mock_client: MagicMock) -> None:
    planner = MagicMock()
    d = DirectorNoStack(client=mock_client, planner=planner)
    d._cycle()
    planner.choose_pipeline_step.assert_not_called()
    mock_client.execute_agent.assert_not_called()


def test_pipeline_runs_once_then_router_done(mock_client: MagicMock) -> None:
    """First step run StoryAgent; second routing returns done → one execute."""
    mock_client.get_unread_messages.return_value = [
        {"id": "msg_1", "content": "Write a short film idea."}
    ]
    planner = MagicMock()
    planner.merge_session_goal.return_value = "Write a short film idea."
    planner.choose_pipeline_step.side_effect = [
        PipelineRouteDecision("StoryAgent", False, "start"),
        PipelineRouteDecision(None, True, "goal met"),
    ]

    call_n = {"n": 0}

    def executions_side_effect(_tid: str):
        call_n["n"] += 1
        if call_n["n"] <= 1:
            return []
        return [
            {
                "id": "exec_1",
                "status": "COMPLETED",
                "agent_id": "StoryAgent",
                "results": {},
                "error": None,
            }
        ]

    mock_client.get_executions_by_task.side_effect = executions_side_effect

    d = DirectorNoStack(client=mock_client, planner=planner)
    d._cycle()

    assert planner.choose_pipeline_step.call_count == 2
    first_kw = planner.choose_pipeline_step.call_args_list[0].kwargs
    second_kw = planner.choose_pipeline_step.call_args_list[1].kwargs
    assert first_kw["after_frontend_user_message"] is True
    assert second_kw["after_frontend_user_message"] is False
    mock_client.execute_agent.assert_called_once_with(
        "StoryAgent",
        d.task_id,
        execute_fields={"text": "Write a short film idea."},
    )
    mock_client.update_message_read_status.assert_called_once()


def test_pipeline_two_agents_then_done(mock_client: MagicMock) -> None:
    planner = MagicMock()
    planner.merge_session_goal.return_value = "Full film"
    planner.choose_pipeline_step.side_effect = [
        PipelineRouteDecision("StoryAgent", False, ""),
        PipelineRouteDecision("ScreenplayAgent", False, ""),
        PipelineRouteDecision(None, True, "ok"),
    ]
    mock_client.get_unread_messages.return_value = [{"id": "m1", "content": "Full film"}]

    n = {"v": 0}

    def exec_se(_tid: str):
        n["v"] += 1
        if n["v"] == 1:
            return []
        if n["v"] == 2:
            return [{"id": "e1", "agent_id": "StoryAgent", "status": "COMPLETED", "results": {}, "error": None}]
        return [
            {"id": "e1", "agent_id": "StoryAgent", "status": "COMPLETED", "results": {}, "error": None},
            {"id": "e2", "agent_id": "ScreenplayAgent", "status": "COMPLETED", "results": {}, "error": None},
        ]

    mock_client.get_executions_by_task.side_effect = exec_se

    d = DirectorNoStack(client=mock_client, planner=planner)
    d._cycle()

    assert mock_client.execute_agent.call_count == 2
    assert mock_client.execute_agent.call_args_list[0][0][0] == "StoryAgent"
    assert mock_client.execute_agent.call_args_list[1][0][0] == "ScreenplayAgent"


def test_prior_user_chat_lines_excludes_current_message(mock_client: MagicMock) -> None:
    mock_client.list_messages.return_value = [
        {
            "id": "a",
            "sender_type": "user",
            "content": "first ask",
            "timestamp": "2026-01-01T00:00:00",
        },
        {
            "id": "b",
            "sender_type": "user",
            "content": "second ask",
            "timestamp": "2026-01-02T00:00:00",
        },
    ]
    assert _prior_user_chat_lines(
        mock_client, current_user_message_id="b", max_lines=10
    ) == ["first ask"]


def test_chat_content_dict_serializes_full_json_no_goal_shortcut() -> None:
    """Structured message content is passed as JSON for merge LLM; no ``goal`` field extraction."""
    raw = {"goal": "ignored as sole field", "hint": "keep both"}
    out = chat_content_as_user_text(raw)
    assert '"goal"' in out and '"hint"' in out
    assert out == json.dumps(raw, ensure_ascii=False)


def test_merge_session_goal_no_prior_does_not_call_llm() -> None:
    llm = MagicMock()
    p = LlmSubAgentPlanner(llm_client=llm)
    assert (
        p.merge_session_goal(
            latest_user_message="  delta  ",
            global_memory=[],
            execution_summary=None,
        )
        == "delta"
    )
    llm.call.assert_not_called()


def test_pipeline_execute_uses_merged_goal_string(mock_client: MagicMock) -> None:
    """When planner.merge_session_goal returns a merged brief, execute_fields.text uses it."""
    mock_client.get_unread_messages.return_value = [{"id": "m1", "content": "change tone"}]
    planner = MagicMock()
    planner.merge_session_goal.return_value = "MERGED FULL BRIEF"
    planner.choose_pipeline_step.side_effect = [
        PipelineRouteDecision("StoryAgent", False, ""),
        PipelineRouteDecision(None, True, ""),
    ]
    n = {"v": 0}

    def exec_se(_tid: str):
        n["v"] += 1
        if n["v"] == 1:
            return []
        return [
            {
                "id": "e1",
                "agent_id": "StoryAgent",
                "status": "COMPLETED",
                "results": {},
                "error": None,
            }
        ]

    mock_client.get_executions_by_task.side_effect = exec_se

    d = DirectorNoStack(client=mock_client, planner=planner)
    d._cycle()

    planner.merge_session_goal.assert_called_once()
    mock_client.execute_agent.assert_called_once_with(
        "StoryAgent",
        d.task_id,
        execute_fields={"text": "MERGED FULL BRIEF"},
    )


def test_latest_execution_summary_shape(mock_client: MagicMock) -> None:
    mock_client.get_executions_by_task.return_value = [
        {"id": "a", "status": "FAILED"},
        {
            "id": "b",
            "status": "COMPLETED",
            "agent_id": "VideoAgent",
            "results": {"x": 1},
            "error": None,
        },
    ]
    s = _latest_execution_summary(mock_client, "tid")
    assert s is not None
    assert s["execution_id"] == "b"
    assert s["agent_id"] == "VideoAgent"
