"""Video generation service — wraps a video generation backend.

Called by Assistant as a post-processing step **after** VideoAgent's
JSON plan passes the quality gate.  Flow:

    VideoAgent (LLM plan)
        → Evaluator (quality gate)
        → VideoService.generate_clip()   ← this module
        → AssetManager.save_binary()
        → update ``video_asset.uri`` in the asset dict

Currently ships with a **mock** backend that produces empty MP4 placeholder
files.  To use a real backend (e.g. RunwayML, Pika, Sora), subclass
``VideoService`` and override ``generate_clip``.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Minimal valid MP4 (ftyp box only) — used by MockVideoService.
_MOCK_MP4_HEADER = (
    b"\x00\x00\x00\x1c"  # box size = 28
    b"ftyp"  # box type
    b"isom"  # major brand
    b"\x00\x00\x02\x00"  # minor version
    b"isomiso2mp41"  # compatible brands
)


class VideoService:
    """Abstract video generation service.

    Subclass and override ``generate_clip`` / ``assemble_scene`` /
    ``assemble_final`` to plug in a real video backend.
    """

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
        """Generate a single shot video clip.

        Args:
            shot_id:         Identifier of the shot being rendered.
            keyframe_images: List of keyframe image bytes that anchor the clip.
            prompt:          Visual/motion description for the clip.
            duration_sec:    Target duration in seconds.
            fps:             Target frames per second.
            width / height:  Output resolution.

        Returns:
            Raw video bytes (MP4).
        """
        raise NotImplementedError(
            "VideoService.generate_clip() must be overridden by a concrete backend."
        )

    async def assemble_scene(
        self,
        *,
        scene_id: str,
        clip_bytes_list: list[bytes],
        transitions: list[dict],
    ) -> bytes:
        """Stitch shot clips into a scene-level clip with transitions.

        Default implementation simply concatenates clip bytes (placeholder).
        Override for proper NLE assembly.
        """
        return b"".join(clip_bytes_list)

    async def assemble_final(
        self,
        *,
        scene_bytes_list: list[bytes],
    ) -> bytes:
        """Assemble scene clips into the final video.

        Default implementation concatenates (placeholder).
        """
        return b"".join(scene_bytes_list)


class MockVideoService(VideoService):
    """Mock backend that returns minimal placeholder MP4 bytes.

    Use during development / testing when no real video backend is available.
    """

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
        transitions: list[dict] | None = None,
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
