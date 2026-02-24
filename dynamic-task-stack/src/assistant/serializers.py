"""Serialization helpers for Assistant HTTP responses.

Keeps route handlers focused on request validation and service orchestration.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .models import Assistant, AgentExecution, ExecutionStatus
from .workspace.models import FileMetadata, LogEntry


def serialize_assistant_value(obj: Any) -> Any:
    """Serialize Assistant dataclasses/enums into JSON-compatible values."""
    if isinstance(obj, ExecutionStatus):
        return obj.value
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, (Assistant, AgentExecution)):
        return {k: serialize_assistant_value(v) for k, v in obj.__dict__.items()}
    if isinstance(obj, list):
        return [serialize_assistant_value(item) for item in obj]
    if isinstance(obj, dict):
        return {k: serialize_assistant_value(v) for k, v in obj.items()}
    return obj


def file_metadata_to_dict(file_meta: FileMetadata) -> dict[str, Any]:
    return {
        "id": file_meta.id,
        "filename": file_meta.filename,
        "description": file_meta.description,
        "file_type": file_meta.file_type,
        "file_extension": file_meta.file_extension,
        "file_path": file_meta.file_path,
        "size_bytes": file_meta.size_bytes,
        "created_at": file_meta.created_at.isoformat(),
        "created_by": file_meta.created_by,
        "tags": file_meta.tags,
        "metadata": file_meta.metadata,
    }


def file_search_item_to_dict(file_meta: FileMetadata) -> dict[str, Any]:
    return {
        "id": file_meta.id,
        "filename": file_meta.filename,
        "description": file_meta.description,
        "file_type": file_meta.file_type,
        "file_path": file_meta.file_path,
        "created_at": file_meta.created_at.isoformat(),
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
