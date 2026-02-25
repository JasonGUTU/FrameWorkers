"""Reusable video backend services for agents."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

_MOCK_MP4_HEADER = (
    b"\x00\x00\x00\x1c"
    b"ftyp"
    b"isom"
    b"\x00\x00\x02\x00"
    b"isomiso2mp41"
)


class VideoService:
    """Abstract video generation service."""

    async def generate_clip(
        self,
        *,
        shot_id: str,
        keyframe_images: list[bytes],
        prompt: str,
        duration_sec: float,
        fps: int = 24,
        width: int = 1024,
        height: int = 576,
        **kwargs: Any,
    ) -> bytes:
        raise NotImplementedError(
            "VideoService.generate_clip() must be overridden by a concrete backend."
        )

    async def assemble_scene(
        self,
        *,
        scene_id: str,
        clip_bytes_list: list[bytes],
        transitions: list[dict[str, Any]],
    ) -> bytes:
        return b"".join(clip_bytes_list)

    async def assemble_final(
        self,
        *,
        scene_bytes_list: list[bytes],
    ) -> bytes:
        return b"".join(scene_bytes_list)


class MockVideoService(VideoService):
    """Mock backend that returns minimal placeholder MP4 bytes."""

    async def generate_clip(
        self,
        *,
        shot_id: str,
        keyframe_images: list[bytes] | None = None,
        prompt: str = "",
        duration_sec: float = 3.0,
        fps: int = 24,
        width: int = 1024,
        height: int = 576,
        **kwargs: Any,
    ) -> bytes:
        logger.info(
            "[MockVideoService] Generating placeholder clip for %s (%.1fs)",
            shot_id,
            duration_sec,
        )
        return _MOCK_MP4_HEADER

    async def assemble_scene(
        self,
        *,
        scene_id: str,
        clip_bytes_list: list[bytes],
        transitions: list[dict[str, Any]] | None = None,
    ) -> bytes:
        logger.info("[MockVideoService] Assembling scene %s", scene_id)
        return _MOCK_MP4_HEADER

    async def assemble_final(
        self,
        *,
        scene_bytes_list: list[bytes],
    ) -> bytes:
        logger.info("[MockVideoService] Assembling final video")
        return _MOCK_MP4_HEADER
