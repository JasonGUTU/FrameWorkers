# File Manager - Manages all file resources in the workspace

from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import json
import logging
import re

from .models import FileMetadata

logger = logging.getLogger(__name__)


class FileManager:
    """
    Manages all file resources in the workspace
    
    Responsibilities:
    - Store files in Runtime/{workspace_id}/ directory
    - Assign unique IDs to files
    - Track file metadata (description, time, path)
    - Provide file query and retrieval interfaces
    """
    
    def __init__(self, workspace_id: str, runtime_base_path: Path):
        """
        Initialize file manager
        
        Args:
            workspace_id: ID of the workspace
            runtime_base_path: Base path to Runtime directory (project root)
        """
        self.workspace_id = workspace_id
        self.runtime_base_path = Path(runtime_base_path)
        self.workspace_runtime_path = self.runtime_base_path / workspace_id
        
        # File metadata storage: file_id -> FileMetadata
        self._file_metadata: Dict[str, FileMetadata] = {}
        
        # Monotonic counter for file_id generation
        self._file_counter = 0
        
        # Ensure workspace directory exists
        self.workspace_runtime_path.mkdir(parents=True, exist_ok=True)
        
        # Load existing file metadata if any
        self._load_metadata()
    
    def _load_metadata(self):
        """Load file metadata from disk"""
        metadata_file = self.workspace_runtime_path / ".file_metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._file_counter = data.get('counter', 0)
                    for file_id, meta_dict in data.get('files', {}).items():
                        # Convert datetime strings back to datetime objects
                        meta_dict['created_at'] = datetime.fromisoformat(meta_dict['created_at'])
                        self._file_metadata[file_id] = FileMetadata(**meta_dict)
            except Exception as e:
                logger.warning("Failed to load file metadata: %s", e)

    # ------------------------------------------------------------------
    # Internal boundary helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _metadata_to_json_dict(metadata: FileMetadata) -> Dict[str, Any]:
        return {
            'id': metadata.id,
            'filename': metadata.filename,
            'description': metadata.description,
            'file_type': metadata.file_type,
            'file_extension': metadata.file_extension,
            'file_path': metadata.file_path,
            'size_bytes': metadata.size_bytes,
            'created_at': metadata.created_at.isoformat(),
            'created_by': metadata.created_by,
            'tags': metadata.tags,
            'metadata': metadata.metadata
        }

    @staticmethod
    def _sort_newest_first(files: List[FileMetadata]) -> List[FileMetadata]:
        return sorted(files, key=lambda x: x.created_at, reverse=True)

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

    def _next_file_identity(self) -> Dict[str, str]:
        self._file_counter += 1
        file_id = f"file_{self._file_counter:06d}_{uuid.uuid4().hex[:8]}"
        return {
            "file_id": file_id,
        }

    def _build_file_metadata(
        self,
        *,
        file_id: str,
        filename: str,
        description: str,
        extension: str,
        file_path: Path,
        size_bytes: int,
        created_by: Optional[str],
        tags: Optional[List[str]],
        metadata: Optional[Dict[str, Any]],
    ) -> FileMetadata:
        return FileMetadata(
            id=file_id,
            filename=filename,
            description=description,
            file_type=self._determine_file_type(extension),
            file_extension=extension,
            file_path=str(file_path),
            size_bytes=size_bytes,
            created_at=datetime.now(),
            created_by=created_by,
            tags=tags or [],
            metadata=metadata or {},
        )
    
    def _save_metadata(self):
        """Save file metadata to disk"""
        metadata_file = self.workspace_runtime_path / ".file_metadata.json"
        try:
            data = {
                'counter': self._file_counter,
                'files': {}
            }
            for file_id, metadata in self._file_metadata.items():
                data['files'][file_id] = self._metadata_to_json_dict(metadata)
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning("Failed to save file metadata: %s", e)
    
    def _get_file_extension(self, filename: str) -> str:
        """Extract file extension from filename"""
        return Path(filename).suffix.lower()
    
    def _determine_file_type(self, extension: str) -> str:
        """Determine file type from extension"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'}
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'}
        text_extensions = {'.txt', '.md', '.json', '.xml', '.csv'}
        
        if extension in image_extensions:
            return 'image'
        elif extension in video_extensions:
            return 'video'
        elif extension in text_extensions:
            return 'text'
        else:
            return 'other'
    
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
        """
        Write bytes to ``workspace_runtime_path / relative_path`` (task-scoped layout).

        ``relative_path`` uses ``/`` separators; ``..`` and absolute paths are rejected.
        """
        rel = self._sanitize_relative_workspace_path(relative_path)
        dest = (self.workspace_runtime_path / rel).resolve()
        base = self.workspace_runtime_path.resolve()
        if not str(dest).startswith(str(base)):
            raise ValueError("path escapes workspace")
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "wb") as fh:
            fh.write(file_content)

        identity = self._next_file_identity()
        file_id = identity["file_id"]
        extension = self._get_file_extension(filename)
        size_bytes = len(file_content)
        file_metadata = self._build_file_metadata(
            file_id=file_id,
            filename=filename,
            description=description,
            extension=extension,
            file_path=dest,
            size_bytes=size_bytes,
            created_by=created_by,
            tags=tags,
            metadata=metadata,
        )
        self._file_metadata[file_id] = file_metadata
        self._save_metadata()
        return file_metadata
    
    def get_file(self, file_id: str) -> Optional[FileMetadata]:
        """
        Get file metadata by ID
        
        Args:
            file_id: File ID
        
        Returns:
            FileMetadata or None if not found
        """
        return self._file_metadata.get(file_id)
    
    def read_binary_from_uri(self, uri: str) -> Optional[bytes]:
        """Read binary payload from a filesystem uri/path."""
        if not uri:
            return None

        file_path = Path(uri)
        if not file_path.exists() or not file_path.is_file():
            return None

        try:
            return file_path.read_bytes()
        except Exception:
            return None
    
    def list_files(self) -> List[FileMetadata]:
        """
        List files in workspace.
        
        Returns list of FileMetadata instances.
        """
        results = list(self._file_metadata.values())

        # Sort by creation time (newest first)
        results = self._sort_newest_first(results)
        return results
    
    def delete_file(self, file_id: str) -> bool:
        """
        Delete a file from the workspace
        
        Args:
            file_id: File ID to delete
        
        Returns:
            True if deleted successfully, False otherwise
        """
        metadata = self._file_metadata.get(file_id)
        if metadata is None:
            return False
        
        # Delete file from disk
        file_path = Path(metadata.file_path)
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception as e:
                logger.warning("Failed to delete file %s: %s", file_path, e)
        
        # Remove from metadata
        del self._file_metadata[file_id]
        self._save_metadata()
        
        return True
    
