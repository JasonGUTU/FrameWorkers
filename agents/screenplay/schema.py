"""Schema definitions for ScreenplayAgent input / output interfaces.

Unified screenplay: each scene has ``shots[]`` — one row per continuous take,
combining narrative (former ``Block``) and visual plan (former storyboard ``Shot``).
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..common_schema import Meta, DurationEstimate


# ---------------------------------------------------------------------------
# Continuity & heading (unchanged)
# ---------------------------------------------------------------------------


class ContinuityRefs(BaseModel):
    props: list[str] = Field(default_factory=list)
    wardrobe_character_ids: list[str] = Field(default_factory=list)


class CharacterWardrobeNote(BaseModel):
    character_id: str = ""
    wardrobe: str = Field("", json_schema_extra={"creative": True})
    must_keep: list[str] = Field(default_factory=list, json_schema_extra={"creative": True})


class SceneContinuity(BaseModel):
    props_present: list[str] = Field(default_factory=list)
    character_wardrobe_notes: list[CharacterWardrobeNote] = Field(default_factory=list)
    must_keep_scene_facts: list[str] = Field(default_factory=list, json_schema_extra={"creative": True})


class SceneHeading(BaseModel):
    location_id: str = ""
    location_name: str = ""
    interior_exterior: str = "INT"  # INT | EXT
    time_of_day: str = "DAY"  # DAY | NIGHT | CUSTOM


class SceneEnd(BaseModel):
    turn: str = Field("", json_schema_extra={"creative": True})
    emotional_shift: str = Field("", json_schema_extra={"creative": True})


# ---------------------------------------------------------------------------
# Visual / consistency (from former storyboard)
# ---------------------------------------------------------------------------


class Camera(BaseModel):
    angle: str = "eye_level"
    movement: str = "static"
    framing_notes: str = Field("", json_schema_extra={"creative": True})


class KeyframePlan(BaseModel):
    keyframe_count: int = 1
    keyframe_notes: list[str] = Field(default_factory=list, json_schema_extra={"creative": True})


class LocationLock(BaseModel):
    location_id: str = ""
    time_of_day: str = "DAY"
    environment_notes: list[str] = Field(default_factory=list, json_schema_extra={"creative": True})


class CharacterLock(BaseModel):
    character_id: str = ""
    identity_notes: list[str] = Field(default_factory=list, json_schema_extra={"creative": True})
    wardrobe_notes: list[str] = Field(default_factory=list, json_schema_extra={"creative": True})
    must_keep: list[str] = Field(default_factory=list, json_schema_extra={"creative": True})


class PropLock(BaseModel):
    prop_id: str = ""
    prop_name: str = ""
    must_keep: list[str] = Field(default_factory=list, json_schema_extra={"creative": True})


class StyleLock(BaseModel):
    global_style_notes: list[str] = Field(default_factory=list, json_schema_extra={"creative": True})
    must_avoid: list[str] = Field(default_factory=list, json_schema_extra={"creative": True})


class SceneConsistencyPack(BaseModel):
    location_lock: LocationLock = Field(default_factory=LocationLock)
    character_locks: list[CharacterLock] = Field(default_factory=list)
    props_lock: list[PropLock] = Field(default_factory=list)
    style_lock: StyleLock = Field(default_factory=StyleLock)


# ---------------------------------------------------------------------------
# Unified shot = narrative + visual
# ---------------------------------------------------------------------------


class ScriptShot(BaseModel):
    """One continuous take: script line + shot planning."""

    shot_id: str = ""
    order: int = 0
    block_type: str = ""  # action | dialogue | narration | monologue | beat
    character_id: str = ""
    character_name: str = ""
    text: str = Field("", json_schema_extra={"creative": True})
    continuity_refs: ContinuityRefs = Field(default_factory=ContinuityRefs)
    estimated_duration_sec: float = 3.0
    shot_type: str = "medium"
    camera: Camera = Field(default_factory=Camera)
    visual_goal: str = Field("", json_schema_extra={"creative": True})
    action_focus: str = Field("", json_schema_extra={"creative": True})
    characters_in_frame: list[str] = Field(default_factory=list)
    props_in_frame: list[str] = Field(default_factory=list)
    keyframe_plan: KeyframePlan = Field(default_factory=KeyframePlan)


class ScreenplaySceneSource(BaseModel):
    screenplay_asset_id: str = ""
    screenplay_scene_id: str = ""


class ScreenplayScene(BaseModel):
    scene_id: str = ""
    order: int = 0
    linked_story_step_id: str = ""
    source: ScreenplaySceneSource = Field(default_factory=ScreenplaySceneSource)
    heading: SceneHeading = Field(default_factory=SceneHeading)
    summary: str = Field("", json_schema_extra={"creative": True})
    estimated_duration: DurationEstimate = Field(default_factory=DurationEstimate)
    continuity: SceneContinuity = Field(default_factory=SceneContinuity)
    scene_consistency_pack: SceneConsistencyPack = Field(default_factory=SceneConsistencyPack)
    scene_end: SceneEnd = Field(default_factory=SceneEnd)
    shots: list[ScriptShot] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Screenplay content
# ---------------------------------------------------------------------------


class ScreenplayContent(BaseModel):
    title: str = Field("", json_schema_extra={"creative": True})
    scenes: list[ScreenplayScene] = Field(default_factory=list)


class ScreenplayMetrics(BaseModel):
    target_duration_sec: float = 0.0
    estimated_total_duration_sec: float = 0.0
    sum_scene_duration_sec: float = 0.0
    scene_count: int = 0
    shot_count_total: int = 0
    sum_shot_duration_sec: float = 0.0
    avg_shots_per_scene: float = 0.0
    dialogue_block_count: int = 0  # shots with block_type dialogue (name kept for metrics compat)
    action_block_count: int = 0  # shots with block_type action


# ---------------------------------------------------------------------------
# Top-level I/O
# ---------------------------------------------------------------------------


class Screenplay(BaseModel):
    meta: Meta = Field(default_factory=Meta)
    content: ScreenplayContent = Field(default_factory=ScreenplayContent)
    metrics: ScreenplayMetrics = Field(default_factory=ScreenplayMetrics)


class ScreenplayConstraints(BaseModel):
    target_duration_sec: float = 10.0
    max_shots_per_scene: int = 12
    language: str = "en"


class ScreenplayAgentInput(BaseModel):
    """Input payload for ScreenplayAgent."""

    story_blueprint: dict = Field(default_factory=dict)
    constraints: ScreenplayConstraints = Field(default_factory=ScreenplayConstraints)
    user_provided_text: str = Field(
        default="",
        description=(
            "Raw screenplay text. When non-empty the agent structures this text "
            "into ScreenplayAgentOutput instead of generating from story_blueprint."
        ),
    )


class ScreenplayAgentOutput(Screenplay):
    pass
