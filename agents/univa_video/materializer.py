"""UnivaVideoMaterializer — I2V per shot + FFmpeg merge.

Mirrors UniVA's storyvideo_gen Stages 4+6:
  - Per shot: image_to_video_generate(keyframe_image, prompt) → 5s MP4
  - Final: FFmpeg concat all shots → merged video
"""

from __future__ import annotations

import asyncio
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from typing import TYPE_CHECKING

from ..descriptor import BaseMaterializer, MediaAsset
from inference.generation.video_generators.service import VideoService

if TYPE_CHECKING:
    from ..base_agent import MaterializeContext
    from .schema import UnivaVideoInput

logger = logging.getLogger(__name__)

MAX_RETRIES = 2


class UnivaVideoMaterializer(BaseMaterializer):

    def __init__(self, video_service: VideoService) -> None:
        self.video_svc = video_service

    @staticmethod
    def _build_shot_image_index(typed_input: "UnivaVideoInput") -> dict[int, str]:
        """Map shot_id (int) → local image path from typed_input.shot_keyframes."""
        index: dict[int, str] = {}
        for img in typed_input.shot_keyframes:
            path = img.path or ""
            if path.startswith("file://"):
                path = path[7:]
            if not path:
                continue
            # Extract shot_id from sys_id pattern: img_shot_{N}_keyframe
            for part in Path(path).stem.split("_"):
                if part.isdigit():
                    sid = int(part)
                    if sid not in index and "shot" in Path(path).stem:
                        index[sid] = path
                        break
        return index

    def _find_keyframe_bytes(
        self,
        shot_id: int,
        typed_input: "UnivaVideoInput",
    ) -> bytes | None:
        """Find keyframe image bytes for a shot — load from file path."""
        if not hasattr(self, "_shot_image_index"):
            self._shot_image_index = self._build_shot_image_index(typed_input)
        path = self._shot_image_index.get(shot_id)
        if not path:
            return None
        try:
            return Path(path).read_bytes()
        except Exception as e:
            logger.warning("[UnivaVideo] Failed to read keyframe for shot %s: %s", shot_id, e)
            return None

    @staticmethod
    def _merge_clips_ffmpeg(clip_bytes_list: list[bytes]) -> bytes:
        """Merge multiple MP4 clips into a single MP4 using FFmpeg concat demuxer."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            clip_paths = []
            for i, clip in enumerate(clip_bytes_list):
                p = tmpdir_path / f"clip_{i:03d}.mp4"
                p.write_bytes(clip)
                clip_paths.append(p)

            concat_file = tmpdir_path / "concat.txt"
            concat_file.write_text(
                "\n".join(f"file '{p}'" for p in clip_paths),
                encoding="utf-8",
            )

            output_path = tmpdir_path / "merged.mp4"
            cmd = [
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0",
                "-i", str(concat_file),
                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
                "-an",
                str(output_path),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                # Fallback: try copy mode
                cmd_copy = [
                    "ffmpeg", "-y",
                    "-f", "concat", "-safe", "0",
                    "-i", str(concat_file),
                    "-c", "copy",
                    str(output_path),
                ]
                subprocess.run(cmd_copy, capture_output=True, text=True, timeout=120)

            if output_path.exists():
                return output_path.read_bytes()
            raise RuntimeError(f"FFmpeg merge failed: {result.stderr[:500]}")

    async def materialize(
        self,
        ctx: "MaterializeContext",
        asset_dict: dict[str, Any],
    ) -> list[MediaAsset]:
        typed_input = ctx.typed_input  # type: UnivaVideoInput
        media_assets: list[MediaAsset] = []
        content = asset_dict.get("content", {})
        shot_videos = content.get("shot_videos", [])

        # ==================================================================
        # Phase 1: Generate per-shot video clips (I2V, sequential)
        # ==================================================================
        # Sequential because video generation is heavy and we want ordered results.
        clip_bytes_list: list[bytes] = []

        for sv in shot_videos:
            shot_id = sv.get("shot_id", 0)
            prompt = sv.get("video_prompt", "")

            keyframe_bytes = self._find_keyframe_bytes(shot_id, typed_input)
            keyframe_images = [keyframe_bytes] if keyframe_bytes else []

            clip_data = None
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    clip_data = await self.video_svc.generate_clip(
                        shot_id=str(shot_id),
                        keyframe_images=keyframe_images,
                        prompt=prompt,
                    )
                    logger.info(
                        "[UnivaVideo] Shot %s clip generated (%d bytes)",
                        shot_id, len(clip_data),
                    )
                    break
                except Exception as e:
                    logger.warning(
                        "[UnivaVideo] Shot %s attempt %d failed: %s",
                        shot_id, attempt, e,
                    )

            if clip_data:
                clip_bytes_list.append(clip_data)
                video_asset = sv.get("video_asset", {})
                media_assets.append(MediaAsset(
                    sys_id=f"clip_shot_{shot_id}",
                    data=clip_data,
                    extension="mp4",
                    uri_holder=video_asset,
                ))

        logger.info(
            "[UnivaVideo] Phase 1 done: %d/%d shot clips",
            len(clip_bytes_list), len(shot_videos),
        )

        # ==================================================================
        # Phase 2: Merge all clips into final video (FFmpeg)
        # ==================================================================
        if clip_bytes_list:
            try:
                merged = self._merge_clips_ffmpeg(clip_bytes_list)
                final_asset = content.get("final_video_asset", {})
                media_assets.append(MediaAsset(
                    sys_id="clip_final",
                    data=merged,
                    extension="mp4",
                    uri_holder=final_asset,
                ))
                logger.info(
                    "[UnivaVideo] Final video merged (%d bytes from %d clips)",
                    len(merged), len(clip_bytes_list),
                )
            except Exception as e:
                logger.error("[UnivaVideo] FFmpeg merge failed: %s", e)

        return media_assets
