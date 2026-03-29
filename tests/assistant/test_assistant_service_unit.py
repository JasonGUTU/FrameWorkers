from __future__ import annotations

import os
import json
from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest

import src.assistant.service as service_module
from src.assistant.models import AgentExecution, ExecutionStatus
from src.assistant.state_store import AssistantStateStore


def _seed_json_snapshot(
    workspace,
    *,
    task_id: str,
    agent_id: str,
    asset_key: str,
    execution_id: str,
    payload: dict,
) -> None:
    raw = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    rel = f"artifacts/{asset_key}/{agent_id}_{asset_key}_{execution_id}.json"
    meta = workspace.store_file_at_relative_path(
        rel,
        raw,
        filename=f"{agent_id}_{asset_key}_{execution_id}.json",
        description="test json snapshot",
        created_by=agent_id,
        tags=[agent_id, task_id, "asset_json"],
        metadata={
            "execution_id": execution_id,
            "task_id": task_id,
            "producer_agent_id": agent_id,
            "asset_key": asset_key,
            "asset_variant": "json_snapshot",
        },
    )
    # New pipeline relies on global_memory artifact_locations for input resolution.
    workspace.add_memory_entry(
        content=f"seed {asset_key}",
        task_id=task_id,
        agent_id=agent_id,
        artifact_locations=[
            {"role": asset_key, "path": str(meta.file_path)},
        ],
        execution_result={"status": "COMPLETED", "execution_id": execution_id},
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
        asset_key="upstream_asset",
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
    ua = inputs["input_bundle_v2"]["upstream_asset"]
    assert ua["summary"] == "ok"


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
        asset_key="upstream_asset",
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


def test_service_build_execution_inputs_text_seed_and_optional_media(assistant_env):
    svc, storage, _agent = assistant_env

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
        asset_key="upstream_asset",
        execution_id=execution.id,
        payload={"summary": "ok"},
    )
    inputs = svc.build_execution_inputs(
        agent_id="DummyAgent",
        task_id="task_1",
        workspace=workspace,
        execute_fields={"text": "merge test"},
    )
    assert "upstream_asset" in inputs["input_bundle_v2"]
    assert inputs["input_bundle_v2"]["source_text"] == "merge test"

    m = svc.build_execution_inputs(
        agent_id="DummyAgent",
        task_id="task_1",
        workspace=workspace,
        execute_fields={
            "text": "draft",
            "image": "data:image/png;base64,abc",
            "video": "https://example.com/v.mp4",
        },
    )
    assert m["input_bundle_v2"]["image"] == "data:image/png;base64,abc"
    assert m["input_bundle_v2"]["video"] == "https://example.com/v.mp4"


