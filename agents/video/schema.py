"""Schema definitions for VideoAgent input / output interfaces."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..common_schema import ImageReferenceEntry, Meta


# ---------------------------------------------------------------------------
# Video sub-models
# ---------------------------------------------------------------------------

class ShotSemanticContext(BaseModel):
    """Per-shot language-neutral semantic context for video generation.

    This is the agent-layer mirror of the inference-layer dataclass of the
    same name in ``inference/generation/video_generators/types.py``. It
    carries per-shot information only — scene-level fields (location_id,
    time_of_day, environment_notes, style_notes, must_avoid) live on
    ``VideoScene.scene_context`` and are merged in by the materializer.

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

    # Camera / framing (from screenplay shot.camera)
    camera_angle: str = ""
    camera_movement: str = ""
    framing_notes: str = Field("", json_schema_extra={"creative": True})

    # Motion hints mirrored from keyframes_metadata for this shot.
    video_motion_hints: list[str] = Field(default_factory=list)

    # Dialogue + delivery tone mirrored from screenplay shot.text /
    # shot.emotion_hint for spoken shots (block_type in {dialogue,
    # narration, monologue}). Empty for action shots. These drive the
    # video-generation backend's native speech + lip-sync when
    # ``generate_audio=True`` — see
    # ``inference/generation/video_generators/service.py:_compose_prompt``.
    dialogue_text: str = Field("", json_schema_extra={"creative": True})
    emotion_hint: str = ""

    # ISO 639-1 code mirrored from upstream screenplay.meta.language.
    # Threaded into Kling's prompt by FalVideoService._compose_prompt so
    # ALL voiced content (explicit dialogue + ambient battle voices the
    # model may auto-fill on action shots) comes out in one language.
    # Empty disables the directive.
    language: str = ""


class ShotSegment(BaseModel):
    """Minimal video generation unit — one shot rendered to a clip."""

    shot_id: str = ""
    # LLM-authored per-shot semantic context. Mirrored from upstream
    # screenplay + keyframes_metadata via the agent's single LLM call.
    # Materializer reads these via attribute access, NEVER from upstream
    # payloads.
    semantic_context: ShotSemanticContext = Field(default_factory=ShotSemanticContext)
    # Per-shot render duration in seconds. The Kling I2V backend only
    # accepts 5 or 10 (string enum) and silently rounds anything else,
    # so the LLM is instructed to choose between the two — typically by
    # dividing the screenplay scene-level estimated_duration_seconds
    # across shots. Defaults to 5 when the LLM omits the field.
    duration_sec: float = 5.0


class TransitionPlan(BaseModel):
    from_shot_id: str = ""
    to_shot_id: str = ""
    transition_type: str = "cut"  # cut | dissolve | fade | soft


class SceneContext(BaseModel):
    """Scene-level context shared by every shot in the scene.

    Moved up from per-shot ``ShotSemanticContext`` to eliminate
    LLM-authored duplication across shots. The materializer merges this
    into each shot's inference-layer semantic context before calling
    VideoService.
    """

    location_id: str = ""
    time_of_day: str = ""
    environment_notes: list[str] = Field(default_factory=list)
    style_notes: list[str] = Field(default_factory=list)
    must_avoid: list[str] = Field(default_factory=list)


class VideoScene(BaseModel):
    scene_id: str = ""
    order: int = 0
    scene_context: SceneContext = Field(default_factory=SceneContext)
    shot_segments: list[ShotSegment] = Field(default_factory=list)
    transition_plan: list[TransitionPlan] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Video content
# ---------------------------------------------------------------------------

class VideoContent(BaseModel):
    scenes: list[VideoScene] = Field(default_factory=list)


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
