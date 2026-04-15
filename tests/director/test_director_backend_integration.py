"""End-to-end: real ``BackendAPIClient`` + real Flask backend + scripted planner.

Where ``test_director_plan.py`` uses an in-memory ``_FakeBackend`` (which
matches the director's outgoing call shape by construction), this file wires
``BackendAPIClient._request`` through Flask's test client so every URL,
request body, and response is parsed against the real routes. If the client
and backend disagree on any endpoint, field name, or enum value, this test
fails.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_repo_root = Path(__file__).resolve().parents[2]
_pkg_root = _repo_root / "plan-stack-backend"
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))
if str(_pkg_root) not in sys.path:
    sys.path.insert(0, str(_pkg_root))

if "flask_cors" not in sys.modules:
    flask_cors_stub = types.ModuleType("flask_cors")
    flask_cors_stub.CORS = lambda *args, **kwargs: None
    sys.modules["flask_cors"] = flask_cors_stub

from src.app import create_app  # noqa: E402
from src.plan_stack.state_store import PlanStackStateStore  # noqa: E402
from src.plan_stack.storage import storage as global_plan_storage  # noqa: E402
from src.assistant.state_store import assistant_state_store  # noqa: E402

from director_agent.api_client import BackendAPIClient, BackendAPIError  # noqa: E402
from director_agent.director import (  # noqa: E402
    DirectorAgent,
    run_plan_pipeline,
)
from director_agent.router import (  # noqa: E402
    LlmSubAgentPlanner,
    PlanStepSpec,
)


def _reset_backend_state() -> None:
    fresh = PlanStackStateStore()
    global_plan_storage._state = fresh
    global_plan_storage.user_messages = fresh.user_messages
    global_plan_storage.plan_steps = fresh.plan_steps
    global_plan_storage.plan_layers = fresh.plan_layers
    global_plan_storage.lock = fresh.lock
    global_plan_storage._batch_mutator._state = fresh
    global_plan_storage._execution_flow._state = fresh
    assistant_state_store.executions.clear()
    assistant_state_store.execution_counter = 0


class _FlaskTransportClient(BackendAPIClient):
    """``BackendAPIClient`` that routes HTTP through Flask's test_client."""

    def __init__(self, flask_test_client) -> None:
        super().__init__(base_url="http://localhost", timeout=5.0)
        self._flask = flask_test_client

    def _request(self, method, endpoint, data=None, params=None):
        method_up = method.upper()
        kwargs = {"json": data} if data is not None else {}
        if params:
            # Flask test_client wants ``query_string=...``
            kwargs["query_string"] = params
        fn = getattr(self._flask, method_up.lower())
        resp = fn(endpoint, **kwargs)
        if resp.status_code >= 400:
            body = resp.get_data(as_text=True)
            raise BackendAPIError(
                f"{method_up} {endpoint} → {resp.status_code}: {body}"
            )
        if not resp.is_json:
            raise BackendAPIError(
                f"Non-JSON response from {method_up} {endpoint}"
            )
        return resp.get_json()


@pytest.fixture
def wired_client():
    _reset_backend_state()
    app = create_app()
    with app.test_client() as flask_client:
        yield _FlaskTransportClient(flask_client)
    _reset_backend_state()


class _FakePlanner:
    """Scripted planner driving the director end-to-end."""

    def __init__(self, plan_specs, merged_goal="merged", replan_decision=None):
        self._plan_specs = list(plan_specs)
        self._merged_goal = merged_goal
        self._replan_decision = replan_decision
        self.calls = {
            "merge": 0,
            "plan": 0,
            "replan": 0,
        }

    def merge_session_goal(self, *, latest_user_message, stack_memory, prior_user_chat_lines=None):
        self.calls["merge"] += 1
        return self._merged_goal

    def plan_pipeline_upfront(self, *, user_goal, available_agents, stack_memory=None, max_steps=20):
        self.calls["plan"] += 1
        return list(self._plan_specs)

    def replan_on_failure(self, **kwargs):
        self.calls["replan"] += 1
        from director_agent.router import ReplanDecision
        return self._replan_decision or ReplanDecision(action="skip")


