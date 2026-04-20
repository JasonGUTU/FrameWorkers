"""Video extend materializer — generates continuation clip via video service.

Extracts the last frame from the source video as the starting frame,
then calls the video generation service in image-to-video mode
with the continuation prompt.
"""

from __future__ import annotations

import logging
from typing import Any, TYPE_CHECKING

from ..descriptor import BaseMaterializer, MediaAsset
from inference.generation.video_generators.service import VideoService

if TYPE_CHECKING:
    from ..base_agent import MaterializeContext
    from .schema import VideoExtendAgentInput

logger = logging.getLogger(__name__)


class VideoExtendMaterializer(BaseMaterializer):
    """Generate video continuation via the video service."""

    def __init__(self, video_service: VideoService) -> None:
        self.svc = video_service

    async def materialize(
        self,
        ctx: "MaterializeContext",
        asset_dict: dict[str, Any],
    ) -> list[MediaAsset]:
        typed_input: VideoExtendAgentInput = ctx.typed_input
        content = asset_dict.get("content", {})
        spec = content.get("extension_spec", {})

        # Local uri_holder — the persisted content JSON has no asset block;
        # ArtifactWriter still needs a dict to stamp uri into for ArtifactRef.
        uri_holder: dict[str, Any] = {}

        # Extract last frame from source video
        last_frame = await self.svc.extract_last_frame(typed_input.source_video_path)

        if not last_frame:
            logger.warning(
                "VideoExtendMaterializer: could not extract last frame from %s",
                typed_input.source_video_path,
            )
            return []

        # Generate continuation using I2V with last frame as starting point
        result = await self.svc.generate_clip(
            shot_id="extend_001",
            keyframe_images=[last_frame],
            prompt=spec.get("continuation_prompt", ""),
            duration_sec=spec.get("target_duration_seconds", 5.0),
        )

        result_bytes = result.bytes if hasattr(result, "bytes") else result
        if not result_bytes:
            logger.warning("VideoExtendMaterializer: generate_clip returned empty")
            return []

        return [MediaAsset(
            sys_id="video_extend_output",
            data=result_bytes,
            extension="mp4",
            uri_holder=uri_holder,
        )]
