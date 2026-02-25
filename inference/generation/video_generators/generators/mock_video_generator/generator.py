"""Concrete video generator backed by mock video service."""

from __future__ import annotations

from typing import Any, Dict

from ....base_generator import GeneratorMetadata
from ...service import MockVideoService
from ..base_service_generator import BaseServiceVideoGenerator


class MockVideoGenerator(BaseServiceVideoGenerator):
    """Generate placeholder clips via `MockVideoService`."""

    def __init__(self) -> None:
        super().__init__(service=MockVideoService())

    def get_metadata(self) -> GeneratorMetadata:
        return GeneratorMetadata(
            id="mock_video_generator",
            name="Mock Video Generator",
            description="Concrete video generator using mock service backend",
            capabilities=["text_to_video", "image_to_video", "video_to_video"],
            input_schema={
                "prompt": {"type": "string", "required": False},
                "duration": {"type": "integer", "required": False, "default": 3},
                "fps": {"type": "integer", "required": False, "default": 24},
                "width": {"type": "integer", "required": False, "default": 1024},
                "height": {"type": "integer", "required": False, "default": 576},
            },
            output_schema={
                "video": {"type": "string", "description": "Video data URL"},
                "metadata": {"type": "object"},
            },
        )

    def generate(self, **kwargs) -> Dict[str, Any]:
        clip = self.run_service_generate_clip(
            shot_id="registry_clip",
            prompt=kwargs.get("prompt", ""),
            duration_sec=float(kwargs.get("duration", 3)),
            fps=int(kwargs.get("fps", 24)),
            width=int(kwargs.get("width", 1024)),
            height=int(kwargs.get("height", 576)),
        )
        data_url = self.to_video_data_url(clip)
        return {"video": data_url, "metadata": {"bytes": len(clip)}}
