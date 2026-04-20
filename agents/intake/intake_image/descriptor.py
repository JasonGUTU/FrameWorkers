"""IntakeImageAgent descriptor — built from a single AgentSpec."""

from __future__ import annotations

from pydantic import BaseModel

from ...common_schema import ResolvedArtifactEntry
from ...descriptor import AgentSpec, InputLabelSpec, SubAgentDescriptor
from .agent import IntakeImageAgent
from .evaluator import IntakeImageEvaluator
from .labels import INPUT_LABEL_RAW_IMAGE_UPLOAD
from .schema import IntakeImageInput


def build_input(
    _step_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    raw = resolved_artifacts.get(INPUT_LABEL_RAW_IMAGE_UPLOAD)
    if isinstance(raw, list):
        raw = raw[0] if raw else None
    entry = ResolvedArtifactEntry.coerce(raw)
    return IntakeImageInput(raw_image_path=entry.path)


def build_captions(agent_id: str, _output_dict: dict) -> dict:
    # Pure role/载体 caption — intentionally independent of output_dict.
    # Content (visual_description, image_asset) lives only in the JSON
    # snapshot payload; consumers read it via entry.payload, not caption.
    # See MEMORY:feedback_caption_role_not_content.
    return {
        agent_id: {
            "caption": (
                "Structured metadata document (JSON) for a user-uploaded "
                "image. Payload carries the visual description and image-"
                "asset metadata."
            ),
            "scope": "global",
        },
    }


SPEC = AgentSpec(
    agent_id="IntakeImageAgent",
    inputs=[
        InputLabelSpec(
            name=INPUT_LABEL_RAW_IMAGE_UPLOAD,
            cardinality="single",
            description=(
                "A raw user-uploaded image artifact whose caption starts "
                "with 'Raw user upload (mime=image/' and has scope "
                "'raw_pending'. Pick the single most recent such pending "
                "image upload."
            ),
        ),
    ],
    output_description=(
        "a caption-rich image artifact with a vision-LLM caption, "
        "discoverable by downstream agents via semantic-typed image "
        "labels (e.g. [character_reference], [style_reference])."
    ),
    purpose_and_routing=(
        """Intake raw user-uploaded image(s) as character / location / style reference artifact(s). Trigger: user uploaded image(s) as creative reference."""
    ),
    input_preamble=(
        "I convert raw user-uploaded images into caption-rich workspace "
        "artifacts. I am invoked once per upload, before any content "
        "agent runs."
    ),
    promotes_consumed_inputs_to_global=True,
)


DESCRIPTOR = SubAgentDescriptor.from_spec(
    SPEC,
    agent_factory=lambda llm: IntakeImageAgent(llm_client=llm),
    evaluator_factory=IntakeImageEvaluator,
    build_input=build_input,
    build_captions=build_captions,
)
