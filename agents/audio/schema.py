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
    sample_rate: int = 44100


class NarrationSegment(BaseModel):
    """A single narration/dialogue segment aligned to a shot."""

    segment_id: str = ""
    linked_shot_id: str = ""
    speaker: str = ""
    text: str = Field("", json_schema_extra={"creative": True})
    audio_asset: AudioAsset = Field(default_factory=AudioAsset)
    audio_generation_prompt: str = ""


class MusicCue(BaseModel):
    """Scene-level music track."""

    cue_id: str = ""
    scene_id: str = ""
    mood: str = Field("", json_schema_extra={"creative": True})
    audio_asset: AudioAsset = Field(default_factory=AudioAsset)
    audio_generation_prompt: str = ""


class AmbienceBed(BaseModel):
    """Scene-level ambient sound bed."""

    ambience_id: str = ""
    scene_id: str = ""
    description: str = Field("", json_schema_extra={"creative": True})
    audio_asset: AudioAsset = Field(default_factory=AudioAsset)
    audio_generation_prompt: str = ""


class AudioMix(BaseModel):
    """Final mix for a scene."""

    mix_id: str = ""
    scene_id: str = ""
    audio_asset: AudioAsset = Field(default_factory=AudioAsset)


class DeliveryVideoAsset(BaseModel):
    """Pointer to final muxed video (video + audio)."""

    asset_id: str = ""
    uri: str = ""
    format: str = "mp4"


class AudioScene(BaseModel):
    scene_id: str = ""
    order: int = 0
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
    final_delivery_asset: DeliveryVideoAsset = Field(default_factory=DeliveryVideoAsset)


class AudioMetrics(BaseModel):
    scene_count: int = 0
    narration_segment_count: int = 0


# ---------------------------------------------------------------------------
# Top-level I/O
# ---------------------------------------------------------------------------

class AudioPackage(BaseModel):
    """Full Audio Package asset."""

    meta: Meta = Field(default_factory=Meta)
    content: AudioContent = Field(default_factory=AudioContent)
    metrics: AudioMetrics = Field(default_factory=AudioMetrics)
    # Per-media-artifact captions keyed by sys_id (e.g. "aud_narr_sc_001_01").
    # Populated by recompute_metrics(); read by ArtifactWriter to build ArtifactRef entries.
    # Excluded from JSON snapshot to keep persisted files clean.


class AudioAgentInput(BaseModel):
    """Input payload for AudioAgent — univa-style JSON-text pass-through.

    ``screenplay_json_text`` is the **entire** upstream screenplay payload
    serialized as a raw JSON text blob. AudioAgent's LLM reads this text
    directly and reasons about whatever shape the upstream happens to
    produce — there is NO field-name unpacking in ``build_input`` or in
    the agent. This removes the hidden string-keyed coupling between
    ScreenplayAgent's internal field names and AudioAgent's consumer code.

    ``final_video_path`` is the direct file path to the finished MP4 file,
    selected by InputResolver via the ``[final_video]`` label against a
    **video FILE entry** (mime video/mp4), NOT against a JSON manifest.
    AudioMaterializer loads bytes from this path directly when muxing the
    final delivery — no payload unwrap, no JSON parsing.
    """

    screenplay_json_text: str = ""
    final_video_path: str = ""


class AudioAgentOutput(AudioPackage):
    """Output payload for AudioAgent (alias for AudioPackage)."""

    pass
