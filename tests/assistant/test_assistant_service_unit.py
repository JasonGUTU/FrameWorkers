from __future__ import annotations

import os
import shutil
from datetime import datetime, timedelta
from types import SimpleNamespace

import src.assistant.service as service_module
from src.assistant.models import ExecutionStatus
from src.assistant.state_store import AssistantStateStore


def test_service_build_execution_inputs_includes_assets(assistant_env):
    svc, storage, _agent = assistant_env

    execution = storage.create_execution("UpstreamAgent", "task_1", {"x": 1})
    execution.status = ExecutionStatus.COMPLETED
    execution.results = {"summary": "ok", "_internal": "ignore"}
    execution.completed_at = datetime.now() + timedelta(seconds=1)
    storage.update_execution(execution)

    workspace = svc.prepare_environment("task_1")
    inputs = svc.build_execution_inputs(
        agent_id="DummyAgent",
        task_id="task_1",
        workspace=workspace,
        additional_inputs={"extra": 123},
    )

    assert inputs["task_id"] == "task_1"
    assert inputs["task_description"] == "draft idea"
    assert inputs["extra"] == 123
    assert inputs["assets"]["upstream_asset"] == {"summary": "ok"}
    assert "_internal" not in inputs["assets"]["upstream_asset"]


def test_service_build_execution_inputs_merges_additional_assets(assistant_env):
    svc, storage, _agent = assistant_env

    execution = storage.create_execution("UpstreamAgent", "task_1", {"x": 1})
    execution.status = ExecutionStatus.COMPLETED
    execution.results = {"summary": "ok"}
    execution.completed_at = datetime.now() + timedelta(seconds=1)
    storage.update_execution(execution)

    workspace = svc.prepare_environment("task_1")
    inputs = svc.build_execution_inputs(
        agent_id="DummyAgent",
        task_id="task_1",
        workspace=workspace,
        additional_inputs={
            "assets": {
                "user_screenplay": "custom screenplay",
            }
        },
    )

    assert "upstream_asset" in inputs["assets"]
    assert inputs["assets"]["user_screenplay"] == "custom screenplay"


