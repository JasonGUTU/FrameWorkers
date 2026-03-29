from __future__ import annotations

import sys
import types
from pathlib import Path
from types import SimpleNamespace

import pytest

# Make `dynamic-task-stack/src` and repo root importable.
_repo_root = Path(__file__).resolve().parents[2]
_pkg_root = _repo_root / "dynamic-task-stack"
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))
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
from src.assistant.state_store import AssistantStateStore


class _DummyPipelineResult:
    def __init__(self):
        self.output = SimpleNamespace(model_dump=lambda: {"summary": "integration ok"})
        self.asset_dict = None
        self.media_assets = []


class _DummyPipelineAgent:
    async def run(self, _typed_input, input_bundle_v2=None, materialize_ctx=None):
        return _DummyPipelineResult()


class _EchoPipelineResult:
    def __init__(self, payload: dict):
        self.output = None
        self.asset_dict = payload
        self.media_assets = []


class _ProducerPipelineAgent:
    async def run(self, typed_input, input_bundle_v2=None, materialize_ctx=None):
        seed = typed_input.get("seed", "")
        return _EchoPipelineResult({"content": {"seed": seed}})


class _ConsumerPipelineAgent:
    async def run(self, typed_input, input_bundle_v2=None, materialize_ctx=None):
        observed = typed_input.get("observed_seed", "")
        return _EchoPipelineResult({"observed_seed": observed})


class _DummyDescriptor:
    def __init__(self, name: str, asset_key: str):
        self.agent_id = name
        self.asset_key = asset_key
        self.catalog_entry = f"{name} integration descriptor"

    def build_equipped_agent(self, _llm):
        return _DummyPipelineAgent()

    def build_input(self, task_id, input_bundle_v2, config):
        return {
            "task_id": task_id,
            "input_bundle_v2": input_bundle_v2,
            "language": config.language,
        }


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
                    "agent_type": "pipeline",
                    "capabilities": caps,
                    "asset_key": desc.asset_key,
                }
            )
        return {
            "total_agents": len(agents),
            "agents": agents,
            "all_capabilities": sorted(capabilities),
            "agent_ids": [agent["id"] for agent in agents],
        }


class _ProducerDescriptor:
    agent_id = "ProducerAgent"
    asset_key = "producer_asset"
    catalog_entry = "Producer integration descriptor"

    def build_equipped_agent(self, _llm):
        return _ProducerPipelineAgent()

    def build_input(self, task_id, input_bundle_v2, config):
        source_text = input_bundle_v2.get("source_text", "")
        if isinstance(source_text, dict):
            source_text = source_text.get("goal", "")
        return {
            "task_id": task_id,
            "seed": source_text,
            "language": config.language,
        }


class _ConsumerDescriptor:
    agent_id = "ConsumerAgent"
    asset_key = "consumer_asset"
    catalog_entry = "Consumer integration descriptor"

    def build_equipped_agent(self, _llm):
        return _ConsumerPipelineAgent()

    def build_input(self, task_id, input_bundle_v2, config):
        producer_asset = input_bundle_v2.get("producer_asset", {})
        return {
            "task_id": task_id,
            "observed_seed": producer_asset.get("content", {}).get("seed", ""),
            "language": config.language,
        }


