# Memory Manager — short-term structured memory only (STM).
# Long-term (LTM) persistence and brief aggregation are intentionally disabled.

from __future__ import annotations

import json
import logging
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MemoryManager:
    """
    Manages structured short-term memory entries (JSON file on disk).

    Long-term tier is not stored: ``add_memory_entry(..., tier='long_term')`` raises
    ``ValueError``; ``list_memory_entries(tier='long_term')`` returns ``[]``;
    ``get_memory_brief`` always returns ``long_term: []``.
    """

    MAX_ENTRY_COUNT = 2000
    MEMORY_KINDS = {
        "note",
        "constraint",
        "decision",
        "strategy",
        "failure_pattern",
        "next_action",
        "user_preference",
        "execution_summary",
    }

    def __init__(self, workspace_id: str, runtime_base_path: Path):
        self.workspace_id = workspace_id
        self.runtime_base_path = Path(runtime_base_path)
        self.workspace_runtime_path = self.runtime_base_path / workspace_id
        self.short_term_entries_path = (
            self.workspace_runtime_path / "memory_entries_short_term.json"
        )
        self.legacy_entries_path = self.workspace_runtime_path / "memory_entries.json"
        self.workspace_runtime_path.mkdir(parents=True, exist_ok=True)
        self._ensure_structured_entries_storage()

    def _ensure_structured_entries_storage(self) -> None:
        if not self.short_term_entries_path.exists():
            self._write_entries(self.short_term_entries_path, [])

    @staticmethod
    def _sanitize_text(value: Any) -> str:
        return str(value or "").strip()

    @staticmethod
    def _normalize_kind(kind: str) -> str:
        normalized = MemoryManager._sanitize_text(kind).lower()
        return normalized if normalized in MemoryManager.MEMORY_KINDS else "note"

    def _read_entries(self, path: Path) -> List[Dict[str, Any]]:
        if not path.exists():
            return []
        try:
            raw = path.read_text(encoding="utf-8")
            data = json.loads(raw) if raw.strip() else []
            return data if isinstance(data, list) else []
        except Exception as exc:
            logger.warning("Failed to read memory entries file %s: %s", path, exc)
            return []

    def _write_entries(self, path: Path, entries: List[Dict[str, Any]]) -> None:
        try:
            path.write_text(
                json.dumps(entries, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as exc:
            logger.warning("Failed to write memory entries file %s: %s", path, exc)
            raise

    def add_memory_entry(
        self,
        *,
        content: str,
        tier: str = "short_term",
        kind: str = "note",
        task_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        source_asset_refs: Optional[List[str]] = None,
        priority: int = 3,
        confidence: Optional[float] = None,
        ttl_runs: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        normalized_tier = self._sanitize_text(tier).lower()
        if normalized_tier == "long_term":
            raise ValueError(
                "long_term memory is disabled; only short_term entries are supported"
            )
        if normalized_tier != "short_term":
            normalized_tier = "short_term"

        text = self._sanitize_text(content)
        if not text:
            raise ValueError("content must be non-empty")

        entry: Dict[str, Any] = {
            "id": f"mem_{uuid.uuid4().hex[:12]}",
            "tier": "short_term",
            "kind": self._normalize_kind(kind),
            "content": text,
            "task_id": task_id or "",
            "agent_id": agent_id or "",
            "source_asset_refs": list(source_asset_refs or []),
            "priority": int(priority),
            "confidence": confidence,
            "ttl_runs": ttl_runs,
            "metadata": dict(metadata or {}),
            "created_at": datetime.now(UTC).isoformat(),
        }

        entries = self._read_entries(self.short_term_entries_path)
        entries.append(entry)
        if len(entries) > self.MAX_ENTRY_COUNT:
            entries = entries[-self.MAX_ENTRY_COUNT :]
        self._write_entries(self.short_term_entries_path, entries)
        return entry

    def list_memory_entries(
        self,
        *,
        tier: Optional[str] = None,
        task_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        kinds: Optional[List[str]] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        if tier and self._sanitize_text(tier).lower() == "long_term":
            return []

        entries = self._read_entries(self.short_term_entries_path)
        filtered: List[Dict[str, Any]] = []
        for item in reversed(entries):
            if not isinstance(item, dict):
                continue
            if task_id and item.get("task_id") != task_id:
                continue
            if agent_id and item.get("agent_id") != agent_id:
                continue
            if kinds and item.get("kind") not in kinds:
                continue
            filtered.append(item)
            if len(filtered) >= limit:
                break
        return list(reversed(filtered))

    def search_memory_entries(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        q = self._sanitize_text(query).lower()
        if not q:
            return []
        matches: List[Dict[str, Any]] = []
        for item in reversed(self._read_entries(self.short_term_entries_path)):
            if not isinstance(item, dict):
                continue
            if q in self._sanitize_text(item.get("content", "")).lower():
                matches.append(item)
            if len(matches) >= limit:
                break
        return list(reversed(matches))

    @staticmethod
    def _score_entry(entry: Dict[str, Any]) -> float:
        try:
            p = float(entry.get("priority", 3))
        except (TypeError, ValueError):
            p = 3.0
        try:
            c = float(entry.get("confidence", 0.5) or 0.5)
        except (TypeError, ValueError):
            c = 0.5
        return p * 10 + c

    def get_memory_brief(
        self,
        *,
        task_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        short_term_limit: int = 6,
    ) -> Dict[str, Any]:
        all_entries = self._read_entries(self.short_term_entries_path)
        candidates: List[Dict[str, Any]] = []
        for item in all_entries:
            if not isinstance(item, dict):
                continue
            if task_id and agent_id:
                if item.get("task_id") != task_id and item.get("agent_id") != agent_id:
                    continue
            elif task_id:
                if item.get("task_id") != task_id:
                    continue
            elif agent_id:
                if item.get("agent_id") != agent_id:
                    continue
            candidates.append(item)

        candidates.sort(key=self._score_entry, reverse=True)
        cap = max(0, short_term_limit)
        return {
            "short_term": candidates[:cap],
            "long_term": [],
        }

    def get_memory_info(self) -> Dict[str, Any]:
        entries = self._read_entries(self.short_term_entries_path)
        return {
            "entries_count": len(entries),
            "short_term_entries_count": len(entries),
            "long_term_entries_count": 0,
            "short_term_entries_file_path": str(self.short_term_entries_path),
            "long_term_entries_file_path": None,
            "legacy_entries_file_path": str(self.legacy_entries_path),
        }
