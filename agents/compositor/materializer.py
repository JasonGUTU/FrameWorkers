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
            tracks = (sub_data.get("content", sub_data) or {}).get("tracks", [])
            for track in tracks:
                if not isinstance(track, dict):
                    continue
                srt = (track.get("srt_text") or "").strip()
                if srt:
                    subtitle_srts.append(srt)

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
