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
        compiled = content.get("compiled_video", {})
        compiled["asset_id"] = "highlight_reel"

        clips_spec = content.get("clips", [])
        if not clips_spec:
            logger.warning("HighlightMaterializer: no clips selected")
            return []

        clip_bytes_list: list[bytes] = []
        for clip in clips_spec:
            start = clip.get("start_time", 0)
            end = clip.get("end_time", 0)
            if end <= start:
                continue
            try:
                clip_data = await self.svc.clip_segment(
                    typed_input.source_video_path, start, end,
                )
                if clip_data:
                    clip_bytes_list.append(clip_data)
            except Exception as exc:
                logger.error(
                    "HighlightMaterializer: clip failed (%.1f-%.1f): %s",
                    start, end, exc,
                )

        if not clip_bytes_list:
            logger.warning("HighlightMaterializer: no clips extracted")
            return []

        reel_bytes = await self.svc.concat_clips(clip_bytes_list)
        if not reel_bytes:
            logger.warning("HighlightMaterializer: concat returned empty")
            return []

        return [MediaAsset(
            sys_id="highlight_reel",
            data=reel_bytes,
            extension="mp4",
            uri_holder=compiled,
        )]
