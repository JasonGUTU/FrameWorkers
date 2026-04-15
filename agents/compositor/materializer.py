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
        delivery = content.get("delivery_asset", {})
        delivery["asset_id"] = "compositor_final"

        plan = content.get("plan", {})

        # Extract SRT text from subtitle input if it looks like JSON with tracks
        subtitle_srt = ""
        raw_sub = typed_input.subtitle_json_text
        if raw_sub:
            import json
            try:
                sub_data = json.loads(raw_sub)
                tracks = sub_data.get("content", sub_data).get("tracks", [])
                if tracks:
                    subtitle_srt = tracks[0].get("srt_text", "")
            except (json.JSONDecodeError, AttributeError):
                subtitle_srt = raw_sub

        result_bytes = await self.svc.compose(
            video_path=typed_input.video_file_path,
            audio_path=typed_input.audio_file_path,
            subtitle_srt=subtitle_srt,
            plan=plan,
        )

        if not result_bytes:
            logger.warning("CompositorMaterializer: compose returned empty bytes")
            return []

        return [MediaAsset(
            sys_id="compositor_final",
            data=result_bytes,
            extension="mp4",
            uri_holder=delivery,
        )]
