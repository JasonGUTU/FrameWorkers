"""Schema definitions for VideoAgent input / output interfaces."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..common_schema import ImageReferenceEntry, Meta


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


class ShotSemanticContext(BaseModel):
    """Per-shot language-neutral semantic context for video generation.

    This is the agent-layer mirror of the inference-layer dataclass of the
    same name in ``inference/generation/video_generators/types.py``. It
    carries everything a video generation service needs to turn a
    starting keyframe + motion intent into a moving clip — and carries
    nothing else.

    All fields are **LLM-authored**: VideoAgent's LLM reads the upstream
    screenplay + keyframes_metadata JSON text blobs and mirrors the
    relevant per-shot information into this structure. VideoMaterializer
    then reads these fields from the agent's own output (no upstream
    payload lookup).
    """

    # Creative intent (from screenplay shot)
    shot_type: str = ""
    visual_goal: str = Field("", json_schema_extra={"creative": True})
    action_focus: str = Field("", json_schema_extra={"creative": True})
    characters_in_frame: list[str] = Field(default_factory=list)
    props_in_frame: list[str] = Field(default_factory=list)

    # Camera / framing (from screenplay shot.camera)
    camera_angle: str = ""
    camera_movement: str = ""
    framing_notes: str = Field("", json_schema_extra={"creative": True})

    # Scene-level context (from screenplay scene.scene_consistency_pack)
    scene_id: str = ""
    location_id: str = ""
    time_of_day: str = ""
    environment_notes: list[str] = Field(default_factory=list)
    style_notes: list[str] = Field(default_factory=list)
    must_avoid: list[str] = Field(default_factory=list)

    # Keyframe planning (from screenplay shot.keyframe_plan + keyframes_metadata)
    keyframe_notes: list[str] = Field(default_factory=list)
    keyframe_prompt_summaries: list[str] = Field(default_factory=list)
    video_motion_hints: list[str] = Field(default_factory=list)


class ShotSegment(BaseModel):
    """Minimal video generation unit — one shot rendered to a clip."""

    shot_id: str = ""
    order: int = 0
    video_asset: VideoAsset = Field(default_factory=VideoAsset)
    # LLM-authored per-shot semantic context. Mirrored from upstream
    # screenplay + keyframes_metadata via the agent's single LLM call.
    # Materializer reads these via attribute access, NEVER from upstream
    # payloads.
    semantic_context: ShotSemanticContext = Field(default_factory=ShotSemanticContext)
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
    # Per-clip captions keyed by sys_id (e.g. "clip_sh_001", "clip_final").
    # Populated by recompute_metrics(); read by ArtifactWriter for per-artifact registry entries.
    # Excluded from JSON snapshot to keep persisted files clean.


# --- Input types ---

class VideoAgentInput(BaseModel):
    """Input payload for VideoAgent — univa-style JSON-text pass-through.

    ``screenplay_json_text`` is the **entire** upstream screenplay payload
    serialized as a raw JSON text blob. ``keyframes_metadata_json_text``
    is the same for the upstream keyframe step's output. VideoAgent's
    LLM reads these two text blobs directly, mirrors the per-shot
    semantic information into its own ``ShotSegment.semantic_context``
    fields, and writes the structured output that the materializer
    consumes via typed attribute access.

    There is NO field-name unpacking in ``build_input`` or in the agent
    code — both inputs flow as opaque strings, eliminating the
    string-keyed coupling between upstream schemas (screenplay /
    keyframes_package) and the VideoAgent / VideoMaterializer code.

    ``shot_stills`` is a list of typed ``ImageReferenceEntry`` entries
    (each already carrying a direct ``path`` + ``scope`` like
    ``shot:sh_001``), selected by InputResolver via the ``[shot_stills]``
    collection label. Materializer pairs these with ShotSegments by
    matching scope → shot_id.
    """

    screenplay_json_text: str = ""
    keyframes_metadata_json_text: str = ""
    shot_stills: list[ImageReferenceEntry] = Field(default_factory=list)


class VideoAgentOutput(VideoPackage):
    """Output payload for VideoAgent (alias for VideoPackage)."""

    pass
