"""Schema definitions for SubtitleAgent input / output interfaces."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..common_schema import Meta


# ---------------------------------------------------------------------------
# Subtitle sub-models
# ---------------------------------------------------------------------------

class SubtitleCue(BaseModel):
    """A single subtitle cue with timing and text."""

    cue_id: str = ""
    start_time: str = Field("", description="Start time in SRT format HH:MM:SS,mmm")
    end_time: str = Field("", description="End time in SRT format HH:MM:SS,mmm")
    text: str = Field("", description="Subtitle text for this cue")


class SubtitleTrack(BaseModel):
    """A complete subtitle track for one language."""

    language: str = ""
    cues: list[SubtitleCue] = Field(default_factory=list)
    srt_text: str = Field("", description="Complete SRT-formatted subtitle file content")


# ---------------------------------------------------------------------------
# Content / Metrics
# ---------------------------------------------------------------------------

class SubtitleContent(BaseModel):
    tracks: list[SubtitleTrack] = Field(default_factory=list)


class SubtitleMetrics(BaseModel):
    track_count: int = 0
    total_cue_count: int = 0


# ---------------------------------------------------------------------------
# Top-level I/O
# ---------------------------------------------------------------------------

class SubtitleAgentInput(BaseModel):
    """Input payload for SubtitleAgent.

    ``screenplay_json_text`` is the upstream screenplay (or translated
    screenplay) serialized as raw JSON text.  The LLM reads it to
    extract dialogue/narration lines and their shot ordering.

    ``video_json_text`` is the optional video package JSON text,
    providing actual shot durations for timing alignment.
    """

    screenplay_json_text: str = ""
    video_json_text: str = ""


class SubtitleAgentOutput(BaseModel):
    """Output payload for SubtitleAgent."""

    meta: Meta = Field(default_factory=Meta)
    content: SubtitleContent = Field(default_factory=SubtitleContent)
    metrics: SubtitleMetrics = Field(default_factory=SubtitleMetrics)
