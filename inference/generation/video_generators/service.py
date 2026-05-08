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

from .._mock_data import MOCK_MP4_HEADER
from ..fal_helpers import (
    LazyHttpxClientMixin,
    ensure_fal_runtime_env_loaded,
    extract_fal_media_url,
    fal_subscribe,
    http_download_bytes,
    require_fal_model_var,
)
from ..wavespeed_predict import (
    wavespeed_download_video,
    wavespeed_poll_until_done,
    wavespeed_submit_image_to_video,
    wavespeed_submit_text_to_video,
)
from .types import ShotSemanticContext, VideoClipResult

logger = logging.getLogger(__name__)

# Keys in the fal API ``arguments`` dict that carry base64 image data URLs.
# Stripped before recording the submitted payload in ``VideoClipResult.resolved_payload``
# so audit logs don't balloon with inline image bytes.
_FAL_IMAGE_PAYLOAD_KEYS: frozenset[str] = frozenset(
    {"image_url", "image_urls", "start_image_url", "end_image_url", "tail_image_url"}
)


class VideoService:
    """Abstract video generation service.

    Concrete implementations accept either:

    * ``semantic_context``: a ``ShotSemanticContext`` describing the shot
      in model-neutral language. The service is responsible for turning
      it into a backend-specific text prompt and structured payload.
    * ``prompt``: a pre-composed text prompt string (legacy / direct
      path, used by callers that don't go through ``ShotSemanticContext``
      — e.g. the UniVA video materializer and the smoke scripts).

    When both are provided, ``semantic_context`` takes precedence.
    """

    async def generate_clip(
        self,
        *,
        shot_id: str,
        keyframe_images: list[bytes],
        prompt: str = "",
        semantic_context: ShotSemanticContext | None = None,
        duration_sec: float = 0.0,
        fps: int = 24,
        width: int = 1024,
        height: int = 576,
        **kwargs: Any,
    ) -> VideoClipResult:
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

    async def extract_last_frame(self, video_path: str) -> bytes:
        """Extract the last frame from a video file as PNG bytes.

        Uses ffmpeg to seek to the last frame and output a single PNG.
        """
        ffmpeg_bin = shutil.which("ffmpeg")
        if not ffmpeg_bin or not os.path.isfile(video_path):
            logger.warning("extract_last_frame: ffmpeg or video not available")
            return b""

        with tempfile.TemporaryDirectory(prefix="fw_lastframe_") as tmp_dir:
            out_path = Path(tmp_dir) / "last_frame.png"
            proc = subprocess.run(
                [
                    ffmpeg_bin, "-y",
                    "-sseof", "-0.1",
                    "-i", video_path,
                    "-frames:v", "1",
                    "-update", "1",
                    str(out_path),
                ],
                capture_output=True, check=False, text=True, timeout=30,
            )
            if proc.returncode == 0 and out_path.exists():
                return out_path.read_bytes()
            logger.warning("extract_last_frame failed: %s", (proc.stderr or "").strip()[-200:])
            return b""

    async def clip_segment(
        self, video_path: str, start: float, end: float,
    ) -> bytes:
        """Extract a segment [start, end] from a video file.

        Returns the clipped MP4 bytes.
        """
        ffmpeg_bin = shutil.which("ffmpeg")
        if not ffmpeg_bin or not os.path.isfile(video_path):
            logger.warning("clip_segment: ffmpeg or video not available")
            return b""

        duration = end - start
        if duration <= 0:
            return b""

        with tempfile.TemporaryDirectory(prefix="fw_clip_") as tmp_dir:
            out_path = Path(tmp_dir) / "clip.mp4"
            proc = subprocess.run(
                [
                    ffmpeg_bin, "-y",
                    "-ss", f"{start:.3f}",
                    "-i", video_path,
                    "-t", f"{duration:.3f}",
                    "-c", "copy",
                    "-movflags", "+faststart",
                    str(out_path),
                ],
                capture_output=True, check=False, text=True, timeout=60,
            )
            if proc.returncode == 0 and out_path.exists():
                return out_path.read_bytes()
            logger.warning("clip_segment failed: %s", (proc.stderr or "").strip()[-200:])
            return b""

    async def concat_clips(self, clip_bytes_list: list[bytes]) -> bytes:
        """Concatenate clip bytes into a single MP4."""
        return await self._concat_mp4_segments(clip_bytes_list, label="highlight")

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
        semantic_context: ShotSemanticContext | None = None,
        duration_sec: float = 0.0,
        fps: int = 24,
        width: int = 1024,
        height: int = 576,
        **kwargs: Any,
    ) -> VideoClipResult:
        logger.info(
            "[MockVideoService] Generating placeholder clip for %s (%.1fs)",
            shot_id,
            duration_sec,
        )
        return VideoClipResult(bytes=MOCK_MP4_HEADER, resolved_prompt=prompt)

    async def assemble_scene(
        self,
        *,
        scene_id: str,
        clip_bytes_list: list[bytes],
        transitions: list[dict[str, Any]] | None = None,
    ) -> bytes:
        logger.info("[MockVideoService] Assembling scene %s", scene_id)
        return MOCK_MP4_HEADER

    async def assemble_final(
        self,
        *,
        scene_bytes_list: list[bytes],
    ) -> bytes:
        logger.info("[MockVideoService] Assembling final video")
        return MOCK_MP4_HEADER

    async def extract_last_frame(self, video_path: str) -> bytes:
        from .._mock_data import MOCK_PNG
        logger.info("[MockVideoService] Placeholder last frame for %s", video_path)
        return MOCK_PNG

    async def clip_segment(self, video_path: str, start: float, end: float) -> bytes:
        logger.info("[MockVideoService] Placeholder clip %.1f-%.1f", start, end)
        return MOCK_MP4_HEADER

    async def concat_clips(self, clip_bytes_list: list[bytes]) -> bytes:
        logger.info("[MockVideoService] Placeholder concat %d clips", len(clip_bytes_list))
        return MOCK_MP4_HEADER


