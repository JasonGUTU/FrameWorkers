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
    motion_description: str = Field(
        "", description="Description of motion/camera movement for the extension"
    )


# ---------------------------------------------------------------------------
# Content / Metrics
# ---------------------------------------------------------------------------

class VideoExtendContent(BaseModel):
    extension_spec: ExtensionSpec = Field(default_factory=ExtensionSpec)


class VideoExtendMetrics(BaseModel):
    target_duration_seconds: float = 0.0


# ---------------------------------------------------------------------------
# Top-level I/O
# ---------------------------------------------------------------------------

class VideoExtendAgentInput(BaseModel):
    """Input payload for VideoExtendAgent.

    ``source_video_path``: the video to extend.
    ``continuation_description``: what should happen next.
    ``creative_brief_json_text``: the user's verbatim brief as raw JSON
    text — fallback source for the continuation cue when no explicit
    continuation_instruction artifact is wired up upstream.
    """

    source_video_path: str = ""
    continuation_description: str = ""
    creative_brief_json_text: str = ""


class VideoExtendAgentOutput(BaseModel):
    """Output payload for VideoExtendAgent."""

    meta: Meta = Field(default_factory=Meta)
    content: VideoExtendContent = Field(default_factory=VideoExtendContent)
    metrics: VideoExtendMetrics = Field(default_factory=VideoExtendMetrics)
