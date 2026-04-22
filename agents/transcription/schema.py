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
    text: str = Field("", description="Transcribed text for this segment")


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

    ``raw_segments_json_text`` is populated by TranscriptionMaterializer's
    ``pre_generate`` hook BEFORE the LLM loop starts: the materializer
    calls the STT service once and serializes the raw timestamped
    segments as a JSON text blob here. The agent's ``build_user_prompt``
    renders this inline so the LLM cleans real ASR output instead of
    being asked to invent transcription from just a file path. Left
    empty when running the agent without a materialize_ctx (e.g.
    isolated LLM-only unit tests), in which case the LLM falls back to
    a minimal placeholder output.
    """

    source_media_path: str = ""
    raw_segments_json_text: str = ""


class TranscriptionAgentOutput(BaseModel):
    """Output payload for TranscriptionAgent."""

    meta: Meta = Field(default_factory=Meta)
    content: TranscriptionContent = Field(default_factory=TranscriptionContent)
    metrics: TranscriptionMetrics = Field(default_factory=TranscriptionMetrics)
