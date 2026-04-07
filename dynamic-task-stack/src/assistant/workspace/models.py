"""Workspace data models — storage DTOs shared by the workspace package.

Defines four dataclasses used as records in the workspace's persistence
layer:

  * ``FileMetadata``       — index entry in ``.file_metadata.json``
                             (managed by ``FileManager``)
  * ``LogEntry``           — single line in ``logs.jsonl``
                             (managed by ``LogManager``)
  * ``ArtifactRef``        — single persisted artifact's caption
                             (one element of ``ArtifactRegistryEntry``)
  * ``ArtifactRegistryEntry`` — one execution's group of artifacts
                             (one line in ``artifact_registry.jsonl``,
                             managed by ``ArtifactRegistry``)

These are pure data containers with no behavior.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List


@dataclass
class FileMetadata:
    """Metadata for a file in the workspace"""
    id: str
    filename: str
    description: str
    file_type: str  # e.g., 'image', 'video', 'text', 'json'
    file_extension: str  # e.g., '.png', '.mp4', '.txt'
    file_path: str  # Path in Runtime folder
    size_bytes: int
    created_at: datetime
    created_by: Optional[str] = None  # Agent ID or user ID
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata


@dataclass
class LogEntry:
    """Log entry in JSON format"""
    id: str
    timestamp: datetime
    operation_type: str  # legacy: 'read', 'write', 'create', 'delete'
    resource_type: str   # legacy: 'file', 'memory', 'execution', 'asset'
    resource_id: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    agent_id: Optional[str] = None
    task_id: Optional[str] = None
    # New fields — populated by callers that use the namespaced event API
    event: Optional[str] = None          # e.g. 'execution.completed', 'artifact.persisted'
    level: str = "INFO"                  # INFO | WARN | ERROR
    execution_id: Optional[str] = None
    duration_ms: Optional[int] = None


@dataclass
class ArtifactRef:
    """One persisted artifact with its semantic caption (registry storage unit).

    Stored inside ArtifactRegistryEntry.artifacts.  No payload here — the
    registry is an index; content is loaded on demand by InputResolver.

    Captions (``what`` / ``why``) are written by the producing agent in
    natural language describing the artifact's nature, role, and purpose.
    Downstream consumers find artifacts purely through LLM semantic
    interpretation of these captions — no machine-readable type tags.
    """
    what: str = ""           # Self-describing natural-language caption
    why: str = ""             # Purpose / role / how it relates to the pipeline
    scope: str = "global"     # global | scene:sc_001 | shot:sh_001
    path: str = ""            # Absolute filesystem path
    mime: str = ""            # MIME type


@dataclass
class ArtifactRegistryEntry:
    """One execution's persisted artifacts — each with its own semantic caption."""
    entry_id: str
    execution_id: str
    agent_id: str
    task_id: str
    created_at: datetime
    artifacts: List[ArtifactRef]  # per-artifact captions + paths
