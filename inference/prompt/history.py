"""
Message History - Persistence and formalization of message history

Provides utilities for storing and managing message history.
"""

from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import json
import pickle
from datetime import datetime
from ..core.llm_client import Message


class MessageHistory:
    """
    Manages message history with persistence
    
    Provides methods for storing, loading, and managing conversation history.
    """
    
    def __init__(self, storage_path: Optional[Union[str, Path]] = None, max_messages: Optional[int] = None):
        """
        Initialize Message History
        
        Args:
            storage_path: Path to storage directory/file
            max_messages: Maximum number of messages to keep in memory
        """
        self.storage_path = Path(storage_path) if storage_path else None
        self.max_messages = max_messages
        self.messages: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        
        # Load existing history if storage path exists
        if self.storage_path and self.storage_path.exists():
            self.load()
    
    def add_message(
        self,
        role: str,
        content: Union[str, List[Dict[str, Any]]],
        name: Optional[str] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        tool_call_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Add a message to history
        
        Args:
            role: Message role (system, user, assistant, etc.)
            content: Message content (string or multimodal list)
            name: Optional name for the message
            tool_calls: Optional tool calls
            tool_call_id: Optional tool call ID
            metadata: Optional metadata dictionary
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }
        
        if name:
            message["name"] = name
        if tool_calls:
            message["tool_calls"] = tool_calls
        if tool_call_id:
            message["tool_call_id"] = tool_call_id
        if metadata:
            message["metadata"] = metadata
        
        self.messages.append(message)
        self.metadata["updated_at"] = datetime.now().isoformat()
        
        # Enforce max_messages limit
        if self.max_messages and len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
        
        # Auto-save if storage path is set
        if self.storage_path:
            self.save()
    
    def add_messages(self, messages: List[Union[Message, Dict[str, Any]]]):
        """
        Add multiple messages to history
        
        Args:
            messages: List of Message objects or dictionaries
        """
        for msg in messages:
            if isinstance(msg, Message):
                self.add_message(
                    role=msg.role,
                    content=msg.content,
                    name=msg.name,
                    tool_calls=msg.tool_calls,
                    tool_call_id=msg.tool_call_id
                )
            elif isinstance(msg, dict):
                self.add_message(
                    role=msg.get("role", "user"),
                    content=msg.get("content", ""),
                    name=msg.get("name"),
                    tool_calls=msg.get("tool_calls"),
                    tool_call_id=msg.get("tool_call_id"),
                    metadata=msg.get("metadata")
                )
    
    def get_messages(
        self,
        role: Optional[str] = None,
        limit: Optional[int] = None,
        include_metadata: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get messages from history
        
        Args:
            role: Optional role filter
            limit: Optional limit on number of messages
            include_metadata: Whether to include message metadata
            
        Returns:
            List of message dictionaries
        """
        messages = self.messages
        
        # Filter by role
        if role:
            messages = [msg for msg in messages if msg.get("role") == role]
        
        # Apply limit
        if limit:
            messages = messages[-limit:]
        
        # Remove metadata if not requested
        if not include_metadata:
            messages = [
                {k: v for k, v in msg.items() if k != "metadata"}
                for msg in messages
            ]
        
        return messages
    
    def get_formatted_messages(self, for_api: bool = True) -> List[Dict[str, Any]]:
        """
        Get messages formatted for LLM API
        
        Args:
            for_api: Whether to format for API (removes timestamps/metadata)
            
        Returns:
            Formatted messages
        """
        if for_api:
            return [
                {
                    "role": msg["role"],
                    "content": msg["content"],
                    **({k: v for k, v in msg.items() if k in ["name", "tool_calls", "tool_call_id"] and v is not None})
                }
                for msg in self.messages
            ]
        else:
            return self.messages.copy()
    
    def clear(self):
        """Clear all messages"""
        self.messages = []
        self.metadata["updated_at"] = datetime.now().isoformat()
        if self.storage_path:
            self.save()
    
    def save(self, format: str = "json"):
        """
        Save history to file
        
        Args:
            format: File format ("json" or "pickle")
        """
        if not self.storage_path:
            return
        
        # Ensure directory exists
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "messages": self.messages,
            "metadata": self.metadata,
        }
        
        if format == "json":
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        elif format == "pickle":
            with open(self.storage_path, 'wb') as f:
                pickle.dump(data, f)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def load(self, format: str = "json"):
        """
        Load history from file
        
        Args:
            format: File format ("json" or "pickle")
        """
        if not self.storage_path or not self.storage_path.exists():
            return
        
        try:
            if format == "json":
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            elif format == "pickle":
                with open(self.storage_path, 'rb') as f:
                    data = pickle.load(f)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            self.messages = data.get("messages", [])
            self.metadata.update(data.get("metadata", {}))
        except Exception as e:
            print(f"Warning: Failed to load message history: {e}")
    
    def export(self, output_path: Union[str, Path], format: str = "json"):
        """
        Export history to a different file
        
        Args:
            output_path: Path to export file
            format: File format ("json" or "pickle")
        """
        output_path = Path(output_path)
        data = {
            "messages": self.messages,
            "metadata": self.metadata,
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == "json":
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        elif format == "pickle":
            with open(output_path, 'wb') as f:
                pickle.dump(data, f)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the message history
        
        Returns:
            Dictionary with statistics
        """
        role_counts = {}
        total_tokens = 0
        
        for msg in self.messages:
            role = msg.get("role", "unknown")
            role_counts[role] = role_counts.get(role, 0) + 1
            
            # Estimate tokens
            content = msg.get("content", "")
            if isinstance(content, str):
                total_tokens += len(content) // 4
            elif isinstance(content, list):
                text_parts = [item.get("text", "") for item in content if isinstance(item, dict) and item.get("type") == "text"]
                total_tokens += len(" ".join(text_parts)) // 4
        
        return {
            "total_messages": len(self.messages),
            "role_counts": role_counts,
            "estimated_tokens": total_tokens,
            "created_at": self.metadata.get("created_at"),
            "updated_at": self.metadata.get("updated_at"),
        }
