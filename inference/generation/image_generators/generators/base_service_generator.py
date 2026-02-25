"""Shared base for service-backed image generators."""

from __future__ import annotations

import asyncio
import base64
from typing import Any

from ...base_generator import BaseImageGenerator
from ..service import ImageService


class BaseServiceImageGenerator(BaseImageGenerator):
    """Base class with common helpers for `ImageService` based generators."""

    def __init__(self, service: ImageService | None = None) -> None:
        self._service = service or ImageService()
        super().__init__()

    @staticmethod
    def decode_image_input(value: Any) -> bytes:
        if isinstance(value, bytes):
            return value
        if isinstance(value, str):
            if value.startswith("data:image"):
                return base64.b64decode(value.split(",", 1)[1])
            with open(value, "rb") as f:
                return f.read()
        raise ValueError("images[] must be bytes, data URL, or file path")

    @staticmethod
    def to_image_data_url(image_bytes: bytes, mime: str = "image/png") -> str:
        return f"data:{mime};base64,{base64.b64encode(image_bytes).decode('utf-8')}"

    def run_service_generate(self, prompt: str) -> bytes:
        return asyncio.run(self._service.generate_image(prompt))

    def run_service_edit(self, reference_images: list[bytes], prompt: str) -> bytes:
        return asyncio.run(self._service.edit_image(reference_images, prompt))
