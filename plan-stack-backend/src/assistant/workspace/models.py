"""Workspace data models — storage DTOs shared by the workspace package.

Defines four dataclasses used as records in the workspace's persistence
layer:

  * ``StoredFile``        — transient handle returned by ``FileManager``
                            after writing bytes (no on-disk index)
  * ``LogEntry``          — single line in ``logs.jsonl``
                            (managed by ``LogManager``)
  * ``ArtifactRef``       — single persisted artifact's caption (one
                            element of ``GlobalMemoryEntry.artifacts``)
  * ``GlobalMemoryEntry`` — one execution's group of artifacts (one
                            element in ``global_memory.md``'s Entries
                            JSON array, managed by ``GlobalMemory``)

These are pure data containers with no behavior.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List


@dataclass
class StoredFile:
    """Transient handle returned by ``FileManager.store_file_at_relative_path``.

    Carries just enough information for the caller to log the write and
    register the artifact. Nothing here is persisted on its own — the
    workspace's source of truth for "what files exist" is
    ``GlobalMemory``.
    """
    path: str          # Absolute filesystem path
    filename: str      # Display name (basename or caller-provided)
    size_bytes: int    # Length of the bytes that were written


@dataclass
class LogEntry:
    """One operation event in ``logs.jsonl``.

    Logs are categorized solely by the namespaced ``event`` string
    (e.g. ``execution.completed``, ``artifact.persisted``,
    ``memory.written``). All call sites must populate ``event`` —
    there are no legacy ``operation_type`` / ``resource_type`` fields.
    """
    id: str
    timestamp: datetime
    event: str                              # required namespaced event
    resource_id: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    agent_id: Optional[str] = None
    step_id: Optional[str] = None
    level: str = "INFO"                     # INFO | WARN | ERROR
    execution_id: Optional[str] = None


@dataclass
class ArtifactRef:
    """One persisted artifact with its semantic caption (memory storage unit).

    Stored inside GlobalMemoryEntry.artifacts. No payload here — global
    memory is an index; content is loaded on demand by InputResolver.

    ``caption`` is a short functional description of the artifact's type
    and pipeline role — enough for InputResolver's LLM to match it to a
    consumer's label slot. Creative content details belong in the payload,
    not here.
    """
    caption: str = ""         # Artifact type + pipeline role (1-2 sentences)
    scope: str = "global"     # global | scene:sc_001 | shot:sh_001
    path: str = ""            # Absolute filesystem path
    mime: str = ""            # MIME type


@dataclass
class GlobalMemoryEntry:
    """One execution's persisted artifacts — each with its own semantic caption."""
    execution_id: str
    agent_id: str
    step_id: str
    created_at: datetime
    artifacts: List[ArtifactRef]  # per-artifact captions + paths
