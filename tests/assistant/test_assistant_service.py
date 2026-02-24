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
    class _DummyAgent:
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

    class _DummyRegistry:
        def __init__(self, agents: dict, descriptors: dict):
            self._agents = agents
            self._descriptors = descriptors

        def get_agent(self, agent_id: str):
            return self._agents.get(agent_id)

        def get_descriptor(self, agent_id: str):
            return self._descriptors.get(agent_id)

    storage = AssistantStorage(runtime_base_path=tmp_path / "Runtime")
    agent = _DummyAgent(
        result={
            "report": {
                "file_content": b"hello",
                "filename": "report.txt",
                "description": "unit test report",
            }
        }
    )
    registry = _DummyRegistry(
        agents={"DummyAgent": agent},
        descriptors={"DummyAgent": SimpleNamespace(asset_key="dummy_asset")},
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
