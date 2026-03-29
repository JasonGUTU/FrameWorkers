from __future__ import annotations

import sys
from pathlib import Path

# Make repository root importable in test runner environments.
_repo_root = Path(__file__).resolve().parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from director_agent.reasoning import ReasoningEngine


def test_reasoning_execute_task_when_message_has_task_id():
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
    assert "preferred_agent_id" not in plan


def test_reasoning_execute_task_when_json_content_has_task_id():
    engine = ReasoningEngine()

    plan = engine.reason_and_plan(
        user_message={
            "id": "msg_2",
            "content": '{"task_id": "task_2", "note": "retry"}',
        }
    )

    assert plan["action"] == "execute_task"
    assert plan["target_task_id"] == "task_2"


def test_reasoning_create_task_from_plain_message():
    engine = ReasoningEngine()

    plan = engine.reason_and_plan(
        user_message={
            "id": "msg_3",
            "content": "Write a short story about a robot.",
        }
    )

    assert plan["action"] == "create_task"
    assert plan["task_updates"][0]["description"]["overall_description"].startswith("Write")


def test_reasoning_wait_by_default():
    engine = ReasoningEngine()
    plan = engine.reason_and_plan()
    assert plan["action"] == "wait"
