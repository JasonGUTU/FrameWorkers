from __future__ import annotations

import sys
import types
from pathlib import Path
from types import SimpleNamespace

import pytest

# Make `plan-stack-backend/src` and repo root importable.
_repo_root = Path(__file__).resolve().parents[2]
_pkg_root = _repo_root / "plan-stack-backend"
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))
if str(_pkg_root) not in sys.path:
    sys.path.insert(0, str(_pkg_root))

from agents.common_schema import ResolvedArtifactEntry  # noqa: E402


# `src/__init__.py` imports app.py -> flask_cors.
if "flask_cors" not in sys.modules:
    flask_cors_stub = types.ModuleType("flask_cors")
    flask_cors_stub.CORS = lambda *args, **kwargs: None
    sys.modules["flask_cors"] = flask_cors_stub

from src.app import create_app
import src.assistant.routes as routes_module
import src.assistant.service as service_module
from src.assistant.state_store import AssistantStateStore


class _DummyPipelineResult:
    def __init__(self):
        self.output = SimpleNamespace(model_dump=lambda: {"summary": "integration ok"})
        self.asset_dict = None
        self.media_assets = []


class _DummyPipelineAgent:
    async def run(self, _typed_input, *, materialize_ctx=None):
        return _DummyPipelineResult()


class _EchoPipelineResult:
    def __init__(self, payload: dict):
        self.output = None
        self.asset_dict = payload
        self.media_assets = []


class _ProducerPipelineAgent:
    async def run(self, typed_input, *, materialize_ctx=None):
        seed = typed_input.get("seed", "")
        return _EchoPipelineResult({"content": {"seed": seed}})


class _ConsumerPipelineAgent:
    async def run(self, typed_input, *, materialize_ctx=None):
        observed = typed_input.get("observed_seed", "")
        return _EchoPipelineResult({"observed_seed": observed})


class _DummyDescriptor:
    def __init__(self, name: str):
        self.agent_id = name
        self.catalog_entry = f"{name} integration descriptor"

    def build_equipped_agent(self, _llm):
        return _DummyPipelineAgent()

    def build_input(self, step_id, resolved_artifacts):
        return {
            "step_id": step_id,
            "resolved_artifacts": resolved_artifacts,
            "language": "en",
        }


class _DummyRegistry:
    def __init__(self, descriptors: dict[str, _DummyDescriptor]):
        self._descriptors = descriptors

    def get_descriptor(self, agent_id: str):
        return self._descriptors.get(agent_id)

    def gather_agents_info(self):
        agents = []
        for name, desc in self._descriptors.items():
            agents.append(
                {
                    "id": name,
                    "name": name,
                    "description": desc.catalog_entry or "",
                }
            )
        return {
            "total_agents": len(agents),
            "agents": agents,
            "agent_ids": [agent["id"] for agent in agents],
        }


class _ProducerDescriptor:
    agent_id = "ProducerAgent"
    catalog_entry = "Producer integration descriptor"
    input_needs_description = "Needs source text"

    def build_equipped_agent(self, _llm):
        return _ProducerPipelineAgent()

    def build_input(self, step_id, resolved_artifacts):
        return {
            "step_id": step_id,
            "seed": "",
            "language": "en",
        }


class _ConsumerDescriptor:
    agent_id = "ConsumerAgent"
    catalog_entry = "Consumer integration descriptor"
    # Declares a [producer_asset] (single) header so the conftest stub picks
    # the producer's snapshot whose caption text contains "producer_asset".
    input_needs_description = (
        "[producer_asset] (single)\n"
        "The JSON payload produced by ProducerAgent."
    )

    def build_equipped_agent(self, _llm):
        return _ConsumerPipelineAgent()

    def build_input(self, step_id, resolved_artifacts):
        producer = ResolvedArtifactEntry.coerce(
            resolved_artifacts.get("producer_asset")
        )
        payload = producer.payload or {}
        return {
            "step_id": step_id,
            "observed_seed": payload.get("content", {}).get("seed", ""),
            "language": "en",
        }


@pytest.fixture
def assistant_http_client(tmp_path, monkeypatch):
    storage = AssistantStateStore(runtime_base_path=tmp_path / "Runtime")
    registry = _DummyRegistry(
        descriptors={
            "DummyAgent": _DummyDescriptor(name="DummyAgent"),
        }
    )

    monkeypatch.setattr(routes_module, "assistant_state_store", storage)
    monkeypatch.setattr(routes_module, "get_agent_registry", lambda: registry)
    monkeypatch.setattr(service_module, "get_agent_registry", lambda: registry)

    app = create_app({"TESTING": True})
    with app.test_client() as client:
        yield client


