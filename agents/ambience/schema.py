"""Schema definitions for AmbienceAgent input / output interfaces."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..common_schema import Meta


class AmbienceBed(BaseModel):
    """Single film-global ambience bed (room tone / environmental underlay).

    The agent emits **exactly one** bed whose description covers the
    entire film. Per-scene beds are gone; the video-generation backend's
    in-clip foley handles scene-synchronized event sounds, and this
    bed is a continuous texture underlay for gaps between foley events.

    The bed carries only the LLM-chosen description; track length is no
    longer a creative responsibility — the materializer generates a
    fixed chunk and the downstream audio-mix step's ffmpeg amix
    duration=first filter trims/loops against the actual video.

    The wav file is registered as a separate artifact in global_memory
    under sys_id ``aud_amb_film`` and downstream consumers discover it
    via caption-based resolution, not by reading an asset block.
    """

    ambience_id: str = ""
    description: str = Field("", json_schema_extra={"creative": True})


class AmbienceContent(BaseModel):
    beds: list[AmbienceBed] = Field(default_factory=list)


class AmbienceMetrics(BaseModel):
    bed_count: int = 0


class AmbienceAgentInput(BaseModel):
    """Input payload for AmbienceAgent.

    The agent picks a single film-wide ambient texture from any
    available content signal: a screenplay, a video-analysis report,
    the user's creative brief, or any combination. All three are
    optional JSON-text blobs; the LLM reads structure pragmatically and
    rejects only when none carry a usable environment / atmosphere cue.
    """

    screenplay_json_text: str = ""
    video_analysis_json_text: str = ""
    creative_brief_json_text: str = ""


class AmbienceAgentOutput(BaseModel):
    meta: Meta = Field(default_factory=Meta)
    content: AmbienceContent = Field(default_factory=AmbienceContent)
    metrics: AmbienceMetrics = Field(default_factory=AmbienceMetrics)
