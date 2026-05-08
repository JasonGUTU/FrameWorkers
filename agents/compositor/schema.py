"""Schema definitions for CompositorAgent input / output interfaces."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..common_schema import Meta


# ---------------------------------------------------------------------------
# Composition sub-models
# ---------------------------------------------------------------------------

class ColorGradeSpec(BaseModel):
    """Global color grading specification."""

    brightness: float = Field(0.0, description="Brightness adjustment -1.0 to 1.0")
    contrast: float = Field(0.0, description="Contrast adjustment -1.0 to 1.0")
    saturation: float = Field(0.0, description="Saturation adjustment -1.0 to 1.0")


class SubtitleStyle(BaseModel):
    """Subtitle rendering style."""

    font_size: int = Field(24, description="Font size in pixels")
    font_color: str = Field("#FFFFFF", description="Font color hex")
    outline_color: str = Field("#000000", description="Outline/shadow color hex")
    burn_in: bool = Field(True, description="True = hardcode into video, False = soft embed")


class CompositionPlan(BaseModel):
    """The LLM-planned composition specification."""

    color_grade: ColorGradeSpec = Field(default_factory=ColorGradeSpec)
    subtitle_style: SubtitleStyle = Field(default_factory=SubtitleStyle)
    output_resolution: str = Field("1920x1080", description="Output resolution WxH")
    output_fps: int = Field(30, description="Output frame rate")


# ---------------------------------------------------------------------------
# Content / Metrics
# ---------------------------------------------------------------------------

class CompositorContent(BaseModel):
    plan: CompositionPlan = Field(default_factory=CompositionPlan)


class CompositorMetrics(BaseModel):
    has_subtitles: bool = False
    has_audio: bool = False


# ---------------------------------------------------------------------------
# Top-level I/O
# ---------------------------------------------------------------------------

class CompositorAgentInput(BaseModel):
    """Input payload for CompositorAgent.

    The LLM receives screenplay + video + audio + subtitle data as JSON
    text blobs and plans the composition (color grade, subtitle style).
    The materializer then executes the plan via FFmpeg.

    ``subtitle_json_texts`` is a list so bilingual / multilingual flows
    (subtitle step → translation step → this compositor) can pass every
    language track through for simultaneous burn-in.

    ``illustration_image_paths`` + ``segment_timing_json_text`` populate
    the slideshow-mode branch: when present (and video_package / video_file
    are absent), the materializer assembles the video track by ffmpeg-
    concat'ing still images with per-segment durations instead of muxing
    an existing mp4. Paths are already ordered by segment_id at build_input
    time so the materializer iterates them in render order without
    re-sorting.
    """

    screenplay_json_text: str = ""
    video_json_text: str = ""
    audio_json_text: str = ""
    subtitle_json_texts: list[str] = Field(default_factory=list)
    video_file_path: str = ""
    audio_file_path: str = ""
    illustration_image_paths: list[str] = Field(default_factory=list)
    segment_timing_json_text: str = ""


class CompositorAgentOutput(BaseModel):
    """Output payload for CompositorAgent."""

    meta: Meta = Field(default_factory=Meta)
    content: CompositorContent = Field(default_factory=CompositorContent)
    metrics: CompositorMetrics = Field(default_factory=CompositorMetrics)
