"""Memory manager — workspace-level semantic memory in markdown.

Responsibilities:
  * Store semantic decisions and project context — the "why" behind agent
    work — as structured JSON entries embedded in ``global_memory.md``.
  * Render a workspace file tree text representation for LLM prompts.

What it does NOT do:
  * Store artifact paths or per-file metadata — those live in
    ``artifact_registry.jsonl`` (managed by ``ArtifactRegistry``).
  * Decide what to remember — callers (Workspace, AssetManager) choose.

Used by:
  * ``Workspace.add_memory_entry`` / ``list_memory_entries`` /
    ``get_memory_brief`` / ``get_workspace_root_file_tree_text``.
  * ``service.AssistantService`` calls these via the Workspace facade
    after each execution to record the agent's contribution.
"""

from __future__ import annotations

import json
import logging
import os
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

GLOBAL_MEMORY_FILENAME = "global_memory.md"

ENTRIES_HEADER = "## Entries"
JSON_FENCE_OPEN = "```json"
JSON_FENCE_CLOSE = "```"


def _assistant_global_memory_row_limit_default() -> int:
    try:
        n = int(os.getenv("ASSISTANT_GLOBAL_MEMORY_CONTEXT_ENTRIES_MAX", "20").strip())
        return max(1, min(n, 500))
    except ValueError:
        return 20


