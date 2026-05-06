"""Video extend materializer — generates continuation clip via video service.

Extracts the last frame from the source video as the starting frame,
then calls the video generation service in image-to-video mode
with the continuation prompt.
"""

from __future__ import annotations

import logging
from typing import Any, TYPE_CHECKING

from ..base_agent import DEFAULT_ASSET_RETRIES
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

        # Extract last frame from source video — frame extraction is
        # deterministic (ffmpeg), so a failure is structural, not transient:
        # raise immediately rather than retry.
        last_frame = await self.svc.extract_last_frame(typed_input.source_video_path)
        if not last_frame:
            raise RuntimeError(
                f"VideoExtendMaterializer: could not extract last frame from "
                f"{typed_input.source_video_path}"
            )

        # Generate continuation with partial-resume retry budget for
        # transient gen failures (network / rate-limit / occasional model
        # error). On exhaustion, raise so the outer run loop sees the
        # failure and can rework + retry.
        last_exc: Exception | None = None
        result_bytes: bytes | None = None
        for attempt in range(1, DEFAULT_ASSET_RETRIES + 1):
            try:
                result = await self.svc.generate_clip(
                    shot_id="extend_001",
                    keyframe_images=[last_frame],
                    prompt=spec.get("continuation_prompt", ""),
                    duration_sec=spec.get("target_duration_seconds", 5.0),
                )
                result_bytes = result.bytes if hasattr(result, "bytes") else result
                if result_bytes:
                    break
                last_exc = RuntimeError("generate_clip returned empty bytes")
            except Exception as exc:
                last_exc = exc
            logger.warning(
                "[attempt %d/%d] VideoExtendMaterializer.generate_clip failed: %s",
                attempt, DEFAULT_ASSET_RETRIES, last_exc,
            )

        if not result_bytes:
            raise RuntimeError(
                f"VideoExtendMaterializer.generate_clip failed after "
                f"{DEFAULT_ASSET_RETRIES} attempts: {last_exc}"
            )

        return [MediaAsset(
            sys_id="video_extend_output",
            data=result_bytes,
            extension="mp4",
            uri_holder=uri_holder,
        )]
