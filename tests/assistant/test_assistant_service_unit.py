from __future__ import annotations

import os
import json
from datetime import datetime, timedelta

import src.assistant.service as service_module
from src.assistant.models import AgentExecution, ExecutionStatus
from src.assistant.state_store import AssistantStateStore


def _execution_results_dict(storage: AssistantStateStore, result: dict) -> dict:
    """Sub-agent payload lives on stored ``AgentExecution``, not on ``execute`` HTTP summary."""
    ex_id = result.get("execution_id")
    assert ex_id
    ex = storage.get_execution(ex_id)
    assert ex is not None
    assert isinstance(ex.results, dict)
    return ex.results


def _seed_json_snapshot(
    workspace,
    *,
    task_id: str,
    agent_id: str,
    caption_label: str,
    execution_id: str,
    payload: dict,
) -> None:
    """Seed a JSON snapshot artifact whose caption contains ``caption_label``.

    The conftest InputResolver stub matches consumer ``[label] (single|collection)``
    headers against artifact caption text, so the seeded ``what`` field embeds
    ``caption_label`` as a substring.
    """
    raw = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    rel = f"artifacts/{agent_id}/{agent_id}_{execution_id}.json"
    stored = workspace.store_file_at_relative_path(
        rel,
        raw,
        filename=f"{agent_id}_{execution_id}.json",
    )
    # Register artifact so conftest stub can resolve it via global_memory.
    from src.assistant.workspace.models import ArtifactRef as _ArtifactRef
    workspace.global_memory.register(
        execution_id=execution_id,
        agent_id=agent_id,
        task_id=task_id,
        artifacts=[
            _ArtifactRef(
                what=f"{caption_label} JSON artifact",
                why="seeded by test helper",
                scope="global",
                path=stored.path,
                mime="application/json",
            )
        ],
    )


def test_service_build_execution_inputs_includes_assets(assistant_env):
    svc, storage, _agent = assistant_env

    execution = storage.create_execution("UpstreamAgent", "task_1", {"x": 1})
    execution.status = ExecutionStatus.COMPLETED
    execution.results = {"summary": "ok", "_internal": "ignore"}
    execution.completed_at = datetime.now() + timedelta(seconds=1)
    storage.update_execution(execution)

    workspace = svc.prepare_environment()
    _seed_json_snapshot(
        workspace,
        task_id="task_1",
        agent_id="UpstreamAgent",
        caption_label="upstream_asset",
        execution_id=execution.id,
        payload={"summary": "ok", "_internal": "ignore"},
    )
    inputs = svc.build_execution_inputs(
        agent_id="DummyAgent",
        task_id="task_1",
        workspace=workspace,
        execute_fields={
            "text": "draft idea",
            "extra": 123,
        },
    )

    assert inputs["task_id"] == "task_1"
    assert inputs["execute_fields"]["text"] == "draft idea"
    assert inputs["execute_fields"]["extra"] == 123
    # resolved_artifacts is keyed by the consumer's [label] headers; DummyAgent
    # declares [upstream_asset] (single) in conftest, so the producer's snapshot
    # (whose caption contains "upstream_asset") lands under that key.
    resolved = inputs["input_bundle_v2"].get("_resolved_artifacts", {})
    assert isinstance(resolved, dict), f"expected dict, got: {type(resolved)}"
    upstream = resolved.get("upstream_asset", {})
    assert isinstance(upstream, dict) and upstream.get("payload", {}).get("summary") == "ok", (
        f"expected upstream_asset with summary=ok in resolved_artifacts, got: {resolved}"
    )


