"""Schema definitions for VideoExtendAgent input / output interfaces."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..common_schema import Meta


# ---------------------------------------------------------------------------
# Video extend sub-models
# ---------------------------------------------------------------------------

class ExtensionSpec(BaseModel):
    """LLM-planned video extension specification."""

    continuation_prompt: str = Field(
        "", description="Prompt describing what happens next in the video"
    )
    target_duration_seconds: float = Field(
        5.0, description="How many seconds to extend by"
    )
    maintain_style: bool = Field(
        True, description="Keep visual style consistent with source"
    )
    motion_description: str = Field(
        "", description="Description of motion/camera movement for the extension"
    )


class VideoAsset(BaseModel):
    """Pointer to a generated video file."""

    asset_id: str = ""
    uri: str = ""
    format: str = "mp4"


# ---------------------------------------------------------------------------
# Content / Metrics
# ---------------------------------------------------------------------------

class VideoExtendContent(BaseModel):
    extension_spec: ExtensionSpec = Field(default_factory=ExtensionSpec)
    output_video: VideoAsset = Field(default_factory=VideoAsset)


class VideoExtendMetrics(BaseModel):
    target_duration_seconds: float = 0.0


# ---------------------------------------------------------------------------
# Top-level I/O
# ---------------------------------------------------------------------------

class VideoExtendAgentInput(BaseModel):
    """Input payload for VideoExtendAgent.

    ``source_video_path``: the video to extend.
    ``continuation_description``: what should happen next.
    """

    source_video_path: str = ""
    continuation_description: str = ""


class VideoExtendAgentOutput(BaseModel):
    """Output payload for VideoExtendAgent."""

    meta: Meta = Field(default_factory=Meta)
    content: VideoExtendContent = Field(default_factory=VideoExtendContent)
    metrics: VideoExtendMetrics = Field(default_factory=VideoExtendMetrics)
