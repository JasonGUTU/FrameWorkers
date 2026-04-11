"""Common schema types shared across all agents."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Shared atomic types
# ---------------------------------------------------------------------------

class QualityScore(BaseModel):
    """A single quality dimension with numeric score and free-text notes."""

    score: float = Field(0.0, ge=0.0, le=1.0, description="Quality score 0–1")
    notes: list[str] = Field(default_factory=list)


class ImageAsset(BaseModel):
    """Pointer to a generated image file."""

    asset_id: str = ""
    uri: str = ""
    width: int = 1024
    height: int = 576
    format: str = "png"  # png | jpg | webp


class Meta(BaseModel):
    """Standard asset metadata header shared by all agent outputs.

    Orchestration uses Task Stack task_id elsewhere. Do not add project_id
    to LLM JSON; it is not part of this schema.
    """

    draft_id: str = ""
    asset_id: str = ""
    asset_type: str = ""
    schema_version: str = "0.3"
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    created_by_agent: str = ""
    language: str = "en"



class ImageReferenceEntry(BaseModel):
    """A single image reference that flows from the workspace into a sub-agent's
    typed input.

    Used by any agent that needs to receive image artifacts (character /
    location / style references for KeyFrameAgent, shot stills for
    VideoAgent, shot keyframes for UnivaVideoAgent, etc.) — the schema is
    deliberately generic so the same type works for all label categories.

    The shape mirrors the InputResolver-resolved entry: ``path`` is always
    populated with the workspace file path; the caption fields preserve
    the producer's natural-language description so the consuming agent's
    LLM can decide how to use each entry. ``scope`` is sometimes used by
    materializers to disambiguate per-shot images (e.g. ``"shot:sh_001"``).
    """

    path: str = ""
    caption: str = ""
    mime: str = ""
    scope: str = ""


