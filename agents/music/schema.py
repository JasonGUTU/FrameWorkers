"""Schema definitions for MusicAgent input / output interfaces."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..common_schema import Meta


class MusicCue(BaseModel):
    """Single film-global background music cue.

    Post-refactor the MusicAgent emits **exactly one** cue whose duration
    covers the entire film; per-scene cues are gone because scene-level
    audio alignment is no longer needed (Kling bakes dialogue + foley
    into the video clips themselves, and BGM is just a global underlay).

    The cue carries only LLM-chosen semantics (mood + duration target);
    the wav file the materializer generates is registered as a separate
    artifact in global_memory (sys_id ``aud_music_film``) and
    downstream consumers discover it via caption-based resolution, not
    by reading an asset block from this payload.
    """

    cue_id: str = ""
    mood: str = Field("", json_schema_extra={"creative": True})
    duration_seconds: float = Field(
        0.0,
        description=(
            "Total film length target for the global BGM track, in "
            "seconds. MusicAgent's LLM estimates this from the screenplay "
            "(sum of spoken-word-count/2.5 + action_shots*3 across every "
            "scene). The materializer chunks+concats to reach the target; "
            "AudioMix then amix+trims against the actual video duration."
        ),
    )


class MusicContent(BaseModel):
    cues: list[MusicCue] = Field(default_factory=list)


class MusicMetrics(BaseModel):
    cue_count: int = 0


class MusicAgentInput(BaseModel):
    """Input payload for MusicAgent.

    At least ONE of the two JSON text fields must be populated — the
    agent derives mood + duration from a screenplay when available,
    else falls back to a VideoAnalysisAgent output (scene moods +
    video_summary.duration_seconds). Both are raw JSON text blobs so
    the LLM reads structure directly from whatever shape is present.
    """

    screenplay_json_text: str = ""
    video_analysis_json_text: str = ""


class MusicAgentOutput(BaseModel):
    meta: Meta = Field(default_factory=Meta)
    content: MusicContent = Field(default_factory=MusicContent)
    metrics: MusicMetrics = Field(default_factory=MusicMetrics)
