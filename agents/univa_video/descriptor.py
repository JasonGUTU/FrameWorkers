"""UnivaVideoAgent descriptor — built from a single AgentSpec."""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel

from inference.generation import select_video_service

from ..common_schema import ImageReferenceEntry, ResolvedArtifactEntry
from ..descriptor import AgentSpec, InputLabelSpec, SubAgentDescriptor
from .agent import UnivaVideoAgent
from .evaluator import UnivaVideoEvaluator
from .labels import INPUT_LABEL_SHOT_KEYFRAMES, INPUT_LABEL_STORYBOARD
from .materializer import UnivaVideoMaterializer
from .schema import UnivaVideoInput


def build_input(
    _step_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    """Univa-style pass-through: dump the entire upstream payload as JSON text."""
    sb = ResolvedArtifactEntry.coerce(resolved_artifacts.get(INPUT_LABEL_STORYBOARD))
    return UnivaVideoInput(
        storyboard_json_text=json.dumps(
            sb.payload or {}, ensure_ascii=False, indent=2
        ),
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
        "caption": (
            f"Univa video assembly manifest: {shot_count} shot(s). "
            f"Final visual deliverable."
        ),
        "scope": "global",
    }
    for sv in shots:
        shot_id = sv.get("shot_id") if isinstance(sv, dict) else None
        if shot_id is not None:
            caps[f"clip_shot_{shot_id}"] = {
                "caption": (
                    f"Video clip for shot {shot_id}. One segment of the "
                    f"Univa final video."
                ),
                "scope": f"shot:{shot_id}",
            }
    caps["clip_final"] = {
        "caption": (
            f"Complete assembled Univa video ({shot_count} shots). "
            f"Final visual deliverable."
        ),
        "scope": "global",
    }
    return caps


SPEC = AgentSpec(
    agent_id="UnivaVideoAgent",
    inputs=[
        InputLabelSpec(
            name=INPUT_LABEL_STORYBOARD,
            cardinality="single",
            description=(
                "The UniVA-style storyboard document defining the "
                "ordered list of shots with their creative direction. "
                "Choose at most one."
            ),
        ),
        InputLabelSpec(
            name=INPUT_LABEL_SHOT_KEYFRAMES,
            cardinality="collection",
            description=(
                "The actual rendered keyframe images for the planned "
                "shots in the storyboard. Each one is a still depicting "
                "one specific shot, intended to be animated into a "
                "moving clip. Include every per-shot keyframe image. Do "
                "not include standalone character or location reference "
                "images that are not tied to a specific shot."
            ),
        ),
    ],
    output_description=(
        "univa_video (per-shot 5s MP4 clips + final merged video)."
    ),
    purpose_and_routing=(
        "Generate video clips from keyframe images using I2V, then "
        "merge into a continuous video using UniVA's pipeline approach. "
        "Last step of the UniVA-track pipeline (runs after "
        "UnivaKeyFrameAgent)."
    ),
    input_preamble=(
        "I render and assemble the UniVA-style video from per-shot "
        "keyframe images.\n\n"
        "For each [label] below, find every artifact in the registry "
        "whose caption describes the same kind of thing. Use the "
        "natural-language caption only."
    ),
)


DESCRIPTOR = SubAgentDescriptor.from_spec(
    SPEC,
    agent_factory=lambda llm: UnivaVideoAgent(llm_client=llm),
    evaluator_factory=UnivaVideoEvaluator,
    build_input=build_input,
    build_captions=build_captions,
    service_factories={"video_service": lambda ctx: select_video_service()},
    materializer_factory=materializer_factory,
)
