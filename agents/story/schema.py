"""Schema definitions for StoryAgent input / output interfaces."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..common_schema import DurationEstimate, Meta


# ---------------------------------------------------------------------------
# Story Blueprint sub-models
# ---------------------------------------------------------------------------

class StyleInfo(BaseModel):
    genre: list[str] = Field(default_factory=list, json_schema_extra={"creative": True})
    tone_keywords: list[str] = Field(default_factory=list, json_schema_extra={"creative": True})


class CastMember(BaseModel):
    character_id: str = ""
    name: str = Field("", json_schema_extra={"creative": True})
    role: str = ""  # protagonist | antagonist | support
    profile: str = Field("", json_schema_extra={"creative": True})
    motivation: str = Field("", json_schema_extra={"creative": True})
    flaw: str = Field("", json_schema_extra={"creative": True})


class Location(BaseModel):
    location_id: str = ""
    name: str = Field("", json_schema_extra={"creative": True})
    description: str = Field("", json_schema_extra={"creative": True})


class StoryArcStep(BaseModel):
    step_id: str = ""
    order: int = 0
    step_type: str = ""  # setup | inciting | turn | crisis | climax | resolution
    summary: str = Field("", json_schema_extra={"creative": True})
    conflict: str = Field("", json_schema_extra={"creative": True})
    turning_point: str = Field("", json_schema_extra={"creative": True})


class SceneOutlineItem(BaseModel):
    scene_id: str = ""
    order: int = 0
    linked_step_id: str = ""
    location_id: str = ""
    time_of_day_hint: str = "DAY"  # DAY | NIGHT | CUSTOM
    characters_present: list[str] = Field(default_factory=list)
    goal: str = Field("", json_schema_extra={"creative": True})
    conflict: str = Field("", json_schema_extra={"creative": True})
    turn: str = Field("", json_schema_extra={"creative": True})


# ---------------------------------------------------------------------------
# Story Blueprint content
# ---------------------------------------------------------------------------

class StoryBlueprintContent(BaseModel):
    logline: str = Field("", json_schema_extra={"creative": True})
    estimated_duration: DurationEstimate = Field(default_factory=DurationEstimate)
    style: StyleInfo = Field(default_factory=StyleInfo)
    cast: list[CastMember] = Field(default_factory=list)
    locations: list[Location] = Field(default_factory=list)
    story_arc: list[StoryArcStep] = Field(default_factory=list)
    scene_outline: list[SceneOutlineItem] = Field(default_factory=list)


class StoryMetrics(BaseModel):
    character_count: int = 0
    location_count: int = 0
    scene_count: int = 0


# ---------------------------------------------------------------------------
# Top-level I/O
# ---------------------------------------------------------------------------

class StoryBlueprint(BaseModel):
    """Full Story Blueprint asset."""

    meta: Meta = Field(default_factory=Meta)
    content: StoryBlueprintContent = Field(default_factory=StoryBlueprintContent)
    metrics: StoryMetrics = Field(default_factory=StoryMetrics)


class StoryAgentInput(BaseModel):
    """Input payload for StoryAgent.

    When ``user_provided_text`` is non-empty the agent operates in
    **structuring mode**: it converts a detailed story outline into
    the Story Blueprint JSON schema while preserving the user's
    characters, locations, and plot points.  ``draft_idea`` may be
    empty in this case.
    """

    project_id: str = ""
    draft_id: str = ""
    draft_idea: str = ""
    user_provided_text: str = Field(
        default="",
        description=(
            "When non-empty, StoryAgent enters structuring mode: "
            "the text is treated as a detailed story outline to be "
            "structured into a Story Blueprint, preserving the user's "
            "original characters, locations, and plot points verbatim."
        ),
    )


class StoryAgentOutput(StoryBlueprint):
    """Output payload for StoryAgent (alias for StoryBlueprint)."""

    pass
