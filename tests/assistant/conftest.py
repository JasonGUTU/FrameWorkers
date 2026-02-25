"""Shared pytest fixtures/helpers for assistant unit tests.

This file is auto-loaded by pytest for the entire `tests/assistant/` folder.
It centralizes import path setup, stubs, and reusable fixtures so each test
file can stay focused on behavior.
"""

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


class _DummyPipelineResult:
    def __init__(self, output: dict | None = None):
        self.output = SimpleNamespace(model_dump=lambda: output or {"ok": True})
        self.asset_dict = None
        self.media_assets = []


class _DummyPipelineAgent:
    async def run(self, _typed_input, upstream=None, materialize_ctx=None):
        return _DummyPipelineResult()


class DummyDescriptor:
    def __init__(self, asset_key: str):
        self.asset_key = asset_key
        self.catalog_entry = "dummy descriptor"
        self.asset_type = "dummy_asset_type"

    def build_equipped_agent(self, _llm):
        return _DummyPipelineAgent()

    def build_input(self, project_id, draft_id, assets, config):
        return {
            "project_id": project_id,
            "draft_id": draft_id,
            "assets": assets,
            "language": config.language,
        }

    def build_upstream(self, _assets):
        return {}


class DummyRegistry:
    def __init__(self, descriptors: dict):
        self._descriptors = descriptors

    def get_descriptor(self, agent_id: str):
        return self._descriptors.get(agent_id)


@pytest.fixture
def assistant_env(tmp_path, monkeypatch):
    storage = AssistantStorage(runtime_base_path=tmp_path / "Runtime")
    registry = DummyRegistry(
        descriptors={
            "UpstreamAgent": DummyDescriptor(asset_key="upstream_asset"),
            "DummyAgent": DummyDescriptor(asset_key="dummy_asset"),
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
    return svc, storage, None
