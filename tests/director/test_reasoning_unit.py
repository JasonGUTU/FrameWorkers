from __future__ import annotations

import sys
from pathlib import Path

# Make repository root importable in test runner environments.
_repo_root = Path(__file__).resolve().parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from director_agent.reasoning import ReasoningEngine


def test_reasoning_creates_execute_plan_for_existing_task_message():
    engine = ReasoningEngine()

    plan = engine.reason_and_plan(
        user_message={
            "id": "msg_1",
            "task_id": "task_1",
            "content": "Please regenerate video and audio with faster pacing.",
        }
    )

    assert plan["action"] == "execute_task"
    assert plan["target_task_id"] == "task_1"
    assert plan["preferred_agent_id"] == "VideoAgent"


def test_reasoning_prefers_explicit_agent_from_json_content():
    engine = ReasoningEngine()

    plan = engine.reason_and_plan(
        user_message={
            "id": "msg_2",
            "task_id": "task_2",
            "content": '{"rerun_agents": ["AudioAgent", "StoryboardAgent"]}',
        }
    )

    assert plan["action"] == "execute_task"
    assert plan["preferred_agent_id"] == "AudioAgent"


def test_select_agent_for_task_honors_preferred_agent_id():
    engine = ReasoningEngine()
    selected = engine.select_agent_for_task(
        task={
            "description": {
                "preferred_agent_id": "AudioAgent",
            }
        },
        available_agents=[
            {"id": "StoryAgent"},
            {"id": "AudioAgent"},
        ],
    )
    assert selected == "AudioAgent"


def test_reasoning_falls_back_to_latest_execution_agent():
    engine = ReasoningEngine()
    plan = engine.reason_and_plan(
        user_message={
            "id": "msg_3",
            "task_id": "task_3",
            "content": "Please optimize this output.",
        },
        task_summary={
            "task_id": "task_3",
            "agent_id": "VideoAgent",
            "status": "COMPLETED",
        },
    )
    assert plan["action"] == "execute_task"
    assert plan["preferred_agent_id"] == "VideoAgent"


def test_reasoning_can_suggest_agent_from_short_term_memory():
    engine = ReasoningEngine()
    plan = engine.reason_and_plan(
        user_message={
            "id": "msg_4",
            "task_id": "task_4",
            "content": "继续处理这个任务。",
        },
        short_term_memory=[
            {
                "kind": "execution_summary",
                "metadata": {"suggested_next_agent": "AudioAgent"},
            }
        ],
    )
    assert plan["action"] == "execute_task"
    assert plan["preferred_agent_id"] == "AudioAgent"
