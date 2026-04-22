"""Schema definitions for NarratorAgent input / output interfaces.

The agent's output carries two populations of fields:

  * **Pre-materialize** (set by ``generate()`` by mirroring the upstream
    NarrationAgent script): ``language`` / ``lines``. These form the
    deterministic worklist the materializer iterates.
  * **Post-materialize** (filled in place by ``NarratorMaterializer``):
    ``clips`` / ``segment_timings`` / ``srt_text`` / ``total_duration_sec``.
    These are the timing + subtitle artifacts downstream consumers
    (slideshow compositor) read.

Structural (L1) checks only validate the pre-materialize population;
the L3 asset check validates the post-materialize one.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..common_schema import Meta


# ---------------------------------------------------------------------------
# Pre-materialize: mirrored worklist from NarrationAgent
# ---------------------------------------------------------------------------

class NarratorLineSnapshot(BaseModel):
    """One pending TTS line copied from NarrationAgent.

    ``segment_id`` is the parent segment the line belongs to — needed by
    the materializer to aggregate per-segment timing for the slideshow
    compositor.
    """

    line_id: str = ""  # ln_001
    segment_id: str = ""  # seg_001 — parent
    text: str = ""
    pause_after_ms: int = 0


# ---------------------------------------------------------------------------
# Post-materialize: timing + subtitle payload
# ---------------------------------------------------------------------------

class NarratorClip(BaseModel):
    """Per-line timing in the concatenated narrator audio."""

    line_id: str = ""
    start_sec: float = 0.0
    end_sec: float = 0.0
    duration_sec: float = 0.0


class NarratorSegmentTiming(BaseModel):
    """Per-segment timing (sum of member-line clips + trailing pause).

    The slideshow compositor uses ``duration_sec`` to set how long each
    illustration stays on screen; ``start_sec`` gives the exact frame
    offset where the next illustration cuts in.
    """

    segment_id: str = ""
    start_sec: float = 0.0
    end_sec: float = 0.0
    duration_sec: float = 0.0
    line_ids: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Top-level content
# ---------------------------------------------------------------------------

class NarratorContent(BaseModel):
    language: str = ""
    speaker: str = Field(
        "",
        description=(
            "TTS voice identifier actually used (e.g. 'alloy' for OpenAI-"
            "style voices). Selected by the materializer; empty until "
            "materialize runs."
        ),
    )
    lines: list[NarratorLineSnapshot] = Field(default_factory=list)

    # Post-materialize fields — populated by NarratorMaterializer.
    total_duration_sec: float = 0.0
    clips: list[NarratorClip] = Field(default_factory=list)
    segment_timings: list[NarratorSegmentTiming] = Field(default_factory=list)
    srt_text: str = ""


class NarratorMetrics(BaseModel):
    line_count: int = 0
    segment_count: int = 0
    total_duration_sec: float = 0.0


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------

class NarratorAgentInput(BaseModel):
    """Input payload for NarratorAgent — raw JSON text of the NarrationAgent
    output. The agent's ``generate()`` parses segments + lines out of this
    text (no LLM call) into the output's ``lines`` worklist."""

    narration_script_json_text: str = ""


class NarratorAgentOutput(BaseModel):
    meta: Meta = Field(default_factory=Meta)
    content: NarratorContent = Field(default_factory=NarratorContent)
    metrics: NarratorMetrics = Field(default_factory=NarratorMetrics)
