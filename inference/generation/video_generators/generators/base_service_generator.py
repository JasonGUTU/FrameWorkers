"""Shared base for service-backed video generators."""

from __future__ import annotations

import asyncio
import base64

from ...base_generator import BaseVideoGenerator
from ..service import VideoService


class BaseServiceVideoGenerator(BaseVideoGenerator):
    """Base class with common helpers for `VideoService` based generators."""

    def __init__(self, service: VideoService) -> None:
        self._service = service
        super().__init__()

    @staticmethod
    def to_video_data_url(video_bytes: bytes, mime: str = "video/mp4") -> str:
        return f"data:{mime};base64,{base64.b64encode(video_bytes).decode('utf-8')}"

    def run_service_generate_clip(
        self,
        *,
        shot_id: str,
        prompt: str,
        duration_sec: float,
        fps: int,
        width: int,
        height: int,
    ) -> bytes:
        return asyncio.run(
            self._service.generate_clip(
                shot_id=shot_id,
                keyframe_images=[],
                prompt=prompt,
                duration_sec=duration_sec,
                fps=fps,
                width=width,
                height=height,
            )
        )
