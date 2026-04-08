"""Log manager — append-only operation log in JSON Lines format.

Responsibilities:
  * Append one ``LogEntry`` per recorded event to ``logs.jsonl``.
  * Categorize every entry by its namespaced ``event`` string
    (e.g. ``execution.completed``, ``artifact.persisted``,
    ``memory.written``).
  * Filter logs by ``event`` / ``agent_id`` / ``task_id`` / ``level`` /
    ``execution_id`` when serving queries.

What it does NOT do:
  * Decide what to log — callers (Workspace methods, ArtifactWriter
    callbacks) are responsible for choosing event names and details.
  * Aggregate or summarize — read-side filtering only.

Used by:
  * ``Workspace`` exposes ``add_log`` (via ``_add_log``) and ``get_logs``.
  * ``routes.py`` exposes ``get_logs`` over HTTP.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import logging

from .models import LogEntry

logger = logging.getLogger(__name__)


class LogManager:
    """Append-only ``logs.jsonl`` writer / reader for one workspace.

    Every entry carries a namespaced ``event`` string. Recommended namespaces:

    * ``workspace.*`` — workspace lifecycle (e.g. ``workspace.created``)
    * ``user.*`` — caller-driven events (e.g. ``user.upload``)
    * ``execution.*`` — agent execution lifecycle
    * ``artifact.*`` — file persistence events emitted by ArtifactWriter
    * ``memory.*`` — global memory writes
    """

    def __init__(self, workspace_id: str, runtime_base_path: Path):
        self.workspace_id = workspace_id
        self.runtime_base_path = Path(runtime_base_path)
        self.workspace_runtime_path = self.runtime_base_path / workspace_id
        self.log_file_path = self.workspace_runtime_path / "logs.jsonl"

        self._logs: List[LogEntry] = []
        self.workspace_runtime_path.mkdir(parents=True, exist_ok=True)
        self._load_logs()

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _log_to_json_dict(log_entry: LogEntry) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "id": log_entry.id,
            "timestamp": log_entry.timestamp.isoformat(),
            "event": log_entry.event,
            "resource_id": log_entry.resource_id,
            "details": log_entry.details,
            "agent_id": log_entry.agent_id,
            "task_id": log_entry.task_id,
            "level": log_entry.level,
        }
        if log_entry.execution_id is not None:
            d["execution_id"] = log_entry.execution_id
        return d

    @staticmethod
    def _parse_log_line(line: str) -> Optional[LogEntry]:
        line = line.strip()
        if not line:
            return None
        data = json.loads(line)
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        # Drop any historical fields that no longer live on LogEntry so
        # legacy logs.jsonl files written before the schema cleanup still
        # parse cleanly.
        for legacy in ("operation_type", "resource_type"):
            data.pop(legacy, None)
        # Old jsonl rows lacked a top-level event — historically the
        # categorisation lived in details.event_type. Promote it so the
        # row can still be filtered by event after parsing.
        if not data.get("event"):
            details = data.get("details") or {}
            event_type = details.get("event_type") if isinstance(details, dict) else None
            data["event"] = str(event_type or "")
        data.setdefault("level", "INFO")
        data.setdefault("execution_id", None)
        data.pop("duration_ms", None)
        return LogEntry(**data)

    @staticmethod
    def _matches_filters(
        log_entry: LogEntry,
        *,
        event: Optional[str] = None,
        agent_id: Optional[str] = None,
        task_id: Optional[str] = None,
        level: Optional[str] = None,
        execution_id: Optional[str] = None,
    ) -> bool:
        if event and log_entry.event != event:
            return False
        if agent_id and log_entry.agent_id != agent_id:
            return False
        if task_id and log_entry.task_id != task_id:
            return False
        if level and log_entry.level != level:
            return False
        if execution_id and log_entry.execution_id != execution_id:
            return False
        return True

    @staticmethod
    def _sort_newest_first(logs: List[LogEntry]) -> List[LogEntry]:
        return sorted(logs, key=lambda x: x.timestamp, reverse=True)

    def _load_logs(self):
        if not self.log_file_path.exists():
            return
        try:
            with open(self.log_file_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        log_entry = self._parse_log_line(line)
                        if log_entry:
                            self._logs.append(log_entry)
                    except Exception as e:
                        logger.warning("Failed to parse log entry: %s", e)
        except Exception as e:
            logger.warning("Failed to load logs: %s", e)

    def _append_log_to_file(self, log_entry: LogEntry):
        try:
            with open(self.log_file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(self._log_to_json_dict(log_entry), ensure_ascii=False) + "\n")
        except Exception as e:
            logger.warning("Failed to write log entry: %s", e)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_log(
        self,
        *,
        event: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        agent_id: Optional[str] = None,
        task_id: Optional[str] = None,
        level: str = "INFO",
        execution_id: Optional[str] = None,
    ) -> LogEntry:
        """Append a log entry. ``event`` is required and must be a
        non-empty namespaced string (e.g. ``"artifact.persisted"``).
        """
        if not event:
            raise ValueError("LogManager.add_log requires a non-empty event")
        log_entry = LogEntry(
            id=f"log_{uuid.uuid4().hex[:12]}",
            timestamp=datetime.now(),
            event=event,
            resource_id=resource_id,
            details=details or {},
            agent_id=agent_id,
            task_id=task_id,
            level=level,
            execution_id=execution_id,
        )
        self._logs.append(log_entry)
        self._append_log_to_file(log_entry)
        return log_entry

    def get_logs(
        self,
        *,
        event: Optional[str] = None,
        agent_id: Optional[str] = None,
        task_id: Optional[str] = None,
        limit: Optional[int] = None,
        level: Optional[str] = None,
        execution_id: Optional[str] = None,
    ) -> List[LogEntry]:
        """Get logs with optional filters."""
        results = [
            log_entry
            for log_entry in self._logs
            if self._matches_filters(
                log_entry,
                event=event,
                agent_id=agent_id,
                task_id=task_id,
                level=level,
                execution_id=execution_id,
            )
        ]
        results = self._sort_newest_first(results)
        if limit:
            results = results[:limit]
        return results
