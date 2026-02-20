"""Schema definitions for KeyFrameAgent input / output interfaces."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..common_schema import Meta, ImageAsset


# ---------------------------------------------------------------------------
# KeyFrame sub-models
# ---------------------------------------------------------------------------

class KeyframeConstraintsApplied(BaseModel):
    characters_in_frame: list[str] = Field(default_factory=list)
    props_in_frame: list[str] = Field(default_factory=list)
    style_notes: list[str] = Field(default_factory=list)


class Keyframe(BaseModel):
    """A single generated keyframe image for a shot."""

    keyframe_id: str = ""
    order: int = 0
    image_asset: ImageAsset = Field(default_factory=ImageAsset)
    prompt_summary: str = Field("", json_schema_extra={"creative": True})
    constraints_applied: KeyframeConstraintsApplied = Field(
        default_factory=KeyframeConstraintsApplied
    )


class ShotKeyframeSource(BaseModel):
    storyboard_shot_id: str = ""
    linked_blocks: list[str] = Field(default_factory=list)


class ShotKeyframes(BaseModel):
    """Keyframes for a single shot."""

    shot_id: str = ""
    order: int = 0
    source: ShotKeyframeSource = Field(default_factory=ShotKeyframeSource)
    estimated_duration_sec: float = 3.0
    keyframes: list[Keyframe] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Stability keyframes (scene-level anchors)
# ---------------------------------------------------------------------------

class StabilityAnchorKeyframe(BaseModel):
    """Unified stability anchor for characters, locations, and props."""

    entity_type: str = ""  # character | location | prop
    entity_id: str = ""  # char_001, loc_001, prop_001
    display_name: str = ""  # human-readable name (props only)
    purpose: str = ""
    keyframe_id: str = ""
    image_asset: ImageAsset = Field(default_factory=ImageAsset)
    prompt_summary: str = Field("", json_schema_extra={"creative": True})


class StabilityKeyframes(BaseModel):
    characters: list[StabilityAnchorKeyframe] = Field(default_factory=list)
    locations: list[StabilityAnchorKeyframe] = Field(default_factory=list)
    props: list[StabilityAnchorKeyframe] = Field(default_factory=list)


class KeyframeSceneSource(BaseModel):
    storyboard_asset_id: str = ""
    storyboard_scene_id: str = ""


class KeyframeScene(BaseModel):
    scene_id: str = ""
    order: int = 0
    source: KeyframeSceneSource = Field(default_factory=KeyframeSceneSource)
    stability_keyframes: StabilityKeyframes = Field(default_factory=StabilityKeyframes)
    shots: list[ShotKeyframes] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# KeyFrames content
# ---------------------------------------------------------------------------

class KeyframesContent(BaseModel):
    global_anchors: StabilityKeyframes = Field(default_factory=StabilityKeyframes)
    scenes: list[KeyframeScene] = Field(default_factory=list)


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


# --- Input types ---

class KeyframeConstraints(BaseModel):
    image_resolution: str = "1024x576"
    image_format: str = "png"
    style_policy: str = "consistent_with_scene"


class KeyFrameAgentInput(BaseModel):
    """Input payload for KeyFrameAgent."""

    project_id: str = ""
    draft_id: str = ""
    storyboard: dict = Field(default_factory=dict)
    constraints: KeyframeConstraints = Field(default_factory=KeyframeConstraints)


class KeyFrameAgentOutput(KeyframesPackage):
    """Output payload for KeyFrameAgent (alias for KeyframesPackage)."""

    pass
