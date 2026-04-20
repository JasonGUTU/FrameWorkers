"""Schema definitions for StoryAgent input / output interfaces."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..common_schema import Meta


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
    """Input payload for StoryAgent — univa-style JSON-text pass-through.

    ``creative_brief_json_text`` is the **entire** upstream IntakeTextAgent
    payload serialized as a raw JSON text blob. StoryAgent's LLM reads
    this text directly and extracts the brief from whatever shape it
    finds (typically ``content.text``). There is NO field-name unpacking
    in ``build_input`` or in the agent — this removes the hidden
    string-keyed coupling between IntakeTextAgent's internal field names
    and StoryAgent's consumer code.

    ``reference_analysis_json_text`` is the optional VideoAnalysisAgent
    payload of an inspiration / reference video. When present the LLM
    should treat its genre / mood / entities / scene summaries as
    creative seeds for the new story (matching tone / template pacing),
    alongside the primary brief — enabling flows like "analyse this hit
    drama and write me a same-genre sequel story". Empty string when
    no reference analysis was routed in.
    """

    creative_brief_json_text: str = ""
    reference_analysis_json_text: str = ""


class StoryAgentOutput(StoryBlueprint):
    """Output payload for StoryAgent (alias for StoryBlueprint)."""

    pass
