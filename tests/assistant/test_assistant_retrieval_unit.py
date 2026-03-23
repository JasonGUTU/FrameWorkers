from __future__ import annotations

from src.assistant.workspace_context import WorkspaceContextBuilder
from src.assistant.state_store import AssistantStateStore


def test_workspace_context_builder_collects_files_memory_logs(tmp_path):
    storage = AssistantStateStore(runtime_base_path=tmp_path / "Runtime")
    workspace = storage.create_global_workspace()
    workspace.add_memory_entry(
        content="memory content for assistant",
        tier="short_term",
        kind="execution_summary",
        task_id="task_x",
        agent_id="DummyAgent",
    )
    workspace.store_file(
        b"abc",
        filename="a.txt",
        description="text file",
        created_by="DummyAgent",
        tags=["task_x"],
    )
    workspace.log_manager.add_log(
        operation_type="write",
        resource_type="execution",
        agent_id="DummyAgent",
        task_id="task_x",
    )

    context_builder = WorkspaceContextBuilder(workspace)
    context = context_builder.get_context_for_agent("DummyAgent", "task_x")

    assert context["agent_id"] == "DummyAgent"
    assert context["task_id"] == "task_x"
    assert len(context["files"]) >= 1
    assert "short_term" in context["memory_brief"]
    assert len(context["memory_brief"]["short_term"]) >= 1
    assert context["memory_brief"].get("long_term") == []
    assert len(context["recent_logs"]) >= 1
