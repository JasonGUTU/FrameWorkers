"""Schema definitions for NarrationAgent input / output interfaces."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..common_schema import Meta


class AudioAsset(BaseModel):
    asset_id: str = ""
    uri: str = ""
    format: str = "wav"


class NarrationSegment(BaseModel):
    segment_id: str = ""
    linked_shot_id: str = ""
    speaker: str = ""
    text: str = Field("", json_schema_extra={"creative": True})
    audio_asset: AudioAsset = Field(default_factory=AudioAsset)
    audio_generation_prompt: str = ""


class NarrationContent(BaseModel):
    segments: list[NarrationSegment] = Field(default_factory=list)


class NarrationMetrics(BaseModel):
    segment_count: int = 0


class NarrationAgentInput(BaseModel):
    """Input: screenplay JSON text (dialogue/narration lines to voice)."""
    screenplay_json_text: str = ""


class NarrationAgentOutput(BaseModel):
    meta: Meta = Field(default_factory=Meta)
    content: NarrationContent = Field(default_factory=NarrationContent)
    metrics: NarrationMetrics = Field(default_factory=NarrationMetrics)
