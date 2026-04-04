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
    """A single generated keyframe image for a shot.

    ``prompt_summary`` is for **image** APIs only (L3 still). ``video_motion_hint``
    is for **image-to-video** text: subtle motion / temporal intent, kept separate
    to avoid duplicating long still descriptions in the video model prompt.
    """

    keyframe_id: str = ""
    order: int = 0
    image_asset: ImageAsset = Field(default_factory=ImageAsset)
    prompt_summary: str = Field("", json_schema_extra={"creative": True})
    video_motion_hint: str = Field(
        "",
        json_schema_extra={"creative": True},
        description="Short I2V motion cue; not sent to image generation.",
    )
    # Filled by KeyframeMaterializer: exact string sent to the image API (incl. style suffix).
    image_generation_prompt: str = ""
    # Filled in-process for skeleton consistency; not read by KeyframeMaterializer or Video.
    # Excluded from model_dump → smaller workspace JSON, no change to image/video prompts.
    constraints_applied: KeyframeConstraintsApplied = Field(
        default_factory=KeyframeConstraintsApplied,
        exclude=True,
    )


class ShotKeyframeSource(BaseModel):
    source_shot_id: str = ""


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
    # Skeleton / audit only; materializer ignores. Omitted from persisted JSON.
    display_name: str = Field(default="", exclude=True)
    purpose: str = Field(default="", exclude=True)
    keyframe_id: str = ""
    image_asset: ImageAsset = Field(default_factory=ImageAsset)
    prompt_summary: str = Field("", json_schema_extra={"creative": True})
    image_generation_prompt: str = ""


class StabilityKeyframes(BaseModel):
    characters: list[StabilityAnchorKeyframe] = Field(default_factory=list)
    locations: list[StabilityAnchorKeyframe] = Field(default_factory=list)
    props: list[StabilityAnchorKeyframe] = Field(default_factory=list)


class KeyframeSceneSource(BaseModel):
    screenplay_asset_id: str = ""
    screenplay_scene_id: str = ""


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

    screenplay: dict = Field(default_factory=dict)
    constraints: KeyframeConstraints = Field(default_factory=KeyframeConstraints)


class KeyFrameAgentOutput(KeyframesPackage):
    """Output payload for KeyFrameAgent (alias for KeyframesPackage)."""

    pass
