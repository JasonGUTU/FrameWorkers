"""BriefEnricherAgent descriptor — built from a single AgentSpec."""

from __future__ import annotations

import json

from pydantic import BaseModel

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import AgentSpec, InputLabelSpec, SubAgentDescriptor
from .agent import BriefEnricherAgent
from .evaluator import BriefEnricherEvaluator
from .labels import (
    INPUT_LABEL_IMAGE_DESCRIPTIONS,
    INPUT_LABEL_IMAGE_FILES,
    INPUT_LABEL_RAW_BRIEF,
)
from .schema import BriefEnricherInput


def build_input(
    _step_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    brief = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_RAW_BRIEF)
    )
    images = ResolvedArtifactEntry.coerce_list(
        resolved_artifacts.get(INPUT_LABEL_IMAGE_DESCRIPTIONS)
    )
    image_files = ResolvedArtifactEntry.coerce_list(
        resolved_artifacts.get(INPUT_LABEL_IMAGE_FILES)
    )
    image_payloads = [img.payload or {} for img in images]
    image_paths = [f.path for f in image_files if f.path]
    return BriefEnricherInput(
        raw_brief_json_text=json.dumps(
            brief.payload or {}, ensure_ascii=False, indent=2
        ),
        image_payloads_json_text=json.dumps(
            image_payloads, ensure_ascii=False, indent=2
        ),
        image_paths=image_paths,
    )


def build_captions(agent_id: str, output_dict: dict) -> dict:
    content = output_dict.get("content", {})
    caps: dict = {}
    caps[agent_id] = {
        "caption": (
            "Enriched creative brief with visual reference descriptions "
            "integrated. Supersedes the raw user brief for story "
            "generation — contains the user's original concept plus "
            "detailed visual descriptions of uploaded reference images."
        ),
        "scope": "global",
    }
    # Update existing image captions with role-specific info.
    # Keys starting with "_update:" tell the persist layer to call
    # global_memory.update_caption_by_path() instead of registering a
    # new entry. One asset = one caption.
    #
    # ``role`` is a closed enum (character | location | prop | style) —
    # safe to put in caption as a categorical role tag. ``entity_hint``
    # is free-form LLM text (e.g. "an elderly watchmaker") — NOT in
    # caption, stays in the JSON payload.
    # See MEMORY:feedback_caption_role_not_content.
    image_paths = content.get("image_paths", [])
    for cls in content.get("image_classifications", []):
        if not isinstance(cls, dict):
            continue
        idx = cls.get("image_index", -1)
        role = cls.get("role", "general")
        if 0 <= idx < len(image_paths):
            caps[f"_update:ref_{role}_{idx}"] = {
                "caption": (
                    f"Global {role} reference image. "
                    f"Visual identity anchor for downstream keyframe generation."
                ),
                "scope": "global",
                "path": image_paths[idx],
            }
    return caps


SPEC = AgentSpec(
    agent_id="BriefEnricherAgent",
    inputs=[
        InputLabelSpec(
            name=INPUT_LABEL_RAW_BRIEF,
            cardinality="single",
            description=(
                "The raw creative brief — the user's text describing the "
                "story or video concept. Typically the output of "
                "IntakeTextAgent. Choose the single most recent text "
                "brief."
            ),
        ),
        InputLabelSpec(
            name=INPUT_LABEL_IMAGE_DESCRIPTIONS,
            cardinality="collection",
            description=(
                "The JSON descriptor artifacts from IntakeImageAgent. "
                "Each entry's payload contains a visual_description of "
                "the uploaded image. Match by caption mentioning "
                "'reference image' and mime=application/json. Include "
                "every processed image upload."
            ),
        ),
        InputLabelSpec(
            name=INPUT_LABEL_IMAGE_FILES,
            cardinality="collection",
            description=(
                "The actual uploaded image FILES (PNG/JPG) registered by "
                "IntakeImageAgent. Each entry's path points directly to "
                "the image file on disk (not a JSON descriptor). Match "
                "by mime=image/*. Include every uploaded image file."
            ),
        ),
    ],
    output_description=(
        "enriched creative brief with the images' visual details woven "
        "in + per-image role classifications (character / location / "
        "style / etc.)."
    ),
    purpose_and_routing=(
        """Fold a visual description (from an uploaded reference image) into the user's text brief, producing one unified enriched brief for the story writer. Trigger: image-reference creative flow (user uploaded an image as character / location / style reference)."""
    ),
    input_preamble=(
        "I merge visual descriptions from uploaded reference images into "
        "the user's creative brief so that downstream story generation "
        "creates characters / locations / props that MATCH the uploaded "
        "images."
    ),
)


DESCRIPTOR = SubAgentDescriptor.from_spec(
    SPEC,
    agent_factory=lambda llm: BriefEnricherAgent(llm_client=llm),
    evaluator_factory=BriefEnricherEvaluator,
    build_input=build_input,
    build_captions=build_captions,
)
