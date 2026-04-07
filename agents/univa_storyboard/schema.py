"""Schema definitions for UnivaStoryboardAgent.

Mirrors UniVA's storyboard JSON format exactly so downstream agents
(UnivaKeyFrameAgent, UnivaVideoAgent) consume it without translation.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..common_schema import ArtifactCaption, Meta


# ---------------------------------------------------------------------------
# Storyboard sub-models (match UniVA's storyboard_gen.txt output format)
# ---------------------------------------------------------------------------

class UnivaCharacter(BaseModel):
    """A character entry in the storyboard."""
    id: str = Field("", description="Unique ID like char_1, char_2")
    name: str = Field("", json_schema_extra={"creative": True})
    description: str = Field(
        "", json_schema_extra={"creative": True},
        description="Static appearance description — no actions or emotions",
    )


class UnivaShotPerspective(BaseModel):
    distance: str = Field("", description="wide shot | medium shot | close-up")
    angle: str = Field("", description="eye-level | low angle | high angle")
    lens: str = Field("", description="Optional: wide-angle lens | telephoto lens")


class UnivaShot(BaseModel):
    """A single shot in the storyboard."""
    id: int = 0
    setting_description: str = Field("", json_schema_extra={"creative": True})
    plot_correspondence: str = Field("", json_schema_extra={"creative": True})
    onstage_characters: list[str] = Field(default_factory=list)
    static_shot_description: str = Field("", json_schema_extra={"creative": True})
    shot_perspective_design: UnivaShotPerspective = Field(
        default_factory=UnivaShotPerspective,
    )
    audio_description: str = Field("", json_schema_extra={"creative": True})
    video_type: str = Field("text2video", description="Suggested generation type")


# ---------------------------------------------------------------------------
# Top-level content
# ---------------------------------------------------------------------------

class UnivaStoryboardContent(BaseModel):
    characters: list[UnivaCharacter] = Field(default_factory=list)
    shots: list[UnivaShot] = Field(default_factory=list)
    style: str = Field("", json_schema_extra={"creative": True})


class UnivaStoryboardMetrics(BaseModel):
    character_count: int = 0
    shot_count: int = 0


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------

class UnivaStoryboardInput(BaseModel):
    user_prompt: str = Field("", description="The story/video concept prompt")


class UnivaStoryboardOutput(BaseModel):
    meta: Meta = Field(default_factory=Meta)
    content: UnivaStoryboardContent = Field(default_factory=UnivaStoryboardContent)
    metrics: UnivaStoryboardMetrics = Field(default_factory=UnivaStoryboardMetrics)
    artifact_caption: ArtifactCaption = Field(default_factory=ArtifactCaption)
