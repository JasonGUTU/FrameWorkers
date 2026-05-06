"""Style transfer materializer — applies visual style to video."""

from __future__ import annotations

import logging
from typing import Any, TYPE_CHECKING

from ..base_agent import DEFAULT_ASSET_RETRIES
from ..descriptor import BaseMaterializer, MediaAsset
from inference.generation.video_edit_service import VideoEditService

if TYPE_CHECKING:
    from ..base_agent import MaterializeContext
    from .schema import StyleTransferAgentInput

logger = logging.getLogger(__name__)


class StyleTransferMaterializer(BaseMaterializer):
    """Apply style transfer via a video editing service."""

    def __init__(self, video_edit_service: VideoEditService) -> None:
        self.svc = video_edit_service

    async def materialize(
        self,
        ctx: "MaterializeContext",
        asset_dict: dict[str, Any],
    ) -> list[MediaAsset]:
        typed_input: StyleTransferAgentInput = ctx.typed_input
        content = asset_dict.get("content", {})
        output_video = content.get("output_video", {})
        output_video["asset_id"] = "style_transfer_output"

        spec = content.get("style_spec", {})

        # Apply style with partial-resume retry budget. Failure exhausts
        # the budget then raises so the outer run loop can rework + retry.
        last_exc: Exception | None = None
        result_bytes: bytes | None = None
        for attempt in range(1, DEFAULT_ASSET_RETRIES + 1):
            try:
                result_bytes = await self.svc.style_transfer(
                    video_path=typed_input.source_video_path,
                    prompt=spec.get("style_prompt", ""),
                    strength=spec.get("style_strength", 0.7),
                    preserve_motion=spec.get("preserve_motion", True),
                    reference_path=typed_input.style_reference_path or None,
                )
                if result_bytes:
                    break
                last_exc = RuntimeError("style_transfer returned empty bytes")
            except Exception as exc:
                last_exc = exc
            logger.warning(
                "[attempt %d/%d] StyleTransferMaterializer.style_transfer failed: %s",
                attempt, DEFAULT_ASSET_RETRIES, last_exc,
            )

        if not result_bytes:
            raise RuntimeError(
                f"StyleTransferMaterializer.style_transfer failed after "
                f"{DEFAULT_ASSET_RETRIES} attempts: {last_exc}"
            )

        return [MediaAsset(
            sys_id="style_transfer_output",
            data=result_bytes,
            extension="mp4",
            uri_holder=output_video,
        )]