def test_service_passes_full_assets_to_descriptor_and_blocks_mutation(tmp_path, monkeypatch):
    class _EchoPipelineResult:
        def __init__(self, payload):
            self.output = None
            self.asset_dict = {"echo": payload}
            self.media_assets = []

    class _EchoPipelineAgent:
        async def run(self, typed_input, upstream=None, materialize_ctx=None):
            return _EchoPipelineResult(typed_input)

    class _ScopedDescriptor:
        agent_name = "ScopedAgent"
        asset_key = "scoped_asset"
        catalog_entry = "Scoped descriptor"
        upstream_keys = ["source_text"]
        user_text_key = ""

        def build_equipped_agent(self, _llm):
            return _EchoPipelineAgent()

        def build_input(self, project_id, draft_id, assets, config):
            mutable = True
            try:
                assets["source_text"] = "mutated"
            except TypeError:
                mutable = False
            return {
                "project_id": project_id,
                "draft_id": draft_id,
                "allowed_keys": sorted(list(assets.keys())),
                "mutable": mutable,
                "source_text": assets.get("source_text", ""),
                "language": config.language,
            }

        def build_upstream(self, assets):
            return {
                "keys": sorted(list(assets.keys()))
            }

    class _Registry:
        def get_descriptor(self, _agent_id: str):
            return _ScopedDescriptor()

    storage = AssistantStateStore(runtime_base_path=tmp_path / "Runtime")
    monkeypatch.setattr(service_module, "get_agent_registry", lambda: _Registry())
    monkeypatch.setattr(
        service_module.task_storage,
        "get_task",
        lambda _task_id: SimpleNamespace(description="fallback", progress={}),
    )
    svc = service_module.AssistantService(storage)

    result = svc.execute_agent_for_task(
        "ScopedAgent",
        "task_scope",
        additional_inputs={
            "assets": {
                "source_text": "allowed text",
                "story_blueprint": {"content": {"logline": "should be blocked"}},
            }
        },
    )

    echo = result["results"]["echo"]
    assert echo["source_text"] == "allowed text"
    assert set(echo["allowed_keys"]) == {
        "draft_idea",
        "source_text",
        "story_blueprint",
    }
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
        async def run(self, _typed_input, upstream=None, materialize_ctx=None):
            return _DummyPipelineResult()

    class _DummyDescriptor:
        asset_key = "dummy_asset"
        catalog_entry = "Dummy descriptor"

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
    monkeypatch.setattr(
        service_module.task_storage,
        "get_task",
        lambda _task_id: SimpleNamespace(description="draft", progress={}),
    )
    svc = service_module.AssistantService(storage)

    result = svc.execute_agent_for_task("DummyAgent", "task_file")
    workspace = storage.get_global_workspace()
    files = workspace.list_files()

    assert result["status"] == "COMPLETED"
    assert result["results"]["_execution_debug"]["attempts"] == 2
    assert result["results"]["_execution_debug"]["overall_pass"] is True
    assert len(files) == 1
    assert files[0].filename == "report.txt"
    assert files[0].metadata == {
        "execution_id": result["execution_id"],
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

        async def run(self, _typed_input, upstream=None, materialize_ctx=None):
            self._counter += 1
            return _SequencePipelineResult(f"v{self._counter}".encode("utf-8"))

    class _DummyDescriptor:
        asset_key = "dummy_asset"
        catalog_entry = "Dummy descriptor"

        def __init__(self):
            self._agent = _SequencePipelineAgent()

        def build_equipped_agent(self, _llm):
            return self._agent

        def build_input(self, project_id, draft_id, assets, config):
            return {
                "project_id": project_id,
                "draft_id": draft_id,
                "assets": assets,
                "language": config.language,
            }

        def build_upstream(self, _assets):
            return {}

    class _DummyRegistry:
        def __init__(self, descriptor):
            self._descriptor = descriptor

        def get_descriptor(self, _agent_id: str):
            return self._descriptor

    storage = AssistantStateStore(runtime_base_path=tmp_path / "Runtime")
    descriptor = _DummyDescriptor()
    monkeypatch.setattr(service_module, "get_agent_registry", lambda: _DummyRegistry(descriptor))
    monkeypatch.setattr(
        service_module.task_storage,
        "get_task",
        lambda _task_id: SimpleNamespace(description="draft", progress={}),
    )
    svc = service_module.AssistantService(storage)

    first = svc.execute_agent_for_task("DummyAgent", "task_overwrite")
    second = svc.execute_agent_for_task(
        "DummyAgent",
        "task_overwrite",
        additional_inputs={
            "_assistant_control": {"overwrite_assets": True},
        },
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
    assert len(binary_assets) == 1
    assert binary_assets[0].metadata["execution_id"] == second["execution_id"]
    assert len(json_assets) == 1
    assert json_assets[0].metadata["execution_id"] == second["execution_id"]


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
        async def run(self, _typed_input, upstream=None, materialize_ctx=None):
            return _DummyPipelineResult()

    class _DummyDescriptor:
        asset_key = "dummy_asset"
        catalog_entry = "Dummy pipeline descriptor"

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

    class _DummyRegistry:
        def get_descriptor(self, _agent_id: str):
            return _DummyDescriptor()

    storage = AssistantStateStore(runtime_base_path=tmp_path / "Runtime")
    monkeypatch.setattr(service_module, "get_agent_registry", lambda: _DummyRegistry())
    monkeypatch.setattr(
        service_module.task_storage,
        "get_task",
        lambda _task_id: SimpleNamespace(description="draft", progress={}),
    )
    svc = service_module.AssistantService(storage)
    result = svc.execute_agent_for_task("PipelineOnlyAgent", "task_pipeline")

    assert result["status"] == "COMPLETED"
    assert result["results"]["summary"] == "pipeline ok"


def test_service_can_keep_materializer_temp_dir(tmp_path, monkeypatch):
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

        async def run(self, _typed_input, upstream=None, materialize_ctx=None):
            media_asset = _DummyMediaAsset()
            uri = materialize_ctx.persist_binary(media_asset)
            media_asset.uri_holder = {"uri": uri}
            return _DummyPipelineResult(media_asset)

    class _DummyDescriptor:
        asset_key = "dummy_asset"
        catalog_entry = "Dummy pipeline descriptor"

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

    class _DummyRegistry:
        def get_descriptor(self, _agent_id: str):
            return _DummyDescriptor()

    storage = AssistantStateStore(runtime_base_path=tmp_path / "Runtime")
    monkeypatch.setenv("FW_KEEP_ASSISTANT_TEMP", "1")
    monkeypatch.setattr(service_module, "get_agent_registry", lambda: _DummyRegistry())
    monkeypatch.setattr(
        service_module.task_storage,
        "get_task",
        lambda _task_id: SimpleNamespace(description="draft", progress={}),
    )
    svc = service_module.AssistantService(storage)

    result = svc.execute_agent_for_task("PipelineWithMaterializer", "task_temp")
    temp_dir = result["results"].get("_materialize_temp_dir")
    assert temp_dir
    assert os.path.isdir(temp_dir)

    # Explicit cleanup in test to avoid leaking temp files.
    shutil.rmtree(temp_dir, ignore_errors=True)


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

        async def run(self, _typed_input, upstream=None, materialize_ctx=None):
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

        def build_input(self, project_id, draft_id, assets, config):
            return {
                "project_id": project_id,
                "draft_id": draft_id,
                "assets": assets,
                "language": config.language,
            }

        def build_upstream(self, _assets):
            return {}

    class _DummyRegistry:
        def get_descriptor(self, _agent_id: str):
            return _DummyDescriptor()

    storage = AssistantStateStore(runtime_base_path=tmp_path / "Runtime")
    monkeypatch.setattr(service_module, "get_agent_registry", lambda: _DummyRegistry())
    monkeypatch.setattr(
        service_module.task_storage,
        "get_task",
        lambda _task_id: SimpleNamespace(description="draft", progress={}),
    )
    svc = service_module.AssistantService(storage)

    result = svc.execute_agent_for_task("KeyFrameAgent", "task_uri")
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
    )
    keyframes_index = inputs["assets"]["keyframes"]
    assert keyframes_index["asset_key"] == "keyframes"
    assert os.path.isfile(keyframes_index["json_uri"])
    assert keyframes_index["json_uri"] == result["results"]["_asset_index"]["json_uri"]


def test_service_hydrates_indexed_assets_before_agent_build_input(tmp_path, monkeypatch):
    class _ProducerResult:
        def __init__(self):
            self.output = None
            self.asset_dict = {"content": {"value": 42}}
            self.media_assets = []

    class _ProducerAgent:
        async def run(self, _typed_input, upstream=None, materialize_ctx=None):
            return _ProducerResult()

    class _ConsumerResult:
        def __init__(self, observed_value: int):
            self.output = None
            self.asset_dict = {"observed": observed_value}
            self.media_assets = []

    class _ConsumerAgent:
        async def run(self, typed_input, upstream=None, materialize_ctx=None):
            return _ConsumerResult(typed_input.get("observed_value", -1))

    class _ProducerDescriptor:
        agent_name = "ProducerAgent"
        asset_key = "producer_asset"
        asset_type = "producer_asset_type"
        catalog_entry = "Producer descriptor"

        def build_equipped_agent(self, _llm):
            return _ProducerAgent()

        def build_input(self, project_id, draft_id, assets, config):
            return {"project_id": project_id, "draft_id": draft_id}

        def build_upstream(self, _assets):
            return {}

    class _ConsumerDescriptor:
        agent_name = "ConsumerAgent"
        asset_key = "consumer_asset"
        asset_type = "consumer_asset_type"
        upstream_keys = ["producer_asset"]
        user_text_key = ""
        catalog_entry = "Consumer descriptor"

        def build_equipped_agent(self, _llm):
            return _ConsumerAgent()

        def build_input(self, project_id, draft_id, assets, config):
            # Should receive hydrated JSON dict, not index-only dict.
            producer = assets.get("producer_asset", {})
            return {
                "project_id": project_id,
                "draft_id": draft_id,
                "observed_value": producer.get("content", {}).get("value", -1),
            }

        def build_upstream(self, assets):
            return {"producer_asset": assets.get("producer_asset", {})}

    class _Registry:
        def get_descriptor(self, agent_id: str):
            if agent_id == "ProducerAgent":
                return _ProducerDescriptor()
            if agent_id == "ConsumerAgent":
                return _ConsumerDescriptor()
            return None

    storage = AssistantStateStore(runtime_base_path=tmp_path / "Runtime")
    monkeypatch.setattr(service_module, "get_agent_registry", lambda: _Registry())
    monkeypatch.setattr(
        service_module.task_storage,
        "get_task",
        lambda _task_id: SimpleNamespace(description="draft", progress={}),
    )
    svc = service_module.AssistantService(storage)

    producer_result = svc.execute_agent_for_task("ProducerAgent", "task_hydrate")
    assert producer_result["status"] == "COMPLETED"
    assert producer_result["results"]["_asset_index"]["asset_key"] == "producer_asset"

    packaged = svc.build_execution_inputs(
        agent_id="ConsumerAgent",
        task_id="task_hydrate",
        workspace=svc.workspace,
    )
    assert "json_uri" in packaged["assets"]["producer_asset"]

    consumer_result = svc.execute_agent_for_task("ConsumerAgent", "task_hydrate")
    assert consumer_result["status"] == "COMPLETED"
    assert consumer_result["results"]["observed"] == 42
