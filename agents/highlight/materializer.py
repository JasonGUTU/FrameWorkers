"""Highlight materializer — clips and compiles highlight segments.

Reads the LLM-selected clip list, extracts each segment from the source
video, and concatenates them into a highlight reel.

Trust contract: the upstream evaluator (HighlightEvaluator.check_structure)
already enforces every per-clip invariant the materializer depends on —
``end_time > start_time``, ``duration >= 2s``, no overlap with previous
clip, valid numeric bounds (Pydantic). On evaluator failure rework
re-runs the LLM, so by the time we materialize the clips list is clean.
We do NOT silently merge / clip / drop bad rows here (CLAUDE.md §7
forbids materializer-side silent fixes that mask producer drift).
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

        # Track per-clip failures so the reel either succeeds completely
        # or fails loudly. Silently dropping a failing clip distorts the
        # selected highlight set; silently emitting [] when *every* clip
        # fails masks the failure as a PASS with no asset.
        clip_bytes_list: list[bytes] = []
        failures: list[str] = []
        for clip in clips_spec:
            start = float(clip.get("start_time", 0) or 0)
            end = float(clip.get("end_time", 0) or 0)
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
                f"{len(clips_spec)} clip(s); failures="
                f"{'; '.join(failures) or 'none reported'}"
            )
        if failures:
            logger.warning(
                "HighlightMaterializer: %d/%d clips failed and were "
                "dropped: %s",
                len(failures), len(clips_spec), '; '.join(failures),
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
