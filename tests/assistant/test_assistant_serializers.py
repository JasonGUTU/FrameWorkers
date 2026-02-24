from __future__ import annotations

from datetime import datetime

from src.assistant.models import Assistant, AgentExecution, ExecutionStatus
from src.assistant.serializers import (
    file_metadata_to_dict,
    file_search_item_to_dict,
    log_entry_to_dict,
    serialize_assistant_value,
)
from src.assistant.workspace.models import FileMetadata, LogEntry


def test_serializers_handle_assistant_models():
    assistant = Assistant(
        id="assistant_global",
        name="Global Assistant",
        description="desc",
        agent_ids=["a1"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    execution = AgentExecution(
        id="exec_1",
        assistant_id="assistant_global",
        agent_id="a1",
        task_id="t1",
        status=ExecutionStatus.COMPLETED,
        inputs={},
        results={"ok": True},
    )

    assistant_dict = serialize_assistant_value(assistant)
    execution_dict = serialize_assistant_value(execution)

    assert assistant_dict["id"] == "assistant_global"
    assert execution_dict["status"] == "COMPLETED"


def test_serializers_file_and_log_dict_helpers():
    now = datetime.now()
    file_meta = FileMetadata(
        id="f1",
        filename="a.txt",
        description="desc",
        file_type="text",
        file_extension=".txt",
        file_path="/tmp/a.txt",
        size_bytes=3,
        created_at=now,
        created_by="u1",
        tags=["t1"],
        metadata={"k": "v"},
    )
    log = LogEntry(
        id="l1",
        timestamp=now,
        operation_type="write",
        resource_type="file",
        resource_id="f1",
        details={"x": 1},
        agent_id="a1",
        task_id="t1",
    )

    full_file = file_metadata_to_dict(file_meta)
    search_file = file_search_item_to_dict(file_meta)
    log_dict = log_entry_to_dict(log)

    assert full_file["file_extension"] == ".txt"
    assert "size_bytes" not in search_file
    assert log_dict["resource_type"] == "file"
