"""Schema definitions for KeyFrameAgent input / output interfaces."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..common_schema import ImageReferenceEntry, Meta


# ---------------------------------------------------------------------------
# KeyFrame sub-models
# ---------------------------------------------------------------------------

class Keyframe(BaseModel):
    """A single generated keyframe image for a shot.

    ``prompt_summary`` is for **image** APIs only (L3 still). ``video_motion_hint``
    is for **image-to-video** text: subtle motion / temporal intent, kept separate
    to avoid duplicating long still descriptions in the video model prompt.
    """

    prompt_summary: str = Field("", json_schema_extra={"creative": True})
    video_motion_hint: str = Field(
        "",
        json_schema_extra={"creative": True},
        description="Short I2V motion cue; not sent to image generation.",
    )


class ShotKeyframes(BaseModel):
    """Keyframes for a single shot.

    ``characters_in_frame`` / ``props_in_frame`` are mirrored from the
    upstream screenplay shot. They tell the L3 materializer which L2
    character / prop anchors to bundle as multi-image references for the
    shot's i2i edit, so character / prop identity is preserved without
    relying on text-only cues.
    """

    shot_id: str = ""
    characters_in_frame: list[str] = Field(default_factory=list)
    props_in_frame: list[str] = Field(default_factory=list)
    keyframes: list[Keyframe] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Stability keyframes (scene-level anchors)
# ---------------------------------------------------------------------------

class StabilityAnchorKeyframe(BaseModel):
    """Unified stability anchor for characters, locations, and props."""

    entity_id: str = ""  # char_001, loc_001, prop_001
    prompt_summary: str = Field("", json_schema_extra={"creative": True})
    # Runtime channel for user-uploaded reference image paths. Populated
    # by ``KeyFrameAgent._prefill_reference_images`` after the LLM call,
    # read by ``KeyframeMaterializer`` L1 pre-check loop to skip t2i when
    # a reference image is supplied. Persisted in the JSON artifact —
    # cannot be ``Field(exclude=True)`` because base_agent feeds the
    # materializer ``output.model_dump(...)``, and Pydantic v2 honors
    # field-level exclude unconditionally on every dump variant.
    reference_image_uri: str = ""


class StabilityKeyframes(BaseModel):
    characters: list[StabilityAnchorKeyframe] = Field(default_factory=list)
    locations: list[StabilityAnchorKeyframe] = Field(default_factory=list)
    props: list[StabilityAnchorKeyframe] = Field(default_factory=list)


class KeyframeScene(BaseModel):
    scene_id: str = ""
    stability_keyframes: StabilityKeyframes = Field(default_factory=StabilityKeyframes)
    shots: list[ShotKeyframes] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# KeyFrames content
# ---------------------------------------------------------------------------

class KeyframesContent(BaseModel):
    global_anchors: StabilityKeyframes = Field(default_factory=StabilityKeyframes)
    scenes: list[KeyframeScene] = Field(default_factory=list)
    # LLM-authored: mirrored from the upstream screenplay's scene-level
    # style_lock (aggregated across scenes, deduped). KeyframeMaterializer
    # reads these directly from the agent's own output.
    style_notes: list[str] = Field(default_factory=list)
    must_avoid: list[str] = Field(default_factory=list)


class KeyframesMetrics(BaseModel):
    scene_count: int = 0
    shot_count: int = 0
    keyframe_count_total: int = 0
    avg_keyframes_per_shot: float = 0.0
    global_character_anchor_count: int = 0
    global_location_anchor_count: int = 0
    global_prop_anchor_count: int = 0
    stability_character_keyframe_count: int = 0
    stability_location_keyframe_count: int = 0
    stability_prop_keyframe_count: int = 0


# ---------------------------------------------------------------------------
# Top-level I/O
# ---------------------------------------------------------------------------

class KeyframesPackage(BaseModel):
    """Full Keyframes Package asset."""

    meta: Meta = Field(default_factory=Meta)
    content: KeyframesContent = Field(default_factory=KeyframesContent)
    metrics: KeyframesMetrics = Field(default_factory=KeyframesMetrics)
    # Per-media-artifact captions keyed by sys_id (e.g. "img_char_001_global").
    # Populated by recompute_metrics(); read by ArtifactWriter to build ArtifactRef entries.
    # Excluded from JSON snapshot to keep persisted files clean.


# --- Input types ---

class KeyFrameAgentInput(BaseModel):
    """Input payload for KeyFrameAgent — univa-style JSON-text pass-through.

    ``screenplay_json_text`` is the **entire** upstream screenplay payload
    serialized as a raw JSON text blob. This agent's LLM reads this text
    directly and reasons about whatever shape the upstream happens to
    produce — there is NO field-name unpacking in ``build_input`` or in
    the agent code. This removes the string-keyed coupling between the
    upstream screenplay's internal field names and this consumer.

    ``character_references`` / ``location_references`` / ``style_references``
    are typed image reference lists selected via their respective labels;
    each entry carries a direct ``path`` that is pre-filled into the
    matching global anchor's ``reference_image_uri`` (Python-only field)
    so the materializer can use the user-supplied image instead of
    running text-to-image.
    """

    screenplay_json_text: str = ""
    character_references: list[ImageReferenceEntry] = Field(default_factory=list)
    location_references: list[ImageReferenceEntry] = Field(default_factory=list)
    prop_references: list[ImageReferenceEntry] = Field(default_factory=list)
    style_references: list[ImageReferenceEntry] = Field(default_factory=list)


class KeyFrameAgentOutput(KeyframesPackage):
    """Output payload for KeyFrameAgent (alias for KeyframesPackage)."""

    pass
