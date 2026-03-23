from __future__ import annotations

import sys
from pathlib import Path

# Make repository root importable in test runner environments.
_repo_root = Path(__file__).resolve().parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from director_agent.director import DirectorAgent


class _ReasoningCapture:
    def __init__(self):
        self.last_task_summary = None
        self.last_short_term_memory = None

    def reason_and_plan(self, **kwargs):
        self.last_task_summary = kwargs.get("task_summary")
        self.last_short_term_memory = kwargs.get("short_term_memory")
        return {
            "action": "wait",
            "task_updates": [],
            "agent_id": None,
            "reasoning": "unit test",
        }

    def should_trigger_reflection(self, execution_result):
        return False


class _ApiBusy:
    def __init__(self):
        self.unread_called = False

    def get_all_tasks(self):
        return [{"id": "task_1", "status": "IN_PROGRESS"}]

    def get_unread_messages(self, **kwargs):
        self.unread_called = True
        return []


class _ApiIdle:
    def __init__(self):
        self.unread_called = False

    def get_all_tasks(self):
        return [{"id": "task_1", "status": "COMPLETED"}]

    def get_unread_messages(self, **kwargs):
        self.unread_called = True
        return [{"id": "msg_1", "task_id": "task_1", "content": "请优化这个结果"}]

    def update_message_read_status(self, msg_id, director_read_status=None, user_read_status=None):
        return {"id": msg_id}

    def get_task_stack(self):
        return []

    def get_execution_pointer(self):
        return None

    def get_executions_by_task(self, task_id):
        return [
            {
                "id": "exec_1",
                "status": "COMPLETED",
                "agent_id": "VideoAgent",
                "results": {"content": {"summary": "ok"}},
                "error": None,
            }
        ]

    def get_workspace_memory_brief(self, task_id=None, agent_id=None, short_term_limit=6):
        return {
            "task_id": task_id,
            "agent_id": agent_id,
            "short_term": [{"kind": "execution_summary", "content": "recent run"}],
            "long_term": [],
        }

    def get_next_task(self):
        return None


def test_director_waits_when_previous_execution_still_running():
    api = _ApiBusy()
    director = DirectorAgent(api_client=api)
    director.reasoning_engine = _ReasoningCapture()

    director._cycle()

    assert api.unread_called is False


def test_director_passes_latest_execution_summary_to_reasoning():
    api = _ApiIdle()
    reasoning = _ReasoningCapture()
    director = DirectorAgent(api_client=api)
    director.reasoning_engine = reasoning
    director._cycle()

    assert api.unread_called is True
    assert reasoning.last_task_summary is not None
    assert reasoning.last_task_summary["task_id"] == "task_1"
    assert reasoning.last_task_summary["agent_id"] == "VideoAgent"
    assert reasoning.last_short_term_memory is not None
    assert reasoning.last_short_term_memory[0]["kind"] == "execution_summary"


def test_director_passes_message_content_without_ltm_rewrite():
    api = _ApiIdle()
    director = DirectorAgent(api_client=api)

    inputs = director._build_assistant_inputs_for_execution(
        task_id="task_1",
        agent_id="VideoAgent",
        message_content="Please regenerate this video.",
    )

    assert inputs is not None
    assert "assets" in inputs
    assert inputs["assets"]["source_text"] == "Please regenerate this video."
    assert inputs["_memory_brief"]["long_term"] == []
