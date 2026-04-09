"""UnivaKeyFrameAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from ..descriptor import SubAgentDescriptor
from ..contracts import InputBundleV2
from .agent import UnivaKeyFrameAgent
from .labels import INPUT_LABEL_STORYBOARD
from .schema import UnivaKeyFrameInput
from .evaluator import UnivaKeyFrameEvaluator
from .materializer import UnivaKeyFrameMaterializer
from inference.generation import select_image_service


def build_input(
    _task_id: str,
    input_bundle_v2: InputBundleV2,
) -> BaseModel:
    """Construct typed input from the pipeline bundle."""
    resolved = input_bundle_v2.resolved_artifacts
    sb = resolved.get(INPUT_LABEL_STORYBOARD, {})
    payload = sb.get("payload", {}) if isinstance(sb, dict) else {}
    content = payload.get("content", {}) if isinstance(payload, dict) else {}
    return UnivaKeyFrameInput(storyboard=content)


def materializer_factory(services: dict[str, Any]) -> UnivaKeyFrameMaterializer:
    return UnivaKeyFrameMaterializer(image_service=services["image_service"])


CATALOG_ENTRY = (
    "UnivaKeyFrameAgent\n"
    "  - Input: univa_storyboard (characters[], shots[], style)\n"
    "  - Output: univa_keyframes (character reference images + per-shot keyframe images)\n"
    "  - Purpose: Generate character images with LLM-refined prompts and\n"
    "    per-shot keyframes using UniVA's character-referenced image generation approach."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_id="UnivaKeyFrameAgent",
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: UnivaKeyFrameAgent(llm_client=llm),
    evaluator_factory=UnivaKeyFrameEvaluator,
    build_input=build_input,
    service_factories={
        "image_service": lambda ctx: select_image_service(),
    },
    materializer_factory=materializer_factory,
    input_needs_description=(
        "I generate character reference images and per-shot keyframes for the "
        "UniVA-style pipeline.\n\n"
        "For each [label] below, find every artifact in the registry whose caption "
        "describes the same kind of thing. Use the natural-language caption only.\n\n"
        f"[{INPUT_LABEL_STORYBOARD}] (single)\n"
        "The UniVA-style storyboard document: a structured plan listing the cast "
        "of characters with descriptions and the shots that make up the video, "
        "each shot with its setting, plot beat, static visual description, and "
        "camera design. Choose at most one."
    ),
)
