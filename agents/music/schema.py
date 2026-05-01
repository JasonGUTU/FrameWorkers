"""Schema definitions for MusicAgent input / output interfaces."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..common_schema import Meta


class MusicCue(BaseModel):
    """Single film-global background music cue.

    The agent emits **exactly one** cue whose mood covers the entire
    film. Per-scene cues are gone because scene-level audio alignment is
    no longer needed (the video-generation backend bakes dialogue + foley
    into the video clips themselves; BGM is just a global underlay).

    The cue carries only the LLM-chosen mood; track length is no longer
    a creative responsibility — the materializer generates a fixed
    chunk and the downstream audio-mix step's ffmpeg amix
    duration=longest filter trims/loops against the actual video.

    The wav file is registered as a separate artifact in global_memory
    under sys_id ``aud_music_film`` and downstream consumers discover
    it via caption-based resolution, not by reading an asset block.
    """

    cue_id: str = ""
    mood: str = Field("", json_schema_extra={"creative": True})


class MusicContent(BaseModel):
    cues: list[MusicCue] = Field(default_factory=list)


class MusicMetrics(BaseModel):
    cue_count: int = 0


class MusicAgentInput(BaseModel):
    """Input payload for MusicAgent.

    The agent picks a single film-wide mood from any available content
    signal: a screenplay, a video-analysis report, the user's creative
    brief, or any combination. All three are optional JSON-text blobs;
    the LLM reads structure pragmatically and rejects only when none
    carry a usable mood cue.
    """

    screenplay_json_text: str = ""
    video_analysis_json_text: str = ""
    creative_brief_json_text: str = ""


class MusicAgentOutput(BaseModel):
    meta: Meta = Field(default_factory=Meta)
    content: MusicContent = Field(default_factory=MusicContent)
    metrics: MusicMetrics = Field(default_factory=MusicMetrics)
