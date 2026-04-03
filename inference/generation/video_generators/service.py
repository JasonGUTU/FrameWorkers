"""Reusable video backend services for agents."""

from __future__ import annotations

import asyncio
import base64
import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import httpx

from ..fal_helpers import fal_subscribe, http_download_bytes, require_fal_model_var

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
        return await self._concat_mp4_segments(
            clip_bytes_list,
            label=f"scene:{scene_id}",
        )

    async def assemble_final(
        self,
        *,
        scene_bytes_list: list[bytes],
    ) -> bytes:
        return await self._concat_mp4_segments(
            scene_bytes_list,
            label="final",
        )

    async def _concat_mp4_segments(self, segments: list[bytes], *, label: str) -> bytes:
        """Concatenate mp4 segments with ffmpeg concat demuxer.

        Falls back to legacy byte-join only when ffmpeg is unavailable or concat
        fails, so callers still receive a non-empty payload.
        """
        non_empty = [seg for seg in segments if isinstance(seg, (bytes, bytearray)) and seg]
        if not non_empty:
            return b""
        if len(non_empty) == 1:
            return bytes(non_empty[0])

        ffmpeg_bin = shutil.which("ffmpeg")
        if not ffmpeg_bin:
            logger.warning(
                "[VideoService] ffmpeg not found; fallback to byte-join for %s",
                label,
            )
            return b"".join(non_empty)

        try:
            return await asyncio.to_thread(
                self._concat_mp4_segments_sync,
                ffmpeg_bin,
                [bytes(seg) for seg in non_empty],
                label,
            )
        except Exception as exc:
            logger.warning(
                "[VideoService] ffmpeg concat failed for %s; fallback to byte-join: %s",
                label,
                exc,
            )
            return b"".join(non_empty)

    @staticmethod
    def _concat_mp4_segments_sync(ffmpeg_bin: str, segments: list[bytes], label: str) -> bytes:
        with tempfile.TemporaryDirectory(prefix="fw_video_concat_") as tmp_dir:
            tmp_path = Path(tmp_dir)
            parts_file = tmp_path / "parts.txt"
            out_file = tmp_path / "out.mp4"

            lines: list[str] = []
            for idx, payload in enumerate(segments):
                clip_path = tmp_path / f"part_{idx:04d}.mp4"
                clip_path.write_bytes(payload)
                lines.append(f"file '{clip_path.as_posix()}'")
            parts_file.write_text("\n".join(lines), encoding="utf-8")

            proc = subprocess.run(
                [
                    ffmpeg_bin,
                    "-y",
                    "-f",
                    "concat",
                    "-safe",
                    "0",
                    "-i",
                    str(parts_file),
                    "-c",
                    "copy",
                    str(out_file),
                ],
                capture_output=True,
                text=True,
            )
            if proc.returncode != 0 or not out_file.exists():
                stderr_tail = (proc.stderr or "").strip()[-500:]
                raise RuntimeError(
                    f"ffmpeg concat failed for {label} (code={proc.returncode}): {stderr_tail}"
                )

            merged = out_file.read_bytes()
            if not merged:
                raise RuntimeError(f"ffmpeg concat produced empty output for {label}")
            return merged


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


