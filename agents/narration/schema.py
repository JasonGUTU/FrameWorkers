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


class NarrationCharacter(BaseModel):
    """One recurring character in the narrated story.

    Cross-segment character identity is enforced downstream by
    IllustrationMaterializer: it t2i's a portrait anchor from
    ``appearance_prompt`` and attaches that anchor as a CHARACTER
    reference when generating any segment whose
    ``characters_in_segment`` lists this ``character_id``. So
    ``appearance_prompt`` must be specific enough that an image model
    can render a recognisable identity from text alone (face, hair,
    age, distinctive wardrobe). Only include characters who appear in
    2+ segments — single-appearance figures don't need anchoring.
    """

    character_id: str = ""  # char_001
    name: str = Field("", json_schema_extra={"creative": True})
    appearance_prompt: str = Field("", json_schema_extra={"creative": True})


class NarrationSegment(BaseModel):
    """One visual beat: a group of narrator lines read over ONE illustration.

    ``image_prompt`` is the stand-alone scene description IllustrationAgent
    passes to the image model; art-style words belong in ``overall_style``,
    not here (so swapping the anchor style is a single-field edit).

    ``characters_in_segment`` lists the cast character_ids visible in
    THIS segment's illustration — the materializer attaches each
    listed character's portrait anchor as a CHARACTER reference for
    cross-segment identity consistency. Empty list when no cast
    member is visible (pure landscape / object segment).
    """

    segment_id: str = ""  # seg_001
    image_prompt: str = Field("", json_schema_extra={"creative": True})
    lines: list[NarrationLine] = Field(default_factory=list)
    characters_in_segment: list[str] = Field(default_factory=list)


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
    cast: list[NarrationCharacter] = Field(default_factory=list)
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