def test_service_passes_full_assets_to_descriptor_and_blocks_mutation(tmp_path, monkeypatch):
    class _EchoPipelineResult:
        def __init__(self, payload):
            self.output = None
            self.asset_dict = {"echo": payload}
            self.media_assets = []

    class _EchoPipelineAgent:
        async def run(self, typed_input, input_bundle_v2=None, materialize_ctx=None):
            return _EchoPipelineResult(typed_input)

    class _ScopedDescriptor:
        agent_id = "ScopedAgent"
        asset_key = "scoped_asset"
        catalog_entry = "Scoped descriptor"

        def build_equipped_agent(self, _llm):
            return _EchoPipelineAgent()

        def build_input(self, task_id, input_bundle_v2, config):
            mutable = True
            try:
                input_bundle_v2["source_text"] = "mutated"
            except TypeError:
                mutable = False
            return {
                "task_id": task_id,
                "allowed_keys": sorted(list(input_bundle_v2.keys())),
                "mutable": mutable,
                "source_text": input_bundle_v2.get("source_text", ""),
                "language": config.language,
            }

    class _StoryStubDescriptor:
        agent_id = "StoryAgent"
        asset_key = "story_blueprint"
        catalog_entry = "stub"

        def build_equipped_agent(self, _llm):
            return _EchoPipelineAgent()

        def build_input(self, *_a, **_k):
            return {}

    class _Registry:
        def get_descriptor(self, agent_id: str):
            if agent_id == "StoryAgent":
                return _StoryStubDescriptor()
            if agent_id == "ScopedAgent":
                return _ScopedDescriptor()
            return None

    storage = AssistantStateStore(runtime_base_path=tmp_path / "Runtime")
    monkeypatch.setattr(service_module, "get_agent_registry", lambda: _Registry())
    svc = service_module.AssistantService(storage)

    story_ex = storage.create_execution("StoryAgent", "task_scope", {})
    story_ex.status = ExecutionStatus.COMPLETED
    story_ex.results = {"content": {"logline": "should be blocked"}}
    story_ex.completed_at = datetime.now() + timedelta(seconds=1)
    storage.update_execution(story_ex)

    _seed_json_snapshot(
        svc.workspace,
        task_id="task_scope",
        agent_id="StoryAgent",
        asset_key="story_blueprint",
        execution_id=story_ex.id,
        payload={"content": {"logline": "should be blocked"}},
    )

    result = svc.execute_agent_for_task(
        "ScopedAgent",
        "task_scope",
        execute_fields={
            "text": "allowed text",
        },
    )

    echo = result["results"]["echo"]
    assert echo["source_text"] == "allowed text"
    assert {"source_text", "story_blueprint"}.issubset(set(echo["allowed_keys"]))
    assert echo["mutable"] is False


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
        asset_key = "dummy_asset"
        catalog_entry = "Dummy descriptor"

        def build_equipped_agent(self, _llm):
            return _DummyPipelineAgent()

        def build_input(self, task_id, input_bundle_v2, config):
            return {
                "task_id": task_id,
                "input_bundle_v2": input_bundle_v2,
                "language": config.language,
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
    files = workspace.list_files()

    assert result["status"] == "COMPLETED"
    assert result["results"]["_execution_debug"]["attempts"] == 2
    assert result["results"]["_execution_debug"]["overall_pass"] is True
    assert len(files) == 1
    assert files[0].filename == "report.txt"
    latest_execution_id = storage.get_executions_by_task("task_file")[-1].id
    assert files[0].metadata == {
        "execution_id": latest_execution_id,
        "task_id": "task_file",
        "producer_agent_id": "DummyAgent",
        "asset_key": "report",
        "asset_variant": "binary",
    }


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
        asset_key = "dummy_asset"
        catalog_entry = "Dummy descriptor"

        def __init__(self):
            self._agent = _SequencePipelineAgent()

        def build_equipped_agent(self, _llm):
            return self._agent

        def build_input(self, task_id, input_bundle_v2, config):
            return {
                "task_id": task_id,
                "input_bundle_v2": input_bundle_v2,
                "language": config.language,
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
    all_files = workspace.list_files()
    binary_assets = [
        file_meta
        for file_meta in all_files
        if file_meta.metadata.get("asset_key") == "report"
    ]
    json_assets = [
        file_meta
        for file_meta in all_files
        if file_meta.metadata.get("asset_key") == "dummy_asset"
        and file_meta.metadata.get("asset_variant") == "json_snapshot"
    ]

    assert first["status"] == "COMPLETED"
    assert second["status"] == "COMPLETED"
    assert second["results"]["content"]["text"] == "v2"
    latest_execution_id = storage.get_executions_by_task("task_overwrite")[-1].id
    assert len(binary_assets) == 1
    assert binary_assets[0].metadata["execution_id"] == latest_execution_id
    assert len(json_assets) == 1
    assert json_assets[0].metadata["execution_id"] == latest_execution_id


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
        asset_key = "dummy_asset"
        catalog_entry = "Dummy pipeline descriptor"

        def build_equipped_agent(self, _llm):
            return _DummyPipelineAgent()

        def build_input(self, task_id, input_bundle_v2, config):
            return {
                "task_id": task_id,
                "input_bundle_v2": input_bundle_v2,
                "language": config.language,
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
    assert result["results"]["summary"] == "pipeline ok"


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
        asset_key = "dummy_asset"
        catalog_entry = "Dummy pipeline descriptor"

        def build_equipped_agent(self, _llm):
            return _DummyPipelineAgent()

        def build_input(self, task_id, input_bundle_v2, config):
            return {
                "task_id": task_id,
                "input_bundle_v2": input_bundle_v2,
                "language": config.language,
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
    assert "_materialize_temp_dir" not in result["results"]


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
                }
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
        asset_key = "keyframes"
        catalog_entry = "Dummy keyframe descriptor"

        def build_equipped_agent(self, _llm):
            return _DummyPipelineAgent()

        def build_input(self, task_id, input_bundle_v2, config):
            return {
                "task_id": task_id,
                "input_bundle_v2": input_bundle_v2,
                "language": config.language,
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
    keyframes_result = result["results"]
    persisted_uri = (
        keyframes_result["content"]["scenes"][0]["shots"][0]["keyframes"][0]["image_asset"]["uri"]
    )
    assert os.path.isfile(persisted_uri)
    assert "fw_media_" not in persisted_uri

    # Pipeline assets should expose lightweight index instead of full JSON body.
    inputs = svc.build_execution_inputs(
        agent_id="KeyFrameAgent",
        task_id="task_uri",
        workspace=svc.workspace,
        execute_fields={
            "text": "draft",
        },
    )
    keyframes_index = inputs["input_bundle_v2"]["keyframes"]
    assert keyframes_index.get("content")


def test_service_hydrates_indexed_assets_before_agent_build_input(tmp_path, monkeypatch):
    class _ProducerResult:
        def __init__(self):
            self.output = None
            self.asset_dict = {"content": {"value": 42}}
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
        asset_key = "producer_asset"
        catalog_entry = "Producer descriptor"

        def build_equipped_agent(self, _llm):
            return _ProducerAgent()

        def build_input(self, task_id, input_bundle_v2, config):
            return {"task_id": task_id}

    class _ConsumerDescriptor:
        agent_id = "ConsumerAgent"
        asset_key = "consumer_asset"
        catalog_entry = "Consumer descriptor"

        def build_equipped_agent(self, _llm):
            return _ConsumerAgent()

        def build_input(self, task_id, input_bundle_v2, config):
            # Should receive hydrated JSON dict, not index-only dict.
            producer = input_bundle_v2.get("producer_asset", {})
            return {
                "task_id": task_id,
                "observed_value": producer.get("content", {}).get("value", -1),
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
    assert producer_result["results"]["_asset_index"]["asset_key"] == "producer_asset"

    packaged = svc.build_execution_inputs(
        agent_id="ConsumerAgent",
        task_id="task_hydrate",
        workspace=svc.workspace,
        execute_fields=dict(_snap),
    )
    assert packaged["input_bundle_v2"]["producer_asset"]["content"]["value"] == 42

    consumer_result = svc.execute_agent_for_task(
        "ConsumerAgent", "task_hydrate", execute_fields=dict(_snap)
    )
    assert consumer_result["status"] == "COMPLETED"
    assert consumer_result["results"]["observed"] == 42


def test_service_build_execution_inputs_includes_global_memory_list(assistant_env):
    svc, _storage, _ = assistant_env
    svc.workspace.add_memory_entry(
        content="stm note",
        task_id="task_gm",
        agent_id="DummyAgent",
    )
    inputs = svc.build_execution_inputs(
        agent_id="DummyAgent",
        task_id="task_gm",
        workspace=svc.workspace,
        execute_fields={"text": "draft"},
    )
    gm = inputs.get("global_memory")
    assert isinstance(gm, list)
    assert len(gm) >= 1
    assert "content" not in gm[0]
    assert gm[0].get("agent_id") == "DummyAgent"


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
    plan = svc._deterministic_output_persist_plan(ex, "video")
    media_items = [p for p in plan if p.get("kind") == "media"]
    assert len(media_items) == 1
    assert media_items[0]["relative_path"] == "artifacts/media/VideoAgent/video/clip_final.mp4"
