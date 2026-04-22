"""Compositor materializer — executes composition plan via FFmpeg.

Reads the LLM-planned composition spec (transitions, color grade,
subtitle burn-in) and muxes video + audio + subtitles into a final
deliverable MP4 using FFmpeg.
"""

from __future__ import annotations

import logging
from typing import Any, TYPE_CHECKING

from ..descriptor import BaseMaterializer, MediaAsset
from inference.generation.compositor_service import CompositorService

if TYPE_CHECKING:
    from ..base_agent import MaterializeContext
    from .schema import CompositorAgentInput

logger = logging.getLogger(__name__)


def _extract_subtitle_tracks(sub_data: Any) -> list[dict]:
    """Return the subtitle ``tracks`` list from whatever upstream shape.

    Directly-routed artifacts and translated artifacts travel the same
    ``subtitle_tracks`` collection label, so InputResolver hands this
    materializer either:

      * A ``SubtitleAgent`` output — tracks live at ``content.tracks``.
      * A ``TranslationAgent`` output — tracks live at
        ``content.translated_payload.content.tracks`` (translation
        preserves the upstream shape under a ``translated_payload``
        wrapper so the consumer sees the original document, just
        translated).

    Translation output gets peeled first: an ``en`` SRT handed in wrapped
    as ``{content: {translated_payload: <SubtitleAgent>}}`` would
    otherwise silently contribute zero tracks under a naive
    ``content.tracks`` read and collapse bilingual flows to monolingual.
    """
    if not isinstance(sub_data, dict):
        return []
    content = sub_data.get("content", sub_data) or {}
    if not isinstance(content, dict):
        return []
    translated = content.get("translated_payload")
    if isinstance(translated, dict):
        inner = translated.get("content", translated) or {}
        if isinstance(inner, dict):
            inner_tracks = inner.get("tracks")
            if isinstance(inner_tracks, list) and inner_tracks:
                return inner_tracks
    tracks = content.get("tracks")
    return tracks if isinstance(tracks, list) else []


class CompositorMaterializer(BaseMaterializer):
    """Compose final video from video + audio + subtitle inputs."""

    def __init__(self, compositor_service: CompositorService) -> None:
        self.svc = compositor_service

    async def materialize(
        self,
        ctx: "MaterializeContext",
        asset_dict: dict[str, Any],
    ) -> list[MediaAsset]:
        typed_input: CompositorAgentInput = ctx.typed_input
        content = asset_dict.get("content", {})
        plan = content.get("plan", {})

        # Local uri_holder — the persisted content JSON has no asset block;
        # ArtifactWriter still needs a dict to stamp uri into for ArtifactRef.
        uri_holder: dict[str, Any] = {}

        # Flatten each subtitle artifact (each artifact may itself carry
        # one or more tracks under content.tracks[*].srt_text) into the
        # list of SRT blobs ffmpeg will stack. Bilingual / multilingual
        # flows pass one artifact per language via the collection label.
        import json

        subtitle_srts: list[str] = []
        for raw_sub in typed_input.subtitle_json_texts:
            if not raw_sub:
                continue
            try:
                sub_data = json.loads(raw_sub)
            except (json.JSONDecodeError, TypeError):
                # Raw SRT body passed as plain text (fallback).
                text = raw_sub.strip()
                if text:
                    subtitle_srts.append(text)
                continue
            for track in _extract_subtitle_tracks(sub_data):
                if not isinstance(track, dict):
                    continue
                srt = (track.get("srt_text") or "").strip()
                if srt:
                    subtitle_srts.append(srt)

        # --- Slideshow-mode branch ---
        # Route decision: illustration_image_paths populated ⇒ we are in
        # illustrated-storytelling mode, build the video track by ffmpeg
        # concat'ing images with per-segment durations. The LLM prompt
        # already rejects mutually-ambiguous inputs (both video_file_path
        # AND illustration_image_paths present), so reaching here with a
        # populated list means this is the intended branch.
        if typed_input.illustration_image_paths:
            images_with_durations = _pair_images_with_durations(
                typed_input.illustration_image_paths,
                typed_input.segment_timing_json_text,
            )
            if not images_with_durations:
                logger.warning(
                    "CompositorMaterializer: slideshow mode but no "
                    "(image, duration) pairs could be built from segment_timing"
                )
                return []
            result_bytes = await self.svc.compose_slideshow(
                images_with_durations=images_with_durations,
                audio_path=typed_input.audio_file_path,
                subtitle_srts=subtitle_srts,
                plan=plan,
            )
        else:
            result_bytes = await self.svc.compose(
                video_path=typed_input.video_file_path,
                audio_path=typed_input.audio_file_path,
                subtitle_srts=subtitle_srts,
                plan=plan,
            )

        if not result_bytes:
            logger.warning("CompositorMaterializer: compose returned empty bytes")
            return []

        return [MediaAsset(
            sys_id="compositor_final",
            data=result_bytes,
            extension="mp4",
            uri_holder=uri_holder,
        )]


def _pair_images_with_durations(
    image_paths: list[str], segment_timing_json_text: str,
) -> list[tuple[str, float]]:
    """Zip illustration paths (ordered by segment) with per-segment durations.

    ``segment_timing_json_text`` is the JSON payload NarratorAgent
    emits — ``content.segment_timings = [{segment_id, duration_sec,
    ...}]`` in segment order. We match by ordinal index (path 0 ↔
    segment_timings[0]), not by segment_id text, because descriptor-side
    ``_sort_image_paths_by_segment`` already put the paths in seg_NNN
    order and NarratorAgent emits segment_timings in the same order.
    Length mismatch is tolerated: extra paths fall back to a 3-second
    default, extra timings are ignored.
    """
    import json
    DEFAULT_DUR_SEC = 3.0

    try:
        timing = json.loads(segment_timing_json_text or "{}")
    except Exception:
        timing = {}
    content = timing.get("content", timing) if isinstance(timing, dict) else {}
    segment_timings = (
        content.get("segment_timings", [])
        if isinstance(content, dict) else []
    )

    durations: list[float] = []
    for st in segment_timings:
        if not isinstance(st, dict):
            continue
        dur = float(st.get("duration_sec", 0.0) or 0.0)
        durations.append(dur if dur > 0 else DEFAULT_DUR_SEC)

    pairs: list[tuple[str, float]] = []
    for i, path in enumerate(image_paths):
        dur = durations[i] if i < len(durations) else DEFAULT_DUR_SEC
        pairs.append((path, dur))
    return pairs
