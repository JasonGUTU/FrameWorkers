"""UnivaVideoAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

import os
from typing import Any

from pydantic import BaseModel

from ..common_schema import ImageReferenceEntry
from ..descriptor import SubAgentDescriptor
from ..contracts import InputBundleV2
from .agent import UnivaVideoAgent
from .labels import INPUT_LABEL_SHOT_KEYFRAMES, INPUT_LABEL_STORYBOARD
from .schema import UnivaVideoInput
from .evaluator import UnivaVideoEvaluator
from .materializer import UnivaVideoMaterializer
from inference.generation.video_generators.service import FalVideoService


def build_input(
    _task_id: str,
    input_bundle_v2: InputBundleV2,
) -> BaseModel:
    """Construct typed input from the pipeline bundle."""
    resolved = input_bundle_v2.resolved_artifacts
    sb = resolved.get(INPUT_LABEL_STORYBOARD, {})
    payload = sb.get("payload", {}) if isinstance(sb, dict) else {}
    content = payload.get("content", {}) if isinstance(payload, dict) else {}

    keyframes_raw = resolved.get(INPUT_LABEL_SHOT_KEYFRAMES, [])
    if not isinstance(keyframes_raw, list):
        keyframes_raw = []
    shot_keyframes: list[ImageReferenceEntry] = []
    for it in keyframes_raw:
        if not isinstance(it, dict):
            continue
        path = str(it.get("path", "") or "").strip()
        if not path:
            continue
        shot_keyframes.append(
            ImageReferenceEntry(
                path=path,
                caption_what=str(it.get("what", "") or ""),
                caption_why=str(it.get("why", "") or ""),
                mime=str(it.get("mime", "") or ""),
                scope=str(it.get("scope", "") or ""),
            )
        )

    return UnivaVideoInput(
        storyboard=content,
        shot_keyframes=shot_keyframes,
    )


def materializer_factory(services: dict[str, Any]) -> UnivaVideoMaterializer:
    return UnivaVideoMaterializer(video_service=services["video_service"])


def _video_service_factory(ctx: Any) -> FalVideoService:
    backend = os.getenv("FW_VIDEO_BACKEND", "fal").strip().lower()
    if backend == "fal":
        return FalVideoService()
    # Extensible: add other backends here
    return FalVideoService()


CATALOG_ENTRY = (
    "UnivaVideoAgent\n"
    "  - Input: univa_storyboard (shot metadata) + univa_keyframes (per-shot images)\n"
    "  - Output: univa_video (per-shot 5s MP4 clips + final merged video)\n"
    "  - Purpose: Generate video clips from keyframe images using I2V,\n"
    "    then merge into a continuous video using UniVA's pipeline approach."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_id="UnivaVideoAgent",
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: UnivaVideoAgent(llm_client=llm),
    evaluator_factory=UnivaVideoEvaluator,
    build_input=build_input,
    service_factories={
        "video_service": _video_service_factory,
    },
    materializer_factory=materializer_factory,
    input_needs_description=(
        "I render and assemble the UniVA-style video from per-shot keyframe images.\n\n"
        "For each [label] below, find every artifact in the registry whose caption "
        "describes the same kind of thing. Use the natural-language caption only.\n\n"
        f"[{INPUT_LABEL_STORYBOARD}] (single)\n"
        "The UniVA-style storyboard document defining the ordered list of shots "
        "with their creative direction. Choose at most one.\n\n"
        f"[{INPUT_LABEL_SHOT_KEYFRAMES}] (collection)\n"
        "The actual rendered keyframe images for the planned shots in the storyboard. "
        "Each one is a still depicting one specific shot, intended to be animated "
        "into a moving clip. Include every per-shot keyframe image. Do not include "
        "standalone character or location reference images that are not tied to a "
        "specific shot."
    ),
)
