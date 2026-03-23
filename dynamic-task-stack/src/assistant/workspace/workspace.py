# Workspace - Main workspace class that coordinates all managers

from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from .file_manager import FileManager
from .memory_manager import MemoryManager
from .log_manager import LogManager
from .asset_manager import AssetManager
from .models import FileMetadata, LogEntry
from ..response_serializers import file_search_item_to_dict, log_search_item_to_dict


class Workspace:
    """
    Workspace - Manages file system, short-term structured memory, and logs

    The workspace provides a unified interface for:
    - File management (images, videos, documents, etc.)
    - Short-term structured memory (STM JSON entries; long-term tier disabled)
    - Logs and records (JSON format)
    
    Each workspace has its own directory in Runtime/{workspace_id}/
    """
    
    def __init__(self, workspace_id: str, runtime_base_path: Path):
        """
        Initialize workspace
        
        Args:
            workspace_id: Unique workspace ID
            runtime_base_path: Base path to Runtime directory (project root)
        """
        self.id = workspace_id
        self.runtime_base_path = Path(runtime_base_path)
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        # Initialize managers
        self.file_manager = FileManager(workspace_id, runtime_base_path)
        self.memory_manager = MemoryManager(workspace_id, runtime_base_path)
        self.log_manager = LogManager(workspace_id, runtime_base_path)
        self.asset_manager = AssetManager(
            self.store_file,
            self._add_log,
            self.file_manager.read_binary_from_uri,
            self.list_files,
            self.delete_file,
            on_change=self._touch,
        )
        
        # Log workspace creation
        self.log_manager.add_log(
            operation_type='create',
            resource_type='workspace',
            resource_id=workspace_id,
            details={'workspace_id': workspace_id}
        )

    # ------------------------------------------------------------------
    # Internal boundary helpers
    # ------------------------------------------------------------------

    def _touch(self) -> None:
        self.updated_at = datetime.now()

    def _add_log(
        self,
        *,
        operation_type: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        task_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.log_manager.add_log(
            operation_type=operation_type,
            resource_type=resource_type,
            resource_id=resource_id,
            agent_id=agent_id,
            task_id=task_id,
            details=details or {},
        )

    # File Management Methods
    
    def store_file(
        self,
        file_content: bytes,
        filename: str,
        description: str,
        created_by: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> FileMetadata:
        """
        Store a file in the workspace
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            description: Description of the file
            created_by: Agent ID or user ID
            tags: Optional tags
            metadata: Optional additional metadata
        
        Returns:
            FileMetadata instance
        """
        file_metadata = self.file_manager.store_file(
            file_content=file_content,
            filename=filename,
            description=description,
            created_by=created_by,
            tags=tags,
            metadata=metadata
        )
        
        # Log file creation
        self._add_log(
            operation_type='create',
            resource_type='file',
            resource_id=file_metadata.id,
            agent_id=created_by,
            details={
                'filename': filename,
                'description': description,
                'file_type': file_metadata.file_type,
                'size_bytes': file_metadata.size_bytes
            }
        )
        
        self._touch()
        return file_metadata
    
    def get_file(self, file_id: str) -> Optional[FileMetadata]:
        """Get file metadata by ID"""
        return self.file_manager.get_file(file_id)
    
    def get_file_content(self, file_id: str) -> Optional[bytes]:
        """Get file content by ID"""
        content = self.file_manager.get_file_content(file_id)
        if content:
            self._add_log(
                operation_type='read',
                resource_type='file',
                resource_id=file_id
            )
        return content
    
    def list_files(
        self,
        file_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        created_by: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[FileMetadata]:
        """List files with optional filters"""
        return self.file_manager.list_files(
            file_type=file_type,
            tags=tags,
            created_by=created_by,
            limit=limit
        )
    
    def search_files(
        self,
        query: str,
        file_type: Optional[str] = None,
        limit: int = 10
    ) -> List[FileMetadata]:
        """Search files by description or filename"""
        return self.file_manager.search_files(query, file_type, limit)
    
    def delete_file(self, file_id: str) -> bool:
        """Delete a file from the workspace"""
        file_meta = self.file_manager.get_file(file_id)
        if file_meta:
            success = self.file_manager.delete_file(file_id)
            if success:
                self._add_log(
                    operation_type='delete',
                    resource_type='file',
                    resource_id=file_id,
                    details={'filename': file_meta.filename}
                )
                self._touch()
            return success
        return False
    
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
        """Add one structured memory entry."""
        entry = self.memory_manager.add_memory_entry(
            content=content,
            tier=tier,
            kind=kind,
            task_id=task_id,
            agent_id=agent_id,
            source_asset_refs=source_asset_refs,
            priority=priority,
            confidence=confidence,
            ttl_runs=ttl_runs,
            metadata=metadata,
        )
        self._add_log(
            operation_type="write",
            resource_type="memory",
            resource_id=entry.get("id"),
            agent_id=agent_id,
            task_id=task_id,
            details={
                "event_type": "memory_entry_added",
                "tier": entry.get("tier"),
                "kind": entry.get("kind"),
                "priority": entry.get("priority"),
            },
        )
        self._touch()
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
        """List structured memory entries with optional filters."""
        return self.memory_manager.list_memory_entries(
            tier=tier,
            task_id=task_id,
            agent_id=agent_id,
            kinds=kinds,
            limit=limit,
        )

    def get_memory_brief(
        self,
        *,
        task_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        short_term_limit: int = 6,
    ) -> Dict[str, Any]:
        """Build concise memory brief for planning/execution."""
        return self.memory_manager.get_memory_brief(
            task_id=task_id,
            agent_id=agent_id,
            short_term_limit=short_term_limit,
        )

    def get_memory_info(self) -> Dict[str, Any]:
        """Get structured memory information"""
        return self.memory_manager.get_memory_info()
    
    # Log Methods
    
    def get_logs(
        self,
        operation_type: Optional[str] = None,
        resource_type: Optional[str] = None,
        agent_id: Optional[str] = None,
        task_id: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[LogEntry]:
        """Get logs with optional filters"""
        return self.log_manager.get_logs(
            operation_type=operation_type,
            resource_type=resource_type,
            agent_id=agent_id,
            task_id=task_id,
            limit=limit
        )
    
    def get_recent_logs(self, count: int = 10) -> List[LogEntry]:
        """Get most recent logs"""
        return self.log_manager.get_recent_logs(count)

    def get_log_insights(
        self,
        *,
        window_hours: Optional[int] = None,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """Get strategy-level log insights for triage and trend checks."""
        return self.log_manager.get_strategy_insights(
            window_hours=window_hours,
            top_k=top_k,
        )

    def log_execution_started(self, execution: Any) -> None:
        """Write execution started event for assistant orchestration."""
        self._add_log(
            operation_type="write",
            resource_type="execution",
            resource_id=execution.id,
            agent_id=execution.agent_id,
            task_id=execution.task_id,
            details={
                "event_type": "execution_started",
                "status": str(getattr(execution.status, "value", execution.status)),
            },
        )

    def log_execution_result(self, execution: Any) -> None:
        """Write terminal execution event (completed/failed)."""
        status = str(getattr(execution.status, "value", execution.status))
        event_type = "execution_completed" if status == "COMPLETED" else "execution_failed"
        retry_attempts = None
        eval_summary = None
        results = getattr(execution, "results", None)
        if isinstance(results, dict):
            debug = results.get("_execution_debug", {})
            if isinstance(debug, dict):
                attempts = debug.get("attempts")
                if isinstance(attempts, int):
                    retry_attempts = attempts
                summary = debug.get("eval_summary")
                if isinstance(summary, str) and summary:
                    eval_summary = summary
        self._add_log(
            operation_type="write",
            resource_type="execution",
            resource_id=execution.id,
            agent_id=execution.agent_id,
            task_id=execution.task_id,
            details={
                "event_type": event_type,
                "status": status,
                "error": getattr(execution, "error", None),
                "has_results": getattr(execution, "results", None) is not None,
                "retry_attempts": retry_attempts,
                "eval_summary": eval_summary,
            },
        )

    # Asset Methods

    def is_asset_index_entry(self, value: Any) -> bool:
        """Check whether value is an asset index entry."""
        return self.asset_manager.is_asset_index_entry(value)

    def hydrate_indexed_assets(self, assets: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve lightweight asset indexes to full JSON payloads."""
        return self.asset_manager.hydrate_indexed_assets(assets)

    def collect_materialized_files(self, media_assets: list[Any]) -> Dict[str, Any]:
        """Collect generated media files from temporary uris."""
        return self.asset_manager.collect_materialized_files(media_assets)

    def build_pipeline_asset_value(
        self,
        *,
        execution_results: Optional[Dict[str, Any]],
        descriptor_asset_key: str,
        execution_id: str,
    ) -> Dict[str, Any]:
        """Build one entry for pipeline shared assets from an execution record."""
        return self.asset_manager.build_pipeline_asset_value(
            execution_results=execution_results,
            descriptor_asset_key=descriptor_asset_key,
            execution_id=execution_id,
        )

    def persist_execution_assets(
        self,
        execution: Any,
        *,
        overwrite_existing: bool = False,
    ) -> Dict[str, str]:
        """Persist file/media assets for an execution."""
        return self.asset_manager.persist_execution_assets(
            execution,
            overwrite_existing=overwrite_existing,
        )

    def persist_execution_json_snapshot(
        self,
        execution: Any,
        *,
        asset_key: str,
        overwrite_existing: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """Persist JSON snapshot and return lightweight index for this execution."""
        return self.asset_manager.persist_execution_json_snapshot(
            execution,
            asset_key=asset_key,
            overwrite_existing=overwrite_existing,
        )
    
    # Comprehensive Search Methods
    
    def search_all(
        self,
        query: str,
        search_files: bool = True,
        search_memory: bool = True,
        search_logs: bool = True,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Comprehensive search across workspace
        
        Args:
            query: Search query string
            search_files: Whether to search files
            search_memory: Whether to search memory
            search_logs: Whether to search logs
            limit: Maximum results per category
        
        Returns:
            Dictionary with search results
        """
        results = {}
        
        if search_files:
            results['files'] = [file_search_item_to_dict(f) for f in self.search_files(query, limit=limit)]
        
        if search_memory:
            results['memory'] = self.memory_manager.search_memory_entries(query, limit=limit)
        
        if search_logs:
            results['logs'] = [
                log_search_item_to_dict(log)
                for log in self.log_manager.search_logs(query, limit=limit)
            ]
        
        return results
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get workspace summary
        
        Returns:
            Dictionary with workspace statistics
        """
        return {
            'workspace_id': self.id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'file_count': self.file_manager.get_file_count(),
            'memory_info': self.memory_manager.get_memory_info(),
            'log_count': self.log_manager.get_log_count(),
            'runtime_path': str(self.file_manager.workspace_runtime_path)
        }