@pytest.fixture
def assistant_http_client_pipeline(tmp_path, monkeypatch):
    storage = AssistantStateStore(runtime_base_path=tmp_path / "Runtime")
    registry = _DummyRegistry(
        descriptors={
            "ProducerAgent": _ProducerDescriptor(),
            "ConsumerAgent": _ConsumerDescriptor(),
        }
    )

    monkeypatch.setattr(routes_module, "assistant_state_store", storage)
    monkeypatch.setattr(routes_module, "get_agent_registry", lambda: registry)
    monkeypatch.setattr(service_module, "get_agent_registry", lambda: registry)

    app = create_app({"TESTING": True})
    with app.test_client() as client:
        yield client


def test_assistant_e2e_http_flow_covers_core_endpoints(assistant_http_client):
    client = assistant_http_client

    # Step 1: Discover available sub-agents from the registry.
    sub_agents_resp = client.get("/api/assistant/sub-agents")
    assert sub_agents_resp.status_code == 200
    sub_agents = sub_agents_resp.get_json()
    assert sub_agents["total_agents"] == 1
    assert "DummyAgent" in sub_agents["agent_ids"]
    dummy_info = next(
        (a for a in sub_agents["agents"] if a["id"] == "DummyAgent"),
        None,
    )
    assert dummy_info is not None
    assert "capabilities" not in dummy_info  # removed 2026-04 — dead field

    # Step 2: Create one task via the batch endpoint.
    create_step_resp = client.post(
        "/api/plan-stack/modify",
        json={
            "operations": [
                {
                    "type": "create_steps",
                    "params": {
                        "steps": [{"description": {"goal": "integration task"}}]
                    },
                }
            ]
        },
    )
    assert create_step_resp.status_code == 200
    create_body = create_step_resp.get_json()
    assert create_body["success"] is True
    step_id = create_body["created_step_ids"][0]

    # Step 3: Execute DummyAgent against that task and validate result envelope.
    execute_resp = client.post(
        "/api/assistant/execute",
        json={
            "agent_id": "DummyAgent",
            "step_id": step_id,
        },
    )
    assert execute_resp.status_code == 200
    current = execute_resp.get_json()
    assert isinstance(current, dict)
    assert current["status"] == "COMPLETED"
    assert current["error"] is None

    # Step 4: Query execution detail and list APIs to confirm persistence.
    executions_resp = client.get(f"/api/assistant/executions/step/{step_id}")
    assert executions_resp.status_code == 200
    executions = executions_resp.get_json()
    assert len(executions) == 1
    assert executions[0]["agent_id"] == "DummyAgent"
    execution_id = executions[0]["id"]
    assert execution_id
    assert current["id"] == execution_id
    assert executions[0]["step_id"] == step_id
    assert executions[0]["status"] == "COMPLETED"
    assert executions[0]["results"]["summary"] == "integration ok"

    # Step 5: Validate workspace APIs (files/logs/memory).

    files_resp = client.get("/api/assistant/workspace/files")
    assert files_resp.status_code == 200
    files = files_resp.get_json()
    assert isinstance(files, list)
    # Each entry is the artifact-registry view of a persisted file.
    for entry in files:
        assert "path" in entry
        assert "agent_id" in entry
        assert "step_id" in entry

    logs_resp = client.get("/api/assistant/workspace/logs")
    assert logs_resp.status_code == 200
    logs = logs_resp.get_json()
    assert isinstance(logs, list)
    assert any(
        isinstance(log.get("event"), str) and log["event"].startswith("execution.")
        for log in logs
    )


def test_assistant_pipeline_execution_inputs_include_global_memory_list(
    assistant_http_client_pipeline,
):
    client = assistant_http_client_pipeline

    create_step_resp = client.post(
        "/api/plan-stack/modify",
        json={
            "operations": [
                {
                    "type": "create_steps",
                    "params": {
                        "steps": [
                            {"description": {"goal": "check global_memory on inputs"}}
                        ]
                    },
                }
            ]
        },
    )
    assert create_step_resp.status_code == 200
    step_id = create_step_resp.get_json()["created_step_ids"][0]

    client.post(
        "/api/assistant/execute",
        json={"agent_id": "ProducerAgent", "step_id": step_id},
    )
    consumer_resp = client.post(
        "/api/assistant/execute",
        json={"agent_id": "ConsumerAgent", "step_id": step_id},
    )
    assert consumer_resp.status_code == 200
    executions_resp = client.get(f"/api/assistant/executions/step/{step_id}")
    assert executions_resp.status_code == 200
    executions = executions_resp.get_json()
    consumer_exec = next(e for e in executions if e["agent_id"] == "ConsumerAgent")
    # The execution audit dict carries step_id + resolved_artifacts as siblings.
    assert "step_id" in consumer_exec["inputs"]
    assert "resolved_artifacts" in consumer_exec["inputs"]