class FalVideoService(VideoService, LazyHttpxClientMixin):
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

    @staticmethod
    def _is_fal_kling_model(model: str) -> bool:
        return "kling-video" in model

    async def generate_clip(
        self,
        *,
        shot_id: str,
        keyframe_images: list[bytes],
        prompt: str = "",
        semantic_context: ShotSemanticContext | None = None,
        duration_sec: float = 0.0,
        fps: int = 24,
        width: int = 1024,
        height: int = 576,
        **kwargs: Any,
    ) -> VideoClipResult:
        logger.info("[fal.ai] Generating video shot=%s model=%s", shot_id, self.model)

        image_data_urls: list[str] = [
            f"data:image/png;base64,{base64.b64encode(img).decode('utf-8')}"
            for img in (keyframe_images or [])
        ]

        # Compose the text prompt. ``semantic_context`` wins over ``prompt``
        # when both are provided; falling back to ``prompt`` keeps the legacy
        # path working for callers that build prompts themselves (UniVA
        # video materializer, smoke scripts).
        if semantic_context is not None:
            composed_prompt = self._compose_prompt(
                semantic_context,
                anchor_image_count=len(image_data_urls),
            )
        else:
            composed_prompt = prompt

        if self._is_fal_kling_model(self.model):
            arguments = self._build_kling_arguments(
                prompt=composed_prompt,
                shot_id=shot_id,
                image_data_urls=image_data_urls,
                duration_sec=duration_sec,
                kwargs=kwargs,
            )
        else:
            arguments = self._build_default_arguments(
                prompt=composed_prompt,
                shot_id=shot_id,
                image_data_urls=image_data_urls,
                duration_sec=duration_sec,
                fps=fps,
                width=width,
                height=height,
                kwargs=kwargs,
            )

        # Pack entity-anchor consistency constraints into the fal payload
        # when this model endpoint advertises a slot for it. This is the
        # single place in the codebase that knows fal's literal field names.
        if semantic_context is not None and self.structured_constraints_field:
            arguments[self.structured_constraints_field] = self._pack_fal_constraints(
                semantic_context
            )

        result = await self._submit(arguments)
        video_url = extract_fal_media_url(result, media_type="video")
        clip_bytes = await self._download_binary(video_url)

        # Build an audit-friendly view of the submitted payload. Strips
        # inline base64 image data URLs so the persisted record doesn't
        # balloon with megabytes of binary.
        resolved_payload: dict[str, Any] = {
            k: v for k, v in arguments.items() if k not in _FAL_IMAGE_PAYLOAD_KEYS
        }
        return VideoClipResult(
            bytes=clip_bytes,
            resolved_prompt=composed_prompt,
            resolved_payload=resolved_payload,
        )

    # Test seams: tests/agents/test_media_materializers.py overrides these
    # to capture submitted arguments and stub network I/O without monkey-
    # patching module globals. Keep them as 1-line wrappers.

    async def _submit(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return await fal_subscribe(self._api_key, self.model, arguments)

    async def _download_binary(self, url: str) -> bytes:
        return await http_download_bytes(self.http, url)

    # ------------------------------------------------------------------
    # Argument builders (split per model family so generate_clip stays
    # readable; a future provider-specific subclass can override one of
    # these without touching the rest of the pipeline).
    # ------------------------------------------------------------------

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

    def _build_kling_arguments(
        self,
        *,
        prompt: str,
        shot_id: str,
        image_data_urls: list[str],
        duration_sec: float,
        kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        arguments: dict[str, Any] = {"prompt": prompt}

        source_video_url = kwargs.get("source_video_url")
        if isinstance(source_video_url, str) and source_video_url:
            arguments["video_url"] = source_video_url

        arguments["duration"] = self._kling_duration_enum(
            duration_sec if duration_sec > 0 else 5.0
        )

        kling_dual_anchor = False
        if len(image_data_urls) >= 2 and self._kling_uses_start_end_frame_fields(self.model):
            arguments["start_image_url"] = image_data_urls[0]
            arguments["end_image_url"] = image_data_urls[-1]
            kling_dual_anchor = True
            logger.info(
                "[fal.ai] Kling start/end frames for shot=%s (%d anchors -> 2)",
                shot_id,
                len(image_data_urls),
            )
        elif len(image_data_urls) >= 2:
            arguments["image_url"] = image_data_urls[0]
            arguments["tail_image_url"] = image_data_urls[-1]
            kling_dual_anchor = True
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

        # generate_audio policy (Kling 2.6 Pro and newer produce dialogue +
        # foley baked into the mp4 when enabled — this is load-bearing for
        # the whole "Kling-atomic dialogue+foley" architecture). Default is
        # ON, overridable per-call via kwargs and globally via the
        # ``FAL_VIDEO_GENERATE_AUDIO`` env var (set to "0"/"false" for
        # emergency kill-switch). Dual-anchor still defaults OFF because
        # Kling rejects end_image_url + audio together.
        if "generate_audio" in kwargs:
            arguments["generate_audio"] = bool(kwargs["generate_audio"])
        elif kling_dual_anchor:
            arguments["generate_audio"] = False
        else:
            env_flag = (os.getenv("FAL_VIDEO_GENERATE_AUDIO", "true") or "").strip().lower()
            arguments["generate_audio"] = env_flag not in {"0", "false", "no", "off"}

        return arguments

    def _build_default_arguments(
        self,
        *,
        prompt: str,
        shot_id: str,
        image_data_urls: list[str],
        duration_sec: float,
        fps: int,
        width: int,
        height: int,
        kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        arguments: dict[str, Any] = {"prompt": prompt}

        source_video_url = kwargs.get("source_video_url")
        if isinstance(source_video_url, str) and source_video_url:
            arguments["video_url"] = source_video_url

        # NOTE: structured consistency constraints are injected at the top
        # of ``generate_clip`` from ``semantic_context`` (via
        # ``_pack_fal_constraints``) — not here. This keeps fal's literal
        # field names out of every argument builder.

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
        elif image_data_urls:
            arguments["image_url"] = image_data_urls[0]

        return arguments

    # ------------------------------------------------------------------
    # Semantic context → fal prompt / payload
    #
    # The two methods below are the *only* places in the repo that know
    # how to translate a language-neutral ``ShotSemanticContext`` into
    # this model family's expected inputs — specifically fal's
    # task-first text prompt templating and the literal
    # ``entity_anchor_constraints`` payload shape. Nothing in the agents
    # layer constructs these strings.
    # ------------------------------------------------------------------

    def _compose_prompt(
        self,
        ctx: ShotSemanticContext,
        *,
        anchor_image_count: int,
    ) -> str:
        """Render a ShotSemanticContext into a fal-flavored I2V text prompt.

        Encodes the prompt templating decisions this model family expects:
        task-first ordering, ``" | "`` section separators, scene-tone
        omission when an explicit motion hint prefix is present, and the
        per-shot ``"Ref:"`` line that signals to the model the attached
        still is look-consistency-only.
        """
        vmh0 = (
            ctx.video_motion_hints[0].strip()
            if ctx.video_motion_hints
            else ""
        )
        motion_active = bool(vmh0)
        omit_scene_tone_blocks = motion_active

        parts: list[str] = [f"Shot {ctx.shot_id}"]
        # Dialogue + emotion go right after the shot header so Kling's
        # speech-synthesis branch sees the line before the visual details.
        # The verbatim line is quoted to mark "say exactly this". Empty
        # dialogue_text skips the clause (action-only shots produce foley
        # only, no speech).
        if ctx.dialogue_text.strip():
            tone = ctx.emotion_hint.strip()
            tone_suffix = f", delivered in a {tone} tone" if tone else ""
            parts.append(
                "DIALOGUE: the character on-screen speaks aloud the "
                "following line, lips in visible sync with each syllable: "
                f"\u300c{ctx.dialogue_text.strip()}\u300d"
                f"{tone_suffix}. AUDIO-ONLY \u2014 do NOT render this line "
                f"as on-screen text, caption, subtitle, or chyron; the "
                f"viewer must HEAR it, not SEE it written."
            )
        # Language directive \u2014 when set, force ALL voiced content (the
        # explicit dialogue line AND any ambient voices the model may
        # auto-generate on action shots) into a single language. Without
        # this, Kling defaults to its English training prior on action
        # shots, producing English battle cries inside e.g. a Three-
        # Kingdoms setting. See ShotSemanticContext.language docstring.
        if ctx.language.strip():
            parts.append(
                f"LANGUAGE: all voiced content in this shot \u2014 both spoken "
                f"dialogue and any ambient voices, shouts, or battle cries \u2014 "
                f"must be in language code '{ctx.language.strip()}'. Do NOT "
                f"emit voices in any other language."
            )
        # Global no-on-screen-text directive. Kling 2.6 Pro empirically
        # burns dialogue text into the frame as a caption when the prompt
        # mentions a spoken line \u2014 and even on action shots can render
        # location names / chyrons. CompositorAgent owns subtitle burn-in
        # at the FINAL stage; per-shot mp4s must come back text-free so
        # they don't double-stack.
        parts.append(
            "NO_ON_SCREEN_TEXT: this clip must contain ZERO rendered "
            "text, captions, subtitles, signs, chyrons, or any other "
            "graphic text in the frame. Spoken / voiced content stays "
            "audio-only."
        )
        if omit_scene_tone_blocks:
            parts.append(
                "Ref: one L3 still for look; motion from text prefix + below."
            )
        else:
            parts.append(
                "Visual reference: a single Layer-3 shot still "
                "(composition, cast, props); use it for look consistency "
                "only — motion/timing follow this text prompt."
            )
        if ctx.shot_type:
            parts.append(f"Type: {ctx.shot_type}")
        if ctx.visual_goal:
            parts.append(f"Visual goal: {ctx.visual_goal}")
        if ctx.action_focus:
            parts.append(f"Action focus: {ctx.action_focus}")
        if ctx.characters_in_frame:
            parts.append(
                "Characters in frame: " + ", ".join(ctx.characters_in_frame)
            )
        if ctx.location_id or ctx.time_of_day:
            scene_bits: list[str] = []
            if ctx.location_id:
                scene_bits.append(f"location_id={ctx.location_id}")
            if ctx.time_of_day:
                scene_bits.append(f"time_of_day={ctx.time_of_day}")
            parts.append("Scene context: " + ", ".join(scene_bits))
        if not omit_scene_tone_blocks and ctx.environment_notes:
            parts.append(
                "Scene environment notes: " + " || ".join(ctx.environment_notes)
            )
        if not omit_scene_tone_blocks and ctx.style_notes:
            parts.append("Scene style notes: " + " || ".join(ctx.style_notes))
        if not omit_scene_tone_blocks and ctx.must_avoid:
            parts.append("Scene must avoid: " + " || ".join(ctx.must_avoid))
        if ctx.camera_angle or ctx.camera_movement:
            camera_bits: list[str] = []
            if ctx.camera_angle:
                camera_bits.append(f"angle={ctx.camera_angle}")
            if ctx.camera_movement:
                camera_bits.append(f"movement={ctx.camera_movement}")
            parts.append("Camera: " + ", ".join(camera_bits))
        if ctx.framing_notes:
            parts.append(f"Framing notes: {ctx.framing_notes}")
        parts.append(f"Anchor images: {anchor_image_count}")
        if ctx.action_focus and not omit_scene_tone_blocks:
            parts.append(
                "Task focus: in this scene, complete this shot action: "
                + ctx.action_focus
            )

        body = " | ".join(parts)
        if motion_active:
            body = vmh0 + " | " + body
        return body

    def _pack_fal_constraints(
        self,
        ctx: ShotSemanticContext,
    ) -> dict[str, Any]:
        """Pack a ShotSemanticContext into this fal model's entity-anchor
        consistency-constraint payload shape.

        This is the single place in the codebase that knows the literal
        fal field names (``consistency_type`` / ``keyframe_role`` / etc.).
        """
        return {
            "shot_id": ctx.shot_id,
            "consistency_type": "entity_anchor_constraints",
            "keyframe_role": "shot_still_l3_only",
            "characters_in_frame": list(ctx.characters_in_frame),
            "scene_context": {
                "scene_id": ctx.scene_id,
                "location_id": ctx.location_id,
                "time_of_day": ctx.time_of_day,
                "environment_notes": list(ctx.environment_notes),
                "style_notes": list(ctx.style_notes),
                "must_avoid": list(ctx.must_avoid),
            },
            "visual_goal": ctx.visual_goal,
            "action_focus": ctx.action_focus,
            "camera": {
                "angle": ctx.camera_angle,
                "movement": ctx.camera_movement,
                "framing_notes": ctx.framing_notes,
            },
            "storyboard_keyframe_notes": list(ctx.keyframe_notes),
            "keyframe_prompt_summaries": list(ctx.keyframe_prompt_summaries),
            "keyframe_video_motion_hints": list(ctx.video_motion_hints),
        }


class WavespeedVideoService(VideoService, LazyHttpxClientMixin):
    """Video generation via WaveSpeed.ai (UniVA-compatible T2V / I2V endpoints)."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        provider: str | None = None,
        t2v_model: str | None = None,
        i2v_model: str | None = None,
        aspect_ratio: str | None = None,
        timeout: float = 300.0,
        poll_interval_sec: float = 2.0,
    ) -> None:
        ensure_fal_runtime_env_loaded()
        self._api_key = (api_key or os.getenv("WAVESPEED_API_KEY", "")).strip()
        if not self._api_key:
            raise RuntimeError(
                "WAVESPEED_API_KEY is required for WavespeedVideoService. "
                "Set it in `.env` (see `.env.example`) or pass api_key=..."
            )
        self.provider = (provider or os.getenv("WAVESPEED_VIDEO_PROVIDER", "bytedance")).strip()
        self.t2v_model = (
            t2v_model or os.getenv("WAVESPEED_VIDEO_T2V_MODEL", "seedance-v1-pro-t2v-480p")
        ).strip()
        self.i2v_model = (
            i2v_model or os.getenv("WAVESPEED_VIDEO_I2V_MODEL", "seedance-v1-pro-i2v-480p")
        ).strip()
        self.aspect_ratio = (
            aspect_ratio or os.getenv("WAVESPEED_VIDEO_ASPECT_RATIO", "16:9")
        ).strip()
        self.timeout = timeout
        self.poll_interval_sec = poll_interval_sec
        self._http: httpx.AsyncClient | None = None

    @staticmethod
    def _duration_int(duration_sec: float) -> int:
        """Many Seedance-style endpoints accept 5 or 10 second clips."""
        return 10 if float(duration_sec) > 5.5 else 5

    async def generate_clip(
        self,
        *,
        shot_id: str,
        keyframe_images: list[bytes],
        prompt: str = "",
        semantic_context: ShotSemanticContext | None = None,
        duration_sec: float = 0.0,
        fps: int = 24,
        width: int = 1024,
        height: int = 576,
        **kwargs: Any,
    ) -> VideoClipResult:
        del fps, width, height  # WaveSpeed payload uses fixed profile per model
        # WaveSpeed's current integration does not yet consume the semantic
        # context — callers pass a pre-composed ``prompt``. If semantic_context
        # is supplied alongside an empty prompt, ignore it (until a renderer
        # is added) rather than crashing, so legacy and new callers both work.
        del semantic_context
        dur = self._duration_int(duration_sec if duration_sec > 0 else 5.0)
        logger.info(
            "[wavespeed] Generating video shot=%s provider=%s t2v=%s i2v=%s",
            shot_id,
            self.provider,
            self.t2v_model,
            self.i2v_model,
        )
        client = self.http
        if keyframe_images:
            request_id = await wavespeed_submit_image_to_video(
                client,
                self._api_key,
                provider=self.provider,
                model=self.i2v_model,
                prompt=prompt,
                image_png_or_jpeg=keyframe_images[0],
                duration=dur,
            )
            resolved_payload = {
                "provider": self.provider,
                "model": self.i2v_model,
                "duration": dur,
                "mode": "i2v",
            }
        else:
            request_id = await wavespeed_submit_text_to_video(
                client,
                self._api_key,
                provider=self.provider,
                model=self.t2v_model,
                prompt=prompt,
                aspect_ratio=self.aspect_ratio,
                duration=dur,
            )
            resolved_payload = {
                "provider": self.provider,
                "model": self.t2v_model,
                "duration": dur,
                "aspect_ratio": self.aspect_ratio,
                "mode": "t2v",
            }
        out_url = await wavespeed_poll_until_done(
            client,
            self._api_key,
            request_id,
            poll_interval_sec=self.poll_interval_sec,
            timeout_sec=self.timeout,
        )
        clip_bytes = await wavespeed_download_video(client, out_url)
        return VideoClipResult(
            bytes=clip_bytes,
            resolved_prompt=prompt,
            resolved_payload=resolved_payload,
        )
