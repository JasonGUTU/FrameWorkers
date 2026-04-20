"""Schema definitions for VideoAnalysisAgent input / output interfaces."""

from __future__ import annotations

import mimetypes
import os

from pydantic import BaseModel, Field, field_validator

from ..common_schema import Meta


# ---------------------------------------------------------------------------
# Analysis sub-models
# ---------------------------------------------------------------------------

class SceneSegment(BaseModel):
    """A detected scene segment in the video."""

    scene_id: str = ""
    start_time: float = Field(0.0, description="Start time in seconds")
    end_time: float = Field(0.0, description="End time in seconds")
    description: str = Field("", description="Visual description of this scene")
    setting: str = Field("", description="Location / environment")
    mood: str = Field("", description="Emotional tone / atmosphere")
    entities: list[str] = Field(
        default_factory=list,
        description="People, objects, or notable elements in this scene"
    )
    tension_score: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
        description=(
            "Narrative / dramatic intensity 0–1 (0 = calm/exposition, "
            "1 = peak climax / reversal / shock). Quiet dialogue ≈ 0.1–0.3, "
            "rising conflict ≈ 0.4–0.6, action / emotional peaks ≈ 0.7–1.0."
        ),
    )
    is_climax_candidate: bool = Field(
        False,
        description=(
            "True iff this scene is a plausible climax / major reversal / "
            "emotional high-point. Typically 1–3 scenes per video, "
            "sometimes zero (slice-of-life / purely informational footage)."
        ),
    )


class VideoSummary(BaseModel):
    """High-level summary of the video content."""

    title: str = Field("", description="Suggested title for the video")
    summary: str = Field("", description="2-4 sentence overall summary")
    genre: str = Field("", description="Content genre/category")
    language: str = Field("", description="Detected spoken language, if any")
    duration_seconds: float = Field(0.0, description="Total video duration")


# ---------------------------------------------------------------------------
# Content / Metrics
# ---------------------------------------------------------------------------

class VideoAnalysisContent(BaseModel):
    video_summary: VideoSummary = Field(default_factory=VideoSummary)
    scenes: list[SceneSegment] = Field(default_factory=list)


class VideoAnalysisMetrics(BaseModel):
    scene_count: int = 0
    duration_seconds: float = 0.0
    entity_count: int = 0


# ---------------------------------------------------------------------------
# Top-level I/O
# ---------------------------------------------------------------------------

class VideoAnalysisAgentInput(BaseModel):
    """Input payload for VideoAnalysisAgent.

    ``source_video_path``: REQUIRED absolute path to an existing video file
    (``video/*`` MIME). VideoAnalysisAgent performs **video** analysis, not
    image analysis — the path MUST resolve to a video file; images, audio,
    empty strings, and missing files are all rejected at validation time.
    """

    source_video_path: str = Field(
        ...,
        min_length=1,
        description="Absolute path to an existing video/* file.",
    )

    @field_validator("source_video_path")
    @classmethod
    def _must_be_existing_video_file(cls, v: str) -> str:
        if not v:
            raise ValueError(
                "source_video_path is required and must be a non-empty path; "
                "VideoAnalysisAgent only analyzes real video bytes — it does "
                "NOT accept a text description in place of a video."
            )
        if not os.path.isfile(v):
            raise ValueError(
                f"source_video_path does not point to an existing file: {v!r}"
            )
        mime, _ = mimetypes.guess_type(v)
        if not mime or not mime.startswith("video/"):
            raise ValueError(
                f"source_video_path must be a video/* file (got mime={mime!r} "
                f"for path {v!r}); this analysis step does not analyze images "
                f"— use the image-intake step for image modality."
            )
        return v


class VideoAnalysisAgentOutput(BaseModel):
    """Output payload for VideoAnalysisAgent."""

    meta: Meta = Field(default_factory=Meta)
    content: VideoAnalysisContent = Field(default_factory=VideoAnalysisContent)
    metrics: VideoAnalysisMetrics = Field(default_factory=VideoAnalysisMetrics)
