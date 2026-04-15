"""Inpaint materializer — executes video inpainting via edit service.

Supports multiple mask modes:
- manual: uses provided mask directly
- depth_foreground/depth_background: runs depth estimation to auto-generate mask
- object_track: runs object tracking + segmentation to auto-generate mask
Then calls the inpainting model with the mask + prompt.
"""

from __future__ import annotations

import logging
from typing import Any, TYPE_CHECKING

from ..descriptor import BaseMaterializer, MediaAsset
from inference.generation.video_edit_service import VideoEditService

if TYPE_CHECKING:
    from ..base_agent import MaterializeContext
    from .schema import InpaintAgentInput

logger = logging.getLogger(__name__)


class InpaintMaterializer(BaseMaterializer):
    """Apply inpainting via a video editing service."""

    def __init__(self, video_edit_service: VideoEditService) -> None:
        self.svc = video_edit_service

    async def materialize(
        self,
        ctx: "MaterializeContext",
        asset_dict: dict[str, Any],
    ) -> list[MediaAsset]:
        typed_input: InpaintAgentInput = ctx.typed_input
        content = asset_dict.get("content", {})
        output_video = content.get("output_video", {})
        output_video["asset_id"] = "inpaint_output"

        spec = content.get("inpaint_spec", {})
        mask_mode = spec.get("mask_mode", "manual")

        # Step 1: get or generate mask
        mask: bytes | str
        if mask_mode == "manual":
            mask = typed_input.mask_path
        elif mask_mode in ("depth_foreground", "depth_background"):
            depth_result = await self.svc.estimate_depth(typed_input.source_video_path)
            mask = depth_result.foreground if mask_mode == "depth_foreground" else depth_result.background
        elif mask_mode == "object_track":
            mask = await self.svc.track_object(
                typed_input.source_video_path,
                spec.get("replacement_description", ""),
            )
        else:
            logger.warning("InpaintMaterializer: unknown mask_mode %s", mask_mode)
            mask = typed_input.mask_path

        # Step 2: inpaint
        result_bytes = await self.svc.inpaint(
            video_path=typed_input.source_video_path,
            mask=mask,
            prompt=spec.get("inpaint_prompt", ""),
            blend_px=spec.get("blend_edge_px", 8),
        )

        if not result_bytes:
            logger.warning("InpaintMaterializer: inpaint returned empty")
            return []

        return [MediaAsset(
            sys_id="inpaint_output",
            data=result_bytes,
            extension="mp4",
            uri_holder=output_video,
        )]
