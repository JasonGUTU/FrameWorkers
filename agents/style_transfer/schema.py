"""Schema definitions for StyleTransferAgent input / output interfaces."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..common_schema import Meta


# ---------------------------------------------------------------------------
# Style transfer sub-models
# ---------------------------------------------------------------------------

class StyleSpec(BaseModel):
    """LLM-planned style transfer specification."""

    style_description: str = Field(
        "", description="Detailed description of the target visual style"
    )
    style_prompt: str = Field(
        "", description="Optimized prompt for the video edit model"
    )
    preserve_motion: bool = Field(
        True, description="Whether to preserve original motion/camera movement"
    )
    style_strength: float = Field(
        0.7, ge=0.0, le=1.0,
        description="How strongly to apply the style (0=original, 1=full style)"
    )


# ---------------------------------------------------------------------------
# Content / Metrics
# ---------------------------------------------------------------------------

class StyleTransferContent(BaseModel):
    """Style transfer payload — metadata only.

    The styled mp4 binary is registered as a separate global_memory
    artifact under sys_id ``style_transfer_output`` (Pattern B);
    downstream consumers discover it via caption-based InputResolver
    routing, not by reading a URI field off this content.
    """

    style_spec: StyleSpec = Field(default_factory=StyleSpec)


class StyleTransferMetrics(BaseModel):
    style_strength: float = 0.0
    preserve_motion: bool = True


# ---------------------------------------------------------------------------
# Top-level I/O
# ---------------------------------------------------------------------------

class StyleTransferAgentInput(BaseModel):
    """Input payload for StyleTransferAgent.

    ``source_video_path`` is the video file to restyle.
    ``style_description`` is a natural-language description of the
    desired style (e.g. 'anime', 'oil painting', 'cyberpunk').
    ``style_reference_path`` is an optional reference image for the style.
    ``creative_brief_json_text`` is the user's verbatim brief as raw JSON
    text — fallback source for the style when no dedicated style_reference
    artifact is wired up upstream.
    """

    source_video_path: str = ""
    style_description: str = ""
    style_reference_path: str = ""
    creative_brief_json_text: str = ""


class StyleTransferAgentOutput(BaseModel):
    """Output payload for StyleTransferAgent."""

    meta: Meta = Field(default_factory=Meta)
    content: StyleTransferContent = Field(default_factory=StyleTransferContent)
    metrics: StyleTransferMetrics = Field(default_factory=StyleTransferMetrics)