def test_service_build_execution_inputs_allows_empty_execute_fields(assistant_env):
    svc, storage, _ = assistant_env
    execution = storage.create_execution("UpstreamAgent", "task_1", {"x": 1})
    execution.status = ExecutionStatus.COMPLETED
    execution.results = {"summary": "ok"}
    execution.completed_at = datetime.now() + timedelta(seconds=1)
    storage.update_execution(execution)
    workspace = svc.prepare_environment()
    _seed_json_snapshot(
        workspace,
        task_id="task_1",
        agent_id="UpstreamAgent",
        caption_label="upstream_asset",
        execution_id=execution.id,
        payload={"summary": "ok"},
    )
    inputs = svc.build_execution_inputs(
        agent_id="DummyAgent",
        task_id="task_1",
        workspace=workspace,
        execute_fields={"extra": 1},
    )
    assert inputs["execute_fields"] == {"extra": 1}
    assert "source_text" not in inputs["input_bundle_v2"]


def test_service_execute_and_persist_file_outputs(tmp_path, monkeypatch):
    class _DummyPipelineResult:
        def __init__(self):
            self.output = None
            self.asset_dict = {
                "report": {
                    "file_content": b"hello",
                    "filename": "report.txt",
                    "description": "unit test report",
                }
            }
            self.media_assets = []
            self.attempts = 2
            self.eval_result = {
                "overall_pass": True,
                "summary": "L1/L2 passed after one retry.",
            }

    class _DummyPipelineAgent:
        async def run(self, _typed_input, input_bundle_v2=None, materialize_ctx=None):
            return _DummyPipelineResult()

    class _DummyDescriptor:
        catalog_entry = "Dummy descriptor"

        def build_equipped_agent(self, _llm):
            return _DummyPipelineAgent()

        def build_input(self, task_id, input_bundle_v2):
            return {
                "task_id": task_id,
                "input_bundle_v2": input_bundle_v2,
                "language": (getattr(input_bundle_v2, "hints", None) or {}).get("language") or "en",
            }

    class _DummyRegistry:
        def __init__(self, descriptors: dict):
            self._descriptors = descriptors

        def get_descriptor(self, agent_id: str):
            return self._descriptors.get(agent_id)

    storage = AssistantStateStore(runtime_base_path=tmp_path / "Runtime")
    registry = _DummyRegistry(
        descriptors={"DummyAgent": _DummyDescriptor()},
    )
    monkeypatch.setattr(service_module, "get_agent_registry", lambda: registry)
    svc = service_module.AssistantService(storage)

    result = svc.execute_agent_for_task(
        "DummyAgent",
        "task_file",
        execute_fields={
            "text": "draft",
        },
    )
    workspace = storage.get_global_workspace()
    artifacts = workspace.list_workspace_artifacts()

    assert result["status"] == "COMPLETED"
    rdict = _execution_results_dict(storage, result)
    assert rdict["_execution_debug"]["attempts"] == 2
    assert rdict["_execution_debug"]["overall_pass"] is True
    # The dummy agent only emits one binary (`report.txt`); its results have
    # no structured top-level keys, so no JSON snapshot is written.
    # task_id prefix is now baked into the filename: task_file_report.txt.
    binary = [a for a in artifacts if a["filename"] == "task_file_report.txt"]
    assert len(binary) == 1
    latest_execution_id = storage.get_executions_by_task("task_file")[-1].id
    assert binary[0]["execution_id"] == latest_execution_id
    assert binary[0]["task_id"] == "task_file"
    assert binary[0]["agent_id"] == "DummyAgent"


