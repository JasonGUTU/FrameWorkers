"""JSON-safe serialization shared by Task Stack and Assistant routes.

Handles dataclasses, Pydantic BaseModels, enums, datetimes, nested
containers, and binary payloads (``bytes`` / ``bytearray`` are rewritten
to a stub ``{"_type": "binary", "size_bytes": ...}`` so JSON responses
never carry raw bytes).
"""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel


def serialize_for_api(obj: Any) -> Any:
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, BaseModel):
        # Pydantic models (e.g. ResolvedArtifactEntry carried inside
        # execution inputs) aren't JSON-serializable out of the box.
        # Convert via model_dump and recurse so nested BaseModels,
        # datetimes, and enums still get normalised.
        return serialize_for_api(obj.model_dump())
    if is_dataclass(obj):
        return {
            field.name: serialize_for_api(getattr(obj, field.name))
            for field in fields(obj)
        }
    if isinstance(obj, (bytes, bytearray)):
        # Never return raw binary payloads in JSON responses.
        return {
            "_type": "binary",
            "size_bytes": len(obj),
        }
    if isinstance(obj, list):
        return [serialize_for_api(item) for item in obj]
    if isinstance(obj, dict):
        return {key: serialize_for_api(value) for key, value in obj.items()}
    return obj
