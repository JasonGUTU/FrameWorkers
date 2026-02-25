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


def test_workspace_search_methods_return_expected_shapes(monkeypatch):
    client = BackendAPIClient(base_url="http://unit-test")

    def _fake_request(method, endpoint, data=None, params=None):
        if endpoint == "/api/assistant/workspace/files/search":
            return [{"id": "file_1"}]
        if endpoint == "/api/assistant/workspace/search":
            return {"files": [], "memory": "", "logs": []}
        raise AssertionError(f"Unexpected endpoint: {endpoint}")

    monkeypatch.setattr(client, "_request", _fake_request)

    file_results = client.search_workspace_files(query="scene", limit=5)
    assert file_results[0]["id"] == "file_1"

    all_results = client.search_workspace(query="scene", types=["files", "logs"])
    assert "logs" in all_results


def test_request_raises_backend_error_for_non_json_response(monkeypatch):
    client = BackendAPIClient(base_url="http://unit-test")

    class _DummySession:
        def request(self, **kwargs):
            return _DummyResponse(ValueError("invalid-json"))

    monkeypatch.setattr(client, "session", _DummySession())

    with pytest.raises(BackendAPIError):
        client._request("GET", "/health")
