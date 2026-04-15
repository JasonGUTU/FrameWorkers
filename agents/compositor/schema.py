"""Schema definitions for CompositorAgent input / output interfaces."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..common_schema import Meta


# ---------------------------------------------------------------------------
# Composition sub-models
# ---------------------------------------------------------------------------

class TransitionSpec(BaseModel):
    """Transition between two shots."""

    from_shot_id: str = ""
    to_shot_id: str = ""
    transition_type: str = Field("cut", description="cut | crossfade | fade_black | wipe")
    duration_ms: int = Field(0, description="Transition duration in milliseconds (0 for cut)")


class ColorGradeSpec(BaseModel):
    """Global color grading specification."""

    brightness: float = Field(0.0, description="Brightness adjustment -1.0 to 1.0")
    contrast: float = Field(0.0, description="Contrast adjustment -1.0 to 1.0")
    saturation: float = Field(0.0, description="Saturation adjustment -1.0 to 1.0")
    tone: str = Field("", description="Overall tone description (e.g. warm, cool, cinematic)")


class SubtitleStyle(BaseModel):
    """Subtitle rendering style."""

    font_size: int = Field(24, description="Font size in pixels")
    font_color: str = Field("#FFFFFF", description="Font color hex")
    outline_color: str = Field("#000000", description="Outline/shadow color hex")
    position: str = Field("bottom", description="Position: bottom | top")
    burn_in: bool = Field(True, description="True = hardcode into video, False = soft embed")


class CompositionPlan(BaseModel):
    """The LLM-planned composition specification."""

    transitions: list[TransitionSpec] = Field(default_factory=list)
    color_grade: ColorGradeSpec = Field(default_factory=ColorGradeSpec)
    subtitle_style: SubtitleStyle = Field(default_factory=SubtitleStyle)
    output_resolution: str = Field("1920x1080", description="Output resolution WxH")
    output_fps: int = Field(30, description="Output frame rate")
    output_format: str = Field("mp4", description="Output container format")


class DeliveryAsset(BaseModel):
    """Pointer to the final composited video file."""

    asset_id: str = ""
    uri: str = ""
    format: str = "mp4"
    resolution: str = ""
    duration_seconds: float = 0.0


# ---------------------------------------------------------------------------
# Content / Metrics
# ---------------------------------------------------------------------------

class CompositorContent(BaseModel):
    plan: CompositionPlan = Field(default_factory=CompositionPlan)
    delivery_asset: DeliveryAsset = Field(default_factory=DeliveryAsset)


class CompositorMetrics(BaseModel):
    transition_count: int = 0
    has_subtitles: bool = False
    has_audio: bool = False


# ---------------------------------------------------------------------------
# Top-level I/O
# ---------------------------------------------------------------------------

class CompositorAgentInput(BaseModel):
    """Input payload for CompositorAgent.

    The LLM receives screenplay + video + audio + subtitle data as JSON
    text blobs and plans the composition (transitions, color grade,
    subtitle style).  The materializer then executes the plan via FFmpeg.
    """

    screenplay_json_text: str = ""
    video_json_text: str = ""
    audio_json_text: str = ""
    subtitle_json_text: str = ""
    video_file_path: str = ""
    audio_file_path: str = ""


class CompositorAgentOutput(BaseModel):
    """Output payload for CompositorAgent."""

    meta: Meta = Field(default_factory=Meta)
    content: CompositorContent = Field(default_factory=CompositorContent)
    metrics: CompositorMetrics = Field(default_factory=CompositorMetrics)
