"""Ambience materializer — generates environmental sounds per scene."""

from __future__ import annotations

import json
import logging
from typing import Any, TYPE_CHECKING

from ..descriptor import BaseMaterializer, MediaAsset
from inference.generation.audio_generators.service import AudioService

if TYPE_CHECKING:
    from ..base_agent import MaterializeContext

logger = logging.getLogger(__name__)


class AmbienceMaterializer(BaseMaterializer):

    def __init__(self, audio_service: AudioService) -> None:
        self.svc = audio_service

    async def materialize(self, ctx: "MaterializeContext", asset_dict: dict[str, Any]) -> list[MediaAsset]:
        pending: list[MediaAsset] = []
        for bed in asset_dict.get("content", {}).get("beds", []):
            desc = bed.get("description", "")
            scene_id = bed.get("scene_id", "")
            target_dur = bed.get("duration_seconds", 30.0)
            audio_asset = bed.get("audio_asset", {})
            asset_id = audio_asset.get("asset_id", "")
            if asset_id:
                try:
                    segments: list[bytes] = []
                    remaining = max(target_dur, 10.0)
                    seg_idx = 0
                    while remaining > 0:
                        seg_dur = min(remaining, 30.0)
                        result = await self.svc.generate_ambience(
                            description=desc, scene_id=scene_id, duration_sec=seg_dur,
                        )
                        segments.append(result.bytes)
                        remaining -= seg_dur
                        seg_idx += 1
                    if len(segments) == 1:
                        final_bytes = segments[0]
                    else:
                        from inference.generation.audio_generators.service import AudioService
                        joined = AudioService._ffmpeg_concat(segments)
                        final_bytes = joined if joined else b"".join(segments)
                    bed["audio_generation_prompt"] = json.dumps(
                        {"kind": "ambience", "description": desc, "target_duration": target_dur, "segments": seg_idx},
                        ensure_ascii=False,
                    )
                    pending.append(MediaAsset(
                        sys_id=asset_id, data=final_bytes,
                        extension="wav", uri_holder=audio_asset,
                    ))
                except Exception as exc:
                    logger.error("Ambience generation failed for %s: %s", asset_id, exc)
        return pending
