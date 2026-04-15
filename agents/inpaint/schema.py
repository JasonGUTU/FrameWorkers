"""Schema definitions for InpaintAgent input / output interfaces."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..common_schema import Meta


# ---------------------------------------------------------------------------
# Inpaint sub-models
# ---------------------------------------------------------------------------

class InpaintSpec(BaseModel):
    """LLM-planned inpainting specification."""

    mask_mode: str = Field(
        "manual",
        description="Mask source: manual | depth_foreground | depth_background | object_track"
    )
    replacement_description: str = Field(
        "", description="What to fill in the masked region"
    )
    inpaint_prompt: str = Field(
        "", description="Optimized prompt for the inpainting model"
    )
    preserve_unmasked: bool = Field(
        True, description="Keep unmasked regions pixel-identical"
    )
    blend_edge_px: int = Field(
        8, ge=0, description="Feather radius at mask boundary in pixels"
    )


class VideoAsset(BaseModel):
    """Pointer to a generated video file."""

    asset_id: str = ""
    uri: str = ""
    format: str = "mp4"


# ---------------------------------------------------------------------------
# Content / Metrics
# ---------------------------------------------------------------------------

class InpaintContent(BaseModel):
    inpaint_spec: InpaintSpec = Field(default_factory=InpaintSpec)
    output_video: VideoAsset = Field(default_factory=VideoAsset)


class InpaintMetrics(BaseModel):
    mask_mode: str = ""
    has_replacement: bool = False


# ---------------------------------------------------------------------------
# Top-level I/O
# ---------------------------------------------------------------------------

class InpaintAgentInput(BaseModel):
    """Input payload for InpaintAgent.

    ``source_video_path``: the video to edit.
    ``mask_mode``: how to generate the mask:
      - 'manual': use mask_path as an explicit mask image/video
      - 'depth_foreground': auto-mask foreground via depth estimation
      - 'depth_background': auto-mask background via depth estimation
      - 'object_track': track and mask a specific object (described in
        replacement_description)
    ``mask_path``: explicit mask file (for manual mode).
    ``replacement_description``: what to paint in the masked region.
    """

    source_video_path: str = ""
    mask_mode: str = "manual"
    mask_path: str = ""
    replacement_description: str = ""


class InpaintAgentOutput(BaseModel):
    """Output payload for InpaintAgent."""

    meta: Meta = Field(default_factory=Meta)
    content: InpaintContent = Field(default_factory=InpaintContent)
    metrics: InpaintMetrics = Field(default_factory=InpaintMetrics)
