"""ScreenplayAgent descriptor — built from a single AgentSpec."""

from __future__ import annotations

import json

from pydantic import BaseModel

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import AgentSpec, InputLabelSpec, SubAgentDescriptor
from .agent import ScreenplayAgent
from .evaluator import ScreenplayEvaluator
from .labels import INPUT_LABEL_STORY
from .schema import ScreenplayAgentInput


def build_input(
    _step_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    """Univa-style pass-through: dump upstream story payload as raw JSON text.

    Single input: the upstream story_blueprint, selected by InputResolver
    via the ``[story]`` label. ScreenplayAgent has no concept of free-text
    user directives — any such directive flows in through the upstream
    re-run pattern (Director re-runs StoryAgent with the new brief; the
    updated story_blueprint reaches ScreenplayAgent through this same
    ``[story]`` label).
    """
    story = ResolvedArtifactEntry.coerce(resolved_artifacts.get(INPUT_LABEL_STORY))
    return ScreenplayAgentInput(
        story_json_text=json.dumps(
            story.payload or {}, ensure_ascii=False, indent=2
        ),
    )


def build_captions(agent_id: str, output_dict: dict) -> dict:
    content = output_dict.get("content", {})
    scenes = content.get("scenes", [])
    scene_count = len(scenes)
    shot_count = sum(len(s.get("shots", [])) for s in scenes if isinstance(s, dict))
    return {
        agent_id: {
            "caption": (
                f"Screenplay: {scene_count} scene(s), {shot_count} shot(s). "
                f"Input for keyframe planning and audio scoring."
            ),
            "scope": "global",
        },
    }


SPEC = AgentSpec(
    agent_id="ScreenplayAgent",
    inputs=[
        InputLabelSpec(
            name=INPUT_LABEL_STORY,
            cardinality="single",
            description=(
                "The high-level narrative plan for the whole video — "
                "written before any scene breakdown exists. It defines "
                "the logline, the cast of characters, the locations, the "
                "overall story arc, and a coarse scene-level outline. It "
                "does NOT yet contain a per-shot breakdown, dialogue, or "
                "camera direction; that is exactly what I will produce. "
                "Choose at most one such document for this story."
            ),
        ),
    ],
    output_description=(
        "screenplay (scenes -> shots: script + visual plan + per-scene "
        "consistency packs + per-scene mood/tone + "
        "estimated_duration_seconds)."
    ),
    purpose_and_routing=(
        """Turn a story blueprint into a scene/shot-structured screenplay with dialogue, action beats, and camera direction. The screenplay encodes shot-level dialogue / mood / duration consumed by downstream rendering and audio agents."""
    ),
    input_preamble=(
        "I take a high-level story plan and turn it into a full unified "
        "screenplay (scenes broken into shots, with visual direction, "
        "dialogue, and consistency packs)."
    ),
)


DESCRIPTOR = SubAgentDescriptor.from_spec(
    SPEC,
    agent_factory=lambda llm: ScreenplayAgent(llm_client=llm),
    evaluator_factory=ScreenplayEvaluator,
    build_input=build_input,
    build_captions=build_captions,
)
