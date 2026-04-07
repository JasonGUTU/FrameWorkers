"""Schema definitions for VideoAgent input / output interfaces."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..common_schema import ArtifactCaption, ImageReferenceEntry, Meta


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
    fps: int = 24


class ShotSegment(BaseModel):
    """Minimal video generation unit — one shot rendered to a clip."""

    shot_id: str = ""
    order: int = 0
    video_asset: VideoAsset = Field(default_factory=VideoAsset)
    # Filled by VideoMaterializer: main prompt and JSON-serialized consistency_constraints.
    video_generation_prompt: str = ""
    video_generation_constraints_json: str = ""


class TransitionPlan(BaseModel):
    from_shot_id: str = ""
    to_shot_id: str = ""
    transition_type: str = "cut"  # cut | dissolve | fade | soft


class SceneClipAsset(BaseModel):
    """Scene-level assembled clip."""

    asset_id: str = ""
    uri: str = ""
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


# ---------------------------------------------------------------------------
# Top-level I/O
# ---------------------------------------------------------------------------

class VideoPackage(BaseModel):
    """Full Video Package asset."""

    meta: Meta = Field(default_factory=Meta)
    content: VideoContent = Field(default_factory=VideoContent)
    metrics: VideoMetrics = Field(default_factory=VideoMetrics)
    artifact_caption: ArtifactCaption = Field(default_factory=ArtifactCaption)
    # Per-clip captions keyed by sys_id (e.g. "clip_sh_001", "clip_final").
    # Populated by recompute_metrics(); read by asset_manager for per-artifact registry entries.
    # Excluded from JSON snapshot to keep persisted files clean.
    per_artifact_captions: dict = Field(default_factory=dict, exclude=True)


# --- Input types ---

class VideoAgentInput(BaseModel):
    """Input payload for VideoAgent.

    Carries everything VideoAgent (LLM-free skeleton-builder) and the
    VideoMaterializer need:

    - ``screenplay``: the structured screenplay payload (selected via the
      ``[screenplay]`` label).
    - ``keyframes_metadata``: the keyframes_package payload from the
      keyframe step (selected via the ``[keyframes_metadata]`` label).
      Materializer reads ``prompt_summary`` and ``video_motion_hint`` from
      it for each shot.
    - ``shot_stills``: the rendered L3 starting-frame images for each shot
      (selected via the ``[shot_stills]`` collection label). Each entry
      carries a ``path`` and a ``scope`` like ``"shot:sh_001"`` so the
      materializer can pair an image with the right shot.
    """

    screenplay: dict = Field(default_factory=dict)
    keyframes_metadata: dict = Field(default_factory=dict)
    shot_stills: list[ImageReferenceEntry] = Field(default_factory=list)


class VideoAgentOutput(VideoPackage):
    """Output payload for VideoAgent (alias for VideoPackage)."""

    pass
