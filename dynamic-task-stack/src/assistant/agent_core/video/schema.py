"""Schema definitions for VideoAgent input / output interfaces."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..common_schema import Meta


# ---------------------------------------------------------------------------
# Video sub-models
# ---------------------------------------------------------------------------

class VideoAsset(BaseModel):
    """Pointer to a generated video file."""

    asset_id: str = ""
    uri: str = ""
    width: int = 1024
    height: int = 576
    format: str = "mp4"
    duration_sec: float = 0.0
    fps: int = 24


class ShotSegment(BaseModel):
    """Minimal video generation unit — one shot rendered to a clip."""

    shot_id: str = ""
    order: int = 0
    estimated_duration_sec: float = 3.0
    actual_duration_sec: float = 0.0
    video_asset: VideoAsset = Field(default_factory=VideoAsset)


class TransitionPlan(BaseModel):
    from_shot_id: str = ""
    to_shot_id: str = ""
    transition_type: str = "cut"  # cut | dissolve | fade | soft
    duration_sec: float = 0.0


class SceneClipAsset(BaseModel):
    """Scene-level assembled clip."""

    asset_id: str = ""
    uri: str = ""
    scene_duration_sec: float = 0.0
    format: str = "mp4"


class VideoScene(BaseModel):
    scene_id: str = ""
    order: int = 0
    shot_segments: list[ShotSegment] = Field(default_factory=list)
    transition_plan: list[TransitionPlan] = Field(default_factory=list)
    scene_clip_asset: SceneClipAsset = Field(default_factory=SceneClipAsset)


# ---------------------------------------------------------------------------
# Video content
# ---------------------------------------------------------------------------

class VideoContent(BaseModel):
    scenes: list[VideoScene] = Field(default_factory=list)
    final_video_asset: VideoAsset = Field(default_factory=VideoAsset)


class VideoMetrics(BaseModel):
    scene_count: int = 0
    shot_segment_count: int = 0
    total_duration_sec: float = 0.0
    avg_shot_duration_sec: float = 0.0


# ---------------------------------------------------------------------------
# Top-level I/O
# ---------------------------------------------------------------------------

class VideoPackage(BaseModel):
    """Full Video Package asset."""

    meta: Meta = Field(default_factory=Meta)
    content: VideoContent = Field(default_factory=VideoContent)
    metrics: VideoMetrics = Field(default_factory=VideoMetrics)


# --- Input types ---

class VideoConstraints(BaseModel):
    fps: int = 24
    output_resolution: str = "1024x576"
    shot_motion_policy: str = "moderate"  # minimal | moderate | cinematic
    transition_policy: str = "cut"  # cut | soft


class VideoAgentInput(BaseModel):
    """Input payload for VideoAgent."""

    project_id: str = ""
    draft_id: str = ""
    storyboard: dict = Field(default_factory=dict)
    keyframes: dict = Field(default_factory=dict)
    constraints: VideoConstraints = Field(default_factory=VideoConstraints)


class VideoAgentOutput(VideoPackage):
    """Output payload for VideoAgent (alias for VideoPackage)."""

    pass
