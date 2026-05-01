"""StyleTransferAgent descriptor — built from a single AgentSpec."""

from __future__ import annotations

import json

from pydantic import BaseModel

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import AgentSpec, InputLabelSpec, SubAgentDescriptor
from .agent import StyleTransferAgent
from .evaluator import StyleTransferEvaluator
from .labels import (
    INPUT_LABEL_CREATIVE_BRIEF,
    INPUT_LABEL_SOURCE_VIDEO,
    INPUT_LABEL_STYLE_REFERENCE,
)
from .materializer import StyleTransferMaterializer
from .schema import StyleTransferAgentInput


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
    brief = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_CREATIVE_BRIEF)
    )

    style_desc = style_ref.caption or ""
    if style_ref.payload and isinstance(style_ref.payload.get("style"), str):
        style_desc = style_ref.payload["style"]

    brief_text = (
        json.dumps(brief.payload, ensure_ascii=False, indent=2)
        if brief.payload
        else ""
    )

    return StyleTransferAgentInput(
        source_video_path=video.path,
        style_description=style_desc,
        style_reference_path=style_ref.path,
        creative_brief_json_text=brief_text,
    )


def build_captions(agent_id: str, _output_dict: dict) -> dict:
    # Caption role: signal "style-transfer output video" so downstream
    # video agents can discover me. Content (style_description) lives
    # in the JSON payload, NOT in caption.
    # See MEMORY:feedback_caption_role_not_content.
    return {
        agent_id: {
            "caption": (
                "Style-transferred video: visual style applied to a "
                "source video. Structured manifest — see payload for "
                "the style specification."
            ),
            "scope": "global",
        },
        "style_transfer_output": {
            "caption": (
                "Style-transferred video binary (mp4) — source video with "
                "visual style applied. Can be re-ingested by downstream "
                "video agents (analysis / extension / inpainting / "
                "compositing)."
            ),
            "scope": "global",
        },
    }


def materializer_factory(services: dict) -> StyleTransferMaterializer:
    return StyleTransferMaterializer(
        video_edit_service=services["video_edit_service"]
    )


SPEC = AgentSpec(
    agent_id="StyleTransferAgent",
    inputs=[
        InputLabelSpec(
            name=INPUT_LABEL_SOURCE_VIDEO,
            cardinality="single",
            description=(
                "The source video FILE on disk to restyle — a binary "
                "mp4 artifact (mime=video/mp4) whose actual bytes the "
                "materializer feeds to the style-transfer video model. "
                "This label targets the mp4 binary specifically, NOT "
                "any JSON/manifest video_package artifact that may "
                "coexist."
            ),
        ),
        InputLabelSpec(
            name=INPUT_LABEL_STYLE_REFERENCE,
            cardinality="single",
            description=(
                "A style reference — either an image whose visual style "
                "to mimic, or a text artifact describing the desired "
                "style. The caption should describe the target aesthetic "
                "(e.g. 'Studio Ghibli watercolor', 'cyberpunk neon noir')."
            ),
        ),
        InputLabelSpec(
            name=INPUT_LABEL_CREATIVE_BRIEF,
            cardinality="single",
            optional=True,
            description=(
                "The user's verbatim natural-language brief for the "
                "whole pipeline (auto-persisted from chat / text upload). "
                "Fallback source for the target visual style when the "
                "user wrote the style cue inline in plain text (e.g. "
                "'convert this to Studio Ghibli', 'ink-wash style') and "
                "no dedicated [style_reference] artifact exists. Read "
                "alongside [style_reference]; treat [style_reference] as "
                "primary when both are present."
            ),
        ),
    ],
    output_description=(
        "stylized_video (source video with new visual style applied)."
    ),
    purpose_and_trigger=(
        """Apply a visual style transfer to an existing video. The stylised video IS the deliverable by default. Trigger: requests to apply a visual style transformation (anime, ink-wash, cyberpunk, oil painting, named-artist style, etc.) to an existing clip."""
    ),
    input_preamble=(
        "I apply visual style transfer to a video — transforming its "
        "appearance (anime, oil painting, watercolor, cyberpunk, etc.) "
        "while preserving the original motion and content."
    ),
)


DESCRIPTOR = SubAgentDescriptor.from_spec(
    SPEC,
    agent_factory=lambda llm: StyleTransferAgent(llm_client=llm),
    evaluator_factory=StyleTransferEvaluator,
    build_input=build_input,
    build_captions=build_captions,
    service_factories={
        "video_edit_service": lambda ctx: __import__(
            "inference.generation", fromlist=["select_video_edit_service"]
        ).select_video_edit_service(),
    },
    materializer_factory=materializer_factory,
)
