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
from src.assistant.state_store import AssistantStateStore


class _DummyPipelineResult:
    def __init__(self, output: dict | None = None):
        self.output = SimpleNamespace(model_dump=lambda: output or {"ok": True})
        self.asset_dict = None
        self.media_assets = []


class _DummyPipelineAgent:
    async def run(self, _typed_input, input_bundle_v2=None, materialize_ctx=None):
        return _DummyPipelineResult()


class DummyDescriptor:
    def __init__(self, asset_key: str):
        self.asset_key = asset_key
        self.catalog_entry = "dummy descriptor"

    def build_equipped_agent(self, _llm):
        return _DummyPipelineAgent()

    def build_input(self, task_id, input_bundle_v2, config):
        return {
            "task_id": task_id,
            "input_bundle_v2": input_bundle_v2,
            "language": config.language,
        }


class DummyRegistry:
    def __init__(self, descriptors: dict):
        self._descriptors = descriptors

    def get_descriptor(self, agent_id: str):
        return self._descriptors.get(agent_id)


@pytest.fixture(autouse=True)
def stub_global_memory_summary_llm(monkeypatch):
    """Avoid real LLM calls when persisting global_memory after each test execution."""

    def _stub(self, execution, deterministic_artifacts=None):
        return {
            "content": "global_memory test summary",
            "artifact_locations": list(deterministic_artifacts or []),
            "artifact_briefs": [],
        }

    monkeypatch.setattr(
        service_module.AssistantService,
        "_extract_global_memory_summary_with_llm",
        _stub,
    )


@pytest.fixture(autouse=True)
def stub_output_persist_plan_llm(monkeypatch):
    """Skip output path LLM; use deterministic persist plan in tests."""

    def _stub(self, workspace, execution, descriptor, base_plan):
        return base_plan

    monkeypatch.setattr(
        service_module.AssistantService,
        "_refine_output_persist_plan_with_llm",
        _stub,
    )


@pytest.fixture(autouse=True)
def stub_input_package_llm(monkeypatch):
    """Avoid real LLM calls for per-execution input packaging."""

    def _stub(self, agent_id, task_id, workspace, packaged_data):
        mem = packaged_data.get("global_memory") or []
        roles: list[str] = []
        for entry in mem:
            if not isinstance(entry, dict):
                continue
            for loc in entry.get("artifact_locations") or []:
                if not isinstance(loc, dict):
                    continue
                role = loc.get("role")
                path = loc.get("path")
                if not (isinstance(role, str) and role.strip()):
                    continue
                # For tests, only select JSON roles; binary roles (e.g. media sys_id)
                # are not loadable via JSON hydration.
                if isinstance(path, str) and path.strip().lower().endswith(".json"):
                    roles.append(role.strip())
        # Stable order + de-dupe
        roles = list(dict.fromkeys(roles))
        if not roles:
            return {}
        return {
            "rationale": "test stub: select all available roles",
            "required_roles": roles,
            "selected_roles": roles,
            "append_to_source_text": "",
        }

    monkeypatch.setattr(
        service_module.AssistantService,
        "_resolve_inputs_for_agent_with_llm",
        _stub,
    )


@pytest.fixture
def assistant_env(tmp_path, monkeypatch):
    storage = AssistantStateStore(runtime_base_path=tmp_path / "Runtime")
    registry = DummyRegistry(
        descriptors={
            "UpstreamAgent": DummyDescriptor(asset_key="upstream_asset"),
            "DummyAgent": DummyDescriptor(asset_key="dummy_asset"),
        },
    )

    monkeypatch.setattr(service_module, "get_agent_registry", lambda: registry)
    svc = service_module.AssistantService(storage)
    return svc, storage, None
