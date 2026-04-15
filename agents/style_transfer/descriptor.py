"""StyleTransferAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

from pydantic import BaseModel

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import SubAgentDescriptor
from .agent import StyleTransferAgent
from .labels import INPUT_LABEL_SOURCE_VIDEO, INPUT_LABEL_STYLE_REFERENCE
from .schema import StyleTransferAgentInput
from .evaluator import StyleTransferEvaluator
from .materializer import StyleTransferMaterializer


def build_input(
    _step_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    video = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_SOURCE_VIDEO)
    )
    style_ref = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_STYLE_REFERENCE)
    )

    # Style description comes from the style reference caption or payload
    style_desc = style_ref.caption or ""
    if style_ref.payload and isinstance(style_ref.payload.get("style"), str):
        style_desc = style_ref.payload["style"]

    return StyleTransferAgentInput(
        source_video_path=video.path,
        style_description=style_desc,
        style_reference_path=style_ref.path,
    )


def build_captions(agent_id: str, output_dict: dict) -> dict:
    content = output_dict.get("content", {})
    spec = content.get("style_spec", {})
    desc = spec.get("style_description", "unknown style")
    return {
        agent_id: {
            "caption": (
                f"Style-transferred video: {desc}. "
                f"Visual style applied to source video."
            ),
            "scope": "global",
        },
    }


def materializer_factory(services: dict) -> StyleTransferMaterializer:
    return StyleTransferMaterializer(video_edit_service=services["video_edit_service"])


CATALOG_ENTRY = (
    "StyleTransferAgent\n"
    "  - Input: a source-video artifact + a style reference (text describing the style, "
    "and/or an uploaded reference image).\n"
    "  - Output: stylized_video (source video with new visual style applied).\n"
    "  - Purpose: Apply visual style transfer to a video (anime, oil painting, cyberpunk, "
    "ink wash, etc.) while preserving motion. Need both an ingested source video AND a user "
    "style description before I can run. The output is itself a finished video — no further "
    "composition needed unless the user also wants subtitles, audio, or another edit chained on."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_id="StyleTransferAgent",
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: StyleTransferAgent(llm_client=llm),
    evaluator_factory=StyleTransferEvaluator,
    build_input=build_input,
    build_captions=build_captions,
    service_factories={
        "video_edit_service": lambda ctx: __import__("inference.generation", fromlist=["select_video_edit_service"]).select_video_edit_service(),
    },
    materializer_factory=materializer_factory,
    input_needs_description=(
        "I apply visual style transfer to a video — transforming its "
        "appearance (anime, oil painting, watercolor, cyberpunk, etc.) "
        "while preserving the original motion and content.\n\n"
        f"[{INPUT_LABEL_SOURCE_VIDEO}] (single)\n"
        "The source video file to restyle.\n\n"
        f"[{INPUT_LABEL_STYLE_REFERENCE}] (single)\n"
        "A style reference — either an image whose visual style to mimic, "
        "or a text artifact describing the desired style. The caption "
        "should describe the target aesthetic."
    ),
)
