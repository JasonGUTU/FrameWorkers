"""Serialization helpers for Assistant HTTP responses.

Primary serializer module for Assistant routes, workspace search payloads,
and execution context shaping.
"""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from .workspace.models import LogEntry


def serialize_response_value(obj: Any) -> Any:
    """Serialize dataclasses/enums into JSON-compatible values."""
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, datetime):
        return obj.isoformat()
    if is_dataclass(obj):
        return {
            field.name: serialize_response_value(getattr(obj, field.name))
            for field in fields(obj)
        }
    if isinstance(obj, (bytes, bytearray)):
        # Never return raw binary payloads in JSON responses.
        return {
            "_type": "binary",
            "size_bytes": len(obj),
        }
    if isinstance(obj, list):
        return [serialize_response_value(item) for item in obj]
    if isinstance(obj, dict):
        return {k: serialize_response_value(v) for k, v in obj.items()}
    return obj


def log_entry_to_dict(log: LogEntry) -> dict[str, Any]:
    return {
        "id": log.id,
        "timestamp": log.timestamp.isoformat(),
        "event": log.event,
        "level": log.level,
        "resource_id": log.resource_id,
        "details": log.details,
        "agent_id": log.agent_id,
        "task_id": log.task_id,
        "execution_id": log.execution_id,
    }