def test_service_overwrite_mode_replaces_previous_asset_files(tmp_path, monkeypatch):
    class _SequencePipelineResult:
        def __init__(self, content: bytes):
            self.output = None
            self.asset_dict = {
                "report": {
                    "file_content": content,
                    "filename": "report.txt",
                    "description": "report snapshot",
                },
                "content": {"text": content.decode("utf-8")},
            }
            self.media_assets = []

    class _SequencePipelineAgent:
        def __init__(self):
            self._counter = 0

        async def run(self, _typed_input, input_bundle_v2=None, materialize_ctx=None):
            self._counter += 1
            return _SequencePipelineResult(f"v{self._counter}".encode("utf-8"))

    class _DummyDescriptor:
        catalog_entry = "Dummy descriptor"

        def __init__(self):
            self._agent = _SequencePipelineAgent()

        def build_equipped_agent(self, _llm):
            return self._agent

        def build_input(self, task_id, input_bundle_v2):
            return {
                "task_id": task_id,
                "input_bundle_v2": input_bundle_v2,
                "language": (getattr(input_bundle_v2, "hints", None) or {}).get("language") or "en",
            }

    class _DummyRegistry:
        def __init__(self, descriptor):
            self._descriptor = descriptor

        def get_descriptor(self, _agent_id: str):
            return self._descriptor

    storage = AssistantStateStore(runtime_base_path=tmp_path / "Runtime")
    descriptor = _DummyDescriptor()
    monkeypatch.setattr(service_module, "get_agent_registry", lambda: _DummyRegistry(descriptor))
    svc = service_module.AssistantService(storage)

    _snap = {"text": "draft"}
    first = svc.execute_agent_for_task("DummyAgent", "task_overwrite", execute_fields=dict(_snap))
    second = svc.execute_agent_for_task(
        "DummyAgent",
        "task_overwrite",
        execute_fields=dict(_snap),
    )

    workspace = storage.get_global_workspace()
    all_artifacts = workspace.list_workspace_artifacts()
    # task_id prefix is baked into the filename: task_overwrite_report.txt.
    binary_assets = [a for a in all_artifacts if a["filename"] == "task_overwrite_report.txt"]
    # JSON snapshot filenames are now <task_id>_<agent_id_lower>_exec_<n>.json,
    # e.g. "task_overwrite_dummyagent_exec_N.json".
    json_assets = [
        a for a in all_artifacts
        if a["mime"] == "application/json" and a["filename"].startswith("task_overwrite_dummyagent_")
    ]

    assert first["status"] == "COMPLETED"
    assert second["status"] == "COMPLETED"
    assert _execution_results_dict(storage, second)["content"]["text"] == "v2"
    latest_execution_id = storage.get_executions_by_task("task_overwrite")[-1].id
    # Coarse (task, agent) wipe means only the latest run's artifacts survive.
    assert len(binary_assets) == 1
    assert binary_assets[0]["execution_id"] == latest_execution_id
    assert len(json_assets) == 1
    assert json_assets[0]["execution_id"] == latest_execution_id


def test_service_executes_pipeline_descriptor_without_adapter(tmp_path, monkeypatch):
    class _DummyPipelineOutput:
        def model_dump(self):
            return {"summary": "pipeline ok"}

    class _DummyPipelineResult:
        def __init__(self):
            self.output = _DummyPipelineOutput()
            self.asset_dict = None
            self.media_assets = []

    class _DummyPipelineAgent:
        async def run(self, _typed_input, input_bundle_v2=None, materialize_ctx=None):
            return _DummyPipelineResult()

    class _DummyDescriptor:
        catalog_entry = "Dummy pipeline descriptor"

        def build_equipped_agent(self, _llm):
            return _DummyPipelineAgent()

        def build_input(self, task_id, input_bundle_v2):
            return {
                "task_id": task_id,
                "input_bundle_v2": input_bundle_v2,
                "language": (getattr(input_bundle_v2, "hints", None) or {}).get("language") or "en",
            }

    class _DummyRegistry:
        def get_descriptor(self, _agent_id: str):
            return _DummyDescriptor()

    storage = AssistantStateStore(runtime_base_path=tmp_path / "Runtime")
    monkeypatch.setattr(service_module, "get_agent_registry", lambda: _DummyRegistry())
    svc = service_module.AssistantService(storage)
    result = svc.execute_agent_for_task(
        "PipelineOnlyAgent",
        "task_pipeline",
        execute_fields={
            "text": "draft",
        },
    )

    assert result["status"] == "COMPLETED"
    assert _execution_results_dict(storage, result)["summary"] == "pipeline ok"


