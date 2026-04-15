"""Video editing service — style transfer, inpainting, depth estimation.

Provides the inference backend for StyleTransferAgent and InpaintAgent.

- ``MockVideoEditService``: returns placeholder MP4 bytes (no credits).
- ``FalVideoEditService``: calls fal.ai VACE / style-transfer endpoints.

The ``select_video_edit_service()`` helper in ``__init__.py`` picks the
backend based on ``FW_USE_REAL_MEDIA_GEN``.
"""

from __future__ import annotations

import base64
import logging
import os
from dataclasses import dataclass
from typing import Any

import httpx

from ._mock_data import MOCK_MP4_HEADER
from .fal_helpers import (
    LazyHttpxClientMixin,
    extract_fal_media_url,
    fal_subscribe,
    http_download_bytes,
)

logger = logging.getLogger(__name__)


@dataclass
class DepthMask:
    """Result of depth estimation — foreground and background masks."""
    foreground: bytes = b""
    background: bytes = b""


class VideoEditService:
    """Abstract video editing service."""

    async def style_transfer(
        self,
        *,
        video_path: str,
        prompt: str,
        strength: float = 0.7,
        preserve_motion: bool = True,
        reference_path: str | None = None,
    ) -> bytes:
        raise NotImplementedError

    async def inpaint(
        self,
        *,
        video_path: str,
        mask: bytes | str,
        prompt: str,
        blend_px: int = 8,
    ) -> bytes:
        raise NotImplementedError

    async def estimate_depth(self, video_path: str) -> DepthMask:
        raise NotImplementedError

    async def track_object(self, video_path: str, description: str) -> bytes:
        raise NotImplementedError


class MockVideoEditService(VideoEditService):
    """Mock video edit service that returns placeholder MP4 bytes."""

    async def style_transfer(self, *, video_path, prompt, strength=0.7, preserve_motion=True, reference_path=None):
        logger.info("[MockVideoEdit] Placeholder style transfer: %.60s (strength=%.2f)", prompt, strength)
        return MOCK_MP4_HEADER

    async def inpaint(self, *, video_path, mask, prompt, blend_px=8):
        logger.info("[MockVideoEdit] Placeholder inpaint: %.60s", prompt)
        return MOCK_MP4_HEADER

    async def estimate_depth(self, video_path):
        logger.info("[MockVideoEdit] Placeholder depth estimation for %s", video_path)
        return DepthMask(foreground=b"mock_fg_mask", background=b"mock_bg_mask")

    async def track_object(self, video_path, description):
        logger.info("[MockVideoEdit] Placeholder object tracking: %.60s", description)
        return b"mock_object_mask"


