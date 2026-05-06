"""Music materializer — generates the single film-wide background music track.

Generates a fixed 30s chunk (most audio-gen backends cap there). Track
length is intentionally not a creative responsibility: the downstream
audio-mix step's ffmpeg amix duration=longest filter trims/loops the
bed against the actual video length, so any reasonable single chunk
works as the source.

Persisted-JSON contract: this materializer does NOT mutate the cue dict.
The wav file is registered in global_memory as a standalone artifact with
sys_id ``aud_music_film``; downstream audio-mix consumers find it by
caption-based resolution, not by reading an asset block from the music
package JSON.
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


# Stable sys_id for the film-wide music wav. The MusicAgent emits exactly
# one cue and the materializer emits exactly one wav, so a constant
# sys_id is sufficient for global_memory registration.
MUSIC_FILM_SYS_ID = "aud_music_film"


class MusicMaterializer(BaseMaterializer):

    def __init__(self, audio_service: AudioService) -> None:
        self.svc = audio_service

    async def materialize(self, ctx: "MaterializeContext", asset_dict: dict[str, Any]) -> list[MediaAsset]:
        pending: list[MediaAsset] = []
        for cue in asset_dict.get("content", {}).get("cues", []):
            mood = cue.get("mood", "neutral")

            # Per-cue partial-resume retry — on exhaustion raise so the
            # outer run loop can rework + retry the whole step.
            last_exc: Exception | None = None
            final_bytes: bytes | None = None
            for attempt in range(1, DEFAULT_ASSET_RETRIES + 1):
                try:
                    result = await self.svc.generate_music(
                        mood=mood, scene_id="", duration_sec=30.0,
                    )
                    final_bytes = result.bytes
                    if final_bytes:
                        break
                    last_exc = RuntimeError("generate_music returned empty bytes")
                except Exception as exc:
                    last_exc = exc
                logger.warning(
                    "[attempt %d/%d] Music generation failed for %s: %s",
                    attempt, DEFAULT_ASSET_RETRIES, MUSIC_FILM_SYS_ID, last_exc,
                )

            if not final_bytes:
                raise RuntimeError(
                    f"Music generation for {MUSIC_FILM_SYS_ID} failed after "
                    f"{DEFAULT_ASSET_RETRIES} attempts: {last_exc}"
                )

            # Local uri_holder: the persist flow sets ``uri_holder["uri"]``
            # after writing the wav to disk and
            # ``collect_materialized_files`` reads it back. We deliberately
            # do NOT use the cue dict as uri_holder so the persisted cue
            # JSON has no audio_asset block.
            uri_holder: dict[str, Any] = {}
            pending.append(MediaAsset(
                sys_id=MUSIC_FILM_SYS_ID, data=final_bytes,
                extension="wav", uri_holder=uri_holder,
            ))
        return pending
