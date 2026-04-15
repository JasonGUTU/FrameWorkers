"""Schema definitions for AmbienceAgent input / output interfaces."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..common_schema import Meta


class AudioAsset(BaseModel):
    asset_id: str = ""
    uri: str = ""
    format: str = "wav"


class AmbienceBed(BaseModel):
    ambience_id: str = ""
    scene_id: str = ""
    description: str = Field("", json_schema_extra={"creative": True})
    duration_seconds: float = Field(0.0, description="Estimated duration in seconds based on scene dialogue/narration length")
    audio_asset: AudioAsset = Field(default_factory=AudioAsset)
    audio_generation_prompt: str = ""


class AmbienceContent(BaseModel):
    beds: list[AmbienceBed] = Field(default_factory=list)


class AmbienceMetrics(BaseModel):
    bed_count: int = 0


class AmbienceAgentInput(BaseModel):
    screenplay_json_text: str = ""


class AmbienceAgentOutput(BaseModel):
    meta: Meta = Field(default_factory=Meta)
    content: AmbienceContent = Field(default_factory=AmbienceContent)
    metrics: AmbienceMetrics = Field(default_factory=AmbienceMetrics)
