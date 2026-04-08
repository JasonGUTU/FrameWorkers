"""Workspace module boundary.

`Workspace` is the facade; managers encapsulate their own storage concerns:
- `FileManager`: stateless byte read/write under the workspace runtime path
- `LogManager`: append-only operation logs (one ``event``-typed line per call)
- `GlobalMemory`: per-execution artifact ledger (``global_memory.md``)
- `ArtifactWriter`: execution-aware persistence, snapshot index, hydration
- `InputResolver`: built per-call to match captions against agent ``[label]`` slots
"""

from .workspace import Workspace
from .file_manager import FileManager
from .log_manager import LogManager
from .artifact_writer import ArtifactWriter
from .global_memory import GlobalMemory
from .input_resolver import InputResolver

__all__ = [
    'Workspace', 'FileManager', 'LogManager',
    'ArtifactWriter', 'GlobalMemory', 'InputResolver',
]
