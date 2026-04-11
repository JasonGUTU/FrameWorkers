"""Schema definitions for IntakeImageAgent input / output interfaces."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ...common_schema import ImageAsset, Meta


class IntakeImageContent(BaseModel):
    visual_description: str = Field(
        "",
        json_schema_extra={"creative": True},
        description="Vision-LLM-generated objective description of what the image shows.",
    )
    image_asset: ImageAsset = Field(default_factory=ImageAsset)


class IntakeImageInput(BaseModel):
    """Input payload for IntakeImageAgent."""

    raw_image_path: str = ""


class IntakeImageOutput(BaseModel):
    meta: Meta = Field(default_factory=Meta)
    content: IntakeImageContent = Field(default_factory=IntakeImageContent)
