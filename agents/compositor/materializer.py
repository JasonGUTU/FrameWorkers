"""Compositor materializer — executes composition plan via FFmpeg.

Reads the LLM-planned composition spec (color grade, subtitle burn-in)
and muxes video + audio + subtitles into a final deliverable MP4 using
FFmpeg.
"""

from __future__ import annotations

import logging
from typing import Any, TYPE_CHECKING

from ..descriptor import BaseMaterializer, MediaAsset
from inference.generation._srt import segments_to_srt
from inference.generation.compositor_service import CompositorService

if TYPE_CHECKING:
    from ..base_agent import MaterializeContext
    from .schema import CompositorAgentInput

logger = logging.getLogger(__name__)


def _extract_srt_texts(sub_data: Any) -> list[str]:
    """Return one or more SRT blobs from any shape routed to ``subtitle_tracks``.

    The ``subtitle_tracks`` collection label is the single rendezvous
    point for every producer of burnable captions. This extractor
    accepts all the shapes that can legitimately show up there, in
    priority order:

      1. ``TranslationAgent`` output — tracks live at
         ``content.translated_payload.content.tracks[*].srt_text``.
         Translation preserves the upstream shape under a
         ``translated_payload`` wrapper so a translated SRT remains an
         SRT; without peeling the wrapper first a bilingual flow
         silently collapses to monolingual.
      2. ``NarratorAgent`` SRT envelope OR legacy ``SubtitleAgent``
         output — tracks live at ``content.tracks[*].srt_text``.
      3. ``TranscriptionAgent`` output — ``content.segments`` carries
         raw per-line timestamps + text; render to SRT here via the
         shared ``segments_to_srt`` helper (pure Python, no LLM — this
         is why SubtitleAgent is no longer a separate step: once
         dialogue is baked into the rendered clips, the ASR segments
         ARE the source of truth for what the viewer hears).
      4. A raw ``srt_text`` field at the top of ``content`` (plain-
         SRT producers).
    """
    if not isinstance(sub_data, dict):
        return []
    content = sub_data.get("content", sub_data) or {}
    if not isinstance(content, dict):
        return []

    # 1. Translated wrapper — peel and recurse on the inner document.
    translated = content.get("translated_payload")
    if isinstance(translated, dict):
        inner_srts = _extract_srt_texts(translated)
        if inner_srts:
            return inner_srts

    # 2. tracks[].srt_text (NarratorAgent / legacy SubtitleAgent shape).
    tracks = content.get("tracks")
    if isinstance(tracks, list):
        out: list[str] = []
        for track in tracks:
            if isinstance(track, dict):
                srt = str(track.get("srt_text") or "").strip()
                if srt:
                    out.append(srt)
        if out:
            return out

    # 3. TranscriptionAgent shape — segments[{start_time, end_time, text}].
    segments = content.get("segments")
    if isinstance(segments, list) and segments:
        rendered = segments_to_srt(segments).strip()
        if rendered:
            return [rendered]

    # 4. Raw srt_text at top of content.
    raw_srt = str(content.get("srt_text") or "").strip()
    if raw_srt:
        return [raw_srt]

    return []


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
            subtitle_srts.extend(_extract_srt_texts(sub_data))

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
                raise RuntimeError(
                    "CompositorMaterializer: slideshow mode but no "
                    "(image, duration) pairs could be built from "
                    "segment_timing — illustration_image_paths and "
                    "segment_timing_json_text are inconsistent or empty"
                )
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
            # Composition failure with valid inputs is structural, not
            # transient — raise so the outer run loop sees the failure.
            raise RuntimeError(
                "CompositorMaterializer: compose returned empty bytes"
            )

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
