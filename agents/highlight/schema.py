"""Schema definitions for HighlightAgent input / output interfaces."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..common_schema import Meta


# ---------------------------------------------------------------------------
# Highlight sub-models
# ---------------------------------------------------------------------------

class HighlightClip(BaseModel):
    """A selected highlight segment."""

    clip_id: str = ""
    start_time: float = Field(0.0, description="Start time in seconds")
    end_time: float = Field(0.0, description="End time in seconds")
    reason: str = Field("", description="Why this segment was selected")
    score: float = Field(0.0, ge=0.0, le=1.0, description="Relevance/quality score")


class VideoAsset(BaseModel):
    """Pointer to a generated video file."""

    asset_id: str = ""
    uri: str = ""
    format: str = "mp4"


# ---------------------------------------------------------------------------
# Content / Metrics
# ---------------------------------------------------------------------------

class HighlightContent(BaseModel):
    criteria: str = Field("", description="Selection criteria used")
    clips: list[HighlightClip] = Field(default_factory=list)
    compiled_video: VideoAsset = Field(default_factory=VideoAsset)


class HighlightMetrics(BaseModel):
    clip_count: int = 0
    total_highlight_seconds: float = 0.0


# ---------------------------------------------------------------------------
# Top-level I/O
# ---------------------------------------------------------------------------

class HighlightAgentInput(BaseModel):
    """Input payload for HighlightAgent.

    ``source_video_path``: the video to extract highlights from.
    ``analysis_json_text``: optional VideoAnalysisAgent output as JSON text
      for informed selection.
    ``criteria``: what kind of highlights to extract (e.g. 'action scenes',
      'emotional moments', 'best visual shots').
    """

    source_video_path: str = ""
    analysis_json_text: str = ""
    criteria: str = ""


class HighlightAgentOutput(BaseModel):
    """Output payload for HighlightAgent."""

    meta: Meta = Field(default_factory=Meta)
    content: HighlightContent = Field(default_factory=HighlightContent)
    metrics: HighlightMetrics = Field(default_factory=HighlightMetrics)
