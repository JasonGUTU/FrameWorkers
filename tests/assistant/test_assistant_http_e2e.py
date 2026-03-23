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
from src.assistant.state_store import AssistantStateStore
from inference.clients import LLMClient


def _is_live_llm_env_ready() -> tuple[bool, str]:
    """Check whether live LLM e2e preconditions are satisfied."""
    if os.getenv("FW_ENABLE_LIVE_LLM_TESTS") != "1":
        return (
            False,
            "Live LLM e2e test disabled. Set FW_ENABLE_LIVE_LLM_TESTS=1 to run.",
        )

    try:
        client = LLMClient()
        resolved_model = client.model or client.default_model
        provider = client.resolve_provider_for_model(resolved_model)
        routing = client.get_runtime_routing()
        provider_key_env = (
            routing.get("provider_key_env", {}).get(provider)
            if isinstance(routing, dict)
            else None
        ) or f"{provider.upper()}_API_KEY"
        key_value = os.getenv(provider_key_env, "").strip()
    except Exception as exc:
        return False, f"Live LLM e2e precheck failed: {exc}"

    if not key_value:
        return (
            False,
            (
                "Live LLM e2e test missing provider key. "
                f"Set {provider_key_env} or configure routing/api_keys."
            ),
        )

    return True, ""


_LIVE_READY, _LIVE_SKIP_REASON = _is_live_llm_env_ready()


class _DummyPipelineResult:
    def __init__(self):
        self.output = SimpleNamespace(model_dump=lambda: {"summary": "integration ok"})
        self.asset_dict = None
        self.media_assets = []


class _DummyPipelineAgent:
    async def run(self, _typed_input, upstream=None, materialize_ctx=None):
        return _DummyPipelineResult()


class _EchoPipelineResult:
    def __init__(self, payload: dict):
        self.output = None
        self.asset_dict = payload
        self.media_assets = []


class _ProducerPipelineAgent:
    async def run(self, typed_input, upstream=None, materialize_ctx=None):
        seed = typed_input.get("seed", "")
        return _EchoPipelineResult({"content": {"seed": seed}})


class _ConsumerPipelineAgent:
    async def run(self, typed_input, upstream=None, materialize_ctx=None):
        observed = typed_input.get("observed_seed", "")
        return _EchoPipelineResult({"observed_seed": observed})


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
                    "agent_type": "pipeline",
                    "capabilities": caps,
                    "asset_key": desc.asset_key,
                    "asset_type": getattr(desc, "asset_type", ""),
                }
            )
        return {
            "total_agents": len(agents),
            "agents": agents,
            "all_capabilities": sorted(capabilities),
            "agent_ids": [agent["id"] for agent in agents],
        }


class _ProducerDescriptor:
    agent_name = "ProducerAgent"
    asset_key = "producer_asset"
    asset_type = "producer_asset_type"
    catalog_entry = "Producer integration descriptor"

    def build_equipped_agent(self, _llm):
        return _ProducerPipelineAgent()

    def build_input(self, project_id, draft_id, assets, config):
        draft_idea = assets.get("draft_idea", "")
        if isinstance(draft_idea, dict):
            draft_idea = draft_idea.get("goal", "")
        return {
            "project_id": project_id,
            "draft_id": draft_id,
            "seed": draft_idea,
            "language": config.language,
        }

    def build_upstream(self, assets):
        return assets


class _ConsumerDescriptor:
    agent_name = "ConsumerAgent"
    asset_key = "consumer_asset"
    asset_type = "consumer_asset_type"
    upstream_keys = ["producer_asset"]
    user_text_key = ""
    catalog_entry = "Consumer integration descriptor"

    def build_equipped_agent(self, _llm):
        return _ConsumerPipelineAgent()

    def build_input(self, project_id, draft_id, assets, config):
        producer_asset = assets.get("producer_asset", {})
        return {
            "project_id": project_id,
            "draft_id": draft_id,
            "observed_seed": producer_asset.get("content", {}).get("seed", ""),
            "language": config.language,
        }

    def build_upstream(self, assets):
        return assets


