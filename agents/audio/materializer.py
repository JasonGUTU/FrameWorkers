"""Audio track materializer — generates TTS, music, ambience via AudioService.

This materializer is a **pure generator** — it calls AudioService to
produce audio bytes and returns ``list[MediaAsset]``.  It never performs
file I/O; persistence is handled exclusively by Assistant.
"""

from __future__ import annotations

import logging
from typing import Any

from ..descriptor import BaseMaterializer, MediaAsset
from .service import AudioService

logger = logging.getLogger(__name__)


class AudioMaterializer(BaseMaterializer):
    """Generate audio tracks for all scenes via AudioService.

    Constructor:
        audio_service: ``AudioService`` instance (TTS + music + ambience).
    """

    def __init__(self, audio_service: AudioService) -> None:
        self.audio_svc = audio_service

    async def materialize(
        self,
        project_id: str,
        asset_dict: dict[str, Any],
        assets: dict[str, Any],
    ) -> list[MediaAsset]:
        """Generate actual audio tracks for all scenes.

        System-generates sequential asset_ids:
          Narration  -- ``aud_narr_{scene_id}_{NN}``
          Music      -- ``aud_music_{scene_id}``
          Ambience   -- ``aud_amb_{scene_id}``
          Scene mix  -- ``aud_mix_{scene_id}``
          Final      -- ``aud_final``

        Returns:
            List of ``MediaAsset`` objects for Assistant to persist.
        """
        pending: list[MediaAsset] = []
        content = asset_dict.get("content", {})
        scene_mix_bytes_list: list[bytes] = []

        for scene in content.get("scenes", []):
            scene_id = scene.get("scene_id", "")
            narration_bytes_list: list[bytes] = []

            # --- Narration segments (TTS) ---
            narr_counter = 0
            for seg in scene.get("narration_segments", []):
                text = seg.get("text", "")
                audio_asset = seg.get("audio_asset", {})
                speaker = seg.get("speaker", "")

                narr_counter += 1
                sys_seg_id = f"aud_narr_{scene_id}_{narr_counter:02d}"
                audio_asset["asset_id"] = sys_seg_id

                if text:
                    try:
                        voice = self._speaker_to_voice(speaker)
                        audio_bytes = await self.audio_svc.generate_speech(
                            text, voice=voice
                        )
                        ext = audio_asset.get("format", "wav")
                        pending.append(MediaAsset(
                            sys_id=sys_seg_id, data=audio_bytes,
                            extension=ext, uri_holder=audio_asset,
                        ))
                        audio_asset["duration_sec"] = len(audio_bytes) / (44100 * 2)
                        narration_bytes_list.append(audio_bytes)
                    except Exception as exc:
                        logger.error("TTS failed for segment %s: %s", sys_seg_id, exc)

            # --- Music cue ---
            music_cue = scene.get("music_cue", {})
            music_asset = music_cue.get("audio_asset", {})
            sys_music_id = f"aud_music_{scene_id}"
            music_asset["asset_id"] = sys_music_id
            music_bytes: bytes | None = None
            if music_cue:
                try:
                    music_bytes = await self.audio_svc.generate_music(
                        mood=music_cue.get("mood", "neutral"),
                        duration_sec=music_cue.get("end_sec", 0) - music_cue.get("start_sec", 0),
                        scene_id=scene_id,
                    )
                    pending.append(MediaAsset(
                        sys_id=sys_music_id, data=music_bytes,
                        extension="wav", uri_holder=music_asset,
                    ))
                except Exception as exc:
                    logger.error("Music generation failed for %s: %s", sys_music_id, exc)

            # --- Ambience bed ---
            ambience = scene.get("ambience_bed", {})
            amb_asset = ambience.get("audio_asset", {})
            sys_amb_id = f"aud_amb_{scene_id}"
            amb_asset["asset_id"] = sys_amb_id
            ambience_bytes: bytes | None = None
            if ambience:
                try:
                    ambience_bytes = await self.audio_svc.generate_ambience(
                        description=ambience.get("description", ""),
                        duration_sec=ambience.get("end_sec", 0) - ambience.get("start_sec", 0),
                        scene_id=scene_id,
                    )
                    pending.append(MediaAsset(
                        sys_id=sys_amb_id, data=ambience_bytes,
                        extension="wav", uri_holder=amb_asset,
                    ))
                except Exception as exc:
                    logger.error("Ambience generation failed for %s: %s", sys_amb_id, exc)

            # --- Scene mix ---
            mix_info = scene.get("mix", {})
            mix_asset = mix_info.get("audio_asset", {})
            sys_mix_id = f"aud_mix_{scene_id}"
            mix_asset["asset_id"] = sys_mix_id
            if mix_info:
                try:
                    mix_bytes = await self.audio_svc.mix_scene_audio(
                        narration_bytes_list=narration_bytes_list,
                        music_bytes=music_bytes,
                        ambience_bytes=ambience_bytes,
                        scene_id=scene_id,
                        duration_sec=scene.get("scene_duration_sec", 0),
                    )
                    pending.append(MediaAsset(
                        sys_id=sys_mix_id, data=mix_bytes,
                        extension="wav", uri_holder=mix_asset,
                    ))
                    scene_mix_bytes_list.append(mix_bytes)
                except Exception as exc:
                    logger.error("Scene mix failed for %s: %s", sys_mix_id, exc)

        # --- Final audio assembly ---
        final = content.get("final_audio_asset", {})
        final["asset_id"] = "aud_final"
        if scene_mix_bytes_list:
            try:
                final_bytes = await self.audio_svc.assemble_final(
                    scene_mix_bytes_list=scene_mix_bytes_list
                )
                pending.append(MediaAsset(
                    sys_id="aud_final", data=final_bytes,
                    extension="wav", uri_holder=final,
                ))
            except Exception as exc:
                logger.error("Final audio assembly failed: %s", exc)

        logger.info("All audio tracks materialized for %s", project_id)
        return pending

    @staticmethod
    def _speaker_to_voice(speaker: str) -> str:
        """Map a character/speaker name to an OpenAI TTS voice.

        Uses a simple hash-based assignment for consistency — the same
        speaker always gets the same voice within a pipeline run.
        """
        voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        if not speaker:
            return "alloy"
        idx = hash(speaker) % len(voices)
        return voices[idx]
