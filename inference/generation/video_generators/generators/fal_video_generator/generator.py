"""Concrete video generator backed by fal.ai video service."""

from __future__ import annotations

import asyncio
import base64
from pathlib import Path
from typing import Any, Dict, Union

from ....base_generator import GeneratorMetadata
from ...service import FalVideoService
from ..base_service_generator import BaseServiceVideoGenerator


class FalVideoGenerator(BaseServiceVideoGenerator):
    """Generate videos via fal.ai."""

    def __init__(self) -> None:
        super().__init__(service=FalVideoService())

    def get_metadata(self) -> GeneratorMetadata:
        return GeneratorMetadata(
            id="fal_video_generator",
            name="fal.ai Video Generator",
            description="Concrete video generator using fal.ai backend",
            capabilities=["text_to_video", "image_to_video", "video_to_video"],
            input_schema={
                "prompt": {"type": "string", "required": True},
                "images": {"type": "array", "required": False},
                "videos": {"type": "array", "required": False},
                "duration": {"type": "integer", "required": False, "default": 1},
                "fps": {"type": "integer", "required": False, "default": 8},
                "width": {"type": "integer", "required": False, "default": 384},
                "height": {"type": "integer", "required": False, "default": 384},
            },
            output_schema={
                "video": {"type": "string", "description": "Video data URL"},
                "metadata": {"type": "object"},
            },
        )

    def generate(self, **kwargs) -> Dict[str, Any]:
        prompt = kwargs.get("prompt", "")
        images = kwargs.get("images", []) or []
        videos = kwargs.get("videos", []) or []

        keyframes = []
        if images:
            keyframes.append(self._decode_binary_input(images[0]))

        source_video_url = None
        if videos:
            source_video_url = self._to_data_url(
                self._decode_binary_input(videos[0]),
                mime="video/mp4",
            )

        clip = asyncio.run(
            self._service.generate_clip(
                shot_id="registry_clip",
                keyframe_images=keyframes,
                prompt=prompt,
                duration_sec=float(kwargs.get("duration", 1)),
                fps=int(kwargs.get("fps", 8)),
                width=int(kwargs.get("width", 384)),
                height=int(kwargs.get("height", 384)),
                source_video_url=source_video_url,
            )
        )
        data_url = self.to_video_data_url(clip)
        return {"video": data_url, "metadata": {"bytes": len(clip), "provider": "fal.ai"}}

    @staticmethod
    def _decode_binary_input(value: Union[str, Path, bytes]) -> bytes:
        if isinstance(value, bytes):
            return value
        if isinstance(value, Path):
            return value.read_bytes()
        if isinstance(value, str):
            if value.startswith("data:"):
                return base64.b64decode(value.split(",", 1)[1])
            return Path(value).read_bytes()
        raise ValueError("inputs[] must be bytes, data URL, or file path")

    @staticmethod
    def _to_data_url(data: bytes, mime: str) -> str:
        return f"data:{mime};base64,{base64.b64encode(data).decode('utf-8')}"
