# Memory Manager - Manages Global Memory (Markdown format)

import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import json


class MemoryManager:
    """
    Manages Global Memory - a Markdown-formatted long string
    
    Responsibilities:
    - Store and retrieve Global Memory
    - Validate memory length (with max length limit)
    - Provide read/write operations
    - Handle memory truncation when too long
    """
    
    # Maximum memory length (in characters)
    MAX_MEMORY_LENGTH = 100000  # 100KB of text
    
    def __init__(self, workspace_id: str, runtime_base_path: Path):
        """
        Initialize memory manager
        
        Args:
            workspace_id: ID of the workspace
            runtime_base_path: Base path to Runtime directory
        """
        self.workspace_id = workspace_id
        self.runtime_base_path = Path(runtime_base_path)
        self.workspace_runtime_path = self.runtime_base_path / workspace_id
        self.memory_file_path = self.workspace_runtime_path / "global_memory.md"
        
        # Ensure workspace directory exists
        self.workspace_runtime_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize memory if it doesn't exist
        if not self.memory_file_path.exists():
            self._write_memory("")
    
    def _read_memory(self) -> str:
        """Read memory from disk"""
        if not self.memory_file_path.exists():
            return ""
        
        try:
            with open(self.memory_file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Warning: Failed to read memory: {e}")
            return ""
    
    def _write_memory(self, content: str):
        """Write memory to disk"""
        try:
            with open(self.memory_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"Warning: Failed to write memory: {e}")
            raise
    
    def _validate_length(self, content: str) -> tuple:
        """
        Validate memory length and truncate if necessary
        
        Args:
            content: Memory content to validate
        
        Returns:
            Tuple of (validated_content, was_truncated)
        """
        if len(content) <= self.MAX_MEMORY_LENGTH:
            return content, False
        
        # Truncate content
        truncated = content[:self.MAX_MEMORY_LENGTH]
        
        # Try to truncate at a reasonable point (end of line or sentence)
        # Find last newline or period before limit
        last_newline = truncated.rfind('\n')
        last_period = truncated.rfind('.')
        
        cutoff = max(last_newline, last_period)
        if cutoff > self.MAX_MEMORY_LENGTH * 0.9:  # Only if reasonable cutoff point
            truncated = truncated[:cutoff + 1]
        
        # Add truncation notice
        truncated += f"\n\n---\n*[Memory truncated due to length limit. Original length: {len(content)} characters]*\n"
        
        return truncated, True
    
    def read_memory(self) -> str:
        """
        Read Global Memory
        
        Returns:
            Memory content as string
        """
        return self._read_memory()
    
    def write_memory(self, content: str, append: bool = False) -> Dict[str, Any]:
        """
        Write to Global Memory
        
        Args:
            content: Content to write
            append: If True, append to existing memory; otherwise replace
        
        Returns:
            Dictionary with operation result:
            - success: bool
            - was_truncated: bool
            - original_length: int
            - final_length: int
            - message: str
        """
        if append:
            existing = self._read_memory()
            if existing:
                content = existing + "\n\n" + content
            new_content, was_truncated = self._validate_length(content)
        else:
            new_content, was_truncated = self._validate_length(content)
        
        original_length = len(content)
        final_length = len(new_content)
        
        # Write to disk
        self._write_memory(new_content)
        
        result = {
            "success": True,
            "was_truncated": was_truncated,
            "original_length": original_length,
            "final_length": final_length,
            "message": "Memory written successfully" + (" (truncated)" if was_truncated else "")
        }
        
        return result
    
    def append_memory(self, content: str) -> Dict[str, Any]:
        """
        Append to Global Memory (convenience method)
        
        Args:
            content: Content to append
        
        Returns:
            Dictionary with operation result
        """
        return self.write_memory(content, append=True)
    
    def clear_memory(self):
        """Clear Global Memory"""
        self._write_memory("")
    
    def get_memory_length(self) -> int:
        """
        Get current memory length
        
        Returns:
            Number of characters in memory
        """
        return len(self._read_memory())
    
    def is_memory_full(self) -> bool:
        """
        Check if memory is at or near capacity
        
        Returns:
            True if memory length >= 90% of max length
        """
        current_length = self.get_memory_length()
        return current_length >= (self.MAX_MEMORY_LENGTH * 0.9)
    
    def get_memory_info(self) -> Dict[str, Any]:
        """
        Get memory information
        
        Returns:
            Dictionary with memory stats
        """
        content = self._read_memory()
        return {
            "length": len(content),
            "max_length": self.MAX_MEMORY_LENGTH,
            "usage_percent": (len(content) / self.MAX_MEMORY_LENGTH) * 100,
            "is_full": self.is_memory_full(),
            "file_path": str(self.memory_file_path)
        }
