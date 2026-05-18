"""ComedyStoryAgent descriptor — comedy-specialised StoryAgent.

Same I/O contract as StoryAgent's descriptor (same labels, same
``build_input`` shape, same ``StoryAgentInput``); only the agent_id,
purpose_and_trigger, output_description, and caption text are
specialised toward comedic blueprints.
"""

from __future__ import annotations

import json

from pydantic import BaseModel

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import AgentSpec, InputLabelSpec, SubAgentDescriptor
from ..story.evaluator import StoryEvaluator
from ..story.labels import (
    INPUT_LABEL_CREATIVE_BRIEF,
    INPUT_LABEL_REFERENCE_ANALYSIS,
)
from ..story.schema import StoryAgentInput
from .agent import ComedyStoryAgent


def build_input(
    _step_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    """Univa-style pass-through: dump upstream payload as raw JSON text."""
    brief = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_CREATIVE_BRIEF)
    )
    reference = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_REFERENCE_ANALYSIS)
    )
    return StoryAgentInput(
        creative_brief_json_text=json.dumps(
            brief.payload or {}, ensure_ascii=False, indent=2
        ),
        reference_analysis_json_text=json.dumps(
            reference.payload, ensure_ascii=False, indent=2
        ) if reference.payload else "",
    )


def build_captions(agent_id: str, output_dict: dict) -> dict:
    content = output_dict.get("content", {})
    scene_count = len(content.get("scene_outline", []))
    char_count = len(content.get("cast", []))
    return {
        agent_id: {
            "caption": (
                f"Comedy story blueprint: {scene_count} scene(s), "
                f"{char_count} character(s). Structured input for "
                f"screenplay generation."
            ),
            "scope": "global",
        },
    }


SPEC = AgentSpec(
    agent_id="ComedyStoryAgent",
    inputs=[
        InputLabelSpec(
            name=INPUT_LABEL_CREATIVE_BRIEF,
            cardinality="single",
            description=(
                "A natural-language brief describing what kind of "
                "comedic video to produce. May be a short prompt or "
                "a longer detailed outline / draft story text. The "
                "caption describes it as a creative brief / project "
                "intent description. If an enriched brief (one that "
                "integrates image reference descriptions) is available, "
                "prefer it over the raw text-intake brief. Pick the "
                "single most recent / most authoritative such brief."
            ),
        ),
        InputLabelSpec(
            name=INPUT_LABEL_REFERENCE_ANALYSIS,
            cardinality="single",
            optional=True,
            description=(
                "Optional scene-level video-analysis report of an "
                "inspiration / reference comedy. The LLM reads its "
                "genre, mood, scene summaries, and entities as creative "
                "seeds to shape tone and pacing of the NEW comedic "
                "blueprint, without copying plot verbatim. Skip this "
                "label when there is no reference video being analysed."
            ),
        ),
    ],
    output_description=(
        "comedy_story_blueprint (logline, cast with comic flaws, "
        "locations, story_arc built on comic reversals, scene_outline "
        "with setup→escalation→punchline shape)."
    ),
    purpose_and_trigger=(
        "Creative blueprint step specialised for COMEDIC film projects "
        "— sitcoms, sketch comedy, satire, parody, slapstick, romantic "
        "comedy, dark comedy, screwball, mockumentary, deadpan or "
        "absurdist humour, cringe comedy, etc. Takes a creative brief "
        "and produces a story blueprint whose scenes are shaped around "
        "setup → escalation → punchline structure, whose cast carries "
        "clear comic flaws, and whose arc is built on comic reversals "
        "(status flips, mistaken identity, escalation from a trivial "
        "seed, ironic comeuppance) rather than tragic / dramatic "
        "catharsis."
    ),
    input_preamble=(
        "I am a comedy-specialised entry point for story planning. I "
        "take a natural-language creative brief and turn it into a "
        "comedy-shaped story blueprint."
    ),
)


DESCRIPTOR = SubAgentDescriptor.from_spec(
    SPEC,
    agent_factory=lambda llm: ComedyStoryAgent(llm_client=llm),
    evaluator_factory=StoryEvaluator,
    build_input=build_input,
    build_captions=build_captions,
)
