"""UnivaStoryboardAgent descriptor — built from a single AgentSpec."""

from __future__ import annotations

import json

from pydantic import BaseModel

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import AgentSpec, InputLabelSpec, SubAgentDescriptor
from .agent import UnivaStoryboardAgent
from .evaluator import UnivaStoryboardEvaluator
from .labels import INPUT_LABEL_CREATIVE_BRIEF
from .schema import UnivaStoryboardInput


def build_input(
    _step_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    """Univa-style pass-through: dump the entire upstream payload as JSON text."""
    brief = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_CREATIVE_BRIEF)
    )
    return UnivaStoryboardInput(
        creative_brief_json_text=json.dumps(
            brief.payload or {}, ensure_ascii=False, indent=2
        ),
    )


def build_captions(agent_id: str, output_dict: dict) -> dict:
    content = output_dict.get("content", {})
    char_count = len(content.get("characters", []))
    shot_count = len(content.get("shots", []))
    return {
        agent_id: {
            "caption": (
                f"Univa storyboard: {char_count} character(s), {shot_count} "
                f"shot(s). Input for keyframe and video generation."
            ),
            "scope": "global",
        },
    }


SPEC = AgentSpec(
    agent_id="UnivaStoryboardAgent",
    inputs=[
        InputLabelSpec(
            name=INPUT_LABEL_CREATIVE_BRIEF,
            cardinality="single",
            description=(
                "A natural-language brief describing the story / video "
                "concept to be produced. The caption describes it as a "
                "creative brief / project intent description. Pick the "
                "single most recent / most authoritative such brief."
            ),
        ),
    ],
    output_description=(
        "univa_storyboard (characters[], shots[], style)."
    ),
    purpose_and_trigger=(
        "Generate a complete storyboard with character definitions and "
        "shot-by-shot breakdown using UniVA's storyboard planning "
        "approach. Pipeline entry point for UniVA-style creation (runs "
        "instead of the standard story + screenplay steps when the "
        "user's plan targets the UniVA track)."
    ),
    input_preamble=(
        "I am the pipeline entry point for UniVA-style storyboard "
        "planning. I take a natural-language creative brief and produce "
        "a storyboard with character definitions and a shot-by-shot "
        "breakdown."
    ),
)


DESCRIPTOR = SubAgentDescriptor.from_spec(
    SPEC,
    agent_factory=lambda llm: UnivaStoryboardAgent(llm_client=llm),
    evaluator_factory=UnivaStoryboardEvaluator,
    build_input=build_input,
    build_captions=build_captions,
)
