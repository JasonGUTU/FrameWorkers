"""ShotPromptAgent — text-crafter output schema.

Per-shot artifact: the assembled video-generation text prompt plus the ordered
image set that pairs with it (driver passes both to the chosen video backend).

Image set ordering is fixed by convention (the [Image N] tags in text_prompt
reference these positions 1-based):
  1. style anchor
  2. storyboard sheet (carries identity + scene per panel)
  3. blocking diagram (camera path metadata)
Character / location anchors are KeyframeAgent-internal (used as i2i refs when
rendering the storyboard) and are NOT passed to the video model directly.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class ShotPromptOutput(BaseModel):
    shot_id: str
    text_prompt: str = Field(
        description="Full video-gen prompt with sections "
                    "[STYLE HEADER] [ROLE ASSIGNMENT] [CAMERA] [TIMELINE BEATS] "
                    "[DIALOGUE] [SFX]. [Image N] tags reference video_image_refs."
    )
    video_image_refs: list[str] = Field(
        min_length=1,
        description="Ordered image paths: characters → location → storyboard → blocking. "
                    "[Image 1]..[Image N] in text_prompt are 1-based indices into this list.",
    )
