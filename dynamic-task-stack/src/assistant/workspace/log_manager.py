# Log Manager - Manages logs and records

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from .models import LogEntry


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
    
    def _load_logs(self):
        """Load logs from disk"""
        if not self.log_file_path.exists():
            return
        
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        # Convert timestamp string to datetime
                        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
                        log_entry = LogEntry(**data)
                        self._logs.append(log_entry)
                    except Exception as e:
                        print(f"Warning: Failed to parse log entry: {e}")
        except Exception as e:
            print(f"Warning: Failed to load logs: {e}")
    
    def _append_log_to_file(self, log_entry: LogEntry):
        """Append a log entry to the log file"""
        try:
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                # Convert datetime to ISO string for JSON
                log_dict = {
                    'id': log_entry.id,
                    'timestamp': log_entry.timestamp.isoformat(),
                    'operation_type': log_entry.operation_type,
                    'resource_type': log_entry.resource_type,
                    'resource_id': log_entry.resource_id,
                    'details': log_entry.details,
                    'agent_id': log_entry.agent_id,
                    'task_id': log_entry.task_id
                }
                f.write(json.dumps(log_dict, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"Warning: Failed to write log entry: {e}")
    
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
        results = []
        
        for log_entry in self._logs:
            # Apply filters
            if operation_type and log_entry.operation_type != operation_type:
                continue
            
            if resource_type and log_entry.resource_type != resource_type:
                continue
            
            if agent_id and log_entry.agent_id != agent_id:
                continue
            
            if task_id and log_entry.task_id != task_id:
                continue
            
            results.append(log_entry)
        
        # Sort by timestamp (newest first)
        results.sort(key=lambda x: x.timestamp, reverse=True)
        
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
        results.sort(key=lambda x: x.timestamp, reverse=True)
        
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
    
    def get_all_logs(self) -> List[LogEntry]:
        """
        Get all logs
        
        Returns:
            List of all LogEntry instances
        """
        return list(self._logs)
    
    def get_log_count(self) -> int:
        """Get total number of log entries"""
        return len(self._logs)
