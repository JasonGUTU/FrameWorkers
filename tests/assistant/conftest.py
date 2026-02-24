"""Shared pytest fixtures/helpers for assistant unit tests."""

from __future__ import annotations

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

import src.assistant.service as service_module
from src.assistant.storage import AssistantStorage


class DummyAgent:
    def __init__(self, result=None):
        self.metadata = SimpleNamespace(
            id="DummyAgent",
            name="Dummy Agent",
            description="test agent",
        )
        self._result = result if result is not None else {"ok": True}

    def get_input_schema(self):
        return {"type": "object"}

    def get_output_schema(self):
        return {"type": "object"}

    def get_capabilities(self):
        return ["unit_test"]

    def execute(self, _inputs):
        return self._result


class DummyRegistry:
    def __init__(self, agents: dict, descriptors: dict):
        self._agents = agents
        self._descriptors = descriptors

    def get_agent(self, agent_id: str):
        return self._agents.get(agent_id)

    def get_descriptor(self, agent_id: str):
        return self._descriptors.get(agent_id)


@pytest.fixture
def assistant_env(tmp_path, monkeypatch):
    storage = AssistantStorage(runtime_base_path=tmp_path / "Runtime")
    agent = DummyAgent()
    registry = DummyRegistry(
        agents={"DummyAgent": agent},
        descriptors={
            "UpstreamAgent": SimpleNamespace(asset_key="upstream_asset"),
            "DummyAgent": SimpleNamespace(asset_key="dummy_asset"),
        },
    )

    monkeypatch.setattr(service_module, "get_agent_registry", lambda: registry)
    monkeypatch.setattr(
        service_module.task_storage,
        "get_task",
        lambda _task_id: SimpleNamespace(
            description="draft idea",
            progress={"stage": "unit-test"},
        ),
    )
    svc = service_module.AssistantService(storage)
    return svc, storage, agent
