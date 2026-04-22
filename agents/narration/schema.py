"""Schema definitions for NarrationAgent input / output interfaces."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..common_schema import Meta


# ---------------------------------------------------------------------------
# Narration sub-models
# ---------------------------------------------------------------------------

class NarrationLine(BaseModel):
    """A single TTS-sized line of narrator prose.

    ``line_id`` is globally sequential across every segment (ln_001,
    ln_002, ...) — NarratorAgent's TTS materializer uses it to stamp
    timestamps back onto the SRT and segment_timing artifacts.
    """

    line_id: str = ""  # ln_001
    text: str = Field("", json_schema_extra={"creative": True})
    pause_after_ms: int = Field(
        0,
        description=(
            "Silence to insert AFTER this line in the concatenated narrator "
            "audio. 0 for flowing prose, 300-600 for paragraph breaks, "
            "800-1200 for dramatic pauses or scene shifts."
        ),
    )


class NarrationSegment(BaseModel):
    """One visual beat: a group of narrator lines read over ONE illustration.

    ``image_prompt`` is the stand-alone scene description IllustrationAgent
    passes to the image model; art-style words belong in ``overall_style``,
    not here (so swapping the anchor style is a single-field edit).
    """

    segment_id: str = ""  # seg_001
    image_prompt: str = Field("", json_schema_extra={"creative": True})
    lines: list[NarrationLine] = Field(default_factory=list)


class NarrationContent(BaseModel):
    language: str = Field(
        "",
        json_schema_extra={"creative": True},
        description="IETF language tag, e.g. 'zh-CN', 'en-US'.",
    )
    overall_style: str = Field(
        "",
        json_schema_extra={"creative": True},
        description=(
            "Short visual-style string (3-8 words) used by IllustrationAgent "
            "as a cross-segment art-style anchor, e.g. "
            "'watercolor storybook, warm palette, soft edges'."
        ),
    )
    segments: list[NarrationSegment] = Field(default_factory=list)


class NarrationMetrics(BaseModel):
    segment_count: int = 0
    line_count: int = 0
    total_chars: int = 0


# ---------------------------------------------------------------------------
# Top-level I/O
# ---------------------------------------------------------------------------

class NarrationAgentInput(BaseModel):
    """Input payload for NarrationAgent — raw creative brief JSON text.

    Accepts both a short brief ('a story about a lonely lighthouse keeper')
    and a long already-written prose. The agent's LLM decides how much to
    expand vs preserve verbatim — same contract StoryAgent uses.
    """

    creative_brief_json_text: str = ""


class NarrationAgentOutput(BaseModel):
    meta: Meta = Field(default_factory=Meta)
    content: NarrationContent = Field(default_factory=NarrationContent)
    metrics: NarrationMetrics = Field(default_factory=NarrationMetrics)
