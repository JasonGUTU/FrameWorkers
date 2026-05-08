"""Schema definitions for ScreenplayAgent input / output interfaces.

Unified screenplay: each scene has ``shots[]`` — one row per continuous take,
combining narrative (former ``Block``) and visual plan (former storyboard ``Shot``).
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from ..common_schema import Meta


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
    """One continuous take: script line + shot planning.

    For spoken shots (block_type ∈ {dialogue, narration, monologue}) the
    ``text`` field is the **verbatim line** the on-screen character
    speaks aloud — it goes straight into the video-generation backend's
    prompt when ``generate_audio=True`` is enabled (see ``FalVideoService.
    _compose_prompt`` and CLAUDE.md's audio architecture section). For
    action shots it is a visible action description, not spoken.
    """

    shot_id: str = ""
    order: int = 0
    block_type: str = ""  # action | dialogue | narration | monologue
    character_id: str = ""
    character_name: str = ""
    text: str = Field("", json_schema_extra={"creative": True})
    # Short delivery-tone descriptor fed to the video-generation backend
    # so it speaks the line with the right emotion (calm / neutral /
    # sad / angry / whispered / excited / warm / tense / urgent). Empty
    # for action shots and for spoken shots where the tone is not strong
    # enough to specify.
    emotion_hint: str = Field("", json_schema_extra={"creative": True})
    continuity_refs: ContinuityRefs = Field(default_factory=ContinuityRefs)
    shot_type: str = "medium"
    camera: Camera = Field(default_factory=Camera)
    visual_goal: str = Field("", json_schema_extra={"creative": True})
    action_focus: str = Field("", json_schema_extra={"creative": True})
    characters_in_frame: list[str] = Field(default_factory=list)
    props_in_frame: list[str] = Field(default_factory=list)
    keyframe_plan: KeyframePlan = Field(default_factory=KeyframePlan)

    @field_validator("props_in_frame", "characters_in_frame", mode="before")
    @classmethod
    def _coerce_id_list(cls, v):
        """Tolerate LLM drift: schema declares list[str] (just the ids), but
        the LLM occasionally emits list[{id_field, name_field, ...}] dicts
        — especially in bilingual prompts where it wants to attach the
        readable name. Pull the id field out and discard the rest so the
        downstream str-list contract holds.
        """
        if not isinstance(v, list):
            return v
        out: list[str] = []
        for item in v:
            if isinstance(item, dict):
                for key in ("prop_id", "character_id", "id"):
                    val = item.get(key)
                    if isinstance(val, str):
                        out.append(val)
                        break
            else:
                out.append(item)
        return out


class ScreenplayScene(BaseModel):
    scene_id: str = ""
    order: int = 0
    linked_story_step_id: str = ""
    heading: SceneHeading = Field(default_factory=SceneHeading)
    summary: str = Field("", json_schema_extra={"creative": True})
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
    scene_count: int = 0
    shot_count_total: int = 0
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


class ScreenplayAgentInput(BaseModel):
    """Input payload for ScreenplayAgent — univa-style JSON-text pass-through.

    ``story_json_text`` is the **entire** upstream story_blueprint payload
    serialized as a raw JSON text blob. ScreenplayAgent's LLM reads this
    text directly and reasons about whatever shape the upstream happens
    to produce — there is NO field-name unpacking in ``build_input`` or
    in the agent. This removes the hidden string-keyed coupling between
    ``StoryBlueprintContent``'s internal field names and ScreenplayAgent's
    consumer code: any well-formed JSON object can be consumed, as long
    as the LLM can read and dramatize it.

    Selected by InputResolver via the ``[story]`` label. This agent has
    NO directive label — any user-level intent flows through the upstream
    re-run mechanism (the Director re-runs the story step with the new
    brief; the updated story_blueprint reaches us via the same ``[story]``
    label).
    """

    story_json_text: str = ""


class ScreenplayAgentOutput(Screenplay):
    pass
