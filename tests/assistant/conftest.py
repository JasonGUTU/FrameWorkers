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
    def __init__(self, input_needs_description: str = ""):
        self.catalog_entry = "dummy descriptor"
        self.input_needs_description = input_needs_description

    def build_equipped_agent(self, _llm):
        return _DummyPipelineAgent()

    def build_input(self, task_id, input_bundle_v2):
        hints = getattr(input_bundle_v2, "hints", None) or {}
        return {
            "task_id": task_id,
            "input_bundle_v2": input_bundle_v2,
            "language": hints.get("language") or "en",
        }


class DummyRegistry:
    def __init__(self, descriptors: dict):
        self._descriptors = descriptors

    def get_descriptor(self, agent_id: str):
        return self._descriptors.get(agent_id)


def _live_e2e_enabled() -> bool:
    """Whether the current process is running a live end-to-end test
    that needs the real Assistant LLM helper paths (no stubs)."""
    import os
    return any(
        os.getenv(name) == "1"
        for name in (
            "FW_ENABLE_FULL_PIPELINE_E2E",
            "FW_ENABLE_INTAKE_E2E",
            "FW_ENABLE_UNIVA_PIPELINE_E2E",
        )
    )


@pytest.fixture(autouse=True)
def stub_output_persist_plan_llm(monkeypatch):
    """Skip output path LLM; use deterministic persist plan in tests.

    Bypassed for live e2e runs so the real LLM-refined persist plan path
    is exercised.
    """
    if _live_e2e_enabled():
        return

    def _stub(self, workspace, execution, descriptor, base_plan):
        return base_plan

    monkeypatch.setattr(
        service_module.AssistantService,
        "_refine_output_persist_plan_with_llm",
        _stub,
    )


@pytest.fixture(autouse=True)
def stub_input_package_llm(monkeypatch, request):
    """Avoid real LLM calls for per-execution input packaging.

    Returns the new InputResolver format: {resolved_artifacts, selected_artifact_paths, rationale}.
    Loads JSON payloads from global_memory for the given task_id.

    Skipped for any live e2e flag so the real InputResolver LLM path is
    exercised end-to-end.
    """
    if _live_e2e_enabled():
        return  # let real InputResolver run

    def _stub(self, agent_id, task_id, workspace):
        """Test stub for InputResolver — caption substring match against [label] headers.

        Mirrors production semantics: parses the consumer agent's
        ``input_needs_description`` for ``[label] (single|collection)`` headers,
        then assigns each registered artifact (JSON snapshots only) to the
        first label whose name appears (case-insensitive) in the artifact's
        ``what``/``why`` caption text. ``single`` labels keep the first match;
        ``collection`` labels accumulate all matches.

        This is a deliberate simplification of the real LLM-driven resolver:
        tests that need resolution to fire must seed artifact captions whose
        text contains the consumer's label name as a substring.
        """
        import json
        import re

        grouped: dict[str, object] = {}
        selected_artifact_paths: list[str] = []

        # 1) Parse consumer's [label] (single|collection) headers.
        try:
            descriptor = self.agent_registry.get_descriptor(agent_id)
        except Exception:
            descriptor = None
        needs = str(getattr(descriptor, "input_needs_description", "") or "")
        label_re = re.compile(
            r"^\s*\[(?P<label>[a-zA-Z_][a-zA-Z0-9_]*)\]\s*\((?P<card>single|collection)\)\s*$",
            re.MULTILINE,
        )
        cardinality: dict[str, str] = {
            m.group("label"): m.group("card").lower()
            for m in label_re.finditer(needs)
        }
        if not cardinality:
            return {
                "resolved_artifacts": {},
                "selected_artifact_paths": [],
                "rationale": "test stub: no [label] headers in input_needs_description",
            }

        # 2) Walk global memory entries scoped to this task; assign artifacts
        #    to the first label whose name occurs in the artifact's caption.
        try:
            entries = workspace.global_memory.list_all()
            for entry in entries:
                if entry.task_id and entry.task_id != task_id:
                    continue
                for artifact in entry.artifacts:
                    path = str(getattr(artifact, "path", "") or "").strip()
                    mime = str(getattr(artifact, "mime", "") or "").strip()
                    if not path:
                        continue
                    # Only JSON snapshots become resolved labels in the stub.
                    if not (mime == "application/json" or path.lower().endswith(".json")):
                        continue
                    what = str(getattr(artifact, "what", "") or "")
                    why = str(getattr(artifact, "why", "") or "")
                    caption_text = f"{what} {why}".lower()

                    matched_label: str | None = None
                    for label in cardinality.keys():
                        if label.lower() in caption_text:
                            matched_label = label
                            break
                    if matched_label is None:
                        continue

                    entry_dict: dict[str, object] = {
                        "what": what,
                        "why": why,
                        "scope": str(getattr(artifact, "scope", "global") or "global"),
                        "path": path,
                        "mime": mime or "application/json",
                    }
                    try:
                        raw = workspace.file_manager.read_binary_from_uri(path)
                        if raw:
                            data = json.loads(raw.decode("utf-8"))
                            if isinstance(data, dict):
                                entry_dict["payload"] = data
                    except Exception:
                        pass

                    if cardinality[matched_label] == "single":
                        if matched_label in grouped:
                            continue  # keep first match for singletons
                        grouped[matched_label] = entry_dict
                    else:
                        bucket = grouped.setdefault(matched_label, [])
                        if isinstance(bucket, list):
                            bucket.append(entry_dict)
                    selected_artifact_paths.append(path)
        except Exception:
            pass
        return {
            "resolved_artifacts": grouped,
            "selected_artifact_paths": list(dict.fromkeys(selected_artifact_paths)),
            "rationale": "test stub: caption substring match against [label] headers",
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
            # Producer: emits artifacts; no input needs to declare.
            "UpstreamAgent": DummyDescriptor(),
            # Consumer: declares one [upstream_asset] (single) label so the
            # InputResolver stub can pick the producer's snapshot whose
            # caption text contains "upstream_asset".
            "DummyAgent": DummyDescriptor(
                input_needs_description=(
                    "[upstream_asset] (single)\n"
                    "The JSON document produced by UpstreamAgent."
                ),
            ),
        },
    )

    monkeypatch.setattr(service_module, "get_agent_registry", lambda: registry)
    svc = service_module.AssistantService(storage)
    return svc, storage, None
