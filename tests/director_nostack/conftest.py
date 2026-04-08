"""Pytest setup for ``director_nostack`` tests (import paths + Assistant LLM stubs for HTTP e2e)."""

from __future__ import annotations

import os
import sys
import types
from pathlib import Path
from types import SimpleNamespace

import pytest

_repo_root = Path(__file__).resolve().parents[2]
_pkg_root = _repo_root / "dynamic-task-stack"
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))
if str(_pkg_root) not in sys.path:
    sys.path.insert(0, str(_pkg_root))

if "flask_cors" not in sys.modules:
    flask_cors_stub = types.ModuleType("flask_cors")
    flask_cors_stub.CORS = lambda *args, **kwargs: None
    sys.modules["flask_cors"] = flask_cors_stub

import src.assistant.routes as routes_module
import src.assistant.service as service_module
from src.app import create_app
from src.assistant.state_store import AssistantStateStore


class _DummyPipelineResult:
    def __init__(self):
        self.output = SimpleNamespace(model_dump=lambda: {"summary": "nostack e2e ok"})
        self.asset_dict = None
        self.media_assets = []


class _DummyPipelineAgent:
    async def run(self, _typed_input, input_bundle_v2=None, materialize_ctx=None):
        return _DummyPipelineResult()


class E2eDummyDescriptor:
    """Minimal pipeline descriptor for director_nostack HTTP e2e (matches assistant e2e style)."""

    def __init__(self, name: str):
        self.agent_id = name
        self.catalog_entry = (
            f"{name}: test pipeline agent for creative briefs (e.g. ~10s video mood pieces); "
            "returns a stub structured result for integration smoke."
        )

    def build_equipped_agent(self, _llm):
        return _DummyPipelineAgent()

    def build_input(self, task_id, input_bundle_v2):
        hints = getattr(input_bundle_v2, "hints", None) or {}
        return {
            "task_id": task_id,
            "input_bundle_v2": input_bundle_v2,
            "language": hints.get("language") or "en",
        }


class E2eDummyRegistry:
    def __init__(self, descriptors: dict[str, E2eDummyDescriptor]):
        self._descriptors = descriptors

    def get_descriptor(self, agent_id: str):
        return self._descriptors.get(agent_id)

    def gather_agents_info(self):
        agents = []
        capabilities: set[str] = set()
        for name, desc in self._descriptors.items():
            caps = ["pipeline_agent"]
            capabilities.update(caps)
            agents.append(
                {
                    "id": name,
                    "name": name,
                    "description": (desc.catalog_entry or "")[:200],
                    "agent_type": "pipeline",
                    "capabilities": list(caps),
                }
            )
        return {
            "total_agents": len(agents),
            "agents": agents,
            "all_capabilities": sorted(capabilities),
            "agent_ids": [a["id"] for a in agents],
        }


@pytest.fixture(autouse=True)
def _nostack_http_e2e_ignore_shell_real_agents(monkeypatch, request):
    """``test_director_nostack_http_e2e`` always uses stub catalog + Assistant LLM stubs.

    Must run **before** ``_stub_assistant_llm_hooks_for_nostack_e2e`` (definition order),
    so a shell ``FW_ENABLE_NOSTACK_REAL_AGENTS=1`` does not skip those stubs.
    """
    try:
        p = getattr(request.node, "path", None) or getattr(request.node, "fspath", None)
    except Exception:
        p = None
    if p is None or p.name != "test_director_nostack_http_e2e.py":
        return
    monkeypatch.setenv("FW_ENABLE_NOSTACK_REAL_AGENTS", "0")


@pytest.fixture(autouse=True)
def _stub_assistant_llm_hooks_for_nostack_e2e(monkeypatch):
    """Keep ``POST /api/assistant/execute`` deterministic in this package's tests."""
    if os.getenv("FW_ENABLE_NOSTACK_REAL_AGENTS") == "1":
        # Real-agent mode: do not stub Assistant's internal LLM hooks.
        # This enables true input packaging and memory summarization.
        return

    def _stub_inputs(self, agent_id, task_id, workspace):
        import json as _json
        resolved_artifacts: list[dict] = []
        selected_artifact_paths: list[str] = []
        try:
            entries = workspace.global_memory.list_all()
            for entry in entries:
                if entry.task_id and entry.task_id != task_id:
                    continue
                for artifact in entry.artifacts:
                    path = str(getattr(artifact, "path", "") or "").strip()
                    mime = str(getattr(artifact, "mime", "") or "").strip()
                    what = str(getattr(artifact, "what", "") or "")
                    why = str(getattr(artifact, "why", "") or "")
                    scope = str(getattr(artifact, "scope", "global") or "global")
                    if not path:
                        continue
                    payload = None
                    if mime == "application/json" or path.lower().endswith(".json"):
                        try:
                            raw = workspace.file_manager.read_binary_from_uri(path)
                            if raw:
                                data = _json.loads(raw.decode("utf-8"))
                                if isinstance(data, dict):
                                    payload = data
                        except Exception:
                            pass
                    resolved_artifacts.append({
                        "what": what, "why": why, "scope": scope,
                        "path": path,
                        "mime": mime or ("application/json" if path.lower().endswith(".json") else ""),
                        "payload": payload,
                    })
                    selected_artifact_paths.append(path)
        except Exception:
            pass
        return {
            "resolved_artifacts": resolved_artifacts,
            "selected_artifact_paths": list(dict.fromkeys(selected_artifact_paths)),
            "rationale": "nostack e2e stub: select all registered artifacts",
        }

    monkeypatch.setattr(
        service_module.AssistantService,
        "_resolve_inputs_for_agent_with_llm",
        _stub_inputs,
    )


@pytest.fixture
def director_nostack_registry() -> E2eDummyRegistry:
    return E2eDummyRegistry(
        descriptors={
            "NostackE2eAgent": E2eDummyDescriptor(name="NostackE2eAgent"),
        }
    )


@pytest.fixture
def director_nostack_http_app(tmp_path, monkeypatch, director_nostack_registry):
    """In-process Flask app + Assistant store + stub sub-agent registry (no TCP)."""
    # By default, keep tests isolated under pytest tmp_path.
    # For the live nostack E2E (real routing LLM), persist artifacts under repo `Runtime/` so
    # humans can inspect outputs after the run.
    if os.getenv("FW_ENABLE_NOSTACK_LIVE_E2E") == "1":
        runtime_base = Path(
            os.getenv(
                "FW_NOSTACK_LIVE_E2E_RUNTIME_DIR",
                str(_repo_root / "Runtime" / "nostack_live_e2e_outputs"),
            )
        )
        runtime_base.mkdir(parents=True, exist_ok=True)
    else:
        runtime_base = tmp_path / "Runtime"

    storage = AssistantStateStore(runtime_base_path=runtime_base)
    monkeypatch.setattr(routes_module, "assistant_state_store", storage)
    if os.getenv("FW_ENABLE_NOSTACK_REAL_AGENTS") != "1":
        monkeypatch.setattr(routes_module, "get_agent_registry", lambda: director_nostack_registry)
        monkeypatch.setattr(service_module, "get_agent_registry", lambda: director_nostack_registry)

    app = create_app({"TESTING": True})
    with app.test_client() as client:
        # Follow `test_full_pipeline_live_e2e` convention so tests can write traces to runtime.
        setattr(client, "_fw_runtime_base", str(runtime_base))
        yield client