# ---------------------------------------------------------------------------
# Sub-agent registry: we register a tiny fake so ``execute_agent`` succeeds
# without touching any real agent pipeline / LLM.
# ---------------------------------------------------------------------------


class _FakeExecutionAgent:
    """Minimal descriptor-less shim that the assistant can run."""

    id = "FakeAgent"

    @staticmethod
    def register_into(registry):
        """Register ``id=FakeAgent`` that always COMPLETES with empty artifacts."""
        # Minimal signature the AgentRegistry expects via gather_agents_info.
        class _FakeDescriptor:
            id = "FakeAgent"
            description = "Fake agent for integration tests"
            capabilities = []
            input_needs_description = {}
            output_labels = []

            def build_input(self, step_id, resolved_artifacts):  # noqa: D401
                return types.SimpleNamespace(step_id=step_id)

            def build_equipped_agent(self, llm_client):
                class _Runner:
                    async def run(self, typed_input, materialize_ctx):
                        return types.SimpleNamespace(
                            outputs=types.SimpleNamespace(),
                            metrics={},
                            artifacts=[],
                            raw_json={},
                        )

                return _Runner()

        registry._descriptors["FakeAgent"] = _FakeDescriptor()


@pytest.fixture
def agents_catalog():
    return [
        {
            "id": "FakeAgent",
            "description": "Fake agent",
            "capabilities": [],
        }
    ]


# ---------------------------------------------------------------------------
# Integration: low-level client → Flask routes
# ---------------------------------------------------------------------------


class TestBackendAPIClientAgainstFlask:
    def test_create_step_and_get_step(self, wired_client):
        resp = wired_client.modify_plan_stack([
            {
                "type": "create_steps",
                "params": {"steps": [{"description": {"agent_id": "FakeAgent", "intent": "hi"}}]},
            },
        ])
        step_id = resp["created_step_ids"][0]
        assert step_id.startswith("step_")
        got = wired_client.get_step(step_id)
        assert got["description"]["agent_id"] == "FakeAgent"

    def test_modify_plan_stack_create_and_layer(self, wired_client):
        resp = wired_client.modify_plan_stack([
            {
                "type": "create_steps",
                "params": {"steps": [{"description": {"agent_id": "FakeAgent", "intent": "x"}}]},
            },
            {"type": "create_layers", "params": {"layers": [{"layer_index": 0}]}},
        ])
        assert resp["success"] is True
        assert len(resp["created_step_ids"]) == 1
        assert resp["created_layer_indices"] == [0]

    def test_modify_plan_stack_add_steps_then_read(self, wired_client):
        resp1 = wired_client.modify_plan_stack([
            {
                "type": "create_steps",
                "params": {"steps": [
                    {"description": {"agent_id": "FakeAgent", "intent": "a"}},
                    {"description": {"agent_id": "FakeAgent", "intent": "b"}},
                ]},
            },
            {"type": "create_layers", "params": {"layers": [{"layer_index": 0}]}},
        ])
        sids = resp1["created_step_ids"]
        wired_client.modify_plan_stack([
            {
                "type": "add_steps_to_layers",
                "params": {"additions": [
                    {"layer_index": 0, "step_id": sids[0]},
                    {"layer_index": 0, "step_id": sids[1]},
                ]},
            }
        ])
        stack = wired_client.get_plan_stack()
        assert len(stack) == 1
        assert len(stack[0]["steps"]) == 2

    def test_get_next_step_then_advance(self, wired_client):
        resp = wired_client.modify_plan_stack([
            {
                "type": "create_steps",
                "params": {"steps": [
                    {"description": {"agent_id": "FakeAgent", "intent": "a"}},
                    {"description": {"agent_id": "FakeAgent", "intent": "b"}},
                ]},
            },
            {"type": "create_layers", "params": {"layers": [{"layer_index": 0}]}},
        ])
        sids = resp["created_step_ids"]
        wired_client.modify_plan_stack([
            {
                "type": "add_steps_to_layers",
                "params": {"additions": [
                    {"layer_index": 0, "step_id": sids[0]},
                    {"layer_index": 0, "step_id": sids[1]},
                ]},
            }
        ])
        wired_client.set_execution_pointer(layer_index=0, step_index=0)
        nxt = wired_client.get_next_step()
        assert nxt["step_id"] == sids[0]
        wired_client.advance_execution_pointer()
        nxt = wired_client.get_next_step()
        assert nxt["step_id"] == sids[1]

    def test_update_step_status_roundtrip(self, wired_client):
        resp = wired_client.modify_plan_stack([
            {
                "type": "create_steps",
                "params": {"steps": [{"description": {"agent_id": "FakeAgent", "intent": "x"}}]},
            },
        ])
        step_id = resp["created_step_ids"][0]
        wired_client.update_step_status(step_id, "COMPLETED")
        got = wired_client.get_step(step_id)
        assert got["status"] == "COMPLETED"


