"""Schema definitions for TranscriptionAgent input / output interfaces."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from ..common_schema import Meta


# ---------------------------------------------------------------------------
# Transcription sub-models
# ---------------------------------------------------------------------------

class TranscriptSegment(BaseModel):
    """A single transcribed segment with timing."""

    segment_id: str = ""
    start_time: float = Field(0.0, description="Start time in seconds")
    end_time: float = Field(0.0, description="End time in seconds")
    speaker: str = Field("", description="Detected or inferred speaker label")
    text: str = Field("", description="Transcribed text for this segment")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="Transcription confidence")


# ---------------------------------------------------------------------------
# Content / Metrics
# ---------------------------------------------------------------------------

class TranscriptionContent(BaseModel):
    language: str = Field("", description="Detected language of the audio")
    segments: list[TranscriptSegment] = Field(default_factory=list)
    full_text: str = Field("", description="Complete transcript as plain text")

    @field_validator("language", "full_text", mode="before")
    @classmethod
    def _coerce_none_to_str(cls, v):
        return v if v is not None else ""


class TranscriptionMetrics(BaseModel):
    language: str = ""
    segment_count: int = 0
    duration_seconds: float = 0.0


# ---------------------------------------------------------------------------
# Top-level I/O
# ---------------------------------------------------------------------------

class TranscriptionAgentInput(BaseModel):
    """Input payload for TranscriptionAgent.

    ``source_media_path`` is the direct file path to the audio or video
    file to transcribe.
    """

    source_media_path: str = ""


class TranscriptionAgentOutput(BaseModel):
    """Output payload for TranscriptionAgent."""

    meta: Meta = Field(default_factory=Meta)
    content: TranscriptionContent = Field(default_factory=TranscriptionContent)
    metrics: TranscriptionMetrics = Field(default_factory=TranscriptionMetrics)