def test_service_materializer_temp_dir_is_cleaned(tmp_path, monkeypatch):
    class _DummyPipelineOutput:
        def model_dump(self):
            return {"summary": "pipeline ok"}

    class _DummyMediaAsset:
        def __init__(self):
            self.sys_id = "tmp_asset"
            self.extension = "png"
            self.data = b"png-bytes"
            self.uri_holder = {}

    class _DummyPipelineResult:
        def __init__(self, media_asset):
            self.output = _DummyPipelineOutput()
            self.asset_dict = None
            self.media_assets = [media_asset]

    class _DummyPipelineAgent:
        materializer = object()

        async def run(self, _typed_input, input_bundle_v2=None, materialize_ctx=None):
            media_asset = _DummyMediaAsset()
            uri = materialize_ctx.persist_binary(media_asset)
            media_asset.uri_holder = {"uri": uri}
            return _DummyPipelineResult(media_asset)

    class _DummyDescriptor:
        catalog_entry = "Dummy pipeline descriptor"

        def build_equipped_agent(self, _llm):
            return _DummyPipelineAgent()

        def build_input(self, task_id, input_bundle_v2):
            return {
                "task_id": task_id,
                "input_bundle_v2": input_bundle_v2,
                "language": (getattr(input_bundle_v2, "hints", None) or {}).get("language") or "en",
            }

    class _DummyRegistry:
        def get_descriptor(self, _agent_id: str):
            return _DummyDescriptor()

    storage = AssistantStateStore(runtime_base_path=tmp_path / "Runtime")
    monkeypatch.setattr(service_module, "get_agent_registry", lambda: _DummyRegistry())
    svc = service_module.AssistantService(storage)

    result = svc.execute_agent_for_task(
        "PipelineWithMaterializer",
        "task_temp",
        execute_fields={
            "text": "draft",
        },
    )
    assert "_materialize_temp_dir" not in _execution_results_dict(storage, result)


def test_service_rewrites_media_asset_uri_to_workspace_path(tmp_path, monkeypatch):
    class _DummyMediaAsset:
        def __init__(self):
            self.sys_id = "img_sh_001_kf_01"
            self.extension = "png"
            self.data = b"png-bytes"
            self.uri_holder = {}

    class _DummyPipelineResult:
        def __init__(self, media_asset):
            self.output = None
            self.asset_dict = {
                "content": {
                    "scenes": [
                        {
                            "scene_id": "sc_001",
                            "shots": [
                                {
                                    "shot_id": "sh_001",
                                    "keyframes": [
                                        {
                                            "keyframe_id": "kf_001",
                                            "image_asset": {
                                                "asset_id": "img_sh_001_kf_01",
                                                "uri": "placeholder",
                                            },
                                        }
                                    ],
                                }
                            ],
                        }
                    ]
                },
                # Caption is stored under results["artifact_caption"] and used
                # by ArtifactWriter as the JSON snapshot's registry caption.
                # The conftest InputResolver stub matches consumer label names
                # against this caption text, so embed "keyframes" here.
                "artifact_caption": {
                    "what": "keyframes plan",
                    "why": "test seed for resolver substring match",
                },
            }
            self.media_assets = [media_asset]

    class _DummyPipelineAgent:
        materializer = object()

        async def run(self, _typed_input, input_bundle_v2=None, materialize_ctx=None):
            media_asset = _DummyMediaAsset()
            uri = materialize_ctx.persist_binary(media_asset)
            media_asset.uri_holder = {
                "asset_id": media_asset.sys_id,
                "uri": uri,
            }
            return _DummyPipelineResult(media_asset)

    class _DummyDescriptor:
        catalog_entry = "Dummy keyframe descriptor"
        input_needs_description = (
            "[keyframes] (single)\n"
            "The keyframes JSON document produced by a prior run."
        )

        def build_equipped_agent(self, _llm):
            return _DummyPipelineAgent()

        def build_input(self, task_id, input_bundle_v2):
            return {
                "task_id": task_id,
                "input_bundle_v2": input_bundle_v2,
                "language": (getattr(input_bundle_v2, "hints", None) or {}).get("language") or "en",
            }

    class _DummyRegistry:
        def get_descriptor(self, _agent_id: str):
            return _DummyDescriptor()

    storage = AssistantStateStore(runtime_base_path=tmp_path / "Runtime")
    monkeypatch.setattr(service_module, "get_agent_registry", lambda: _DummyRegistry())
    svc = service_module.AssistantService(storage)

    result = svc.execute_agent_for_task(
        "KeyFrameAgent",
        "task_uri",
        execute_fields={
            "text": "draft",
        },
    )
    keyframes_result = _execution_results_dict(storage, result)
    persisted_uri = (
        keyframes_result["content"]["scenes"][0]["shots"][0]["keyframes"][0]["image_asset"]["uri"]
    )
    assert os.path.isfile(persisted_uri)
    assert "fw_media_" not in persisted_uri

    # Pipeline assets should expose artifacts via _resolved_artifacts in the new architecture.
    inputs = svc.build_execution_inputs(
        agent_id="KeyFrameAgent",
        task_id="task_uri",
        workspace=svc.workspace,
        execute_fields={
            "text": "draft",
        },
    )
    resolved = inputs["input_bundle_v2"].get("_resolved_artifacts", {})
    kf = resolved.get("keyframes", {})
    assert isinstance(kf, dict) and isinstance(kf.get("payload"), dict) and kf["payload"].get("content"), (
        f"expected keyframes artifact in resolved_artifacts, got: {resolved}"
    )


