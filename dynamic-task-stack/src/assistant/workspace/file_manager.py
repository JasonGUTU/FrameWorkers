"""File manager — stateless byte read/write under the workspace runtime path.

Responsibilities:
  * Write raw bytes to a workspace-relative path; reject path escapes.
  * Read bytes back from absolute filesystem paths.
  * Unlink a workspace file by absolute path.

What it does NOT do:
  * Maintain any metadata index — the artifact registry is the single
    source of truth for "what files exist in this workspace and what
    they are". This module is a thin filesystem boundary, nothing more.
  * Emit log entries — ``Workspace.store_file_at_relative_path`` no
    longer logs at this layer; the meaningful event ("an agent
    artifact has been persisted") is recorded one layer up by
    ``ArtifactWriter`` so log readers see exactly one entry per
    logical persistence.
  * Understand executions, agents, slot keys, or captions.

Used by:
  * ``Workspace`` exposes its methods directly + wires
    ``read_binary_from_uri`` and ``store_file_at_relative_path`` as
    callbacks into ``ArtifactWriter``; ``Workspace`` itself wraps unlink
    via ``_delete_file_at_path``.
  * ``InputResolver._load_json`` reads JSON files via ``read_binary_from_uri``.
"""

from pathlib import Path
from typing import Optional

from .models import StoredFile


class FileManager:
    """Workspace-scoped file I/O. No metadata, no index.

    All persistence concerns (producer agent, captions, etc.) are handled
    by ``GlobalMemory``. ``FileManager`` only knows about bytes and paths
    under ``Runtime/{workspace_id}/``.
    """

    def __init__(self, workspace_id: str, runtime_base_path: Path):
        self.workspace_id = workspace_id
        self.runtime_base_path = Path(runtime_base_path)
        self.workspace_runtime_path = self.runtime_base_path / workspace_id
        self.workspace_runtime_path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _sanitize_relative_workspace_path(raw: str) -> Path:
        """Return a path relative to ``workspace_runtime_path``; reject escapes."""
        if not raw or not str(raw).strip():
            raise ValueError("relative_path must be non-empty")
        s = str(raw).strip().replace("\\", "/")
        if ".." in s or s.startswith("/"):
            raise ValueError("invalid relative_path")
        rel = Path(s)
        if any(p == ".." for p in rel.parts):
            raise ValueError("invalid relative_path")
        return rel

    def store_file_at_relative_path(
        self,
        relative_path: str,
        file_content: bytes,
        filename: str = "",
    ) -> StoredFile:
        """Write bytes under ``Runtime/{workspace_id}/<relative_path>``.

        ``filename`` is optional; if empty, derived from ``relative_path``.
        Returns a transient ``StoredFile`` (path/filename/size). No state
        is kept on this manager.
        """
        rel = self._sanitize_relative_workspace_path(relative_path)
        dest = (self.workspace_runtime_path / rel).resolve()
        base = self.workspace_runtime_path.resolve()
        if not str(dest).startswith(str(base)):
            raise ValueError("path escapes workspace")
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "wb") as fh:
            fh.write(file_content)
        return StoredFile(
            path=str(dest),
            filename=filename or dest.name,
            size_bytes=len(file_content),
        )

    def read_binary_from_uri(self, uri: str) -> Optional[bytes]:
        """Read binary payload from a filesystem uri/path."""
        if not uri:
            return None
        file_path = Path(uri)
        if not file_path.exists() or not file_path.is_file():
            return None
        try:
            return file_path.read_bytes()
        except OSError:
            return None
