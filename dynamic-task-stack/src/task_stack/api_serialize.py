"""JSON-safe serialization for Task Stack API models (dataclasses, enums, nested structures)."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from datetime import datetime
from enum import Enum
from typing import Any


def serialize_for_api(obj: Any) -> Any:
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, datetime):
        return obj.isoformat()
    if is_dataclass(obj):
        return {
            field.name: serialize_for_api(getattr(obj, field.name))
            for field in fields(obj)
        }
    if isinstance(obj, list):
        return [serialize_for_api(item) for item in obj]
    if isinstance(obj, dict):
        return {key: serialize_for_api(value) for key, value in obj.items()}
    return obj