def test_service_hydrates_indexed_assets_before_agent_build_input(tmp_path, monkeypatch):
    class _ProducerResult:
        def __init__(self):
            self.output = None
            self.asset_dict = {
                "content": {"value": 42},
                # Caption text contains "producer_asset" so the conftest stub
                # can match it against the consumer's [producer_asset] label.
                "artifact_caption": {
                    "what": "producer_asset payload",
                    "why": "test seed",
                },
            }
            self.media_assets = []

    class _ProducerAgent:
        async def run(self, _typed_input, input_bundle_v2=None, materialize_ctx=None):
            return _ProducerResult()

    class _ConsumerResult:
        def __init__(self, observed_value: int):
            self.output = None
            self.asset_dict = {"observed": observed_value}
            self.media_assets = []

    class _ConsumerAgent:
        async def run(self, typed_input, input_bundle_v2=None, materialize_ctx=None):
            return _ConsumerResult(typed_input.get("observed_value", -1))

    class _ProducerDescriptor:
        agent_id = "ProducerAgent"
        catalog_entry = "Producer descriptor"

        def build_equipped_agent(self, _llm):
            return _ProducerAgent()

        def build_input(self, task_id, input_bundle_v2):
            return {"task_id": task_id}

    class _ConsumerDescriptor:
        agent_id = "ConsumerAgent"
        catalog_entry = "Consumer descriptor"
        input_needs_description = (
            "[producer_asset] (single)\n"
            "The JSON payload produced by ProducerAgent."
        )

        def build_equipped_agent(self, _llm):
            return _ConsumerAgent()

        def build_input(self, task_id, input_bundle_v2):
            resolved = getattr(input_bundle_v2, "resolved_artifacts", {})
            if not isinstance(resolved, dict):
                resolved = {}
            producer = resolved.get("producer_asset", {})
            payload = producer.get("payload", {}) if isinstance(producer, dict) else {}
            return {
                "task_id": task_id,
                "observed_value": payload.get("content", {}).get("value", -1),
            }

    class _Registry:
        def get_descriptor(self, agent_id: str):
            if agent_id == "ProducerAgent":
                return _ProducerDescriptor()
            if agent_id == "ConsumerAgent":
                return _ConsumerDescriptor()
            return None

    storage = AssistantStateStore(runtime_base_path=tmp_path / "Runtime")
    monkeypatch.setattr(service_module, "get_agent_registry", lambda: _Registry())
    svc = service_module.AssistantService(storage)

    _snap = {"text": "draft"}
    producer_result = svc.execute_agent_for_task(
        "ProducerAgent", "task_hydrate", execute_fields=dict(_snap)
    )
    assert producer_result["status"] == "COMPLETED"
    # _asset_index now keys the producer by agent_id (no asset_key field).
    assert (
        _execution_results_dict(storage, producer_result)["_asset_index"]["agent_id"]
        == "ProducerAgent"
    )

    packaged = svc.build_execution_inputs(
        agent_id="ConsumerAgent",
        task_id="task_hydrate",
        workspace=svc.workspace,
        execute_fields=dict(_snap),
    )
    resolved = packaged["input_bundle_v2"].get("_resolved_artifacts", {})
    assert isinstance(resolved, dict) and "producer_asset" in resolved, (
        f"expected producer_asset in resolved_artifacts, got: {resolved}"
    )

    consumer_result = svc.execute_agent_for_task(
        "ConsumerAgent", "task_hydrate", execute_fields=dict(_snap)
    )
    assert consumer_result["status"] == "COMPLETED"
    assert _execution_results_dict(storage, consumer_result)["observed"] == 42


