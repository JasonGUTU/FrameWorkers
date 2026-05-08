"""Highlight materializer — clips and compiles highlight segments.

Reads the LLM-selected clip list, extracts each segment from the source
video, and concatenates them into a highlight reel.
"""

from __future__ import annotations

import logging
from typing import Any, TYPE_CHECKING

from ..descriptor import BaseMaterializer, MediaAsset
from inference.generation.video_generators.service import VideoService

if TYPE_CHECKING:
    from ..base_agent import MaterializeContext
    from .schema import HighlightAgentInput

logger = logging.getLogger(__name__)


def _merge_overlapping_clips(
    raw_clips: list[dict],
) -> tuple[list[tuple[float, float]], int]:
    """Sort + merge LLM-selected highlight intervals on the source timeline.

    The HighlightAgent's system_prompt instructs the LLM that "clips
    should not overlap", but offers no enforcement; the LLM empirically
    produces overlapping bounds (e.g. ``[(5, 12), (10, 18)]``) in a
    nontrivial fraction of runs because the same standout moment gets
    bracketed twice. Without merging, the materializer cuts each interval
    independently and concatenates them — the viewer then sees the same
    source frames replayed back-to-back.

    Returns ``(merged_intervals, n_dropped)``: ``merged_intervals`` is
    sorted, non-overlapping, and ``n_dropped`` counts how many input
    intervals were folded away (so the caller can log the fix).
    Intervals with ``end <= start`` or non-numeric bounds are silently
    skipped here — the caller already had to filter such bad rows.
    """
    intervals: list[tuple[float, float]] = []
    for clip in raw_clips:
        try:
            start = float(clip.get("start_time", 0) or 0)
            end = float(clip.get("end_time", 0) or 0)
        except (TypeError, ValueError):
            continue
        if end <= start:
            continue
        intervals.append((start, end))
    intervals.sort()

    merged: list[tuple[float, float]] = []
    for start, end in intervals:
        if merged and start <= merged[-1][1]:
            prev_start, prev_end = merged[-1]
            merged[-1] = (prev_start, max(prev_end, end))
        else:
            merged.append((start, end))
    return merged, len(intervals) - len(merged)


class HighlightMaterializer(BaseMaterializer):
    """Clip and compile highlight segments via video service."""

    def __init__(self, video_service: VideoService) -> None:
        self.svc = video_service

    async def materialize(
        self,
        ctx: "MaterializeContext",
        asset_dict: dict[str, Any],
    ) -> list[MediaAsset]:
        typed_input: HighlightAgentInput = ctx.typed_input
        content = asset_dict.get("content", {})

        clips_spec = content.get("clips", [])
        if not clips_spec:
            logger.warning("HighlightMaterializer: no clips selected")
            return []

        # Local uri_holder — the persisted content JSON has no asset block;
        # ArtifactWriter still needs a dict to stamp uri into for ArtifactRef.
        uri_holder: dict[str, Any] = {}

        # Sort + merge LLM-emitted intervals so overlapping picks
        # (e.g. (5, 12) and (10, 18)) collapse into one (5, 18) cut
        # instead of producing a reel that replays the 10-12 source
        # frames twice. See ``_merge_overlapping_clips`` for rationale.
        merged_intervals, dropped = _merge_overlapping_clips(clips_spec)
        if not merged_intervals:
            raise RuntimeError(
                f"HighlightMaterializer: every clip in the {len(clips_spec)}"
                f"-entry LLM selection had invalid bounds (end<=start or"
                f" non-numeric); cannot build reel"
            )
        if dropped:
            logger.warning(
                "HighlightMaterializer: merged %d overlapping LLM clip(s) "
                "into %d non-overlapping interval(s)",
                dropped, len(merged_intervals),
            )

        # Track per-clip failures so the reel either succeeds completely
        # or fails loudly. Silently dropping a failing clip distorts the
        # selected highlight set; silently emitting [] when *every* clip
        # fails masks the failure as a PASS with no asset.
        clip_bytes_list: list[bytes] = []
        failures: list[str] = []
        for start, end in merged_intervals:
            try:
                clip_data = await self.svc.clip_segment(
                    typed_input.source_video_path, start, end,
                )
            except Exception as exc:
                failures.append(f"({start:.1f}-{end:.1f}): {exc}")
                continue
            if clip_data:
                clip_bytes_list.append(clip_data)
            else:
                failures.append(f"({start:.1f}-{end:.1f}): empty bytes")

        if not clip_bytes_list:
            raise RuntimeError(
                f"HighlightMaterializer: no clips extracted from "
                f"{len(merged_intervals)} merged interval(s); failures="
                f"{'; '.join(failures) or 'none reported'}"
            )
        if failures:
            logger.warning(
                "HighlightMaterializer: %d/%d intervals failed and were "
                "dropped: %s",
                len(failures), len(merged_intervals), '; '.join(failures),
            )

        reel_bytes = await self.svc.concat_clips(clip_bytes_list)
        if not reel_bytes:
            raise RuntimeError(
                f"HighlightMaterializer: concat returned empty for "
                f"{len(clip_bytes_list)} clips"
            )

        return [MediaAsset(
            sys_id="highlight_reel",
            data=reel_bytes,
            extension="mp4",
            uri_holder=uri_holder,
        )]
