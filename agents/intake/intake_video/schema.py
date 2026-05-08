"""Schema definitions for IntakeVideoAgent input / output interfaces."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ...common_schema import Meta


class IntakeVideoAsset(BaseModel):
    uri: str = ""


class IntakeVideoContent(BaseModel):
    visual_summary: str = Field(
        "",
        json_schema_extra={"creative": True},
        description="One-sentence description of what the video shows.",
    )
    video_asset: IntakeVideoAsset = Field(default_factory=IntakeVideoAsset)


class IntakeVideoInput(BaseModel):
    raw_video_path: str = ""


class IntakeVideoOutput(BaseModel):
    meta: Meta = Field(default_factory=Meta)
    content: IntakeVideoContent = Field(default_factory=IntakeVideoContent)
