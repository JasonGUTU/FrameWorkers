"""
Message Utilities - General text/image message processing tools.

Provides utilities for handling text-only and multimodal message content.
"""

from typing import List, Dict, Any, Optional, Union
from pathlib import Path
from .image_utils import ImageUtils


class InputUtils:
    """General utilities for text/image message preprocessing."""

    @staticmethod
    def create_multimodal_message(
        text: str,
        image_path: Optional[Union[str, Path]] = None,
        image_base64: Optional[str] = None,
        role: str = "user",
    ) -> Dict[str, Any]:
        """
        Create a single text/image message for LLM APIs.

        Args:
            text: Text content
            image_path: Path to image file (optional)
            image_base64: Base64 encoded image (optional)
            role: Message role (default: "user")

        Returns:
            Message dictionary compatible with OpenAI-style format
        """
        content = [{"type": "text", "text": text}]

        if image_path:
            image_url = ImageUtils.encode_image_to_base64(image_path)
            content.append({
                "type": "image_url",
                "image_url": {"url": image_url},
            })
        elif image_base64:
            if not image_base64.startswith("data:"):
                image_base64 = f"data:image/png;base64,{image_base64}"
            content.append({
                "type": "image_url",
                "image_url": {"url": image_base64},
            })

        return {"role": role, "content": content}

    @staticmethod
    def prepare_multimodal_content(
        text: str,
        images: Optional[List[Union[str, Path]]] = None,
        image_base64_list: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Prepare multimodal content for LLM API

        Args:
            text: Text content
            images: List of image file paths
            image_base64_list: List of base64 encoded images

        Returns:
            List of content items (text and images)
        """
        content = [{"type": "text", "text": text}]

        # Add images from paths
        if images:
            for image_path in images:
                image_url = ImageUtils.encode_image_to_base64(image_path)
                content.append({
                    "type": "image_url",
                    "image_url": {"url": image_url}
                })

        # Add images from base64
        if image_base64_list:
            for image_base64 in image_base64_list:
                if not image_base64.startswith("data:"):
                    image_base64 = f"data:image/png;base64,{image_base64}"
                content.append({
                    "type": "image_url",
                    "image_url": {"url": image_base64}
                })

        return content

    @staticmethod
    def extract_images_from_message(message: Dict[str, Any]) -> List[str]:
        """
        Extract image URLs/base64 from a multimodal message

        Args:
            message: Message dictionary with content

        Returns:
            List of image URLs/base64 strings
        """
        images = []
        content = message.get("content", [])

        if isinstance(content, str):
            # Single text content, no images
            return images

        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "image_url":
                    url = item.get("image_url", {}).get("url", "")
                    if url:
                        images.append(url)

        return images

    @staticmethod
    def extract_text_from_message(message: Dict[str, Any]) -> str:
        """
        Extract text content from a multimodal message

        Args:
            message: Message dictionary with content

        Returns:
            Text content string
        """
        content = message.get("content", "")

        if isinstance(content, str):
            return content

        text_parts = []
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    text_parts.append(item.get("text", ""))

        return " ".join(text_parts)

    @staticmethod
    def validate_multimodal_message(message: Dict[str, Any]) -> bool:
        """
        Validate that a message has proper multimodal format

        Args:
            message: Message dictionary to validate

        Returns:
            True if valid, False otherwise
        """
        if "role" not in message:
            return False

        content = message.get("content")
        if content is None:
            return False

        # String content is valid
        if isinstance(content, str):
            return True

        # List content must have valid items
        if isinstance(content, list):
            for item in content:
                if not isinstance(item, dict):
                    return False
                item_type = item.get("type")
                if item_type == "text":
                    if "text" not in item:
                        return False
                elif item_type == "image_url":
                    if "image_url" not in item:
                        return False
                    if not isinstance(item["image_url"], dict) or "url" not in item["image_url"]:
                        return False
                else:
                    return False

        return True

    @staticmethod
    def count_tokens_multimodal(message: Dict[str, Any], approximate: bool = True) -> int:
        """
        Approximate token count for multimodal message

        Note: This is an approximation. Actual token counts depend on the model.

        Args:
            message: Multimodal message dictionary
            approximate: Whether to use approximation (default: True)

        Returns:
            Approximate token count
        """
        text = InputUtils.extract_text_from_message(message)

        # Rough approximation: 1 token ≈ 4 characters for English
        text_tokens = len(text) // 4 if approximate else len(text.split())

        # Add tokens for images (rough approximation)
        images = InputUtils.extract_images_from_message(message)
        # Each image roughly counts as 170 tokens (OpenAI's approximation)
        image_tokens = len(images) * 170

        return text_tokens + image_tokens


# Backward-compatible aliases kept for existing imports/usages.
MessageUtils = InputUtils
MultimodalUtils = InputUtils
