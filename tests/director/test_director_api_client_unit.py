from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

# Make repository root importable in test runner environments.
_repo_root = Path(__file__).resolve().parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from director_agent.api_client import BackendAPIClient, BackendAPIError


class _DummyResponse:
    def __init__(self, payload: Any, status_code: int = 200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        return None

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload


def test_get_all_agents_normalizes_wrapped_response(monkeypatch):
    client = BackendAPIClient(base_url="http://unit-test")

    monkeypatch.setattr(
        client,
        "_request",
        lambda *args, **kwargs: {
            "total_agents": 1,
            "agents": [{"id": "StoryAgent", "name": "StoryAgent"}],
            "agent_ids": ["StoryAgent"],
        },
    )

    agents = client.get_all_agents()
    assert len(agents) == 1
    assert agents[0]["id"] == "StoryAgent"


def test_workspace_memory_brief_returns_expected_shape(monkeypatch):
    client = BackendAPIClient(base_url="http://unit-test")

    def _fake_request(method, endpoint, data=None, params=None):
        if endpoint == "/api/assistant/workspace/memory/brief":
            return {"global_memory": []}
        raise AssertionError(f"Unexpected endpoint: {endpoint}")

    monkeypatch.setattr(client, "_request", _fake_request)

    brief = client.get_workspace_memory_brief(task_id="task_1")
    assert "global_memory" in brief


def test_request_raises_backend_error_for_non_json_response(monkeypatch):
    client = BackendAPIClient(base_url="http://unit-test")

    class _DummySession:
        def request(self, **kwargs):
            return _DummyResponse(ValueError("invalid-json"))

    monkeypatch.setattr(client, "session", _DummySession())

    with pytest.raises(BackendAPIError):
        client._request("GET", "/health")


def test_push_task_message_matches_backend_contract(monkeypatch):
    client = BackendAPIClient(base_url="http://unit-test")
    captured = {}

    def _fake_request(method, endpoint, data=None, params=None):
        captured["method"] = method
        captured["endpoint"] = endpoint
        captured["data"] = data
        return {"ok": True}

    monkeypatch.setattr(client, "_request", _fake_request)

    client.push_task_message("task_1", sender="DIRECTOR", message="delegated")

    assert captured["method"] == "POST"
    assert captured["endpoint"] == "/api/tasks/task_1/messages"
    assert captured["data"] == {"content": "delegated", "sender_type": "director"}
