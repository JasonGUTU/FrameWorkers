"""Schema definitions for UnivaVideoAgent.

Produces per-shot video clips and a final merged video, mirroring
UniVA's Stage 4 (I2V per shot) + Stage 6 (FFmpeg merge).
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..common_schema import ImageReferenceEntry, Meta


# ---------------------------------------------------------------------------
# Sub-models
# ---------------------------------------------------------------------------

class UnivaVideoAsset(BaseModel):
    """Pointer to a generated video file."""
    asset_id: str = ""
    uri: str = ""
    format: str = "mp4"


class UnivaShotVideo(BaseModel):
    """A single shot's video clip."""
    shot_id: int = 0
    video_prompt: str = Field(
        "", description="Composed from storyboard shot fields (same as keyframe prompt)",
    )
    video_asset: UnivaVideoAsset = Field(default_factory=UnivaVideoAsset)


# ---------------------------------------------------------------------------
# Top-level content
# ---------------------------------------------------------------------------

class UnivaVideoContent(BaseModel):
    shot_videos: list[UnivaShotVideo] = Field(default_factory=list)
    final_video_asset: UnivaVideoAsset = Field(default_factory=UnivaVideoAsset)


class UnivaVideoMetrics(BaseModel):
    shot_count: int = 0


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------

class UnivaVideoInput(BaseModel):
    """Input payload for UnivaVideoAgent — univa-style JSON-text pass-through.

    ``storyboard_json_text`` is the entire upstream UnivaStoryboardAgent
    payload serialized as a raw JSON text blob. See CLAUDE.md §7.

    ``shot_keyframes`` are typed ``ImageReferenceEntry`` entries (direct
    file paths + captions) selected by InputResolver via the
    ``[shot_keyframes]`` collection label.
    """

    storyboard_json_text: str = Field("", description="Upstream UnivaStoryboardAgent payload as raw JSON text")
    shot_keyframes: list[ImageReferenceEntry] = Field(default_factory=list)


class UnivaVideoOutput(BaseModel):
    meta: Meta = Field(default_factory=Meta)
    content: UnivaVideoContent = Field(default_factory=UnivaVideoContent)
    metrics: UnivaVideoMetrics = Field(default_factory=UnivaVideoMetrics)
    # Per-media-artifact captions keyed by sys_id (e.g. "clip_shot_0").
