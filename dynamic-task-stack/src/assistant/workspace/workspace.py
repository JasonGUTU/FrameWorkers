# Workspace - Main workspace class that coordinates all managers

from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from .file_manager import FileManager
from .memory_manager import MemoryManager
from .log_manager import LogManager
from .models import FileMetadata, LogEntry


class Workspace:
    """
    Workspace - Manages file system, global memory, and logs
    
    The workspace provides a unified interface for:
    - File management (images, videos, documents, etc.)
    - Global Memory (Markdown-formatted long string)
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
        
        # Log workspace creation
        self.log_manager.add_log(
            operation_type='create',
            resource_type='workspace',
            resource_id=workspace_id,
            details={'workspace_id': workspace_id}
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
        self.log_manager.add_log(
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
        
        self.updated_at = datetime.now()
        return file_metadata
    
    def get_file(self, file_id: str) -> Optional[FileMetadata]:
        """Get file metadata by ID"""
        return self.file_manager.get_file(file_id)
    
    def get_file_content(self, file_id: str) -> Optional[bytes]:
        """Get file content by ID"""
        content = self.file_manager.get_file_content(file_id)
        if content:
            self.log_manager.add_log(
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
                self.log_manager.add_log(
                    operation_type='delete',
                    resource_type='file',
                    resource_id=file_id,
                    details={'filename': file_meta.filename}
                )
                self.updated_at = datetime.now()
            return success
        return False
    
    # Global Memory Methods
    
    def read_memory(self) -> str:
        """Read Global Memory"""
        memory = self.memory_manager.read_memory()
        self.log_manager.add_log(
            operation_type='read',
            resource_type='memory'
        )
        return memory
    
    def write_memory(self, content: str, append: bool = False) -> Dict[str, Any]:
        """
        Write to Global Memory
        
        Args:
            content: Content to write
            append: If True, append to existing memory
        
        Returns:
            Operation result dictionary
        """
        result = self.memory_manager.write_memory(content, append=append)
        
        self.log_manager.add_log(
            operation_type='write',
            resource_type='memory',
            details={
                'was_truncated': result['was_truncated'],
                'original_length': result['original_length'],
                'final_length': result['final_length']
            }
        )
        
        self.updated_at = datetime.now()
        return result
    
    def append_memory(self, content: str) -> Dict[str, Any]:
        """Append to Global Memory"""
        return self.write_memory(content, append=True)
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Get Global Memory information"""
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
            results['files'] = [
                {
                    'id': f.id,
                    'filename': f.filename,
                    'description': f.description,
                    'file_type': f.file_type,
                    'created_at': f.created_at.isoformat(),
                    'file_path': f.file_path
                }
                for f in self.search_files(query, limit=limit)
            ]
        
        if search_memory:
            memory_content = self.read_memory()
            if query.lower() in memory_content.lower():
                results['memory'] = {
                    'found': True,
                    'length': len(memory_content),
                    'preview': memory_content[:500] + '...' if len(memory_content) > 500 else memory_content
                }
            else:
                results['memory'] = {'found': False}
        
        if search_logs:
            results['logs'] = [
                {
                    'id': log.id,
                    'timestamp': log.timestamp.isoformat(),
                    'operation_type': log.operation_type,
                    'resource_type': log.resource_type,
                    'resource_id': log.resource_id,
                    'details': log.details
                }
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
