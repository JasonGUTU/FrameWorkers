"""Schema definitions for VoiceCloneAgent input / output interfaces."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..common_schema import Meta


# ---------------------------------------------------------------------------
# Voice clone sub-models
# ---------------------------------------------------------------------------

class VoiceProfile(BaseModel):
    """Extracted voice characteristics from reference audio."""

    voice_id: str = Field("", description="Assigned voice profile identifier")
    description: str = Field("", description="Description of the voice characteristics")
    gender: str = Field("", description="Detected gender: male | female | neutral")
    age_range: str = Field("", description="Estimated age range: child | young | adult | elderly")
    tone: str = Field("", description="Voice tone keywords: warm, deep, bright, etc.")


class NarrationSegment(BaseModel):
    """A generated narration segment using the cloned voice."""

    segment_id: str = ""
    text: str = Field("", description="Text spoken in this segment")
    audio_asset_id: str = ""
    uri: str = "placeholder"


class AudioAsset(BaseModel):
    """Pointer to a generated audio file."""

    asset_id: str = ""
    uri: str = ""
    format: str = "wav"


# ---------------------------------------------------------------------------
# Content / Metrics
# ---------------------------------------------------------------------------

class VoiceCloneContent(BaseModel):
    voice_profile: VoiceProfile = Field(default_factory=VoiceProfile)
    segments: list[NarrationSegment] = Field(default_factory=list)
    final_audio: AudioAsset = Field(default_factory=AudioAsset)


class VoiceCloneMetrics(BaseModel):
    segment_count: int = 0
    voice_gender: str = ""


# ---------------------------------------------------------------------------
# Top-level I/O
# ---------------------------------------------------------------------------

class VoiceCloneAgentInput(BaseModel):
    """Input payload for VoiceCloneAgent.

    ``reference_audio_path``: audio sample to clone voice from.
    ``transcript_json_text``: text to speak in the cloned voice,
      as JSON text (may be a transcript, screenplay, or plain text).
    """

    reference_audio_path: str = ""
    transcript_json_text: str = ""


class VoiceCloneAgentOutput(BaseModel):
    """Output payload for VoiceCloneAgent."""

    meta: Meta = Field(default_factory=Meta)
    content: VoiceCloneContent = Field(default_factory=VoiceCloneContent)
    metrics: VoiceCloneMetrics = Field(default_factory=VoiceCloneMetrics)
