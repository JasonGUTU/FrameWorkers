"""Schema definitions for ScreenplayAgent input / output interfaces."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..common_schema import Meta, DurationEstimate


# ---------------------------------------------------------------------------
# Screenplay sub-models
# ---------------------------------------------------------------------------

class ContinuityRefs(BaseModel):
    props: list[str] = Field(default_factory=list)
    wardrobe_character_ids: list[str] = Field(default_factory=list)


class Block(BaseModel):
    """Narrative atom — the smallest indivisible narrative unit in a scene."""

    block_id: str = ""
    block_type: str = ""  # action | dialogue | narration | monologue | beat
    character_id: str = ""
    character_name: str = ""
    text: str = Field("", json_schema_extra={"creative": True})
    continuity_refs: ContinuityRefs = Field(default_factory=ContinuityRefs)


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


class ScreenplayScene(BaseModel):
    scene_id: str = ""
    order: int = 0
    linked_story_step_id: str = ""
    heading: SceneHeading = Field(default_factory=SceneHeading)
    summary: str = Field("", json_schema_extra={"creative": True})
    estimated_duration: DurationEstimate = Field(default_factory=DurationEstimate)
    continuity: SceneContinuity = Field(default_factory=SceneContinuity)
    blocks: list[Block] = Field(default_factory=list)
    scene_end: SceneEnd = Field(default_factory=SceneEnd)


# ---------------------------------------------------------------------------
# Screenplay content
# ---------------------------------------------------------------------------

class ScreenplayContent(BaseModel):
    title: str = Field("", json_schema_extra={"creative": True})
    scenes: list[ScreenplayScene] = Field(default_factory=list)


class ScreenplayMetrics(BaseModel):
    estimated_total_duration_sec: float = 0.0
    sum_scene_duration_sec: float = 0.0
    scene_count: int = 0
    dialogue_block_count: int = 0
    action_block_count: int = 0


# ---------------------------------------------------------------------------
# Top-level I/O
# ---------------------------------------------------------------------------

class Screenplay(BaseModel):
    """Full Screenplay asset."""

    meta: Meta = Field(default_factory=Meta)
    content: ScreenplayContent = Field(default_factory=ScreenplayContent)
    metrics: ScreenplayMetrics = Field(default_factory=ScreenplayMetrics)


class ScreenplayConstraints(BaseModel):
    target_duration_sec: float = 60.0
    language: str = "en"


class ScreenplayAgentInput(BaseModel):
    """Input payload for ScreenplayAgent.

    When ``user_provided_text`` is non-empty the agent operates in
    **structuring mode**: it converts the raw user-provided screenplay
    text into the required JSON schema instead of generating from a
    story blueprint.  ``story_blueprint`` may be empty in this case.
    """

    project_id: str = ""
    draft_id: str = ""
    story_blueprint: dict = Field(default_factory=dict)
    constraints: ScreenplayConstraints = Field(default_factory=ScreenplayConstraints)
    user_provided_text: str = Field(
        default="",
        description=(
            "Raw screenplay text provided by the user.  When non-empty "
            "the agent structures this text into ScreenplayAgentOutput "
            "instead of generating from story_blueprint."
        ),
    )


class ScreenplayAgentOutput(Screenplay):
    """Output payload for ScreenplayAgent (alias for Screenplay)."""

    pass
