# Memory Manager — global memory as one workspace-level markdown file.

from __future__ import annotations

import json
import logging
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

GLOBAL_MEMORY_FILENAME = "global_memory.md"

FILE_TREE_BEGIN = "<!-- FW_FILE_TREE_BEGIN -->"
FILE_TREE_END = "<!-- FW_FILE_TREE_END -->"

ENTRIES_HEADER = "## Entries"
JSON_FENCE_OPEN = "```json"
JSON_FENCE_CLOSE = "```"


class MemoryManager:
    """
    Global memory is one file per workspace:

    ``Runtime/{workspace_id}/global_memory.md``

    Each **entry** in the JSON array has:

    ``content``, ``agent_id``, ``created_at`` (ISO8601 UTC), ``execution_result`` (JSON object,
    execution summary; may be empty ``{}``), and optional ``artifact_locations`` (list of
    ``{"role", "path", ...}`` rows for durable artifact paths).

    The markdown file may include a **File tree** snapshot for **human reading** only.
    Automation must use **live** APIs (``get_workspace_root_file_tree_text``, etc.) and
    ``artifact_locations`` — the embedded tree is not authoritative.
    """

    MAX_ENTRY_COUNT = 2000

    def __init__(self, workspace_id: str, runtime_base_path: Path):
        self.workspace_id = workspace_id
        self.runtime_base_path = Path(runtime_base_path)
        self.workspace_runtime_path = self.runtime_base_path / workspace_id
        self.workspace_runtime_path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _require_task_id(task_id: Optional[str]) -> str:
        tid = str(task_id or "").strip()
        if not tid:
            raise ValueError("task_id is required for global_memory entries")
        if ".." in tid or "/" in tid or "\\" in tid or "\x00" in tid:
            raise ValueError("task_id contains invalid path characters")
        return tid

    def _global_memory_path(self) -> Path:
        return self.workspace_runtime_path / GLOBAL_MEMORY_FILENAME

    @staticmethod
    def _sanitize_text(value: Any) -> str:
        return str(value or "").strip()

    @staticmethod
    def _normalize_artifact_locations(raw: Any) -> List[Dict[str, Any]]:
        if not isinstance(raw, list):
            return []
        out: List[Dict[str, Any]] = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            path = str(item.get("path") or item.get("uri") or "").strip()
            if not path:
                continue
            role = str(item.get("role") or item.get("kind") or "asset").strip() or "asset"
            row: Dict[str, Any] = {"role": role, "path": path}
            ak = item.get("asset_key")
            if isinstance(ak, str) and ak.strip():
                row["asset_key"] = ak.strip()
            desc = item.get("description")
            if isinstance(desc, str) and desc.strip():
                row["description"] = desc.strip()
            out.append(row)
        return out

    @staticmethod
    def _normalize_execution_result(raw: Any) -> Dict[str, Any]:
        if isinstance(raw, dict):
            return dict(raw)
        if isinstance(raw, str) and raw.strip():
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, dict):
                    return dict(parsed)
            except json.JSONDecodeError:
                return {"summary": raw.strip()}
        return {}

    @staticmethod
    def _normalize_entry(raw: Any) -> Dict[str, Any]:
        if not isinstance(raw, dict):
            return {
                "content": "",
                "agent_id": "",
                "created_at": "",
                "execution_result": {},
            }
        base: Dict[str, Any] = {
            "content": MemoryManager._sanitize_text(raw.get("content")),
            "agent_id": MemoryManager._sanitize_text(raw.get("agent_id")),
            "task_id": MemoryManager._sanitize_text(raw.get("task_id")),
            "created_at": MemoryManager._sanitize_text(raw.get("created_at")),
            "execution_result": MemoryManager._normalize_execution_result(
                raw.get("execution_result")
            ),
        }
        al = MemoryManager._normalize_artifact_locations(raw.get("artifact_locations"))
        if al:
            base["artifact_locations"] = al
        return base

    def _parse_entries_json_from_markdown(self, text: str) -> Optional[List[Dict[str, Any]]]:
        if not text.strip():
            return None
        idx = text.find(ENTRIES_HEADER)
        segment = text[idx:] if idx >= 0 else text
        match = re.search(
            r"```json\s*\n([\s\S]*?)\n```",
            segment,
            re.MULTILINE,
        )
        if not match:
            return None
        try:
            data = json.loads(match.group(1).strip())
            if isinstance(data, list):
                return [self._normalize_entry(x) for x in data if isinstance(x, dict)]
        except json.JSONDecodeError as exc:
            logger.warning("Failed to parse JSON entries in global_memory.md: %s", exc)
        return None

    def _read_entries_from_file(self, path: Path) -> List[Dict[str, Any]]:
        if not path.exists():
            return []
        raw = path.read_text(encoding="utf-8")
        parsed = self._parse_entries_json_from_markdown(raw)
        if parsed is not None:
            return [e for e in parsed if e.get("content")]
        logger.warning("global_memory.md present but JSON entries block missing or invalid: %s", path)
        return []

    def _read_entries_aggregate(self) -> List[Dict[str, Any]]:
        return self._read_entries_from_file(self._global_memory_path())

    def _build_file_tree_text(self, root: Path) -> str:
        lines: List[str] = []
        max_lines = 800
        try:
            root = root.resolve()
            all_files = sorted(
                (p for p in root.rglob("*") if p.is_file()),
                key=lambda p: str(p.relative_to(root)).replace("\\", "/"),
            )
        except OSError as exc:
            return f"(unable to list files: {exc})"

        for p in all_files[:max_lines]:
            try:
                rel = p.relative_to(root)
            except ValueError:
                continue
            depth = len(rel.parts)
            indent = "  " * max(0, depth - 1)
            lines.append(f"{indent}{rel.parts[-1]}")
        if len(all_files) > max_lines:
            lines.append(f"... ({len(all_files) - max_lines} more files truncated)")
        return "\n".join(lines) if lines else "(no files yet)"

    def _compose_global_memory_document(
        self,
        entries: List[Dict[str, Any]],
        *,
        file_tree_root: Path,
    ) -> str:
        tree = self._build_file_tree_text(file_tree_root)
        json_body = json.dumps(entries, ensure_ascii=False, indent=2)
        scope = f"workspace `{self.workspace_id}`"
        return (
            f"# Global memory\n\n"
            f"Global memory for {scope}. "
            f"The **Entries** section is the canonical JSON array. "
            f"The **File tree** below is a **human-readable snapshot** at write time (may be truncated); "
            f"for **automation** (persist paths, input packaging, Director), use **live** workspace "
            f"file-tree APIs and ``artifact_locations`` — the snapshot is not authoritative.\n\n"
            f"## File tree\n\n"
            f"{FILE_TREE_BEGIN}\n"
            f"```\n{tree}\n```\n"
            f"{FILE_TREE_END}\n\n"
            f"{ENTRIES_HEADER}\n\n"
            f"{JSON_FENCE_OPEN}\n{json_body}\n{JSON_FENCE_CLOSE}\n"
        )

    def _write_global_memory_file(
        self,
        path: Path,
        entries: List[Dict[str, Any]],
        *,
        file_tree_root: Path,
    ) -> None:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                self._compose_global_memory_document(
                    entries,
                    file_tree_root=file_tree_root,
                ),
                encoding="utf-8",
            )
        except Exception as exc:
            logger.warning("Failed to write global_memory.md at %s: %s", path, exc)
            raise

    def refresh_file_tree(self) -> None:
        """Rewrite ``global_memory.md`` so the human-readable File tree matches disk."""
        path = self._global_memory_path()
        entries = self._read_entries_from_file(path)
        self._write_global_memory_file(
            path,
            entries,
            file_tree_root=self.workspace_runtime_path,
        )

    def add_memory_entry(
        self,
        *,
        content: str,
        task_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        execution_result: Optional[Any] = None,
        artifact_locations: Optional[Any] = None,
    ) -> Dict[str, Any]:
        text = self._sanitize_text(content)
        if not text:
            raise ValueError("content must be non-empty")

        tid = self._require_task_id(task_id)
        er = self._normalize_execution_result(execution_result)
        entry: Dict[str, Any] = {
            "content": text,
            "agent_id": self._sanitize_text(agent_id),
            "task_id": tid,
            "created_at": datetime.now(UTC).isoformat(),
            "execution_result": er,
        }
        al = self._normalize_artifact_locations(artifact_locations)
        if al:
            entry["artifact_locations"] = al

        path = self._global_memory_path()
        entries = self._read_entries_from_file(path) if path.exists() else []
        entries.append(entry)
        if len(entries) > self.MAX_ENTRY_COUNT:
            entries = entries[-self.MAX_ENTRY_COUNT :]
        self._write_global_memory_file(
            path,
            entries,
            file_tree_root=self.workspace_runtime_path,
        )
        return entry

    def list_memory_entries(
        self,
        *,
        task_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        pool = self._read_entries_aggregate()
        if task_id:
            want = self._require_task_id(task_id)
            pool = [x for x in pool if isinstance(x, dict) and x.get("task_id") == want]

        filtered: List[Dict[str, Any]] = []
        for item in reversed(pool):
            if not isinstance(item, dict):
                continue
            if agent_id and item.get("agent_id") != agent_id:
                continue
            filtered.append(item)
            if len(filtered) >= limit:
                break
        return list(reversed(filtered))

    @staticmethod
    def _created_at_sort_key(entry: Dict[str, Any]) -> str:
        return str(entry.get("created_at") or "")

    @staticmethod
    def _entries_without_content(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Same ``global_memory`` entry rows without ``content``; keep ``agent_id`` / ``created_at`` / ``execution_result``."""
        out: List[Dict[str, Any]] = []
        for e in entries:
            if not isinstance(e, dict):
                continue
            slim = {k: v for k, v in e.items() if k != "content"}
            out.append(slim)
        return out

    def _collect_candidates(
        self,
        task_id: Optional[str],
        agent_id: Optional[str],
    ) -> List[Dict[str, Any]]:
        candidates = [
            x for x in self._read_entries_aggregate() if isinstance(x, dict)
        ]
        if task_id:
            want = self._require_task_id(task_id)
            candidates = [x for x in candidates if x.get("task_id") == want]
        if agent_id:
            candidates = [x for x in candidates if x.get("agent_id") == agent_id]
        candidates.sort(key=self._created_at_sort_key, reverse=True)
        return candidates

    def get_memory_brief(
        self,
        *,
        task_id: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """``{"global_memory": [...]}`` without ``content`` (small rows for Director / HTTP)."""
        candidates = self._collect_candidates(task_id, agent_id)
        return {"global_memory": self._entries_without_content(candidates)}

    def workspace_root_file_tree_text(self) -> str:
        """Human-readable tree of all files under the workspace runtime root (includes ``artifacts/``)."""
        return self._build_file_tree_text(self.workspace_runtime_path)

    def file_tree_text_for_task(self, task_id: str) -> str:
        """Human-readable tree of files under this task's runtime directory (for LLM input packing)."""
        tid = self._require_task_id(task_id)
        root = self.workspace_runtime_path / tid
        return self._build_file_tree_text(root)
