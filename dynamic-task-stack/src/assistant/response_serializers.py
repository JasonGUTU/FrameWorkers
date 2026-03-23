"""Serialization helpers for Assistant HTTP responses.

Primary serializer module for Assistant routes, workspace search payloads,
and execution context shaping.
"""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from .workspace.models import FileMetadata, LogEntry


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


def _file_core_fields(file_meta: FileMetadata) -> dict[str, Any]:
    return {
        "id": file_meta.id,
        "filename": file_meta.filename,
        "description": file_meta.description,
        "file_type": file_meta.file_type,
        "file_path": file_meta.file_path,
    }


def file_metadata_to_dict(file_meta: FileMetadata) -> dict[str, Any]:
    return {
        **_file_core_fields(file_meta),
        "file_extension": file_meta.file_extension,
        "size_bytes": file_meta.size_bytes,
        "created_at": file_meta.created_at.isoformat(),
        "created_by": file_meta.created_by,
        "tags": file_meta.tags,
        "metadata": file_meta.metadata,
    }


def file_brief_to_dict(file_meta: FileMetadata) -> dict[str, Any]:
    """Compact file payload for execution context packaging."""
    return _file_core_fields(file_meta)


def file_search_item_to_dict(file_meta: FileMetadata) -> dict[str, Any]:
    return {
        **_file_core_fields(file_meta),
        "created_at": file_meta.created_at.isoformat(),
    }


def log_search_item_to_dict(log: LogEntry) -> dict[str, Any]:
    """Search-friendly log payload."""
    return {
        "id": log.id,
        "timestamp": log.timestamp.isoformat(),
        "operation_type": log.operation_type,
        "resource_type": log.resource_type,
        "resource_id": log.resource_id,
        "details": log.details,
    }


def context_log_item_to_dict(log: LogEntry) -> dict[str, Any]:
    """Compact log payload for execution context packaging."""
    return {
        "timestamp": log.timestamp.isoformat(),
        "operation_type": log.operation_type,
        "resource_type": log.resource_type,
        "resource_id": log.resource_id,
    }


def log_entry_to_dict(log: LogEntry) -> dict[str, Any]:
    return {
        "id": log.id,
        "timestamp": log.timestamp.isoformat(),
        "operation_type": log.operation_type,
        "resource_type": log.resource_type,
        "resource_id": log.resource_id,
        "details": log.details,
        "agent_id": log.agent_id,
        "task_id": log.task_id,
    }