def test_service_global_memory_brief_after_register(assistant_env):
    """``global_memory.md`` is auto-populated by ArtifactWriter; the
    director-facing brief projects each entry down to the slim row shape
    {execution_id, agent_id, task_id, status, created_at}."""
    from src.assistant.workspace.models import ArtifactRef as _ArtifactRef
    svc, _storage, _ = assistant_env
    svc.workspace.global_memory.register(
        execution_id="exec_gm_1",
        agent_id="StoryAgent",
        task_id="task_gm",
        artifacts=[
            _ArtifactRef(
                what="story snapshot",
                why="seeded by test",
                scope="global",
                path="/tmp/test/story.json",
                mime="application/json",
            )
        ],
    )
    rows = svc.workspace.get_global_memory_brief(task_id="task_gm")
    assert isinstance(rows, list)
    assert len(rows) >= 1
    row = rows[0]
    assert set(row.keys()) == {"execution_id", "agent_id", "task_id", "status", "created_at"}
    assert row["agent_id"] == "StoryAgent"
    assert row["task_id"] == "task_gm"
    assert row["status"] == "COMPLETED"


def test_artifact_media_type_subdir():
    S = service_module.AssistantService._artifact_media_type_subdir
    assert S("clip.mp4") == "video"
    assert S("a.MOV") == "video"
    assert S("x.wav") == "audio"
    assert S("a.MP3") == "audio"
    assert S("k.png") == "image"
    assert S("k.JPEG") == "image"
    assert S("unknown.bin") == "other"


def test_deterministic_persist_plan_media_under_artifacts_media_agent_type(assistant_env):
    svc, _, _ = assistant_env
    ex = AgentExecution(
        id="exec_vid",
        assistant_id="asst",
        agent_id="VideoAgent",
        task_id="task_1",
        status=ExecutionStatus.COMPLETED,
        inputs={},
        results={
            "_media_files": {
                "clip_final": {
                    "filename": "clip_final.mp4",
                    "file_content": b"\x00\x00\x00\x18ftyp",
                }
            }
        },
    )
    descriptor = svc.agent_registry.get_descriptor("VideoAgent")
    plan = svc._deterministic_output_persist_plan(ex, descriptor)
    media_items = [p for p in plan if p.get("kind") == "media"]
    assert len(media_items) == 1
    assert media_items[0]["relative_path"] == "artifacts/media/VideoAgent/video/task_1_clip_final.mp4"
