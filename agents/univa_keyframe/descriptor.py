"""UnivaKeyFrameAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import SubAgentDescriptor
from .agent import UnivaKeyFrameAgent
from .labels import INPUT_LABEL_STORYBOARD
from .schema import UnivaKeyFrameInput
from .evaluator import UnivaKeyFrameEvaluator
from .materializer import UnivaKeyFrameMaterializer
from inference.generation import select_image_service


def build_input(
    _step_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    """Univa-style pass-through: dump the entire upstream payload as JSON text."""
    sb = ResolvedArtifactEntry.coerce(resolved_artifacts.get(INPUT_LABEL_STORYBOARD))
    return UnivaKeyFrameInput(
        storyboard_json_text=json.dumps(
            sb.payload or {}, ensure_ascii=False, indent=2
        ),
    )


def materializer_factory(services: dict[str, Any]) -> UnivaKeyFrameMaterializer:
    return UnivaKeyFrameMaterializer(image_service=services["image_service"])


def build_captions(agent_id: str, output_dict: dict) -> dict:
    content = output_dict.get("content", {})
    char_count = len(content.get("character_images", []))
    shot_count = len(content.get("shot_keyframes", []))
    caps: dict = {}
    caps[agent_id] = {
        "caption": (
            f"Univa keyframe planning document: {char_count} character(s), "
            f"{shot_count} shot(s). Consumed by UnivaVideoAgent."
        ),
        "scope": "global",
    }
    for ci in content.get("character_images", []):
        cid = ci.get("char_id", "") if isinstance(ci, dict) else ""
        if cid:
            caps[f"img_{cid}_character"] = {
                "caption": f"Character reference image for {cid}. Visual identity anchor — not a video frame.",
                "scope": "global",
            }
    for kf in content.get("shot_keyframes", []):
        shot_id = kf.get("shot_id") if isinstance(kf, dict) else None
        if shot_id is not None:
            caps[f"img_shot_{shot_id}_keyframe"] = {
                "caption": f"Rendered starting frame for shot {shot_id}. To be animated into a video clip by UnivaVideoAgent.",
                "scope": f"shot:{shot_id}",
            }
    return caps


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
    build_captions=build_captions,
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
