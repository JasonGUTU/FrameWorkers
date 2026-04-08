from __future__ import annotations

from datetime import datetime

from src.assistant.models import Assistant, AgentExecution, ExecutionStatus
from src.assistant.response_serializers import (
    log_entry_to_dict,
    serialize_response_value,
)
from src.assistant.workspace.models import LogEntry


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

    assistant_dict = serialize_response_value(assistant)
    execution_dict = serialize_response_value(execution)

    assert assistant_dict["id"] == "assistant_global"
    assert execution_dict["status"] == "COMPLETED"


def test_log_entry_to_dict_helper():
    now = datetime.now()
    log = LogEntry(
        id="l1",
        timestamp=now,
        event="artifact.persisted",
        resource_id="f1",
        details={"x": 1},
        agent_id="a1",
        task_id="t1",
        execution_id="exec_1",
    )
    log_dict = log_entry_to_dict(log)
    assert log_dict["event"] == "artifact.persisted"
    assert log_dict["details"] == {"x": 1}
    assert log_dict["execution_id"] == "exec_1"
    assert log_dict["level"] == "INFO"


def test_serialize_response_value_rewrites_binary_payloads():
    payload = {"raw": b"\x01\x02", "nested": {"buf": bytearray(b"abc")}}
    serialized = serialize_response_value(payload)
    assert serialized["raw"] == {"_type": "binary", "size_bytes": 2}
    assert serialized["nested"]["buf"] == {"_type": "binary", "size_bytes": 3}