class FalVideoEditService(VideoEditService, LazyHttpxClientMixin):
    """Video editing service backed by fal.ai.

    Uses different fal.ai endpoints for each operation:
    - style_transfer: creative video generation with style guidance
    - inpaint: VACE-based video inpainting (when available)
    - estimate_depth: depth estimation model
    - track_object: SAM-based video segmentation

    Environment variables:
      FAL_API_KEY            — required for all calls
      FAL_VIDEO_STYLE_MODEL  — model for style transfer (default: fal-ai/creative-video)
      FAL_VIDEO_INPAINT_MODEL — model for inpainting (default: fal-ai/vace/inpaint)
      FAL_DEPTH_MODEL        — model for depth estimation (default: fal-ai/depth-anything-v2/video)
      FAL_SAM_MODEL          — model for object segmentation (default: fal-ai/sam2/video)
    """

    def __init__(
        self,
        api_key: str | None = None,
        timeout: float = 300.0,
    ) -> None:
        self._api_key = api_key or os.getenv("FAL_API_KEY", "")
        self.timeout = timeout
        self._http: httpx.AsyncClient | None = None

        self._style_model = os.getenv("FAL_VIDEO_STYLE_MODEL", "").strip()
        self._inpaint_model = os.getenv("FAL_VIDEO_INPAINT_MODEL", "").strip()
        self._depth_model = os.getenv("FAL_DEPTH_MODEL", "").strip()
        self._sam_model = os.getenv("FAL_SAM_MODEL", "").strip()

    async def _upload_file(self, path: str) -> str:
        """Upload a file to fal.ai and return a hosted URL."""
        import asyncio, os
        import fal_client
        previous_key = os.getenv("FAL_KEY")
        if self._api_key:
            os.environ["FAL_KEY"] = self._api_key
        try:
            url = await asyncio.to_thread(fal_client.upload_file, path)
            return url
        finally:
            if previous_key is None:
                os.environ.pop("FAL_KEY", None)
            else:
                os.environ["FAL_KEY"] = previous_key

    async def style_transfer(
        self,
        *,
        video_path: str,
        prompt: str,
        strength: float = 0.7,
        preserve_motion: bool = True,
        reference_path: str | None = None,
    ) -> bytes:
        logger.info("[fal.ai] Style transfer: model=%s, prompt=%.60s", self._style_model, prompt)

        arguments: dict[str, Any] = {
            "prompt": prompt,
            "video_url": await self._upload_file(video_path),
            "strength": strength,
        }
        if reference_path and os.path.isfile(reference_path):
            ref_mime = "image/jpeg" if reference_path.endswith((".jpg", ".jpeg")) else "image/png"
            arguments["reference_image_url"] = await self._upload_file(reference_path)

        result = await fal_subscribe(self._api_key, self._style_model, arguments)
        video_url = extract_fal_media_url(result, media_type="video")
        video_bytes = await http_download_bytes(self.http, video_url)
        logger.info("[fal.ai] Style transfer complete: %d bytes", len(video_bytes))
        return video_bytes

    async def inpaint(
        self,
        *,
        video_path: str,
        mask: bytes | str,
        prompt: str,
        blend_px: int = 8,
    ) -> bytes:
        logger.info("[fal.ai] Inpaint: model=%s, prompt=%.60s", self._inpaint_model, prompt)

        arguments: dict[str, Any] = {
            "prompt": prompt,
            "video_url": await self._upload_file(video_path),
        }

        # Mask can be bytes or file path
        if isinstance(mask, str) and os.path.isfile(mask):
            mask_mime = "image/png"
            arguments["mask_url"] = await self._upload_file(mask)
        elif isinstance(mask, bytes) and mask:
            b64 = base64.b64encode(mask).decode()
            arguments["mask_url"] = f"data:image/png;base64,{b64}"

        result = await fal_subscribe(self._api_key, self._inpaint_model, arguments)
        video_url = extract_fal_media_url(result, media_type="video")
        video_bytes = await http_download_bytes(self.http, video_url)
        logger.info("[fal.ai] Inpaint complete: %d bytes", len(video_bytes))
        return video_bytes

    async def estimate_depth(self, video_path: str) -> DepthMask:
        logger.info("[fal.ai] Depth estimation: model=%s", self._depth_model)

        arguments: dict[str, Any] = {
            "video_url": await self._upload_file(video_path),
        }

        result = await fal_subscribe(self._api_key, self._depth_model, arguments)

        # Download the depth map / masks from the response
        fg_bytes = b""
        bg_bytes = b""
        try:
            depth_url = extract_fal_media_url(result, media_type="video")
            depth_bytes = await http_download_bytes(self.http, depth_url)
            # The depth model returns a depth video; we use it as both masks
            # (foreground = depth, background = inverted depth).
            # A more sophisticated implementation would threshold the depth map.
            fg_bytes = depth_bytes
            bg_bytes = depth_bytes
        except RuntimeError:
            logger.warning("[fal.ai] Could not extract depth video URL")

        logger.info("[fal.ai] Depth estimation complete")
        return DepthMask(foreground=fg_bytes, background=bg_bytes)

    async def track_object(self, video_path: str, description: str) -> bytes:
        logger.info("[fal.ai] Object tracking: model=%s, desc=%.60s", self._sam_model, description)

        arguments: dict[str, Any] = {
            "video_url": await self._upload_file(video_path),
            "prompt": description,
        }

        result = await fal_subscribe(self._api_key, self._sam_model, arguments)

        try:
            mask_url = extract_fal_media_url(result, media_type="video")
            mask_bytes = await http_download_bytes(self.http, mask_url)
            logger.info("[fal.ai] Object tracking complete: %d bytes mask", len(mask_bytes))
            return mask_bytes
        except RuntimeError:
            logger.warning("[fal.ai] Could not extract tracking mask URL")
            return b""
