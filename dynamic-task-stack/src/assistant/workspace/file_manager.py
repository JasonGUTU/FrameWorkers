# File Manager - Manages all file resources in the workspace

import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import json

from .models import FileMetadata


class FileManager:
    """
    Manages all file resources in the workspace
    
    Responsibilities:
    - Store files in Runtime/{workspace_id}/ directory
    - Assign unique IDs and numbers to files
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
        
        # File counter for numbering
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
                print(f"Warning: Failed to load file metadata: {e}")

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
    def _metadata_matches(
        metadata: FileMetadata,
        *,
        file_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        created_by: Optional[str] = None,
    ) -> bool:
        if file_type and metadata.file_type != file_type:
            return False
        if tags and not all(tag in metadata.tags for tag in tags):
            return False
        if created_by and metadata.created_by != created_by:
            return False
        return True

    @staticmethod
    def _sort_newest_first(files: List[FileMetadata]) -> List[FileMetadata]:
        return sorted(files, key=lambda x: x.created_at, reverse=True)

    def _next_file_identity(self, filename: str) -> Dict[str, str]:
        self._file_counter += 1
        extension = self._get_file_extension(filename)
        file_id = f"file_{self._file_counter:06d}_{uuid.uuid4().hex[:8]}"
        numbered_filename = f"file_{self._file_counter:06d}{extension}"
        return {
            "file_id": file_id,
            "extension": extension,
            "numbered_filename": numbered_filename,
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
            print(f"Warning: Failed to save file metadata: {e}")
    
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
            created_by: Agent ID or user ID who created the file
            tags: Optional list of tags
            metadata: Optional additional metadata
        
        Returns:
            FileMetadata instance
        """
        identity = self._next_file_identity(filename)
        file_id = identity["file_id"]
        extension = identity["extension"]
        file_path = self.workspace_runtime_path / identity["numbered_filename"]
        
        # Write file to disk
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Get file size
        size_bytes = len(file_content)
        
        # Create metadata
        file_metadata = self._build_file_metadata(
            file_id=file_id,
            filename=filename,
            description=description,
            extension=extension,
            file_path=file_path,
            size_bytes=size_bytes,
            created_by=created_by,
            tags=tags,
            metadata=metadata,
        )
        
        # Store metadata
        self._file_metadata[file_id] = file_metadata
        self._save_metadata()
        
        return file_metadata
    
    def store_file_from_path(
        self,
        source_path: str,
        description: str,
        created_by: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> FileMetadata:
        """
        Store a file from an existing file path
        
        Args:
            source_path: Path to the source file
            description: Description of the file
            created_by: Agent ID or user ID who created the file
            tags: Optional list of tags
            metadata: Optional additional metadata
        
        Returns:
            FileMetadata instance
        """
        source = Path(source_path)
        if not source.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")
        
        # Read file content
        with open(source, 'rb') as f:
            file_content = f.read()
        
        # Store using store_file
        return self.store_file(
            file_content=file_content,
            filename=source.name,
            description=description,
            created_by=created_by,
            tags=tags,
            metadata=metadata
        )
    
    def get_file(self, file_id: str) -> Optional[FileMetadata]:
        """
        Get file metadata by ID
        
        Args:
            file_id: File ID
        
        Returns:
            FileMetadata or None if not found
        """
        return self._file_metadata.get(file_id)
    
    def get_file_content(self, file_id: str) -> Optional[bytes]:
        """
        Get file content by ID
        
        Args:
            file_id: File ID
        
        Returns:
            File content as bytes or None if not found
        """
        metadata = self.get_file(file_id)
        if metadata is None:
            return None
        
        file_path = Path(metadata.file_path)
        if not file_path.exists():
            return None
        
        with open(file_path, 'rb') as f:
            return f.read()
    
    def list_files(
        self,
        file_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        created_by: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[FileMetadata]:
        """
        List files with optional filters
        
        Args:
            file_type: Filter by file type ('image', 'video', 'text', 'other')
            tags: Filter by tags (file must have all specified tags)
            created_by: Filter by creator
            limit: Maximum number of results
        
        Returns:
            List of FileMetadata instances
        """
        results = [
            metadata
            for metadata in self._file_metadata.values()
            if self._metadata_matches(
                metadata,
                file_type=file_type,
                tags=tags,
                created_by=created_by,
            )
        ]

        # Sort by creation time (newest first)
        results = self._sort_newest_first(results)
        
        # Apply limit
        if limit:
            results = results[:limit]
        
        return results
    
    def search_files(
        self,
        query: str,
        file_type: Optional[str] = None,
        limit: int = 10
    ) -> List[FileMetadata]:
        """
        Search files by description or filename
        
        Args:
            query: Search query string
            file_type: Optional file type filter
            limit: Maximum number of results
        
        Returns:
            List of matching FileMetadata instances
        """
        query_lower = query.lower()
        results = []
        
        for metadata in self._file_metadata.values():
            # Apply file type filter
            if file_type and metadata.file_type != file_type:
                continue
            
            # Search in description and filename
            if (query_lower in metadata.description.lower() or 
                query_lower in metadata.filename.lower()):
                results.append(metadata)
        
        # Sort by creation time (newest first)
        results = self._sort_newest_first(results)
        
        return results[:limit]
    
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
                print(f"Warning: Failed to delete file {file_path}: {e}")
        
        # Remove from metadata
        del self._file_metadata[file_id]
        self._save_metadata()
        
        return True
    
    def update_file_metadata(
        self,
        file_id: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update file metadata
        
        Args:
            file_id: File ID
            description: New description (optional)
            tags: New tags (optional)
            metadata: Additional metadata to merge (optional)
        
        Returns:
            True if updated successfully, False otherwise
        """
        file_meta = self._file_metadata.get(file_id)
        if file_meta is None:
            return False
        
        if description is not None:
            file_meta.description = description
        
        if tags is not None:
            file_meta.tags = tags
        
        if metadata is not None:
            file_meta.metadata.update(metadata)
        
        self._save_metadata()
        return True
    
    def get_all_files(self) -> List[FileMetadata]:
        """
        Get all files in the workspace
        
        Returns:
            List of all FileMetadata instances
        """
        return list(self._file_metadata.values())
    
    def get_file_count(self) -> int:
        """Get total number of files"""
        return len(self._file_metadata)
