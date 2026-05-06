"""Schema definitions for IllustrationAgent input / output interfaces."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..common_schema import Meta


# ---------------------------------------------------------------------------
# Illustration sub-models
# ---------------------------------------------------------------------------

class IllustrationEntry(BaseModel):
    """One generated illustration aligned to a NarrationSegment.

    The PNG binary is registered as a separate global_memory artifact
    under sys_id ``illustration_<segment_id>`` (Pattern B); downstream
    consumers discover it via caption-based InputResolver routing, not
    by reading a URI field off this entry. Schema is metadata-only.
    """

    segment_id: str = ""  # seg_001 — mirrored from NarrationAgent
    image_prompt: str = ""  # mirrored from NarrationAgent for traceability


class IllustrationContent(BaseModel):
    # Mirrored from NarrationAgent's content.overall_style so the
    # materializer can render it into every image prompt without
    # re-parsing upstream JSON at materialize time.
    overall_style: str = ""
    illustrations: list[IllustrationEntry] = Field(default_factory=list)


class IllustrationMetrics(BaseModel):
    illustration_count: int = 0


# ---------------------------------------------------------------------------
# Top-level I/O
# ---------------------------------------------------------------------------

class IllustrationAgentInput(BaseModel):
    """Input payload for IllustrationAgent.

    Raw JSON text of the upstream NarrationAgent output. The agent's
    ``generate()`` parses segments + overall_style out of this text
    (no LLM call) and mirrors them into the output shell so the
    materializer has a stable per-segment worklist.
    """

    narration_script_json_text: str = ""


class IllustrationAgentOutput(BaseModel):
    meta: Meta = Field(default_factory=Meta)
    content: IllustrationContent = Field(default_factory=IllustrationContent)
    metrics: IllustrationMetrics = Field(default_factory=IllustrationMetrics)
