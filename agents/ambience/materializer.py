"""Ambience materializer — generates the single film-wide ambient bed.

Generates a fixed 30s chunk. Track length is intentionally not a
creative responsibility: the downstream audio-mix step's ffmpeg amix
duration=longest filter trims/loops the bed against the actual video
length, so any reasonable single chunk works as the source.

Persisted-JSON contract: this materializer does NOT mutate the bed dict.
The wav file is registered in global_memory as a standalone artifact
with sys_id ``aud_amb_film``; downstream audio-mix consumers find it by
caption-based resolution, not by reading an asset block from the
ambience package JSON.
"""

from __future__ import annotations

import logging
from typing import Any, TYPE_CHECKING

from ..base_agent import DEFAULT_ASSET_RETRIES
from ..descriptor import BaseMaterializer, MediaAsset
from inference.generation.audio_generators.service import AudioService

if TYPE_CHECKING:
    from ..base_agent import MaterializeContext

logger = logging.getLogger(__name__)


# Stable sys_id for the film-wide ambience wav. The AmbienceAgent emits
# exactly one bed and the materializer emits exactly one wav, so a
# constant sys_id is sufficient for global_memory registration.
AMBIENCE_FILM_SYS_ID = "aud_amb_film"


class AmbienceMaterializer(BaseMaterializer):

    def __init__(self, audio_service: AudioService) -> None:
        self.svc = audio_service

    async def materialize(self, ctx: "MaterializeContext", asset_dict: dict[str, Any]) -> list[MediaAsset]:
        pending: list[MediaAsset] = []
        for bed in asset_dict.get("content", {}).get("beds", []):
            desc = bed.get("description", "")

            # Per-bed partial-resume retry — on exhaustion raise so the
            # outer run loop can rework + retry the whole step.
            last_exc: Exception | None = None
            final_bytes: bytes | None = None
            for attempt in range(1, DEFAULT_ASSET_RETRIES + 1):
                try:
                    result = await self.svc.generate_ambience(
                        description=desc, scene_id="", duration_sec=30.0,
                    )
                    final_bytes = result.bytes
                    if final_bytes:
                        break
                    last_exc = RuntimeError("generate_ambience returned empty bytes")
                except Exception as exc:
                    last_exc = exc
                logger.warning(
                    "[attempt %d/%d] Ambience generation failed for %s: %s",
                    attempt, DEFAULT_ASSET_RETRIES, AMBIENCE_FILM_SYS_ID, last_exc,
                )

            if not final_bytes:
                raise RuntimeError(
                    f"Ambience generation for {AMBIENCE_FILM_SYS_ID} failed "
                    f"after {DEFAULT_ASSET_RETRIES} attempts: {last_exc}"
                )

            # Local uri_holder — see MusicMaterializer for rationale.
            # The persisted bed JSON has no audio_asset block.
            uri_holder: dict[str, Any] = {}
            pending.append(MediaAsset(
                sys_id=AMBIENCE_FILM_SYS_ID, data=final_bytes,
                extension="wav", uri_holder=uri_holder,
            ))
        return pending
