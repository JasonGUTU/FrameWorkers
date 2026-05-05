"""Compositor service — FFmpeg-based video+audio mux with subtitle burn-in.

Composes a final deliverable MP4 from:
  - Video track (MP4)
  - Audio track (WAV)
  - Subtitle file (SRT, optional)
  - Composition plan (color grade — applied via ffmpeg eq filter)
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


    async def compose_slideshow(
        self,
        *,
        images_with_durations: list[tuple[str, float]],
        audio_path: str = "",
        subtitle_srts: list[str] | None = None,
        plan: dict[str, Any] | None = None,
        target_fps: int = 30,
    ) -> bytes:
        """Compose a slideshow video: still-image sequence + audio + subtitles.

        Pipeline:
          1. ffmpeg concat demuxer on the (image, duration) list → a
             silent slideshow mp4 at ``target_fps``. Images are force-
             scaled/padded to the plan's ``output_resolution`` so a run
             with mixed image dimensions still renders cleanly.
          2. Delegate to ``self.compose()`` using the intermediate
             slideshow as ``video_path`` — reuses audio mux, subtitle
             burn-in, color grade from the existing pipeline with zero
             duplication.
        """
        real_entries = [
            (p, float(d)) for (p, d) in images_with_durations
            if p and os.path.isfile(p) and float(d) > 0
        ]
        if not real_entries:
            logger.warning(
                "CompositorService.compose_slideshow: no usable "
                "(image, duration) pairs — returning mock bytes",
            )
            return MOCK_MP4_HEADER

        ffmpeg_bin = shutil.which("ffmpeg")
        if not ffmpeg_bin:
            logger.warning(
                "CompositorService.compose_slideshow: ffmpeg not found",
            )
            return MOCK_MP4_HEADER

        plan = plan or {}
        resolution = str(plan.get("output_resolution", "1920x1080"))
        try:
            width, height = [int(x) for x in resolution.lower().split("x", 1)]
        except Exception:
            width, height = 1920, 1080

        temp_dir = tempfile.mkdtemp(prefix="fw_slideshow_")
        filelist_path = os.path.join(temp_dir, "filelist.txt")
        slideshow_path = os.path.join(temp_dir, "slideshow.mp4")

        try:
            # Write ffmpeg concat demuxer filelist. Per the concat format:
            # each image needs a ``file`` line + a ``duration`` line; the
            # LAST image also needs to be repeated WITHOUT a duration
            # because concat ignores the trailing duration otherwise.
            with open(filelist_path, "w", encoding="utf-8") as fh:
                for i, (img_path, dur) in enumerate(real_entries):
                    fh.write(f"file {_quote_ffmpeg_path(img_path)}\n")
                    fh.write(f"duration {dur:.3f}\n")
                # Repeat last file without duration per the concat spec.
                fh.write(f"file {_quote_ffmpeg_path(real_entries[-1][0])}\n")

            # Exact total duration so ffmpeg doesn't stretch the trailing
            # ``file <last>`` repeat beyond its stated segment slot. The
            # concat demuxer's default-1s behavior for stills without a
            # duration line was previously padding the output to
            # (sum(durations) + 1s * last-repeat + rounding) ≈ +13s of
            # freeze-frame. ``-t`` caps cleanly to the narrator timeline.
            total_seconds = sum(d for _, d in real_entries)
            scale_filter = (
                f"scale={width}:{height}:force_original_aspect_ratio="
                f"decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:"
                f"color=black,setsar=1,fps={target_fps},format=yuv420p"
            )
            cmd = [
                ffmpeg_bin, "-y",
                "-f", "concat", "-safe", "0",
                "-i", filelist_path,
                "-vf", scale_filter,
                "-vsync", "cfr",
                "-t", f"{total_seconds:.3f}",
                "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                "-movflags", "+faststart",
                slideshow_path,
            ]
            proc = subprocess.run(
                cmd, capture_output=True, check=False, text=True, timeout=600,
            )
            if proc.returncode != 0 or not os.path.exists(slideshow_path):
                logger.warning(
                    "compose_slideshow ffmpeg concat failed (code=%s): %s",
                    proc.returncode, (proc.stderr or "").strip()[-500:],
                )
                return MOCK_MP4_HEADER

            # Delegate audio mux + subtitle burn-in to the existing
            # compose() pipeline — keeps all FFmpeg logic in one place.
            return await self.compose(
                video_path=slideshow_path,
                audio_path=audio_path,
                subtitle_srts=subtitle_srts,
                plan=plan,
            )

        except Exception as exc:
            logger.warning("compose_slideshow error: %s", exc)
            return MOCK_MP4_HEADER
        finally:
            for p in [filelist_path, slideshow_path]:
                if p and os.path.exists(p):
                    try:
                        os.remove(p)
                    except OSError:
                        pass
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except OSError:
                pass


def _quote_ffmpeg_path(p: str) -> str:
    """Wrap a path in single quotes for ffmpeg's concat demuxer, escaping
    embedded single quotes with the '\\''-ish dance concat expects."""
    escaped = p.replace("'", "'\\''")
    return f"'{escaped}'"


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

    async def compose_slideshow(
        self,
        *,
        images_with_durations: list[tuple[str, float]],
        audio_path: str = "",
        subtitle_srts: list[str] | None = None,
        plan: dict[str, Any] | None = None,
        target_fps: int = 30,
    ) -> bytes:
        logger.info(
            "[MockCompositor] Placeholder compose_slideshow for %d images",
            len(images_with_durations),
        )
        return MOCK_MP4_HEADER
