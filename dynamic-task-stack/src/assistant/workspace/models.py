# Workspace Data Models

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List


@dataclass
class FileMetadata:
    """Metadata for a file in the workspace"""
    id: str
    filename: str
    description: str
    file_type: str  # e.g., 'image', 'video', 'text', 'json'
    file_extension: str  # e.g., '.png', '.mp4', '.txt'
    file_path: str  # Path in Runtime folder
    size_bytes: int
    created_at: datetime
    created_by: Optional[str] = None  # Agent ID or user ID
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata


@dataclass
class LogEntry:
    """Log entry in JSON format"""
    id: str
    timestamp: datetime
    operation_type: str  # 'read', 'write', 'create', 'delete', etc.
    resource_type: str  # 'file', 'memory', 'log'
    resource_id: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    agent_id: Optional[str] = None
    task_id: Optional[str] = None
