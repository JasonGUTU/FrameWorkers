"""Workspace module boundary.

`Workspace` is the facade; managers encapsulate their own storage concerns:
- `FileManager`: stateless byte read/write under the workspace runtime path
- `LogManager`: append-only operation logs (one ``event``-typed line per call)
- `GlobalMemory`: per-execution artifact ledger (``global_memory.md``)
- `ArtifactWriter`: execution-aware persistence, snapshot index, hydration
- `InputResolver`: built per-call to match captions against agent ``[label]`` slots
"""

from .workspace import Workspace

__all__ = ['Workspace']
