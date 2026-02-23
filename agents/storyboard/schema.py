"""Schema definitions for StoryboardAgent input / output interfaces."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..common_schema import Meta, DurationEstimate


# ---------------------------------------------------------------------------
# Storyboard sub-models
# ---------------------------------------------------------------------------

class Camera(BaseModel):
    angle: str = "eye_level"  # eye_level | high | low
    movement: str = "static"  # static | pan | tilt | dolly | handheld
    framing_notes: str = Field("", json_schema_extra={"creative": True})


class KeyframePlan(BaseModel):
    keyframe_count: int = 1
    keyframe_notes: list[str] = Field(default_factory=list, json_schema_extra={"creative": True})


class LocationLock(BaseModel):
    location_id: str = ""
    time_of_day: str = "DAY"  # DAY | NIGHT | CUSTOM
    environment_notes: list[str] = Field(default_factory=list, json_schema_extra={"creative": True})


class CharacterLock(BaseModel):
    character_id: str = ""
    identity_notes: list[str] = Field(default_factory=list, json_schema_extra={"creative": True})
    wardrobe_notes: list[str] = Field(default_factory=list, json_schema_extra={"creative": True})
    must_keep: list[str] = Field(default_factory=list, json_schema_extra={"creative": True})


class PropLock(BaseModel):
    prop_id: str = ""  # prop_001, prop_002, ...
    prop_name: str = ""  # human-readable display name
    must_keep: list[str] = Field(default_factory=list, json_schema_extra={"creative": True})


class StyleLock(BaseModel):
    global_style_notes: list[str] = Field(default_factory=list, json_schema_extra={"creative": True})
    must_avoid: list[str] = Field(default_factory=list, json_schema_extra={"creative": True})


class SceneConsistencyPack(BaseModel):
    """Consistency constraints that all shots within a scene must obey."""

    location_lock: LocationLock = Field(default_factory=LocationLock)
    character_locks: list[CharacterLock] = Field(default_factory=list)
    props_lock: list[PropLock] = Field(default_factory=list)
    style_lock: StyleLock = Field(default_factory=StyleLock)


class Shot(BaseModel):
    """Visual atom — one continuous camera take."""

    shot_id: str = ""
    order: int = 0
    linked_blocks: list[str] = Field(default_factory=list)
    estimated_duration_sec: float = 3.0
    shot_type: str = "medium"  # establishing | wide | medium | closeup | insert | over_the_shoulder
    camera: Camera = Field(default_factory=Camera)
    visual_goal: str = Field("", json_schema_extra={"creative": True})
    action_focus: str = Field("", json_schema_extra={"creative": True})
    characters_in_frame: list[str] = Field(default_factory=list)
    props_in_frame: list[str] = Field(default_factory=list)
    keyframe_plan: KeyframePlan = Field(default_factory=KeyframePlan)


class StoryboardSceneSource(BaseModel):
    screenplay_asset_id: str = ""
    screenplay_scene_id: str = ""


class StoryboardScene(BaseModel):
    scene_id: str = ""
    order: int = 0
    source: StoryboardSceneSource = Field(default_factory=StoryboardSceneSource)
    estimated_duration: DurationEstimate = Field(default_factory=DurationEstimate)
    scene_consistency_pack: SceneConsistencyPack = Field(
        default_factory=SceneConsistencyPack
    )
    shots: list[Shot] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Storyboard content
# ---------------------------------------------------------------------------

class StoryboardContent(BaseModel):
    scenes: list[StoryboardScene] = Field(default_factory=list)


class StoryboardMetrics(BaseModel):
    scene_count: int = 0
    shot_count_total: int = 0
    avg_shots_per_scene: float = 0.0
    sum_shot_duration_sec: float = 0.0
    duration_match_score: float = 0.0


# ---------------------------------------------------------------------------
# Top-level I/O
# ---------------------------------------------------------------------------

class Storyboard(BaseModel):
    """Full Storyboard asset."""

    meta: Meta = Field(default_factory=Meta)
    content: StoryboardContent = Field(default_factory=StoryboardContent)
    metrics: StoryboardMetrics = Field(default_factory=StoryboardMetrics)


class StoryboardConstraints(BaseModel):
    max_shots_per_scene: int = 12
    target_style_notes: str = ""
    language: str = "en"


class StoryboardAgentInput(BaseModel):
    """Input payload for StoryboardAgent.

    StoryboardAgent always operates in **skeleton-first mode**: it
    pre-builds scene shells from the upstream screenplay and asks the
    LLM to fill creative fields (shots, consistency packs, etc.).
    """

    project_id: str = ""
    draft_id: str = ""
    screenplay: dict = Field(default_factory=dict)
    constraints: StoryboardConstraints = Field(default_factory=StoryboardConstraints)


class StoryboardAgentOutput(Storyboard):
    """Output payload for StoryboardAgent (alias for Storyboard)."""

    pass
