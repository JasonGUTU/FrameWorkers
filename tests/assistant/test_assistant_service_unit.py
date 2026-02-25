from __future__ import annotations

from datetime import datetime, timedelta
from types import SimpleNamespace

import src.assistant.service as service_module
from src.assistant.models import ExecutionStatus
from src.assistant.storage import AssistantStorage


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

    storage = AssistantStorage(runtime_base_path=tmp_path / "Runtime")
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
    assert len(files) == 1
    assert files[0].filename == "report.txt"


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
        def get_agent(self, _agent_id: str):
            return None

        def get_descriptor(self, _agent_id: str):
            return _DummyDescriptor()

    storage = AssistantStorage(runtime_base_path=tmp_path / "Runtime")
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
