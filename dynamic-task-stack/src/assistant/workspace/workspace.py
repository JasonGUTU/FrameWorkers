# Workspace - Main workspace class that coordinates all managers

from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from .file_manager import FileManager
from .memory_manager import MemoryManager
from .log_manager import LogManager
from .asset_manager import AssetManager
from .models import FileMetadata, LogEntry


class Workspace:
    """
    Workspace - Manages file system, global memory, and logs

    The workspace provides a unified interface for:
    - File management (images, videos, documents, etc.)
    - Global memory (``global_memory.md`` under workspace runtime root)
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
            self.store_file_at_relative_path,
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

    def store_file_at_relative_path(
        self,
        relative_path: str,
        file_content: bytes,
        filename: str,
        description: str,
        created_by: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> FileMetadata:
        """Write under ``Runtime/{workspace_id}/<relative_path>`` (task-scoped tree)."""
        file_metadata = self.file_manager.store_file_at_relative_path(
            relative_path,
            file_content=file_content,
            filename=filename,
            description=description,
            created_by=created_by,
            tags=tags,
            metadata=metadata,
        )
        self._add_log(
            operation_type="create",
            resource_type="file",
            resource_id=file_metadata.id,
            agent_id=created_by,
            details={
                "filename": filename,
                "description": description,
                "file_type": file_metadata.file_type,
                "size_bytes": file_metadata.size_bytes,
            },
        )
        self.memory_manager.refresh_file_tree()
        self._touch()
        return file_metadata
    
    def get_file(self, file_id: str) -> Optional[FileMetadata]:
        """Get file metadata by ID"""
        return self.file_manager.get_file(file_id)
    
    def list_files(self) -> List[FileMetadata]:
        """List files in workspace."""
        return self.file_manager.list_files()
    
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
                self.memory_manager.refresh_file_tree()
                self._touch()
            return success
        return False
    
    def add_memory_entry(
        self,
        *,
        content: str,
        task_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        execution_result: Optional[Any] = None,
        artifact_locations: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Add one structured memory entry (``content``, ``agent_id``, ``created_at``, ``execution_result``, optional ``artifact_locations``)."""
        entry = self.memory_manager.add_memory_entry(
            content=content,
            task_id=task_id,
            agent_id=agent_id,
            execution_result=execution_result,
            artifact_locations=artifact_locations,
        )
        self._add_log(
            operation_type="write",
            resource_type="memory",
            resource_id=entry.get("created_at"),
            agent_id=agent_id,
            task_id=task_id,
            details={"event_type": "memory_entry_added"},
        )
        self._touch()
        return entry

    def list_memory_entries(
        self,
        *,
        task_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """List global memory entries with optional filters (newest tail, default 20)."""
        return self.memory_manager.list_memory_entries(
            task_id=task_id,
            agent_id=agent_id,
            limit=limit,
        )

    def get_memory_brief(
        self,
        *,
        task_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """``{"global_memory": [...]}`` — brief rows: ``task_id``, ``agent_id``, ``created_at``, ``execution_result`` only."""
        return self.memory_manager.get_memory_brief(
            task_id=task_id,
            agent_id=agent_id,
            limit=limit,
        )

    def get_workspace_root_file_tree_text(self) -> str:
        """Full file tree under workspace runtime root (includes ``artifacts/``); for persist-path LLM."""
        return self.memory_manager.workspace_root_file_tree_text()

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

    def hydrate_indexed_assets(self, assets: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve lightweight asset indexes to full JSON payloads."""
        return self.asset_manager.hydrate_indexed_assets(assets)

    def collect_materialized_files(self, media_assets: list[Any]) -> Dict[str, Any]:
        """Collect generated media files from temporary uris."""
        return self.asset_manager.collect_materialized_files(media_assets)

    def persist_execution_from_plan(
        self,
        execution: Any,
        assignments: List[Dict[str, Any]],
        *,
        overwrite_existing: bool = False,
    ) -> tuple[Dict[str, str], Optional[Dict[str, Any]], List[Dict[str, str]]]:
        """Persist binaries, media, manifest, and JSON snapshot via a single plan."""
        return self.asset_manager.persist_execution_from_plan(
            execution,
            assignments,
            overwrite_existing=overwrite_existing,
        )

