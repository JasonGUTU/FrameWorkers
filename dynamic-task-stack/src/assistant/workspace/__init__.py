"""Workspace module boundary.

`Workspace` is the facade; managers encapsulate their own storage concerns:
- `FileManager`: file bytes + metadata persistence
- `MemoryManager`: global memory read/write/truncation
- `LogManager`: append-only operation logs
"""

from .workspace import Workspace
from .file_manager import FileManager
from .memory_manager import MemoryManager
from .log_manager import LogManager

__all__ = ['Workspace', 'FileManager', 'MemoryManager', 'LogManager']
