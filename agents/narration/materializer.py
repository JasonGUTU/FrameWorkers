"""Narration materializer — TTS for each spoken segment."""

from __future__ import annotations

import json
import logging
from typing import Any, TYPE_CHECKING

from ..descriptor import BaseMaterializer, MediaAsset
from inference.generation.audio_generators.service import AudioService

if TYPE_CHECKING:
    from ..base_agent import MaterializeContext

logger = logging.getLogger(__name__)


class NarrationMaterializer(BaseMaterializer):

    def __init__(self, audio_service: AudioService) -> None:
        self.svc = audio_service

    async def materialize(self, ctx: "MaterializeContext", asset_dict: dict[str, Any]) -> list[MediaAsset]:
        pending: list[MediaAsset] = []
        for seg in asset_dict.get("content", {}).get("segments", []):
            text = seg.get("text", "")
            speaker = seg.get("speaker", "")
            audio_asset = seg.get("audio_asset", {})
            asset_id = audio_asset.get("asset_id", "")
            if text and asset_id:
                try:
                    result = await self.svc.generate_speech(text, speaker_id=speaker)
                    seg["audio_generation_prompt"] = json.dumps(result.resolved_payload, ensure_ascii=False)
                    pending.append(MediaAsset(
                        sys_id=asset_id, data=result.bytes,
                        extension=audio_asset.get("format", "wav"), uri_holder=audio_asset,
                    ))
                except Exception as exc:
                    logger.error("TTS failed for %s: %s", asset_id, exc)
        return pending
