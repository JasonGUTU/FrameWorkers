from __future__ import annotations

import os
import sys
import types
from pathlib import Path
from types import SimpleNamespace

import pytest

# Make `dynamic-task-stack/src` package importable.
_repo_root = Path(__file__).resolve().parents[2]
_pkg_root = _repo_root / "dynamic-task-stack"
if str(_pkg_root) not in sys.path:
    sys.path.insert(0, str(_pkg_root))

# `src/__init__.py` imports app.py -> flask_cors.
if "flask_cors" not in sys.modules:
    flask_cors_stub = types.ModuleType("flask_cors")
    flask_cors_stub.CORS = lambda *args, **kwargs: None
    sys.modules["flask_cors"] = flask_cors_stub

from src.app import create_app
import src.assistant.routes as routes_module
import src.assistant.service as service_module
from src.assistant.storage import AssistantStorage


class _DummyPipelineResult:
    def __init__(self):
        self.output = SimpleNamespace(model_dump=lambda: {"summary": "integration ok"})
        self.asset_dict = None
        self.media_assets = []


class _DummyPipelineAgent:
    async def run(self, _typed_input, upstream=None, materialize_ctx=None):
        return _DummyPipelineResult()


class _DummyDescriptor:
    def __init__(self, name: str, asset_key: str, asset_type: str):
        self.agent_name = name
        self.asset_key = asset_key
        self.asset_type = asset_type
        self.catalog_entry = f"{name} integration descriptor"

    def build_equipped_agent(self, _llm):
        return _DummyPipelineAgent()

    def build_input(self, project_id, draft_id, assets, config):
        return {
            "project_id": project_id,
            "draft_id": draft_id,
            "assets": assets,
            "language": config.language,
        }

    def build_upstream(self, assets):
        return assets


class _DummyRegistry:
    def __init__(self, descriptors: dict[str, _DummyDescriptor]):
        self._descriptors = descriptors

    def get_descriptor(self, agent_id: str):
        return self._descriptors.get(agent_id)

    def gather_agents_info(self):
        agents = []
        capabilities = set()
        for name, desc in self._descriptors.items():
            caps = ["pipeline_agent", desc.asset_key]
            capabilities.update(caps)
            agents.append(
                {
                    "id": name,
                    "name": name,
                    "description": (desc.catalog_entry or "")[:200],
                    "version": "1.0.0",
                    "author": None,
                    "capabilities": caps,
                    "input_schema": {},
                    "output_schema": {},
                    "created_at": "",
                    "updated_at": "",
                }
            )
        return {
            "total_agents": len(agents),
            "agents": agents,
            "all_capabilities": sorted(capabilities),
            "agent_ids": [agent["id"] for agent in agents],
        }


@pytest.fixture
def assistant_http_client(tmp_path, monkeypatch):
    storage = AssistantStorage(runtime_base_path=tmp_path / "Runtime")
    registry = _DummyRegistry(
        descriptors={
            "DummyAgent": _DummyDescriptor(
                name="DummyAgent",
                asset_key="dummy_asset",
                asset_type="dummy_asset_type",
            )
        }
    )

    monkeypatch.setattr(routes_module, "assistant_storage", storage)
    monkeypatch.setattr(routes_module, "get_agent_registry", lambda: registry)
    monkeypatch.setattr(service_module, "get_agent_registry", lambda: registry)

    app = create_app({"TESTING": True})
    with app.test_client() as client:
        yield client


@pytest.fixture
def assistant_http_client_real_agents(tmp_path, monkeypatch):
    storage = AssistantStorage(runtime_base_path=tmp_path / "Runtime")
    monkeypatch.setattr(routes_module, "assistant_storage", storage)

    app = create_app({"TESTING": True})
    with app.test_client() as client:
        yield client


