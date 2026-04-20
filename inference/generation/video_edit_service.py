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
        import asyncio
        import tempfile
        logger.info("[fal.ai] Inpaint: model=%s, prompt=%.60s", self._inpaint_model, prompt)

        arguments: dict[str, Any] = {
            "prompt": prompt,
            "video_url": await self._upload_file(video_path),
            "match_input_num_frames": True,
            "match_input_frames_per_second": True,
        }

        # wan-vace-14b/inpainting expects mask_video_url (a real uploaded URL,
        # not a data URI). Our depth-derived masks are video bytes — write to
        # a temp .mp4 and upload via fal_client.upload_file.
        tmp_mask_path: str | None = None
        try:
            if isinstance(mask, str) and os.path.isfile(mask):
                arguments["mask_video_url"] = await self._upload_file(mask)
            elif isinstance(mask, bytes) and mask:
                with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
                    tmp.write(mask)
                    tmp_mask_path = tmp.name
                arguments["mask_video_url"] = await self._upload_file(tmp_mask_path)

            result = await fal_subscribe(self._api_key, self._inpaint_model, arguments)
        finally:
            if tmp_mask_path and os.path.isfile(tmp_mask_path):
                os.unlink(tmp_mask_path)

        video_url = extract_fal_media_url(result, media_type="video")
        video_bytes = await http_download_bytes(self.http, video_url)
        logger.info("[fal.ai] Inpaint complete: %d bytes", len(video_bytes))
        return video_bytes

    async def estimate_depth(self, video_path: str) -> DepthMask:
        """Run depth estimation, then threshold the depth video into proper
        binary fg / bg mask videos.

        Mask convention: ``WHITE = pixels to inpaint, BLACK = preserve``
        (matches wan-vace-14b/inpainting's expectation).

        depth-anything outputs grayscale where bright = close (foreground),
        dark = far (background). So:
          foreground mask: bright pixels → white  → ``y >= 128 ? 255 : 0``
          background mask: dark pixels   → white  → ``y <  128 ? 255 : 0``
        Without this threshold step the raw depth video gets passed through
        as "mask" and wan-vace-14b silently treats it as no-mask (= pure
        v2v), causing the foreground to be redrawn alongside the background.
        """
        import asyncio
        import subprocess
        import tempfile
        logger.info("[fal.ai] Depth estimation: model=%s", self._depth_model)

        arguments: dict[str, Any] = {
            "video_url": await self._upload_file(video_path),
        }

        result = await fal_subscribe(self._api_key, self._depth_model, arguments)

        fg_bytes = b""
        bg_bytes = b""
        depth_path: str | None = None
        fg_path: str | None = None
        bg_path: str | None = None
        try:
            depth_url = extract_fal_media_url(result, media_type="video")
            depth_bytes = await http_download_bytes(self.http, depth_url)

            with tempfile.NamedTemporaryFile(suffix="_depth.mp4", delete=False) as tmp:
                tmp.write(depth_bytes)
                depth_path = tmp.name
            fg_path = depth_path + ".fg.mp4"
            bg_path = depth_path + ".bg.mp4"

            await asyncio.to_thread(
                subprocess.run,
                ["ffmpeg", "-y", "-i", depth_path,
                 "-vf", "lutyuv=y='if(gte(val\\,128)\\,255\\,0)':u=128:v=128",
                 "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", fg_path],
                check=True, capture_output=True,
            )
            await asyncio.to_thread(
                subprocess.run,
                ["ffmpeg", "-y", "-i", depth_path,
                 "-vf", "lutyuv=y='if(lt(val\\,128)\\,255\\,0)':u=128:v=128",
                 "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", bg_path],
                check=True, capture_output=True,
            )
            with open(fg_path, "rb") as f: fg_bytes = f.read()
            with open(bg_path, "rb") as f: bg_bytes = f.read()
        except (RuntimeError, subprocess.CalledProcessError) as e:
            stderr = getattr(e, "stderr", b"")[:200] if isinstance(e, subprocess.CalledProcessError) else b""
            logger.warning("[fal.ai] depth → binary mask conversion failed: %s %s", e, stderr)
        finally:
            for p in (depth_path, fg_path, bg_path):
                if p and os.path.isfile(p):
                    try: os.unlink(p)
                    except OSError: pass

        logger.info("[fal.ai] Depth estimation complete (fg=%d bytes, bg=%d bytes)",
                    len(fg_bytes), len(bg_bytes))
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
