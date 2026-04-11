"""Schema definitions for IntakeAudioAgent input / output interfaces."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ...common_schema import Meta


class IntakeAudioAsset(BaseModel):
    asset_id: str = ""
    uri: str = ""
    format: str = "wav"


class IntakeAudioContent(BaseModel):
    auditory_summary: str = Field(
        "",
        json_schema_extra={"creative": True},
        description="One-sentence description of what the audio sounds like.",
    )
    audio_asset: IntakeAudioAsset = Field(default_factory=IntakeAudioAsset)


class IntakeAudioInput(BaseModel):
    raw_audio_path: str = ""
    user_intent: str = ""


class IntakeAudioOutput(BaseModel):
    meta: Meta = Field(default_factory=Meta)
    content: IntakeAudioContent = Field(default_factory=IntakeAudioContent)
