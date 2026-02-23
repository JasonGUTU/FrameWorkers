"""Schema definitions for AudioAgent input / output interfaces."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..common_schema import Meta


# ---------------------------------------------------------------------------
# Audio sub-models
# ---------------------------------------------------------------------------

class AudioAsset(BaseModel):
    """Pointer to a generated audio file."""

    asset_id: str = ""
    uri: str = ""
    format: str = "wav"  # wav | mp3 | aac
    duration_sec: float = 0.0
    sample_rate: int = 44100


class NarrationSegment(BaseModel):
    """A single narration/dialogue segment aligned to a shot."""

    segment_id: str = ""
    linked_block_id: str = ""
    linked_shot_id: str = ""
    speaker: str = ""
    text: str = Field("", json_schema_extra={"creative": True})
    start_sec: float = 0.0
    end_sec: float = 0.0
    audio_asset: AudioAsset = Field(default_factory=AudioAsset)


class MusicCue(BaseModel):
    """Scene-level music track."""

    cue_id: str = ""
    scene_id: str = ""
    mood: str = Field("", json_schema_extra={"creative": True})
    start_sec: float = 0.0
    end_sec: float = 0.0
    audio_asset: AudioAsset = Field(default_factory=AudioAsset)


class AmbienceBed(BaseModel):
    """Scene-level ambient sound bed."""

    ambience_id: str = ""
    scene_id: str = ""
    description: str = Field("", json_schema_extra={"creative": True})
    start_sec: float = 0.0
    end_sec: float = 0.0
    audio_asset: AudioAsset = Field(default_factory=AudioAsset)


class AudioMix(BaseModel):
    """Final mix for a scene."""

    mix_id: str = ""
    scene_id: str = ""
    duration_sec: float = 0.0
    audio_asset: AudioAsset = Field(default_factory=AudioAsset)


class AudioScene(BaseModel):
    scene_id: str = ""
    order: int = 0
    scene_duration_sec: float = 0.0
    narration_segments: list[NarrationSegment] = Field(default_factory=list)
    music_cue: MusicCue = Field(default_factory=MusicCue)
    ambience_bed: AmbienceBed = Field(default_factory=AmbienceBed)
    mix: AudioMix = Field(default_factory=AudioMix)


# ---------------------------------------------------------------------------
# Audio content
# ---------------------------------------------------------------------------

class AudioContent(BaseModel):
    scenes: list[AudioScene] = Field(default_factory=list)
    final_audio_asset: AudioAsset = Field(default_factory=AudioAsset)


class AudioMetrics(BaseModel):
    scene_count: int = 0
    narration_segment_count: int = 0
    total_narration_duration_sec: float = 0.0
    total_music_duration_sec: float = 0.0


# ---------------------------------------------------------------------------
# Top-level I/O
# ---------------------------------------------------------------------------

class AudioPackage(BaseModel):
    """Full Audio Package asset."""

    meta: Meta = Field(default_factory=Meta)
    content: AudioContent = Field(default_factory=AudioContent)
    metrics: AudioMetrics = Field(default_factory=AudioMetrics)


class AudioAgentInput(BaseModel):
    """Input payload for AudioAgent.

    Audio alignment rules:
      1. Semantic source: block (from Screenplay) — what to say
      2. Timing alignment: shot (from Storyboard) — when to say
      3. Hard boundary: scene (from Video) — max duration
    """

    project_id: str = ""
    draft_id: str = ""
    screenplay: dict = Field(default_factory=dict)
    storyboard: dict = Field(default_factory=dict)
    video: dict = Field(default_factory=dict)
    constraints: dict = Field(default_factory=dict)


class AudioAgentOutput(AudioPackage):
    """Output payload for AudioAgent (alias for AudioPackage)."""

    pass
