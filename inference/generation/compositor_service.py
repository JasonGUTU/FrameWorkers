"""Compositor service — FFmpeg-based video+audio mux with subtitle burn-in.

Composes a final deliverable MP4 from:
  - Video track (MP4)
  - Audio track (WAV)
  - Subtitle file (SRT, optional)
  - Composition plan (transitions, color grade — applied when ffmpeg supports it)
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import tempfile
from typing import Any

from ._mock_data import MOCK_MP4_HEADER

logger = logging.getLogger(__name__)


class CompositorService:
    """FFmpeg-based video compositor."""

    async def compose(
        self,
        *,
        video_path: str,
        audio_path: str = "",
        subtitle_srts: list[str] | None = None,
        plan: dict[str, Any] | None = None,
    ) -> bytes:
        """Compose final video from video + audio + subtitles.

        ``subtitle_srts`` is a list of SRT blobs (one per language). The
        filter chain stacks every non-empty entry with an increasing
        ``MarginV`` so bilingual / multilingual tracks sit on top of each
        other instead of overlapping. Pass an empty list / None for no
        subtitles.

        Returns the composited MP4 bytes.
        """
        if not video_path or not os.path.isfile(video_path):
            logger.warning("CompositorService: video_path missing or not a file: %s", video_path)
            return MOCK_MP4_HEADER

        plan = plan or {}
        ffmpeg_bin = shutil.which("ffmpeg")
        if not ffmpeg_bin:
            logger.warning("CompositorService: ffmpeg not found, returning raw video")
            with open(video_path, "rb") as fh:
                return fh.read()

        temp_dir = tempfile.mkdtemp(prefix="fw_compositor_")
        out_path = os.path.join(temp_dir, "composed.mp4")
        srt_paths: list[str] = []

        try:
            cmd: list[str] = [ffmpeg_bin, "-y"]

            # Input: video
            cmd += ["-i", video_path]

            # Input: audio (if available)
            has_audio = bool(audio_path) and os.path.isfile(audio_path)
            if has_audio:
                cmd += ["-i", audio_path]

            # Build filter chain
            vfilters: list[str] = []

            # Subtitle burn-in — one filter per track, stacked by MarginV
            # so bilingual flows render with track #1 at bottom and each
            # subsequent track above it.
            # FontName is forced to a CJK-capable family so Chinese /
            # Japanese / Korean cues render real glyphs instead of libass's
            # default-font tofu; the name resolves through fontconfig, which
            # falls back to Latin automatically for non-CJK text.
            style = plan.get("subtitle_style", {})
            font_size = style.get("font_size", 24)
            font_color = (style.get("font_color", "#FFFFFF")).lstrip("#")
            outline_color = (style.get("outline_color", "#000000")).lstrip("#")
            font_name = style.get("font_name", "Noto Sans CJK SC")
            real_srts = [s for s in (subtitle_srts or []) if s and s.strip()]
            for idx, srt_body in enumerate(real_srts):
                srt_path = os.path.join(temp_dir, f"subs_{idx}.srt")
                with open(srt_path, "w", encoding="utf-8") as fh:
                    fh.write(srt_body)
                srt_paths.append(srt_path)
                margin_v = 10 + idx * (font_size + 10)
                vfilters.append(
                    f"subtitles={srt_path}:force_style="
                    f"'FontName={font_name},"
                    f"FontSize={font_size},"
                    f"PrimaryColour=&H00{font_color}&,"
                    f"OutlineColour=&H00{outline_color}&,"
                    f"Outline=2,"
                    f"Shadow=1,"
                    f"MarginV={margin_v}'"
                )

            # Color grading
            cg = plan.get("color_grade", {})
            brightness = cg.get("brightness", 0.0)
            contrast = cg.get("contrast", 0.0)
            saturation = cg.get("saturation", 0.0)
            if any(abs(v) > 0.001 for v in [brightness, contrast, saturation]):
                b = brightness
                c = 1.0 + contrast
                s = 1.0 + saturation
                vfilters.append(f"eq=brightness={b}:contrast={c}:saturation={s}")

            if vfilters:
                cmd += ["-vf", ",".join(vfilters)]

            # Map streams
            cmd += ["-map", "0:v:0"]
            if has_audio:
                cmd += ["-map", "1:a:0", "-c:a", "aac"]
            cmd += ["-c:v", "libx264", "-preset", "fast", "-crf", "23"]
            cmd += ["-movflags", "+faststart", out_path]

            proc = subprocess.run(
                cmd, capture_output=True, check=False, text=True, timeout=300,
            )

            if proc.returncode != 0 or not os.path.exists(out_path):
                logger.warning(
                    "CompositorService ffmpeg failed (code=%s): %s",
                    proc.returncode, (proc.stderr or "").strip()[-500:],
                )
                with open(video_path, "rb") as fh:
                    return fh.read()

            with open(out_path, "rb") as fh:
                result = fh.read()
            logger.info("CompositorService: composed %d bytes", len(result))
            return result

        except Exception as exc:
            logger.warning("CompositorService error: %s", exc)
            with open(video_path, "rb") as fh:
                return fh.read()
        finally:
            for p in [out_path, *srt_paths]:
                if p and os.path.exists(p):
                    try:
                        os.remove(p)
                    except OSError:
                        pass
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except OSError:
                pass


class MockCompositorService(CompositorService):
    """Mock compositor that returns placeholder MP4 bytes."""

    async def compose(
        self,
        *,
        video_path: str,
        audio_path: str = "",
        subtitle_srts: list[str] | None = None,
        plan: dict[str, Any] | None = None,
    ) -> bytes:
        logger.info("[MockCompositor] Placeholder compose for %s", video_path)
        return MOCK_MP4_HEADER
