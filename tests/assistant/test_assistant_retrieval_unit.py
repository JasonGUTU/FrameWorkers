from __future__ import annotations

from src.assistant.retrieval import WorkspaceRetriever
from src.assistant.storage import AssistantStorage


def test_retriever_context_collects_files_memory_logs(tmp_path):
    storage = AssistantStorage(runtime_base_path=tmp_path / "Runtime")
    workspace = storage.create_global_workspace()
    workspace.write_memory("memory content for assistant")
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

    retriever = WorkspaceRetriever(workspace)
    context = retriever.get_context_for_agent("DummyAgent", "task_x")

    assert context["agent_id"] == "DummyAgent"
    assert context["task_id"] == "task_x"
    assert len(context["files"]) >= 1
    assert "memory content" in context["memory"]
    assert len(context["recent_logs"]) >= 1
