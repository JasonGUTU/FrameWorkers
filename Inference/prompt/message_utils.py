"""
Message Utilities - Message compression and manipulation

Provides utilities for compressing and manipulating chat messages.
"""

from typing import List, Dict, Any, Optional, Union
from ..core.llm_client import Message


class MessageUtils:
    """Utilities for message compression and manipulation"""
    
    @staticmethod
    def compress_messages(
        messages: List[Union[Message, Dict[str, Any]]],
        max_tokens: Optional[int] = None,
        strategy: str = "truncate_oldest"
    ) -> List[Dict[str, Any]]:
        """
        Compress multiple messages into fewer messages
        
        Args:
            messages: List of messages to compress
            max_tokens: Maximum tokens to keep (approximate)
            strategy: Compression strategy:
                - "truncate_oldest": Remove oldest messages first
                - "merge_consecutive": Merge consecutive messages from same role
                - "summarize": Summarize old messages (requires LLM call)
                
        Returns:
            Compressed list of messages
        """
        if not messages:
            return []
        
        # Convert to dict format
        formatted = MessageUtils._to_dict_list(messages)
        
        if strategy == "truncate_oldest":
            return MessageUtils._truncate_oldest(formatted, max_tokens)
        elif strategy == "merge_consecutive":
            return MessageUtils._merge_consecutive(formatted)
        elif strategy == "summarize":
            # This would require LLM call, so we'll use merge as fallback
            return MessageUtils._merge_consecutive(formatted)
        else:
            raise ValueError(f"Unknown compression strategy: {strategy}")
    
    @staticmethod
    def merge_consecutive_same_role(
        messages: List[Union[Message, Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        Merge consecutive messages from the same role
        
        Args:
            messages: List of messages
            
        Returns:
            Merged messages
        """
        formatted = MessageUtils._to_dict_list(messages)
        return MessageUtils._merge_consecutive(formatted)
    
    @staticmethod
    def truncate_messages(
        messages: List[Union[Message, Dict[str, Any]]],
        max_tokens: int,
        keep_system: bool = True,
        keep_recent: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Truncate messages to fit within token limit
        
        Args:
            messages: List of messages
            max_tokens: Maximum tokens to keep
            keep_system: Whether to always keep system messages
            keep_recent: Number of recent messages to always keep
            
        Returns:
            Truncated messages
        """
        formatted = MessageUtils._to_dict_list(messages)
        return MessageUtils._truncate_oldest(formatted, max_tokens, keep_system, keep_recent)
    
    @staticmethod
    def extract_system_messages(
        messages: List[Union[Message, Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        Extract all system messages
        
        Args:
            messages: List of messages
            
        Returns:
            List of system messages
        """
        formatted = MessageUtils._to_dict_list(messages)
        return [msg for msg in formatted if msg.get("role") == "system"]
    
    @staticmethod
    def remove_system_messages(
        messages: List[Union[Message, Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        Remove all system messages
        
        Args:
            messages: List of messages
            
        Returns:
            Messages without system messages
        """
        formatted = MessageUtils._to_dict_list(messages)
        return [msg for msg in formatted if msg.get("role") != "system"]
    
    @staticmethod
    def get_message_count_by_role(
        messages: List[Union[Message, Dict[str, Any]]]
    ) -> Dict[str, int]:
        """
        Count messages by role
        
        Args:
            messages: List of messages
            
        Returns:
            Dictionary mapping role to count
        """
        formatted = MessageUtils._to_dict_list(messages)
        counts = {}
        for msg in formatted:
            role = msg.get("role", "unknown")
            counts[role] = counts.get(role, 0) + 1
        return counts
    
    @staticmethod
    def estimate_tokens(
        messages: List[Union[Message, Dict[str, Any]]],
        approximate: bool = True
    ) -> int:
        """
        Estimate token count for messages
        
        Args:
            messages: List of messages
            approximate: Whether to use approximation (default: True)
            
        Returns:
            Estimated token count
        """
        formatted = MessageUtils._to_dict_list(messages)
        total_tokens = 0
        
        for msg in formatted:
            content = msg.get("content", "")
            
            if isinstance(content, str):
                # Rough approximation: 1 token ≈ 4 characters
                tokens = len(content) // 4 if approximate else len(content.split())
            elif isinstance(content, list):
                # Multimodal content
                text_parts = []
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text_parts.append(item.get("text", ""))
                text = " ".join(text_parts)
                tokens = len(text) // 4 if approximate else len(text.split())
                # Add tokens for images (rough approximation: 170 per image)
                image_count = sum(1 for item in content if isinstance(item, dict) and item.get("type") == "image_url")
                tokens += image_count * 170
            else:
                tokens = 0
            
            total_tokens += tokens
        
        # Add overhead for message structure (roughly 4 tokens per message)
        total_tokens += len(formatted) * 4
        
        return total_tokens
    
    @staticmethod
    def _to_dict_list(messages: List[Union[Message, Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Convert Message objects to dicts"""
        result = []
        for msg in messages:
            if isinstance(msg, Message):
                result.append({
                    "role": msg.role,
                    "content": msg.content,
                    **({k: v for k, v in {
                        "name": msg.name,
                        "tool_calls": msg.tool_calls,
                        "tool_call_id": msg.tool_call_id,
                    }.items() if v is not None})
                })
            else:
                result.append(msg)
        return result
    
    @staticmethod
    def _merge_consecutive(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge consecutive messages from the same role"""
        if not messages:
            return []
        
        merged = []
        current_role = None
        current_content_parts = []
        
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")
            
            if role == current_role:
                # Same role, merge content
                if isinstance(content, str):
                    current_content_parts.append(content)
                elif isinstance(content, list):
                    # For multimodal, we'll keep them separate
                    # Just append the text parts
                    text_parts = [item.get("text", "") for item in content if isinstance(item, dict) and item.get("type") == "text"]
                    current_content_parts.extend(text_parts)
            else:
                # Different role, save previous and start new
                if current_role is not None:
                    merged.append({
                        "role": current_role,
                        "content": "\n\n".join(current_content_parts)
                    })
                current_role = role
                if isinstance(content, str):
                    current_content_parts = [content]
                elif isinstance(content, list):
                    text_parts = [item.get("text", "") for item in content if isinstance(item, dict) and item.get("type") == "text"]
                    current_content_parts = text_parts
                else:
                    current_content_parts = []
        
        # Add last message
        if current_role is not None:
            merged.append({
                "role": current_role,
                "content": "\n\n".join(current_content_parts)
            })
        
        return merged
    
    @staticmethod
    def _truncate_oldest(
        messages: List[Dict[str, Any]],
        max_tokens: Optional[int] = None,
        keep_system: bool = True,
        keep_recent: int = 2
    ) -> List[Dict[str, Any]]:
        """Truncate oldest messages"""
        if max_tokens is None:
            return messages
        
        # Separate system and non-system messages
        system_messages = []
        other_messages = []
        
        for msg in messages:
            if msg.get("role") == "system":
                system_messages.append(msg)
            else:
                other_messages.append(msg)
        
        # Always keep system messages if requested
        result = system_messages.copy() if keep_system else []
        
        # Keep recent messages
        recent_messages = other_messages[-keep_recent:] if len(other_messages) > keep_recent else other_messages
        
        # Calculate tokens used
        tokens_used = MessageUtils.estimate_tokens(result + recent_messages)
        
        # Add older messages if we have token budget
        remaining_tokens = max_tokens - tokens_used
        older_messages = other_messages[:-keep_recent] if len(other_messages) > keep_recent else []
        
        # Add older messages until we hit token limit
        for msg in reversed(older_messages):
            msg_tokens = MessageUtils.estimate_tokens([msg])
            if tokens_used + msg_tokens <= max_tokens:
                result.insert(len(system_messages) if keep_system else 0, msg)
                tokens_used += msg_tokens
            else:
                break
        
        # Add recent messages
        result.extend(recent_messages)
        
        return result
