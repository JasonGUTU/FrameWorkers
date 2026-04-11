"""UnivaVideoAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from ..common_schema import ImageReferenceEntry, ResolvedArtifactEntry
from ..descriptor import SubAgentDescriptor
from .agent import UnivaVideoAgent
from .labels import INPUT_LABEL_SHOT_KEYFRAMES, INPUT_LABEL_STORYBOARD
from .schema import UnivaVideoInput
from .evaluator import UnivaVideoEvaluator
from .materializer import UnivaVideoMaterializer
from inference.generation import select_video_service


def build_input(
    _task_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    """Construct typed input from the resolved artifact dict."""
    sb = ResolvedArtifactEntry.coerce(resolved_artifacts.get(INPUT_LABEL_STORYBOARD))
    content = (sb.payload or {}).get("content", {})
    if not isinstance(content, dict):
        content = {}
    return UnivaVideoInput(
        storyboard=content,
        shot_keyframes=ImageReferenceEntry.list_from_resolved(
            resolved_artifacts.get(INPUT_LABEL_SHOT_KEYFRAMES)
        ),
    )


def materializer_factory(services: dict[str, Any]) -> UnivaVideoMaterializer:
    return UnivaVideoMaterializer(video_service=services["video_service"])


def build_captions(agent_id: str, output_dict: dict) -> dict:
    content = output_dict.get("content", {})
    shots = content.get("shot_videos", [])
    shot_count = len(shots)
    caps: dict = {}
    caps[agent_id] = {
        "caption": f"Univa video assembly manifest: {shot_count} shot(s). Final visual deliverable.",
        "scope": "global",
    }
    for sv in shots:
        shot_id = sv.get("shot_id") if isinstance(sv, dict) else None
        if shot_id is not None:
            caps[f"clip_shot_{shot_id}"] = {
                "caption": f"Video clip for shot {shot_id}. One segment of the Univa final video.",
                "scope": f"shot:{shot_id}",
            }
    caps["clip_final"] = {
        "caption": f"Complete assembled Univa video ({shot_count} shots). Final visual deliverable.",
        "scope": "global",
    }
    return caps


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
    build_captions=build_captions,
    service_factories={
        "video_service": lambda ctx: select_video_service(),
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