# ---------------------------------------------------------------------------
# Integration: run_plan_pipeline end-to-end with FakePlanner + Flask backend.
# Executes through the real Assistant route + a registered FakeAgent.
# ---------------------------------------------------------------------------


@pytest.fixture
def registered_fake_agent():
    from agents import get_agent_registry
    registry = get_agent_registry()
    _FakeExecutionAgent.register_into(registry)
    yield
    registry._descriptors.pop("FakeAgent", None)


class TestRunPlanPipelineAgainstFlask:
    def test_persists_plan_and_executes_each_step(
        self, wired_client, agents_catalog, registered_fake_agent
    ):
        planner = _FakePlanner(
            plan_specs=[
                PlanStepSpec(agent_id="FakeAgent", intent="a"),
                PlanStepSpec(agent_id="FakeAgent", intent="b"),
            ]
        )
        run_plan_pipeline(
            wired_client,
            planner,
            agents=agents_catalog,
            user_goal="do a then b",
            current_user_message_id="m1",
        )

        stack = wired_client.get_plan_stack()
        assert len(stack) == 1
        step_ids = [e["step_id"] for e in stack[0]["steps"]]
        assert len(step_ids) == 2
        for sid in step_ids:
            step = wired_client.get_step(sid)
            assert step["status"] == "COMPLETED", f"{sid} status = {step['status']}"

    def test_empty_plan_returns_without_mutating_stack(
        self, wired_client, agents_catalog
    ):
        planner = _FakePlanner(plan_specs=[])
        run_plan_pipeline(
            wired_client,
            planner,
            agents=agents_catalog,
            user_goal="x",
            current_user_message_id="m1",
        )
        assert wired_client.get_plan_stack() == []


class TestDirectorCycleAgainstFlask:
    def test_cycle_consumes_unread_message_and_runs_plan(
        self, wired_client, agents_catalog, registered_fake_agent
    ):
        # Seed an unread user message.
        wired_client.create_message("please run fake agent", sender_type="user")

        planner = _FakePlanner(
            plan_specs=[PlanStepSpec(agent_id="FakeAgent", intent="go")]
        )

        director = DirectorAgent(client=wired_client, planner=planner)
        # Stub the agents catalog to avoid relying on a real registry for routing.
        original_get_agents = wired_client.get_all_agents
        wired_client.get_all_agents = lambda: agents_catalog
        try:
            director._cycle()
        finally:
            wired_client.get_all_agents = original_get_agents

        stack = wired_client.get_plan_stack()
        assert len(stack) == 1
        assert len(stack[0]["steps"]) == 1
        sid = stack[0]["steps"][0]["step_id"]
        assert wired_client.get_step(sid)["status"] == "COMPLETED"
        assert planner.calls["plan"] == 1