class MemoryManager:
    """
    Global memory is one file per workspace:

    ``Runtime/{workspace_id}/global_memory.md``

    Each **entry** records semantic decisions and project context — the "why"
    behind agent outputs.  Artifact paths live in ``artifact_registry.jsonl``;
    do not store them here.

    Entry shape::

        {
          "content": {
            "what": "one-sentence description of what was done",
            "why": "key decision rationale",
            "context_note": "optional extra context for future agents"
          },
          "agent_id": "ScreenplayAgent",
          "task_id": "task_1_xxx",
          "execution_id": "exec_2_xxx",
          "created_at": "<ISO8601 UTC>",
          "supersedes": null   // entry_id of superseded entry, or null
        }
    """

    MAX_ENTRY_COUNT = 2000

    def __init__(self, workspace_id: str, runtime_base_path: Path) -> None:
        self.workspace_id = workspace_id
        self.runtime_base_path = Path(runtime_base_path)
        self.workspace_runtime_path = self.runtime_base_path / workspace_id
        self.workspace_runtime_path.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Path helpers
    # ------------------------------------------------------------------

    def _global_memory_path(self) -> Path:
        return self.workspace_runtime_path / GLOBAL_MEMORY_FILENAME

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _require_task_id(task_id: Optional[str]) -> str:
        tid = str(task_id or "").strip()
        if not tid:
            raise ValueError("task_id is required for global_memory entries")
        if ".." in tid or "/" in tid or "\\" in tid or "\x00" in tid:
            raise ValueError("task_id contains invalid path characters")
        return tid

    @staticmethod
    def _sanitize_text(value: Any) -> str:
        return str(value or "").strip()

    # ------------------------------------------------------------------
    # Content normalisation
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_content(raw: Any) -> Dict[str, str]:
        """Accept either a structured dict or a plain string (legacy)."""
        if isinstance(raw, dict):
            return {
                "what": str(raw.get("what") or ""),
                "why": str(raw.get("why") or ""),
                "context_note": str(raw.get("context_note") or ""),
            }
        # Legacy plain-string content — promote to structured form
        text = str(raw or "").strip()
        return {"what": text, "why": "", "context_note": ""}

    @staticmethod
    def _normalize_entry(raw: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "content": MemoryManager._normalize_content(raw.get("content")),
            "agent_id": MemoryManager._sanitize_text(raw.get("agent_id")),
            "task_id": MemoryManager._sanitize_text(raw.get("task_id")),
            "execution_id": MemoryManager._sanitize_text(raw.get("execution_id")),
            "created_at": MemoryManager._sanitize_text(raw.get("created_at")),
            "supersedes": raw.get("supersedes"),  # None or entry reference string
        }

    def _entry_has_content(self, entry: Dict[str, Any]) -> bool:
        c = entry.get("content")
        if isinstance(c, dict):
            return bool(c.get("what") or c.get("why") or c.get("context_note"))
        return bool(c)

    # ------------------------------------------------------------------
    # JSON parsing from markdown
    # ------------------------------------------------------------------

    def _parse_entries_json_from_markdown(self, text: str) -> Optional[List[Dict[str, Any]]]:
        if not text.strip():
            return None
        idx = text.find(ENTRIES_HEADER)
        segment = text[idx:] if idx >= 0 else text
        match = re.search(r"```json\s*\n([\s\S]*?)\n```", segment, re.MULTILINE)
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
            return [e for e in parsed if self._entry_has_content(e)]
        logger.warning("global_memory.md present but JSON entries block missing or invalid: %s", path)
        return []

    def _read_entries_aggregate(self) -> List[Dict[str, Any]]:
        return self._read_entries_from_file(self._global_memory_path())

    # ------------------------------------------------------------------
    # Document composition
    # ------------------------------------------------------------------

    def _compose_global_memory_document(self, entries: List[Dict[str, Any]]) -> str:
        json_body = json.dumps(entries, ensure_ascii=False, indent=2)
        scope = f"workspace `{self.workspace_id}`"
        return (
            f"# Global memory\n\n"
            f"Global memory for {scope}. "
            f"Records semantic decisions and project context — the 'why' behind agent outputs.\n"
            f"Artifact paths are in ``artifact_registry.jsonl`` (not here).\n\n"
            f"{ENTRIES_HEADER}\n\n"
            f"{JSON_FENCE_OPEN}\n{json_body}\n{JSON_FENCE_CLOSE}\n"
        )

    # ------------------------------------------------------------------
    # File writes
    # ------------------------------------------------------------------

    def _write_global_memory_file(self, path: Path, entries: List[Dict[str, Any]]) -> None:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(self._compose_global_memory_document(entries), encoding="utf-8")
        except Exception as exc:
            logger.warning("Failed to write global_memory.md at %s: %s", path, exc)
            raise

    # ------------------------------------------------------------------
    # Public write API
    # ------------------------------------------------------------------

    def add_memory_entry(
        self,
        *,
        content: Any,
        task_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        supersedes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Append one entry to global_memory.md.

        ``content`` may be:
          - a dict with keys ``what``, ``why``, ``context_note``  (preferred)
          - a plain string (promoted to ``{"what": text, ...}``)

        ``supersedes`` should be the ``execution_id`` of the entry being
        replaced (e.g. on re-runs), allowing readers to identify stale entries.
        """
        normalized_content = self._normalize_content(content)
        if not any(normalized_content.values()):
            raise ValueError("content must be non-empty (at least one of what/why/context_note)")

        tid = self._require_task_id(task_id)
        entry: Dict[str, Any] = {
            "content": normalized_content,
            "agent_id": self._sanitize_text(agent_id),
            "task_id": tid,
            "execution_id": self._sanitize_text(execution_id),
            "created_at": datetime.now(UTC).isoformat(),
            "supersedes": supersedes,
        }

        path = self._global_memory_path()
        entries = self._read_entries_from_file(path) if path.exists() else []
        entries.append(entry)
        if len(entries) > self.MAX_ENTRY_COUNT:
            entries = entries[-self.MAX_ENTRY_COUNT:]
        self._write_global_memory_file(path, entries)
        return entry

    # ------------------------------------------------------------------
    # Public read API
    # ------------------------------------------------------------------

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

    _BRIEF_ROW_KEYS: tuple[str, ...] = (
        "task_id",
        "agent_id",
        "execution_id",
        "created_at",
    )

    @classmethod
    def _brief_memory_rows(cls, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for e in entries:
            if not isinstance(e, dict):
                continue
            row = {k: e[k] for k in cls._BRIEF_ROW_KEYS if k in e}
            # Include the 'what' summary for quick context
            content = e.get("content")
            if isinstance(content, dict) and content.get("what"):
                row["what"] = content["what"]
            out.append(row)
        return out

    def _collect_candidates(
        self,
        task_id: Optional[str],
        agent_id: Optional[str],
    ) -> List[Dict[str, Any]]:
        candidates = [x for x in self._read_entries_aggregate() if isinstance(x, dict)]
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
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """``{"global_memory": [...]}`` — brief rows for director/HTTP responses."""
        candidates = self._collect_candidates(task_id, agent_id)
        if limit is None:
            candidates = candidates[: _assistant_global_memory_row_limit_default()]
        elif limit == 0:
            pass
        else:
            candidates = candidates[: max(1, int(limit))]
        return {"global_memory": self._brief_memory_rows(candidates)}

    def workspace_root_file_tree_text(self) -> str:
        """Human-readable tree of all files under the workspace runtime root."""
        return self._build_file_tree_text(self.workspace_runtime_path)

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
