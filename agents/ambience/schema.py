"""Schema definitions for AmbienceAgent input / output interfaces."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..common_schema import Meta


class AmbienceBed(BaseModel):
    """Single film-global ambience bed (room tone / environmental underlay).

    Post-refactor the AmbienceAgent emits **exactly one** bed whose
    duration covers the entire film. Per-scene beds are gone; Kling's
    in-clip foley handles scene-synchronized event sounds, and this bed
    is a continuous texture underlay for gaps between foley events.

    The bed carries only LLM-chosen semantics (description + duration
    target); the wav file the materializer generates is registered as a
    separate artifact in global_memory (sys_id ``aud_amb_film``) and
    downstream consumers discover it via caption-based resolution, not
    by reading an asset block from this payload.
    """

    ambience_id: str = ""
    description: str = Field("", json_schema_extra={"creative": True})
    duration_seconds: float = Field(
        0.0,
        description=(
            "Total film length target for the global ambience bed, in "
            "seconds. Same estimation formula as MusicAgent: "
            "spoken_words/2.5 + action_shots*3 summed across all scenes."
        ),
    )


class AmbienceContent(BaseModel):
    beds: list[AmbienceBed] = Field(default_factory=list)


class AmbienceMetrics(BaseModel):
    bed_count: int = 0


class AmbienceAgentInput(BaseModel):
    """Input payload for AmbienceAgent.

    At least ONE of the two JSON text fields must be populated — the
    agent derives dominant environment + duration from a screenplay
    when available, else falls back to a VideoAnalysisAgent output
    (scene settings + video_summary.duration_seconds). Both are raw
    JSON text blobs.
    """

    screenplay_json_text: str = ""
    video_analysis_json_text: str = ""


class AmbienceAgentOutput(BaseModel):
    meta: Meta = Field(default_factory=Meta)
    content: AmbienceContent = Field(default_factory=AmbienceContent)
    metrics: AmbienceMetrics = Field(default_factory=AmbienceMetrics)
