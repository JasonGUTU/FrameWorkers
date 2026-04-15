"""Schema definitions for MusicAgent input / output interfaces."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..common_schema import Meta


class AudioAsset(BaseModel):
    asset_id: str = ""
    uri: str = ""
    format: str = "wav"


class MusicCue(BaseModel):
    cue_id: str = ""
    scene_id: str = ""
    mood: str = Field("", json_schema_extra={"creative": True})
    duration_seconds: float = Field(0.0, description="Estimated duration in seconds based on scene dialogue/narration length")
    audio_asset: AudioAsset = Field(default_factory=AudioAsset)
    audio_generation_prompt: str = ""


class MusicContent(BaseModel):
    cues: list[MusicCue] = Field(default_factory=list)


class MusicMetrics(BaseModel):
    cue_count: int = 0


class MusicAgentInput(BaseModel):
    screenplay_json_text: str = ""


class MusicAgentOutput(BaseModel):
    meta: Meta = Field(default_factory=Meta)
    content: MusicContent = Field(default_factory=MusicContent)
    metrics: MusicMetrics = Field(default_factory=MusicMetrics)