@pytest.fixture
def assistant_http_client(tmp_path, monkeypatch):
    storage = AssistantStateStore(runtime_base_path=tmp_path / "Runtime")
    registry = _DummyRegistry(
        descriptors={
            "DummyAgent": _DummyDescriptor(
                name="DummyAgent",
                asset_key="dummy_asset",
                asset_type="dummy_asset_type",
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


@pytest.fixture
def assistant_http_client_real_agents(tmp_path, monkeypatch):
    storage = AssistantStateStore(runtime_base_path=tmp_path / "Runtime")
    monkeypatch.setattr(routes_module, "assistant_state_store", storage)

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

    # 5) Workspace endpoints (summary/files/logs/structured-memory/search).
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

    insights_resp = client.get("/api/assistant/workspace/logs/insights?top_k=3")
    assert insights_resp.status_code == 200
    insights = insights_resp.get_json()
    assert "totals" in insights
    assert "breakdown" in insights

    add_entry_resp = client.post(
        "/api/assistant/workspace/memory/entries",
        json={
            "content": "Prefer concise pacing for edits.",
            "tier": "short_term",
            "kind": "note",
            "priority": 4,
            "task_id": task_id,
        },
    )
    assert add_entry_resp.status_code == 201
    entry = add_entry_resp.get_json()
    assert entry["tier"] == "short_term"

    list_entries_resp = client.get(
        f"/api/assistant/workspace/memory/entries?tier=short_term&task_id={task_id}"
    )
    assert list_entries_resp.status_code == 200
    entries = list_entries_resp.get_json()
    assert any(item["id"] == entry["id"] for item in entries)

    ltm_reject = client.post(
        "/api/assistant/workspace/memory/entries",
        json={"content": "should fail", "tier": "long_term"},
    )
    assert ltm_reject.status_code == 400

    brief_resp = client.get(f"/api/assistant/workspace/memory/brief?task_id={task_id}")
    assert brief_resp.status_code == 200
    brief = brief_resp.get_json()
    assert "short_term" in brief
    assert brief.get("long_term") == []

    search_resp = client.get("/api/assistant/workspace/search?query=integration")
    assert search_resp.status_code == 200


def test_director_http_message_flow_supports_poll_and_read_ack(assistant_http_client):
    client = assistant_http_client

    create_message_resp = client.post(
        "/api/messages/create",
        json={"content": "please run assistant task", "sender_type": "director"},
    )
    assert create_message_resp.status_code == 201
    message = create_message_resp.get_json()
    message_id = message["id"]
    assert message["sender_type"] == "director"
    assert message["director_read_status"] == "UNREAD"

    unread_resp = client.get(
        "/api/messages/unread?sender_type=director&check_director_read=true"
    )
    assert unread_resp.status_code == 200
    unread_messages = unread_resp.get_json()
    assert any(item["id"] == message_id for item in unread_messages)

    mark_read_resp = client.put(
        f"/api/messages/{message_id}/read-status",
        json={"director_read_status": "READ"},
    )
    assert mark_read_resp.status_code == 200
    assert mark_read_resp.get_json()["director_read_status"] == "READ"

    unread_after_ack_resp = client.get(
        "/api/messages/unread?sender_type=director&check_director_read=true"
    )
    assert unread_after_ack_resp.status_code == 200
    unread_after_ack = unread_after_ack_resp.get_json()
    assert all(item["id"] != message_id for item in unread_after_ack)


def test_assistant_pipeline_http_flow_reuses_previous_agent_asset(
    assistant_http_client_pipeline,
):
    client = assistant_http_client_pipeline

    create_task_resp = client.post(
        "/api/tasks/create",
        json={"description": {"goal": "chain pipeline assets over http"}},
    )
    assert create_task_resp.status_code == 201
    task_id = create_task_resp.get_json()["id"]

    producer_resp = client.post(
        "/api/assistant/execute",
        json={"agent_id": "ProducerAgent", "task_id": task_id},
    )
    assert producer_resp.status_code == 200
    producer_payload = producer_resp.get_json()
    assert producer_payload["status"] == "COMPLETED"
    assert producer_payload["results"]["content"]["seed"] == "chain pipeline assets over http"

    consumer_resp = client.post(
        "/api/assistant/execute",
        json={"agent_id": "ConsumerAgent", "task_id": task_id},
    )
    assert consumer_resp.status_code == 200
    consumer_payload = consumer_resp.get_json()
    assert consumer_payload["status"] == "COMPLETED"
    assert (
        consumer_payload["results"]["observed_seed"]
        == "chain pipeline assets over http"
    )


@pytest.mark.parametrize(
    "method,path,payload,expected_status,error_substring",
    [
        (
            "post",
            "/api/assistant/execute",
            {},
            400,
            "Invalid JSON body",
        ),
        (
            "get",
            "/api/assistant/workspace/files/search",
            None,
            400,
            "Query parameter required",
        ),
        (
            "get",
            "/api/assistant/workspace/search",
            None,
            400,
            "Query parameter required",
        ),
        (
            "get",
            "/api/assistant/workspace/logs/insights?top_k=0",
            None,
            400,
            "top_k must be a positive integer",
        ),
        (
            "post",
            "/api/messages/create",
            {"content": "invalid sender", "sender_type": "directorx"},
            400,
            "Invalid sender_type",
        ),
    ],
)
def test_assistant_and_taskstack_http_contract_validation_errors(
    assistant_http_client,
    method,
    path,
    payload,
    expected_status,
    error_substring,
):
    client = assistant_http_client
    request_fn = getattr(client, method)
    if payload is None:
        resp = request_fn(path)
    else:
        resp = request_fn(path, json=payload)

    assert resp.status_code == expected_status
    body = resp.get_json()
    assert isinstance(body, dict)
    assert error_substring in body.get("error", "")


def test_assistant_execute_returns_404_for_unknown_sub_agent(assistant_http_client):
    client = assistant_http_client
    create_task_resp = client.post(
        "/api/tasks/create",
        json={"description": {"goal": "unknown agent contract"}},
    )
    assert create_task_resp.status_code == 201
    task_id = create_task_resp.get_json()["id"]

    execute_resp = client.post(
        "/api/assistant/execute",
        json={"agent_id": "UnknownAgent", "task_id": task_id},
    )
    assert execute_resp.status_code == 404
    assert "not found in registry" in execute_resp.get_json()["error"]


@pytest.mark.skipif(
    not _LIVE_READY,
    reason=_LIVE_SKIP_REASON,
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
