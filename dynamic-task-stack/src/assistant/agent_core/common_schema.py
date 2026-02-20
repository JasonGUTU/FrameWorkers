"""Common schema types shared across all agents."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

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
    """Standard asset metadata header shared by all agent outputs."""

    project_id: str = ""
    draft_id: str = ""
    asset_id: str = ""
    asset_type: str = ""
    schema_version: str = "0.3"
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    created_by_agent: str = ""
    language: str = "en"


class AssetRef(BaseModel):
    """Lightweight reference to a versioned asset."""

    asset_id: Optional[str] = ""
    schema_version: str = "0.3"


class DurationEstimate(BaseModel):
    """Duration estimate with confidence."""

    seconds: float = 0.0
    confidence: float = 0.0
