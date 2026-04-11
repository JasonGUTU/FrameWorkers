from __future__ import annotations

from datetime import datetime

from src.assistant.models import AgentExecution, ExecutionStatus
from src.assistant.workspace.models import LogEntry
from src.task_stack.api_serialize import serialize_for_api


def test_serializers_handle_agent_execution_model():
    execution = AgentExecution(
        id="exec_1",
        agent_id="a1",
        task_id="t1",
        status=ExecutionStatus.COMPLETED,
        inputs={},
        results={"ok": True},
    )

    execution_dict = serialize_for_api(execution)

    assert execution_dict["status"] == "COMPLETED"
    assert execution_dict["agent_id"] == "a1"
    assert execution_dict["results"] == {"ok": True}


def test_serialize_for_api_handles_log_entry():
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
    log_dict = serialize_for_api(log)
    assert log_dict["event"] == "artifact.persisted"
    assert log_dict["details"] == {"x": 1}
    assert log_dict["execution_id"] == "exec_1"
    assert log_dict["level"] == "INFO"
    assert log_dict["timestamp"] == now.isoformat()


def test_serialize_for_api_rewrites_binary_payloads():
    payload = {"raw": b"\x01\x02", "nested": {"buf": bytearray(b"abc")}}
    serialized = serialize_for_api(payload)
    assert serialized["raw"] == {"_type": "binary", "size_bytes": 2}
    assert serialized["nested"]["buf"] == {"_type": "binary", "size_bytes": 3}
