"""Schema definitions for UnivaKeyFrameAgent.

Produces character reference images and per-shot keyframe images,
mirroring UniVA's Stage 2 (character image gen) + Stage 3 (keyframe gen).
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..common_schema import ArtifactCaption, ImageAsset, Meta


# ---------------------------------------------------------------------------
# Sub-models
# ---------------------------------------------------------------------------

class UnivaCharacterImage(BaseModel):
    """A generated character reference image."""
    char_id: str = ""
    char_name: str = ""
    original_description: str = Field(
        "", description="Original static description from storyboard",
    )
    refined_prompt: str = Field(
        "", json_schema_extra={"creative": True},
        description="LLM-refined prompt optimized for image generation",
    )
    image_asset: ImageAsset = Field(default_factory=ImageAsset)


class UnivaShotKeyframe(BaseModel):
    """A generated keyframe image for a single shot."""
    shot_id: int = 0
    keyframe_prompt: str = Field(
        "", description="Composed from storyboard shot fields (deterministic)",
    )
    onstage_char_ids: list[str] = Field(default_factory=list)
    image_asset: ImageAsset = Field(default_factory=ImageAsset)


# ---------------------------------------------------------------------------
# Top-level content
# ---------------------------------------------------------------------------

class UnivaKeyFrameContent(BaseModel):
    character_images: list[UnivaCharacterImage] = Field(default_factory=list)
    shot_keyframes: list[UnivaShotKeyframe] = Field(default_factory=list)


class UnivaKeyFrameMetrics(BaseModel):
    character_image_count: int = 0
    shot_keyframe_count: int = 0


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------

class UnivaKeyFrameInput(BaseModel):
    storyboard: dict = Field(
        default_factory=dict,
        description="Full storyboard JSON from UnivaStoryboardAgent",
    )


class UnivaKeyFrameOutput(BaseModel):
    meta: Meta = Field(default_factory=Meta)
    content: UnivaKeyFrameContent = Field(default_factory=UnivaKeyFrameContent)
    metrics: UnivaKeyFrameMetrics = Field(default_factory=UnivaKeyFrameMetrics)
    artifact_caption: ArtifactCaption = Field(default_factory=ArtifactCaption)
    # Per-media-artifact captions keyed by sys_id (e.g. "img_shot_0_keyframe").
    # Populated by recompute_metrics(); read by asset_manager to register
    # each image with its own ArtifactRef.  Excluded from JSON snapshot.
    per_artifact_captions: dict = Field(default_factory=dict, exclude=True)
