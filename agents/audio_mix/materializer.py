"""AudioMix materializer — mixes narration + music + ambience into the final track.

Per-scene mix semantics:
  narration tracks sequentially within each scene  → one narration track
  music cue for the scene (sized to screenplay est) → one music track
  ambience bed for the scene (sized to screenplay est) → one ambience track
  amix the three with duration=longest → scene mix
      (music/ambience run full screenplay estimate; narration is padded
      with silence when it finishes early, per user's intent.)

Final audio = concat(scene_mixes, in screenplay scene order).

URIs on upstream segments/cues/beds point at real workspace files (set by
Assistant after NarrationMaterializer/MusicMaterializer/AmbienceMaterializer
produced the bytes). We read those files back and mix them here.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, TYPE_CHECKING

from ..descriptor import BaseMaterializer, MediaAsset
from inference.generation.audio_generators.service import AudioService

if TYPE_CHECKING:
    from ..base_agent import MaterializeContext
    from .schema import AudioMixAgentInput

logger = logging.getLogger(__name__)


class AudioMixMaterializer(BaseMaterializer):

    def __init__(self, audio_service: AudioService) -> None:
        self.svc = audio_service

    @staticmethod
    def _load_bytes(uri: str) -> bytes | None:
        if not uri or uri == "placeholder":
            return None
        path = uri[7:] if uri.startswith("file://") else uri
        if not os.path.isfile(path):
            logger.warning("[AudioMix] upstream audio not on disk: %s", path)
            return None
        try:
            with open(path, "rb") as fh:
                return fh.read()
        except Exception as exc:
            logger.warning("[AudioMix] failed reading %s: %s", path, exc)
            return None

    @staticmethod
    def _parse(json_text: str) -> dict[str, Any]:
        try:
            parsed = json.loads(json_text) if json_text else {}
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def _build_shot_to_scene_index(screenplay: dict[str, Any]) -> dict[str, str]:
        """Map ``shot_id → scene_id`` from the screenplay's scene/shot tree.

        Narration segments carry only ``linked_shot_id``; to group them by
        scene for per-scene mixing we look each shot up in this index.
        """
        index: dict[str, str] = {}
        for scene in screenplay.get("content", {}).get("scenes", []) or []:
            scene_id = scene.get("scene_id", "") or ""
            if not scene_id:
                continue
            for shot in scene.get("shots", []) or []:
                shot_id = shot.get("shot_id", "") or ""
                if shot_id:
                    index[shot_id] = scene_id
        return index

    async def materialize(self, ctx: "MaterializeContext", asset_dict: dict[str, Any]) -> list[MediaAsset]:
        typed_input = ctx.typed_input  # type: AudioMixAgentInput

        screenplay = self._parse(typed_input.screenplay_json_text)
        narr = self._parse(typed_input.narration_json_text)
        music = self._parse(typed_input.music_json_text)
        amb = self._parse(typed_input.ambience_json_text)

        shot_to_scene = self._build_shot_to_scene_index(screenplay)

        # Group narration bytes by scene, preserving segment_id order within each scene
        segs = sorted(
            narr.get("content", {}).get("segments", []) or [],
            key=lambda s: s.get("segment_id", ""),
        )
        narration_by_scene: dict[str, list[bytes]] = {}
        for seg in segs:
            shot_id = seg.get("linked_shot_id", "") or ""
            scene_id = shot_to_scene.get(shot_id, "")
            uri = (seg.get("audio_asset") or {}).get("uri", "")
            data = self._load_bytes(uri)
            if scene_id and data is not None:
                narration_by_scene.setdefault(scene_id, []).append(data)

        # One music cue / ambience bed per scene (MusicAgent/AmbienceAgent invariant)
        music_by_scene: dict[str, bytes] = {}
        for cue in music.get("content", {}).get("cues", []) or []:
            scene_id = cue.get("scene_id", "") or ""
            data = self._load_bytes((cue.get("audio_asset") or {}).get("uri", ""))
            if scene_id and data is not None:
                music_by_scene[scene_id] = data

        ambience_by_scene: dict[str, bytes] = {}
        for bed in amb.get("content", {}).get("beds", []) or []:
            scene_id = bed.get("scene_id", "") or ""
            data = self._load_bytes((bed.get("audio_asset") or {}).get("uri", ""))
            if scene_id and data is not None:
                ambience_by_scene[scene_id] = data

        pending: list[MediaAsset] = []
        content = asset_dict.get("content", {})
        scene_mix_bytes: list[bytes] = []

        for mix in content.get("scene_mixes", []):
            scene_id = mix.get("scene_id", "") or ""
            mix_asset = mix.get("mix_asset", {})
            sys_mix_id = f"aud_mix_{scene_id}" if scene_id else (mix_asset.get("asset_id") or "")
            mix_asset["asset_id"] = sys_mix_id
            if not sys_mix_id:
                continue
            try:
                mixed = await self.svc.mix_scene_audio(
                    narration_bytes_list=narration_by_scene.get(scene_id, []),
                    music_bytes=music_by_scene.get(scene_id),
                    ambience_bytes=ambience_by_scene.get(scene_id),
                    scene_id=scene_id,
                )
                pending.append(MediaAsset(
                    sys_id=sys_mix_id, data=mixed,
                    extension="wav", uri_holder=mix_asset,
                ))
                scene_mix_bytes.append(mixed)
            except Exception as exc:
                logger.error("[AudioMix] scene mix failed for %s: %s", scene_id, exc)
                if ctx.report_failure is not None:
                    ctx.report_failure(
                        kind="audio_scene_mix", sys_id=sys_mix_id,
                        error=f"{type(exc).__name__}: {exc}",
                    )

        final = content.get("final_audio", {})
        final["asset_id"] = "aud_final"
        if scene_mix_bytes:
            try:
                final_bytes = await self.svc.assemble_final(scene_mix_bytes_list=scene_mix_bytes)
                pending.append(MediaAsset(
                    sys_id="aud_final", data=final_bytes,
                    extension="wav", uri_holder=final,
                ))
            except Exception as exc:
                logger.error("[AudioMix] final assembly failed: %s", exc)
                if ctx.report_failure is not None:
                    ctx.report_failure(
                        kind="audio_final_assembly", sys_id="aud_final",
                        error=f"{type(exc).__name__}: {exc}",
                    )

        return pending
