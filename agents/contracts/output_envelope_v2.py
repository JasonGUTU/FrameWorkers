"""Output envelope v2 contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class StructuredOutputV2:
    semantic_type: str
    schema_ref: str
    payload: dict[str, Any]


@dataclass
class BinaryOutputV2:
    artifact_id: str
    semantic_type: str
    filename: str
    mime: str
    file_content: bytes
    description: str = ""


@dataclass
class OutputEnvelopeV2:
    structured_outputs: list[StructuredOutputV2] = field(default_factory=list)
    binary_outputs: list[BinaryOutputV2] = field(default_factory=list)
    relations: list[dict[str, Any]] = field(default_factory=list)
    naming_specs: list[dict[str, Any]] = field(default_factory=list)
