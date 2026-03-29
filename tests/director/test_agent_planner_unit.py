from __future__ import annotations

import json
import sys
from pathlib import Path

_repo_root = Path(__file__).resolve().parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from director_agent.reasoning import (
    LlmSubAgentPlanner,
    _parse_router_json,
)


def test_parse_router_json_strips_markdown_fence():
    raw = '```json\n{"agent_id": "StoryAgent", "rationale": "x"}\n```'
    data = _parse_router_json(raw)
    assert data["agent_id"] == "StoryAgent"


def test_choose_for_stack_task_uses_mock_llm():
    class _FakeClient:
        def call(self, messages, model=None, config=None):
            return {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "agent_id": "StoryAgent",
                                    "rationale": "start story",
                                }
                            )
                        }
                    }
                ]
            }

    agents = [
        {"id": "StoryAgent", "description": "story", "asset_key": "sb"},
        {"id": "VideoAgent", "description": "video", "asset_key": "v"},
    ]
    planner = LlmSubAgentPlanner(model="test-model", llm_client=_FakeClient())
    picked = planner.choose_for_stack_task(
        task_intent_text="make a film",
        available_agents=agents,
    )
    assert picked == "StoryAgent"


def test_choose_for_followup_uses_mock_llm():
    class _FakeClient:
        def call(self, messages, model=None, config=None):
            return {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "agent_id": "VideoAgent",
                                    "rationale": "continue pipeline",
                                }
                            )
                        }
                    }
                ]
            }

    agents = [
        {"id": "StoryAgent", "description": "story", "asset_key": "sb"},
        {"id": "VideoAgent", "description": "video", "asset_key": "v"},
    ]
    planner = LlmSubAgentPlanner(model="test-model", llm_client=_FakeClient())
    picked = planner.choose_for_followup(
        message_content="make it more cinematic",
        task_intent_text="goal: short film",
        available_agents=agents,
        global_memory=[{"agent_id": "StoryAgent", "execution_result": {"status": "COMPLETED"}}],
        execution_summary={"agent_id": "StoryAgent", "status": "COMPLETED"},
    )
    assert picked == "VideoAgent"


def test_choose_returns_none_when_id_not_in_catalog():
    class _FakeClient:
        def call(self, messages, model=None, config=None):
            return {
                "choices": [
                    {
                        "message": {
                            "content": '{"agent_id": "GhostAgent", "rationale": "no"}'
                        }
                    }
                ]
            }

    planner = LlmSubAgentPlanner(model="test-model", llm_client=_FakeClient())
    assert (
        planner.choose_for_stack_task(
            task_intent_text="x",
            available_agents=[{"id": "StoryAgent", "description": "", "asset_key": ""}],
        )
        is None
    )