@pytest.fixture
def assistant_http_client(tmp_path, monkeypatch):
    storage = AssistantStateStore(runtime_base_path=tmp_path / "Runtime")
    registry = _DummyRegistry(
        descriptors={
            "DummyAgent": _DummyDescriptor(
                name="DummyAgent",
                asset_key="dummy_asset",
            )
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

    # Step 1: Discover assistant singleton and available sub-agents.
    assistant_resp = client.get("/api/assistant")
    assert assistant_resp.status_code == 200
    assistant_payload = assistant_resp.get_json()
    assert assistant_payload["id"] == "assistant_global"
    assert assistant_payload["name"] == "Global Assistant"

    sub_agents_resp = client.get("/api/assistant/sub-agents")
    assert sub_agents_resp.status_code == 200
    sub_agents = sub_agents_resp.get_json()
    assert sub_agents["total_agents"] == 1
    assert "DummyAgent" in sub_agents["agent_ids"]

    sub_agent_resp = client.get("/api/assistant/sub-agents/DummyAgent")
    assert sub_agent_resp.status_code == 200
    sub_agent = sub_agent_resp.get_json()
    assert sub_agent["id"] == "DummyAgent"
    assert "pipeline_agent" in sub_agent["capabilities"]

    # Step 2: Create one task that downstream execution can reference.
    create_task_resp = client.post(
        "/api/tasks/create",
        json={"description": {"goal": "integration task"}},
    )
    assert create_task_resp.status_code == 201
    task_payload = create_task_resp.get_json()
    task_id = task_payload["id"]
    assert task_payload["description"] == {"goal": "integration task"}

    # Step 3: Execute DummyAgent against that task and validate result envelope.
    execute_resp = client.post(
        "/api/assistant/execute",
        json={
            "agent_id": "DummyAgent",
            "task_id": task_id,
            "execute_fields": {"text": task_payload["description"]["goal"]},
        },
    )
    assert execute_resp.status_code == 200
    execution_payload = execute_resp.get_json()
    assert execution_payload["task_id"] == task_id
    assert execution_payload.get("execution_id")
    assert execution_payload["workspace_id"]
    assert execution_payload["status"] == "COMPLETED"
    assert execution_payload["results"]["summary"] == "integration ok"

    # Step 4: Query execution detail and list APIs to confirm persistence.
    executions_resp = client.get(f"/api/assistant/executions/task/{task_id}")
    assert executions_resp.status_code == 200
    executions = executions_resp.get_json()
    assert len(executions) == 1
    assert executions[0]["agent_id"] == "DummyAgent"
    execution_id = executions[0]["id"]
    assert execution_id
    assert execution_payload["execution_id"] == execution_id
    assert executions[0]["task_id"] == task_id
    assert executions[0]["status"] == "COMPLETED"

    # Step 5: Validate workspace APIs (files/logs/memory).

    files_resp = client.get("/api/assistant/workspace/files")
    assert files_resp.status_code == 200
    files = files_resp.get_json()
    assert isinstance(files, list)

    if files:
        file_id = files[0]["id"]
        file_meta_resp = client.get(f"/api/assistant/workspace/files/{file_id}")
        assert file_meta_resp.status_code == 200
        assert file_meta_resp.get_json()["id"] == file_id

    logs_resp = client.get("/api/assistant/workspace/logs")
    assert logs_resp.status_code == 200
    logs = logs_resp.get_json()
    assert isinstance(logs, list)
    assert any(log["resource_type"] == "execution" for log in logs)

    add_entry_resp = client.post(
        "/api/assistant/workspace/memory/entries",
        json={
            "content": "Prefer concise pacing for edits.",
            "task_id": task_id,
        },
    )
    assert add_entry_resp.status_code == 201
    entry = add_entry_resp.get_json()
    assert set(entry.keys()) == {"content", "agent_id", "created_at", "execution_result", "task_id"}

    list_entries_resp = client.get(
        f"/api/assistant/workspace/memory/entries?task_id={task_id}"
    )
    assert list_entries_resp.status_code == 200
    entries = list_entries_resp.get_json()
    assert any(item["created_at"] == entry["created_at"] for item in entries)

    brief_resp = client.get(f"/api/assistant/workspace/memory/brief?task_id={task_id}")
    assert brief_resp.status_code == 200
    brief = brief_resp.get_json()
    assert "global_memory" in brief

def test_assistant_execute_allows_empty_execute_fields(assistant_http_client):
    client = assistant_http_client
    create_task_resp = client.post(
        "/api/tasks/create",
        json={"description": {"goal": "missing snapshot"}},
    )
    assert create_task_resp.status_code == 201
    task_id = create_task_resp.get_json()["id"]
    ok = client.post(
        "/api/assistant/execute",
        json={"agent_id": "DummyAgent", "task_id": task_id, "execute_fields": {}},
    )
    assert ok.status_code == 200


def test_assistant_execute_text_must_be_string_when_present(assistant_http_client):
    client = assistant_http_client
    create_task_resp = client.post(
        "/api/tasks/create",
        json={"description": {"goal": "ok"}},
    )
    assert create_task_resp.status_code == 201
    task_id = create_task_resp.get_json()["id"]
    bad = client.post(
        "/api/assistant/execute",
        json={
            "agent_id": "DummyAgent",
            "task_id": task_id,
            "execute_fields": {"text": {"not": "a string"}},
        },
    )
    assert bad.status_code == 400
    assert "string" in bad.get_json().get("error", "").lower()


def test_assistant_execute_ignores_memory_brief_key(assistant_http_client):
    client = assistant_http_client
    create_task_resp = client.post(
        "/api/tasks/create",
        json={"description": {"goal": "ok"}},
    )
    assert create_task_resp.status_code == 201
    task_id = create_task_resp.get_json()["id"]
    ok = client.post(
        "/api/assistant/execute",
        json={
            "agent_id": "DummyAgent",
            "task_id": task_id,
            "execute_fields": {"_memory_brief": "x"},
        },
    )
    assert ok.status_code == 200


def test_assistant_execute_invalid_execute_fields_type_returns_400(assistant_http_client):
    client = assistant_http_client
    create_task_resp = client.post(
        "/api/tasks/create",
        json={"description": {"goal": "x"}},
    )
    assert create_task_resp.status_code == 201
    task_id = create_task_resp.get_json()["id"]
    bad = client.post(
        "/api/assistant/execute",
        json={"agent_id": "DummyAgent", "task_id": task_id, "execute_fields": "nope"},
    )
    assert bad.status_code == 400
    assert "execute_fields" in bad.get_json().get("error", "")


def test_assistant_pipeline_http_flow_reuses_previous_agent_asset(
    assistant_http_client_pipeline,
):
    client = assistant_http_client_pipeline

    create_task_resp = client.post(
        "/api/tasks/create",
        json={"description": {"goal": "chain pipeline assets over http"}},
    )
    assert create_task_resp.status_code == 201
    task_payload = create_task_resp.get_json()
    task_id = task_payload["id"]
    ef = {"text": task_payload["description"]["goal"]}

    producer_resp = client.post(
        "/api/assistant/execute",
        json={
            "agent_id": "ProducerAgent",
            "task_id": task_id,
            "execute_fields": ef,
        },
    )
    assert producer_resp.status_code == 200
    producer_payload = producer_resp.get_json()
    assert producer_payload["task_id"] == task_id
    assert producer_payload["status"] == "COMPLETED"
    assert producer_payload["results"]["content"]["seed"] == "chain pipeline assets over http"

    consumer_resp = client.post(
        "/api/assistant/execute",
        json={
            "agent_id": "ConsumerAgent",
            "task_id": task_id,
            "execute_fields": ef,
        },
    )
    assert consumer_resp.status_code == 200
    consumer_payload = consumer_resp.get_json()
    assert consumer_payload["task_id"] == task_id
    assert consumer_payload["status"] == "COMPLETED"
    assert (
        consumer_payload["results"]["observed_seed"]
        == "chain pipeline assets over http"
    )


def test_assistant_pipeline_execution_inputs_include_global_memory_list(
    assistant_http_client_pipeline,
):
    client = assistant_http_client_pipeline

    create_task_resp = client.post(
        "/api/tasks/create",
        json={"description": {"goal": "check global_memory on inputs"}},
    )
    assert create_task_resp.status_code == 201
    task_payload = create_task_resp.get_json()
    task_id = task_payload["id"]
    ef = {"text": task_payload["description"]["goal"]}

    client.post(
        "/api/assistant/execute",
        json={"agent_id": "ProducerAgent", "task_id": task_id, "execute_fields": ef},
    )
    consumer_resp = client.post(
        "/api/assistant/execute",
        json={"agent_id": "ConsumerAgent", "task_id": task_id, "execute_fields": ef},
    )
    assert consumer_resp.status_code == 200
    executions_resp = client.get(f"/api/assistant/executions/task/{task_id}")
    assert executions_resp.status_code == 200
    executions = executions_resp.get_json()
    consumer_exec = next(e for e in executions if e["agent_id"] == "ConsumerAgent")
    gm = consumer_exec["inputs"].get("global_memory")
    assert isinstance(gm, list)