class FalVideoService(VideoService):
    """Video generation service backed by fal.ai."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float = 300.0,
        structured_constraints_field: str | None = None,
    ) -> None:
        self._api_key = api_key or os.getenv("FAL_API_KEY", "")
        self.model = require_fal_model_var("FAL_VIDEO_MODEL", explicit=model)
        self.timeout = timeout
        self.structured_constraints_field = (
            structured_constraints_field
            if structured_constraints_field is not None
            else os.getenv("FAL_VIDEO_STRUCTURED_CONSTRAINTS_FIELD", "").strip()
        )
        self._http: httpx.AsyncClient | None = None

    @property
    def http(self) -> httpx.AsyncClient:
        if self._http is None or self._http.is_closed:
            self._http = httpx.AsyncClient(timeout=self.timeout)
        return self._http

    async def close(self) -> None:
        if self._http and not self._http.is_closed:
            await self._http.aclose()

    @staticmethod
    def _is_fal_kling_model(model: str) -> bool:
        return "kling-video" in model

    @staticmethod
    def _kling_uses_start_end_frame_fields(model: str) -> bool:
        """Kling 2.6+ / v3 / o3 use start_image_url (+ optional end_image_url)."""
        return (
            "/v2.6/" in model
            or "/v3/" in model
            or "/o3/" in model
            or "/v2.7/" in model
        )

    @staticmethod
    def _kling_duration_enum(duration_sec: float) -> str:
        """Many Kling endpoints only allow 5s or 10s (string enum)."""
        return "10" if float(duration_sec) > 5.5 else "5"

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
        logger.info("[fal.ai] Generating video shot=%s model=%s", shot_id, self.model)
        arguments: dict[str, Any] = {"prompt": prompt}

        image_data_urls: list[str] = []
        if keyframe_images:
            image_data_urls = [
                f"data:image/png;base64,{base64.b64encode(img).decode('utf-8')}"
                for img in keyframe_images
            ]

        source_video_url = kwargs.get("source_video_url")
        if isinstance(source_video_url, str) and source_video_url:
            arguments["video_url"] = source_video_url

        # Optional: pass structured consistency constraints as a dedicated field
        # when the target fal model endpoint supports it.
        constraints = kwargs.get("consistency_constraints")
        if (
            self.structured_constraints_field
            and isinstance(constraints, dict)
            and constraints
            and not self._is_fal_kling_model(self.model)
        ):
            arguments[self.structured_constraints_field] = constraints

        result: dict[str, Any]
        if self._is_fal_kling_model(self.model):
            arguments["duration"] = self._kling_duration_enum(
                duration_sec if duration_sec > 0 else 5.0
            )
            if len(image_data_urls) >= 2 and self._kling_uses_start_end_frame_fields(self.model):
                arguments["start_image_url"] = image_data_urls[0]
                arguments["end_image_url"] = image_data_urls[-1]
                logger.info(
                    "[fal.ai] Kling start/end frames for shot=%s (%d anchors -> 2)",
                    shot_id,
                    len(image_data_urls),
                )
            elif len(image_data_urls) >= 2:
                arguments["image_url"] = image_data_urls[0]
                arguments["tail_image_url"] = image_data_urls[-1]
                logger.info(
                    "[fal.ai] Kling image_url/tail for shot=%s (%d anchors -> 2)",
                    shot_id,
                    len(image_data_urls),
                )
            elif len(image_data_urls) == 1:
                if self._kling_uses_start_end_frame_fields(self.model):
                    arguments["start_image_url"] = image_data_urls[0]
                else:
                    arguments["image_url"] = image_data_urls[0]
            result = await self._submit(arguments)
        else:
            # Keep common generation knobs optional to maximize model compatibility.
            if duration_sec > 0:
                arguments["duration"] = int(round(duration_sec))
            if fps > 0:
                arguments["fps"] = int(fps)
            if width > 0 and height > 0:
                # ltx-video-v095 accepts preset labels instead of WxH.
                if "ltx-video-v095" in self.model:
                    arguments["resolution"] = "480p" if int(height) <= 480 else "720p"
                else:
                    arguments["resolution"] = f"{int(width)}x{int(height)}"

            if len(image_data_urls) > 1:
                logger.info(
                    "[fal.ai] Using multi-keyframe conditioning for shot=%s (%d anchors)",
                    shot_id,
                    len(image_data_urls),
                )
                arguments["image_urls"] = image_data_urls
                result = await self._submit(arguments)
            else:
                if image_data_urls:
                    arguments["image_url"] = image_data_urls[0]
                result = await self._submit(arguments)

        video_url = self._extract_video_url(result)
        return await self._download_binary(video_url)

    async def _submit(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return await fal_subscribe(self._api_key, self.model, arguments)

    async def _download_binary(self, url: str) -> bytes:
        return await http_download_bytes(self.http, url)

    @staticmethod
    def _extract_video_url(result: dict[str, Any]) -> str:
        video_obj = result.get("video")
        if isinstance(video_obj, dict):
            url = video_obj.get("url")
            if isinstance(url, str) and url:
                return url

        videos = result.get("videos")
        if isinstance(videos, list) and videos:
            first = videos[0]
            if isinstance(first, dict):
                url = first.get("url")
                if isinstance(url, str) and url:
                    return url

        direct_url = result.get("video_url") or result.get("url")
        if isinstance(direct_url, str) and direct_url:
            return direct_url

        raise RuntimeError(f"No video URL found in fal.ai response keys={list(result.keys())}")
