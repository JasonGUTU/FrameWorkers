"""Schema definitions for AudioMixAgent input / output interfaces."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..common_schema import Meta


class AudioAsset(BaseModel):
    asset_id: str = ""
    uri: str = ""
    format: str = "wav"


class SceneMix(BaseModel):
    scene_id: str = ""
    mix_asset: AudioAsset = Field(default_factory=AudioAsset)


class AudioMixContent(BaseModel):
    scene_mixes: list[SceneMix] = Field(default_factory=list)
    final_audio: AudioAsset = Field(default_factory=AudioAsset)


class AudioMixMetrics(BaseModel):
    scene_count: int = 0


class AudioMixAgentInput(BaseModel):
    """Input: JSON text blobs of screenplay + narration / music / ambience packages.

    ``screenplay_json_text`` is included so the materializer can resolve each
    narration segment's ``linked_shot_id`` back to a ``scene_id`` — narration
    segments are emitted per-shot (no scene_id on them), and AudioMix needs to
    group them by scene to sync with per-scene music / ambience tracks.
    """
    screenplay_json_text: str = ""
    narration_json_text: str = ""
    music_json_text: str = ""
    ambience_json_text: str = ""


class AudioMixAgentOutput(BaseModel):
    meta: Meta = Field(default_factory=Meta)
    content: AudioMixContent = Field(default_factory=AudioMixContent)
    metrics: AudioMixMetrics = Field(default_factory=AudioMixMetrics)