def test_assistant_e2e_http_flow_covers_core_endpoints(assistant_http_client):
    client = assistant_http_client

    # 1) Assistant singleton / discovery endpoints.
    assistant_resp = client.get("/api/assistant")
    assert assistant_resp.status_code == 200
    assert assistant_resp.get_json()["id"] == "assistant_global"

    sub_agents_resp = client.get("/api/assistant/sub-agents")
    assert sub_agents_resp.status_code == 200
    sub_agents = sub_agents_resp.get_json()
    assert "DummyAgent" in sub_agents["agent_ids"]

    sub_agent_resp = client.get("/api/assistant/sub-agents/DummyAgent")
    assert sub_agent_resp.status_code == 200
    sub_agent = sub_agent_resp.get_json()
    assert sub_agent["id"] == "DummyAgent"
    assert "pipeline_agent" in sub_agent["capabilities"]

    inputs_resp = client.get("/api/assistant/agents/DummyAgent/inputs")
    assert inputs_resp.status_code == 200
    assert inputs_resp.get_json()["agent_id"] == "DummyAgent"

    # 2) Simulate director creating a task through HTTP.
    create_task_resp = client.post(
        "/api/tasks/create",
        json={"description": {"goal": "integration task"}},
    )
    assert create_task_resp.status_code == 201
    task_id = create_task_resp.get_json()["id"]

    # 3) Simulate director delegating execution to assistant.
    execute_resp = client.post(
        "/api/assistant/execute",
        json={"agent_id": "DummyAgent", "task_id": task_id},
    )
    assert execute_resp.status_code == 200
    execution_payload = execute_resp.get_json()
    assert execution_payload["status"] == "COMPLETED"
    assert execution_payload["results"]["summary"] == "integration ok"
    execution_id = execution_payload["execution_id"]

    # 4) Execution history/detail endpoints.
    execution_resp = client.get(f"/api/assistant/executions/{execution_id}")
    assert execution_resp.status_code == 200
    assert execution_resp.get_json()["id"] == execution_id

    executions_resp = client.get(f"/api/assistant/executions/task/{task_id}")
    assert executions_resp.status_code == 200
    executions = executions_resp.get_json()
    assert len(executions) == 1
    assert executions[0]["agent_id"] == "DummyAgent"

    # 5) Workspace endpoints (summary/files/logs/memory/search).
    workspace_resp = client.get("/api/assistant/workspace")
    assert workspace_resp.status_code == 200
    assert workspace_resp.get_json()["workspace_id"]

    summary_resp = client.get("/api/assistant/workspace/summary")
    assert summary_resp.status_code == 200
    assert summary_resp.get_json()["log_count"] >= 1

    files_resp = client.get("/api/assistant/workspace/files")
    assert files_resp.status_code == 200
    files = files_resp.get_json()

    if files:
        file_id = files[0]["id"]
        file_meta_resp = client.get(f"/api/assistant/workspace/files/{file_id}")
        assert file_meta_resp.status_code == 200
        assert file_meta_resp.get_json()["id"] == file_id

    file_search_resp = client.get("/api/assistant/workspace/files/search?query=integration")
    assert file_search_resp.status_code == 200

    logs_resp = client.get("/api/assistant/workspace/logs")
    assert logs_resp.status_code == 200
    logs = logs_resp.get_json()
    assert any(log["resource_type"] == "execution" for log in logs)

    write_mem_resp = client.post(
        "/api/assistant/workspace/memory",
        json={"content": "integration-memory-note", "append": False},
    )
    assert write_mem_resp.status_code == 200

    memory_resp = client.get("/api/assistant/workspace/memory")
    assert memory_resp.status_code == 200
    assert "integration-memory-note" in memory_resp.get_json()["content"]

    search_resp = client.get("/api/assistant/workspace/search?query=integration")
    assert search_resp.status_code == 200


@pytest.mark.skipif(
    os.getenv("FW_ENABLE_LIVE_LLM_TESTS") != "1" or not os.getenv("OPENAI_API_KEY"),
    reason=(
        "Live LLM e2e test disabled. Set FW_ENABLE_LIVE_LLM_TESTS=1 and OPENAI_API_KEY "
        "to run."
    ),
)
@pytest.mark.parametrize(
    "agent_id,task_goal,additional_inputs",
    [
        (
            "StoryAgent",
            "Generate a concise story blueprint for a short film.",
            {
                "assets": {
                    "draft_idea": (
                        "A retired watchmaker discovers he can rewind one minute of time, "
                        "but only three times before midnight."
                    )
                }
            },
        ),
        (
            "ExamplePipelineAgent",
            "Summarize a source text into a concise structured output.",
            {
                "assets": {
                    "source_text": (
                        "A small team builds a lightweight task orchestration backend. "
                        "They prioritize clear API contracts, concise docs, and reliable tests."
                    )
                }
            },
        ),
    ],
)
def test_assistant_e2e_http_flow_with_real_agents(
    assistant_http_client_real_agents,
    agent_id,
    task_goal,
    additional_inputs,
):
    client = assistant_http_client_real_agents

    create_task_resp = client.post(
        "/api/tasks/create",
        json={"description": {"goal": task_goal}},
    )
    assert create_task_resp.status_code == 201
    task_id = create_task_resp.get_json()["id"]

    execute_resp = client.post(
        "/api/assistant/execute",
        json={
            "agent_id": agent_id,
            "task_id": task_id,
            "additional_inputs": additional_inputs,
        },
    )
    assert execute_resp.status_code == 200
    execution_payload = execute_resp.get_json()
    assert execution_payload["status"] == "COMPLETED"
    assert isinstance(execution_payload["results"], dict)
    assert execution_payload["results"].get("content")

    content = execution_payload["results"]["content"]
    if agent_id == "StoryAgent":
        assert content.get("logline")
    elif agent_id == "ExamplePipelineAgent":
        assert content.get("summary")
    else:
        raise AssertionError(f"Unexpected live test agent: {agent_id}")

    execution_id = execution_payload["execution_id"]
    execution_resp = client.get(f"/api/assistant/executions/{execution_id}")
    assert execution_resp.status_code == 200
    assert execution_resp.get_json()["status"] == "COMPLETED"
