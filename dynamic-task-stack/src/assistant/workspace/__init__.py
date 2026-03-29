"""Workspace module boundary.

`Workspace` is the facade; managers encapsulate their own storage concerns:
- `FileManager`: file bytes + metadata persistence
- `MemoryManager`: per-task ``global_memory.md`` (structured entries + file tree)
- `LogManager`: append-only operation logs
- `AssetManager`: asset persistence, snapshot index, hydration
"""

from .workspace import Workspace
from .file_manager import FileManager
from .memory_manager import MemoryManager
from .log_manager import LogManager
from .asset_manager import AssetManager

__all__ = ['Workspace', 'FileManager', 'MemoryManager', 'LogManager', 'AssetManager']
