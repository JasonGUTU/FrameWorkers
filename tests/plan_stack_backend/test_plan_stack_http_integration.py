"""HTTP integration tests for Plan Stack routes.

These exercise real Flask routes (URL + field names + batch op type values)
end-to-end via Flask test_client. If the director client code and backend
routes are out of sync on any URL, field, or enum value, this test fails.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

_repo_root = Path(__file__).resolve().parents[2]
_pkg_root = _repo_root / "plan-stack-backend"
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))
if str(_pkg_root) not in sys.path:
    sys.path.insert(0, str(_pkg_root))

# Stub flask_cors (src.app imports it)
if "flask_cors" not in sys.modules:
    flask_cors_stub = types.ModuleType("flask_cors")
    flask_cors_stub.CORS = lambda *args, **kwargs: None
    sys.modules["flask_cors"] = flask_cors_stub

from src.app import create_app  # noqa: E402
from src.plan_stack.storage import storage as global_storage  # noqa: E402
from src.plan_stack.state_store import PlanStackStateStore  # noqa: E402


def _reset_storage() -> None:
    """Clear the Plan Stack singleton's internal state between tests.

    Routes bind to ``storage`` at import time so we cannot rebind the name;
    instead we swap the inner ``_state`` and re-point the two child helpers
    that captured it at construction.
    """
    fresh = PlanStackStateStore()
    global_storage._state = fresh
    global_storage._batch_mutator._state = fresh
    global_storage._execution_flow._state = fresh


@pytest.fixture
def client():
    _reset_storage()
    app = create_app()
    with app.test_client() as c:
        yield c
    _reset_storage()


def _ok_json(resp, status=None):
    if status is not None:
        assert resp.status_code == status, (
            f"expected {status}, got {resp.status_code}: {resp.get_data(as_text=True)}"
        )
    assert resp.is_json, f"non-JSON body: {resp.get_data(as_text=True)}"
    return resp.get_json()


def _create_steps(client, descriptions: List[Dict[str, Any]]) -> List[str]:
    """Batch-create steps via ``/api/plan-stack/modify`` and return their ids."""
    body = _ok_json(
        client.post(
            "/api/plan-stack/modify",
            json={
                "operations": [
                    {
                        "type": "create_steps",
                        "params": {
                            "steps": [{"description": d} for d in descriptions]
                        },
                    }
                ]
            },
        )
    )
    assert body["success"] is True, body
    return list(body["created_step_ids"])


def _create_layer(client, layer_index: Optional[int] = None) -> int:
    """Batch-create one layer and return its index."""
    params: Dict[str, Any] = {"layers": [{"layer_index": layer_index}]}
    body = _ok_json(
        client.post(
            "/api/plan-stack/modify",
            json={"operations": [{"type": "create_layers", "params": params}]},
        )
    )
    assert body["success"] is True, body
    return body["created_layer_indices"][0]


def _add_steps_to_layer(client, layer_index: int, step_ids: List[str]) -> None:
    body = _ok_json(
        client.post(
            "/api/plan-stack/modify",
            json={
                "operations": [
                    {
                        "type": "add_steps_to_layers",
                        "params": {
                            "additions": [
                                {"layer_index": layer_index, "step_id": sid}
                                for sid in step_ids
                            ]
                        },
                    }
                ]
            },
        )
    )
    assert body["success"] is True, body


class TestPlanStackStepReads:
    def test_step_create_and_get(self, client):
        [sid] = _create_steps(client, [{"goal": "hello"}])
        assert sid.startswith("step_"), sid

        got = _ok_json(client.get(f"/api/steps/{sid}"), status=200)
        assert got["id"] == sid
        assert got["description"] == {"goal": "hello"}
        assert got["status"] == "PENDING"

    def test_get_all_steps(self, client):
        _create_steps(client, [{"i": i} for i in range(3)])
        body = _ok_json(client.get("/api/steps/list"))
        assert isinstance(body, list)
        assert len(body) == 3

    def test_update_step_status_and_reflect(self, client):
        [sid] = _create_steps(client, [{"goal": "placeholder"}])
        updated = _ok_json(
            client.put(f"/api/steps/{sid}/status", json={"status": "IN_PROGRESS"}),
            status=200,
        )
        assert updated["status"] == "IN_PROGRESS"
        got = _ok_json(client.get(f"/api/steps/{sid}"))
        assert got["status"] == "IN_PROGRESS"


class TestPlanStackLayerAndPointer:
    def test_create_layer_add_step_get_next(self, client):
        [sid] = _create_steps(client, [{"k": "v"}])
        _create_layer(client, layer_index=0)
        _add_steps_to_layer(client, 0, [sid])

        stack = _ok_json(client.get("/api/plan-stack"))
        assert len(stack) == 1
        layer = stack[0]
        assert layer["layer_index"] == 0
        # Response uses ``steps`` (Phase 2 rename), not legacy ``tasks``
        assert "steps" in layer and "tasks" not in layer
        assert layer["steps"][0]["step_id"] == sid

        nxt = _ok_json(client.get("/api/plan-stack/next"))
        assert nxt["step_id"] == sid
        assert nxt["step_index"] == 0
        assert nxt["layer_index"] == 0
        # Response carries full step payload under ``step`` (not legacy ``task``)
        assert nxt["step"]["id"] == sid

    def test_execution_pointer_advance(self, client):
        sids = _create_steps(
            client,
            [{"goal": "placeholder"}, {"goal": "placeholder"}],
        )
        _create_layer(client, layer_index=0)
        _add_steps_to_layer(client, 0, sids)

        _ok_json(
            client.put(
                "/api/execution-pointer/set",
                json={"layer_index": 0, "step_index": 0},
            )
        )
        pointer = _ok_json(client.get("/api/execution-pointer/get"))
        assert pointer["current_layer_index"] == 0
        assert pointer["current_step_index"] == 0

        _ok_json(client.post("/api/execution-pointer/advance"))
        pointer = _ok_json(client.get("/api/execution-pointer/get"))
        assert pointer["current_step_index"] == 1


class TestModifyPlanStackBatch:
    """Exercise the atomic batch endpoint used by the Upfront director."""

    def test_create_steps_batch(self, client):
        body = _ok_json(
            client.post(
                "/api/plan-stack/modify",
                json={
                    "operations": [
                        {
                            "type": "create_steps",
                            "params": {
                                "steps": [
                                    {"description": {"agent_id": "A1", "intent": "do a"}},
                                    {"description": {"agent_id": "A2", "intent": "do b"}},
                                ]
                            },
                        }
                    ]
                },
            )
        )
        assert body["success"] is True, body
        assert len(body["created_step_ids"]) == 2
        assert all(s.startswith("step_") for s in body["created_step_ids"])

    def test_create_layers_batch(self, client):
        body = _ok_json(
            client.post(
                "/api/plan-stack/modify",
                json={
                    "operations": [
                        {
                            "type": "create_layers",
                            "params": {"layers": [{"layer_index": 0}]},
                        }
                    ]
                },
            )
        )
        assert body["success"] is True
        assert body["created_layer_indices"] == [0]

    def test_full_plan_persist_flow(self, client):
        """Mirror the director's ``_persist_plan`` sequence exactly."""
        create_resp = _ok_json(
            client.post(
                "/api/plan-stack/modify",
                json={
                    "operations": [
                        {
                            "type": "create_steps",
                            "params": {
                                "steps": [
                                    {"description": {"agent_id": "A1", "intent": "x"}},
                                    {"description": {"agent_id": "A2", "intent": "y"}},
                                ]
                            },
                        },
                        {
                            "type": "create_layers",
                            "params": {"layers": [{"layer_index": 0}]},
                        },
                    ]
                },
            )
        )
        sids = create_resp["created_step_ids"]
        assert len(sids) == 2

        add_resp = _ok_json(
            client.post(
                "/api/plan-stack/modify",
                json={
                    "operations": [
                        {
                            "type": "add_steps_to_layers",
                            "params": {
                                "additions": [
                                    {"layer_index": 0, "step_id": sids[0]},
                                    {"layer_index": 0, "step_id": sids[1]},
                                ]
                            },
                        }
                    ]
                },
            )
        )
        assert add_resp["success"] is True

        stack = _ok_json(client.get("/api/plan-stack"))
        assert len(stack) == 1
        assert len(stack[0]["steps"]) == 2
        assert [s["step_id"] for s in stack[0]["steps"]] == sids

    def test_unknown_op_type_fails_loudly(self, client):
        resp = client.post(
            "/api/plan-stack/modify",
            json={"operations": [{"type": "create_tasks", "params": {}}]},
        )
        assert resp.status_code in (400, 500), resp.get_data(as_text=True)

    def test_remove_steps_from_layers(self, client):
        create_resp = _ok_json(
            client.post(
                "/api/plan-stack/modify",
                json={
                    "operations": [
                        {
                            "type": "create_steps",
                            "params": {"steps": [{"description": {"goal": "placeholder"}}]},
                        },
                        {
                            "type": "create_layers",
                            "params": {"layers": [{"layer_index": 0}]},
                        },
                    ]
                },
            )
        )
        sid = create_resp["created_step_ids"][0]
        _ok_json(
            client.post(
                "/api/plan-stack/modify",
                json={
                    "operations": [
                        {
                            "type": "add_steps_to_layers",
                            "params": {
                                "additions": [{"layer_index": 0, "step_id": sid}]
                            },
                        }
                    ]
                },
            )
        )
        _ok_json(
            client.post(
                "/api/plan-stack/modify",
                json={
                    "operations": [
                        {
                            "type": "remove_steps_from_layers",
                            "params": {
                                "removals": [{"layer_index": 0, "step_id": sid}]
                            },
                        }
                    ]
                },
            )
        )
        stack = _ok_json(client.get("/api/plan-stack"))
        assert stack[0]["steps"] == []


class TestAssistantExecutionsByStep:
    """``/api/assistant/executions/step/<step_id>`` is the cross-module foreign key."""

    def test_executions_endpoint_reachable_and_empty(self, client):
        [sid] = _create_steps(client, [{"goal": "placeholder"}])
        body = _ok_json(client.get(f"/api/assistant/executions/step/{sid}"))
        assert body == []
