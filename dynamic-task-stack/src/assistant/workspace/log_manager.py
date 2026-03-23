# Log Manager - Manages logs and records

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid
import logging

from .models import LogEntry

logger = logging.getLogger(__name__)


class LogManager:
    """
    Manages logs and records in JSON format
    
    Responsibilities:
    - Store log entries as JSON
    - Record read/write/create/delete operations
    - Provide log query and retrieval interfaces
    """
    
    def __init__(self, workspace_id: str, runtime_base_path: Path):
        """
        Initialize log manager
        
        Args:
            workspace_id: ID of the workspace
            runtime_base_path: Base path to Runtime directory
        """
        self.workspace_id = workspace_id
        self.runtime_base_path = Path(runtime_base_path)
        self.workspace_runtime_path = self.runtime_base_path / workspace_id
        self.log_file_path = self.workspace_runtime_path / "logs.jsonl"  # JSON Lines format
        
        # In-memory log cache
        self._logs: List[LogEntry] = []
        
        # Ensure workspace directory exists
        self.workspace_runtime_path.mkdir(parents=True, exist_ok=True)
        
        # Load existing logs
        self._load_logs()

    # ------------------------------------------------------------------
    # Internal boundary helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _log_to_json_dict(log_entry: LogEntry) -> Dict[str, Any]:
        return {
            'id': log_entry.id,
            'timestamp': log_entry.timestamp.isoformat(),
            'operation_type': log_entry.operation_type,
            'resource_type': log_entry.resource_type,
            'resource_id': log_entry.resource_id,
            'details': log_entry.details,
            'agent_id': log_entry.agent_id,
            'task_id': log_entry.task_id
        }

    @staticmethod
    def _parse_log_line(line: str) -> Optional[LogEntry]:
        line = line.strip()
        if not line:
            return None
        data = json.loads(line)
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return LogEntry(**data)

    @staticmethod
    def _matches_filters(
        log_entry: LogEntry,
        *,
        operation_type: Optional[str] = None,
        resource_type: Optional[str] = None,
        agent_id: Optional[str] = None,
        task_id: Optional[str] = None,
    ) -> bool:
        if operation_type and log_entry.operation_type != operation_type:
            return False
        if resource_type and log_entry.resource_type != resource_type:
            return False
        if agent_id and log_entry.agent_id != agent_id:
            return False
        if task_id and log_entry.task_id != task_id:
            return False
        return True

    @staticmethod
    def _sort_newest_first(logs: List[LogEntry]) -> List[LogEntry]:
        return sorted(logs, key=lambda x: x.timestamp, reverse=True)

    @staticmethod
    def _top_counts(values: List[str], limit: int) -> List[Dict[str, Any]]:
        counter: Dict[str, int] = {}
        for value in values:
            if not value:
                continue
            counter[value] = counter.get(value, 0) + 1
        pairs = sorted(counter.items(), key=lambda item: (-item[1], item[0]))
        return [{"key": key, "count": count} for key, count in pairs[:limit]]
    
    def _load_logs(self):
        """Load logs from disk"""
        if not self.log_file_path.exists():
            return
        
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
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
        """Append a log entry to the log file"""
        try:
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(self._log_to_json_dict(log_entry), ensure_ascii=False) + '\n')
        except Exception as e:
            logger.warning("Failed to write log entry: %s", e)
    
    def add_log(
        self,
        operation_type: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        agent_id: Optional[str] = None,
        task_id: Optional[str] = None
    ) -> LogEntry:
        """
        Add a log entry
        
        Args:
            operation_type: Type of operation ('read', 'write', 'create', 'delete', etc.)
            resource_type: Type of resource ('file', 'memory', 'log')
            resource_id: ID of the resource (optional)
            details: Additional details dictionary (optional)
            agent_id: Agent ID who performed the operation (optional)
            task_id: Task ID associated with the operation (optional)
        
        Returns:
            Created LogEntry instance
        """
        log_entry = LogEntry(
            id=f"log_{uuid.uuid4().hex[:12]}",
            timestamp=datetime.now(),
            operation_type=operation_type,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            agent_id=agent_id,
            task_id=task_id
        )
        
        # Add to in-memory cache
        self._logs.append(log_entry)
        
        # Append to file
        self._append_log_to_file(log_entry)
        
        return log_entry
    
    def get_logs(
        self,
        operation_type: Optional[str] = None,
        resource_type: Optional[str] = None,
        agent_id: Optional[str] = None,
        task_id: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[LogEntry]:
        """
        Get logs with optional filters
        
        Args:
            operation_type: Filter by operation type
            resource_type: Filter by resource type
            agent_id: Filter by agent ID
            task_id: Filter by task ID
            limit: Maximum number of results
        
        Returns:
            List of LogEntry instances
        """
        results = [
            log_entry
            for log_entry in self._logs
            if self._matches_filters(
                log_entry,
                operation_type=operation_type,
                resource_type=resource_type,
                agent_id=agent_id,
                task_id=task_id,
            )
        ]

        # Sort by timestamp (newest first)
        results = self._sort_newest_first(results)
        
        # Apply limit
        if limit:
            results = results[:limit]
        
        return results
    
    def search_logs(
        self,
        query: str,
        limit: int = 50
    ) -> List[LogEntry]:
        """
        Search logs by query string (searches in details)
        
        Args:
            query: Search query string
            limit: Maximum number of results
        
        Returns:
            List of matching LogEntry instances
        """
        query_lower = query.lower()
        results = []
        
        for log_entry in self._logs:
            # Search in details JSON
            details_str = json.dumps(log_entry.details, ensure_ascii=False).lower()
            if query_lower in details_str:
                results.append(log_entry)
        
        # Sort by timestamp (newest first)
        results = self._sort_newest_first(results)
        
        return results[:limit]
    
    def get_recent_logs(self, count: int = 10) -> List[LogEntry]:
        """
        Get most recent logs
        
        Args:
            count: Number of recent logs to retrieve
        
        Returns:
            List of recent LogEntry instances
        """
        return self.get_logs(limit=count)
    
    def get_log_count(self) -> int:
        """Get total number of log entries"""
        return len(self._logs)

    def get_strategy_insights(
        self,
        *,
        window_hours: Optional[int] = None,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """Return strategy-level aggregate insights for operational debugging.

        Insights focus on execution outcomes, failure hotspots, and cross-task
        activity patterns for quick triage.
        """
        logs = list(self._logs)
        since: Optional[datetime] = None
        if window_hours and window_hours > 0:
            since = datetime.now() - timedelta(hours=window_hours)
            logs = [entry for entry in logs if entry.timestamp >= since]

        operation_counts = self._top_counts([entry.operation_type for entry in logs], top_k)
        resource_counts = self._top_counts([entry.resource_type for entry in logs], top_k)
        event_counts = self._top_counts(
            [str(entry.details.get("event_type", "")) for entry in logs],
            top_k,
        )

        execution_logs = [entry for entry in logs if entry.resource_type == "execution"]
        execution_statuses = [
            str(entry.details.get("status", "")).upper()
            for entry in execution_logs
            if entry.details.get("status")
        ]
        completed = sum(1 for status in execution_statuses if status == "COMPLETED")
        failed = sum(1 for status in execution_statuses if status == "FAILED")
        fail_rate = (failed / len(execution_statuses)) if execution_statuses else 0.0

        failed_execution_logs = [
            entry
            for entry in execution_logs
            if str(entry.details.get("status", "")).upper() == "FAILED"
        ]
        failures_by_agent = self._top_counts(
            [entry.agent_id or "" for entry in failed_execution_logs],
            top_k,
        )
        failures_by_task = self._top_counts(
            [entry.task_id or "" for entry in failed_execution_logs],
            top_k,
        )

        task_activity = self._top_counts([entry.task_id or "" for entry in logs], top_k)

        return {
            "window_hours": window_hours,
            "since": since.isoformat() if since else None,
            "totals": {
                "log_count": len(logs),
                "execution_event_count": len(execution_statuses),
                "execution_completed": completed,
                "execution_failed": failed,
                "execution_fail_rate": round(fail_rate, 4),
            },
            "breakdown": {
                "by_operation_type": operation_counts,
                "by_resource_type": resource_counts,
                "by_event_type": event_counts,
            },
            "failure_hotspots": {
                "by_agent": failures_by_agent,
                "by_task": failures_by_task,
            },
            "cross_task_activity": task_activity,
        }
