"""
Image Utilities - Base64 Encoding/Decoding and Image Processing

Provides utilities for handling images in multimodal contexts.
"""

from typing import Optional, Union, BinaryIO
from pathlib import Path
import base64
import io
from PIL import Image


class ImageUtils:
    """Utilities for image encoding, decoding, and processing"""

    @staticmethod
    def encode_image_to_base64(
        image_path: Union[str, Path, BinaryIO],
        format: Optional[str] = None
    ) -> str:
        """
        Encode image to base64 string

        Args:
            image_path: Path to image file or file-like object
            format: Image format (e.g., 'PNG', 'JPEG'). Auto-detected if None

        Returns:
            Base64 encoded string with data URI prefix
        """
        if isinstance(image_path, (str, Path)):
            image_path = Path(image_path)
            if not image_path.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")

            # Detect format from extension if not provided
            if format is None:
                format = image_path.suffix[1:].upper() or "PNG"

            with open(image_path, "rb") as f:
                image_data = f.read()
        else:
            # File-like object
            image_data = image_path.read()
            if format is None:
                format = "PNG"

        # Encode to base64
        base64_str = base64.b64encode(image_data).decode("utf-8")

        # Return with data URI prefix
        mime_type = ImageUtils._get_mime_type(format)
        return f"data:{mime_type};base64,{base64_str}"

    @staticmethod
    def decode_base64_to_image(base64_str: str) -> Image.Image:
        """
        Decode base64 string to PIL Image

        Args:
            base64_str: Base64 encoded string (with or without data URI prefix)

        Returns:
            PIL Image object
        """
        # Remove data URI prefix if present
        if "," in base64_str:
            base64_str = base64_str.split(",", 1)[1]

        # Decode base64
        image_data = base64.b64decode(base64_str)

        # Create PIL Image
        image = Image.open(io.BytesIO(image_data))
        return image

    @staticmethod
    def save_base64_image(base64_str: str, output_path: Union[str, Path], format: Optional[str] = None):
        """
        Save base64 encoded image to file

        Args:
            base64_str: Base64 encoded string
            output_path: Path to save image
            format: Image format (e.g., 'PNG', 'JPEG'). Auto-detected if None
        """
        image = ImageUtils.decode_base64_to_image(base64_str)

        output_path = Path(output_path)
        if format is None:
            format = output_path.suffix[1:].upper() or "PNG"

        image.save(output_path, format=format)

    @staticmethod
    def resize_image(
        image: Union[Image.Image, str, Path],
        max_size: tuple = (1024, 1024),
        maintain_aspect_ratio: bool = True
    ) -> Image.Image:
        """
        Resize image to fit within max_size while maintaining aspect ratio

        Args:
            image: PIL Image, image path, or base64 string
            max_size: Maximum (width, height)
            maintain_aspect_ratio: Whether to maintain aspect ratio

        Returns:
            Resized PIL Image
        """
        # Load image if needed
        if isinstance(image, (str, Path)):
            if Path(image).exists():
                img = Image.open(image)
            else:
                # Assume base64 string
                img = ImageUtils.decode_base64_to_image(image)
        else:
            img = image

        if maintain_aspect_ratio:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
        else:
            img = img.resize(max_size, Image.Resampling.LANCZOS)

        return img

    @staticmethod
    def get_image_info(image: Union[Image.Image, str, Path]) -> dict:
        """
        Get image information (size, format, mode)

        Args:
            image: PIL Image, image path, or base64 string

        Returns:
            Dictionary with image information
        """
        # Load image if needed
        if isinstance(image, (str, Path)):
            if Path(image).exists():
                img = Image.open(image)
            else:
                # Assume base64 string
                img = ImageUtils.decode_base64_to_image(image)
        else:
            img = image

        return {
            "width": img.width,
            "height": img.height,
            "format": img.format,
            "mode": img.mode,
            "size_bytes": len(img.tobytes()) if hasattr(img, "tobytes") else None,
        }

    @staticmethod
    def create_multimodal_message(
        text: str,
        image_path: Optional[Union[str, Path]] = None,
        image_base64: Optional[str] = None,
        role: str = "user",
    ) -> dict:
        """
        Backward-compatible wrapper for message construction.

        Prefer using InputUtils.create_multimodal_message from message_utils.
        """
        from .message_utils import InputUtils

        return InputUtils.create_multimodal_message(
            text=text,
            image_path=image_path,
            image_base64=image_base64,
            role=role,
        )

    @staticmethod
    def _get_mime_type(format: str) -> str:
        """Get MIME type for image format"""
        mime_types = {
            "PNG": "image/png",
            "JPEG": "image/jpeg",
            "JPG": "image/jpeg",
            "GIF": "image/gif",
            "WEBP": "image/webp",
            "BMP": "image/bmp",
            "TIFF": "image/tiff",
        }
        return mime_types.get(format.upper(), "image/png")
