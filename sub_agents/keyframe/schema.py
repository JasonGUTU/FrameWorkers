"""KeyframeAgent — image factory output schema.

Two-phase output:
  Phase 1: per-variant anchor images (character + location)
  Phase 2: per-shot visual pack (storyboard sheet + blocking diagram +
           composition notes that ShotPromptAgent uses to write @ImageN
           role assignment without re-OCR'ing the rendered images).
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class ShotVisualPack(BaseModel):
    """Per-shot bundle from KeyframeAgent Phase 2.

    Blocking diagram was removed — camera info lives in ShotPromptAgent's
    [CAMERA] text section (more reliable than top-down diagram gpt-image-2
    rendered, and that diagram was never fed to the video model anyway).
    """
    storyboard_image_path: str
    panel_composition_notes: list[str] = Field(
        min_length=1,
        description="One entry per panel (in shot.panels order). "
                    "~30-60 words describing framing / character placement / key visual elements. "
                    "Hand-off doc for ShotPromptAgent's @ImageN role assignment writer.",
    )
    storyboard_prompt: str = Field(
        default="",
        description="The exact prompt fed to gpt-image-2 when rendering this shot's storyboard. "
                    "Saved for debugging format-consistency issues across shots.",
    )


class KeyframeOutput(BaseModel):
    style_anchor_path: str = Field(
        description="One PNG capturing the story-wide visual style "
                    "(color palette / lighting / aesthetic). Shared across all shots."
    )
    character_anchors: dict[str, str] = Field(
        description="{character_variant_id: anchor_image_path}"
    )
    location_anchors: dict[str, str] = Field(
        description="{location_variant_id: anchor_image_path}"
    )
    shot_visuals: dict[str, ShotVisualPack] = Field(
        description="{shot_id: pack}"
    )
