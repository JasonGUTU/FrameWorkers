"""StoryAgent descriptor — built from a single AgentSpec."""

from __future__ import annotations

import json

from pydantic import BaseModel

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import AgentSpec, InputLabelSpec, SubAgentDescriptor
from .agent import StoryAgent
from .evaluator import StoryEvaluator
from .labels import INPUT_LABEL_CREATIVE_BRIEF, INPUT_LABEL_REFERENCE_ANALYSIS
from .schema import StoryAgentInput


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
    # Caption role: signal "story blueprint" to a downstream screenplay
    # step. Metrics (scene/char counts) are neutral; genre (free-form LLM
    # text) is NOT in caption — lives in payload.
    # See MEMORY:feedback_caption_role_not_content.
    content = output_dict.get("content", {})
    scene_count = len(content.get("scene_outline", []))
    char_count = len(content.get("cast", []))
    return {
        agent_id: {
            "caption": (
                f"Story blueprint: {scene_count} scene(s), {char_count} "
                f"character(s). Structured input for screenplay generation."
            ),
            "scope": "global",
        },
    }


SPEC = AgentSpec(
    agent_id="StoryAgent",
    inputs=[
        InputLabelSpec(
            name=INPUT_LABEL_CREATIVE_BRIEF,
            cardinality="single",
            description=(
                "A natural-language brief describing what kind of story / "
                "video to produce. May be a short prompt ('a film about a "
                "cat chasing a butterfly') or a longer detailed outline / "
                "draft story text. The caption describes it as a creative "
                "brief / project intent description. If an enriched brief "
                "(one that integrates image reference descriptions) is "
                "available, prefer it over the raw text-intake brief. "
                "Pick the single most recent / most authoritative such "
                "brief."
            ),
        ),
        InputLabelSpec(
            name=INPUT_LABEL_REFERENCE_ANALYSIS,
            cardinality="single",
            optional=True,
            description=(
                "Optional scene-level video-analysis report of an "
                "inspiration / reference video. Present in flows like "
                "'analyse this hit drama and write me a same-genre "
                "sequel / similar new story' — the LLM reads its genre, "
                "mood, scene summaries, and entities as creative seeds "
                "to shape tone and pacing of the NEW blueprint, without "
                "copying plot verbatim. Skip this label when there is "
                "no reference video being analysed."
            ),
        ),
    ],
    output_description=(
        "story_blueprint (logline, cast, locations, story_arc, "
        "scene_outline)."
    ),
    purpose_and_routing=(
        """First creative step for any task that produces a NEW film from scratch. Trigger: requests to create new film content (mini-drama, manhua, trailer, vertical short, etc.) — user provides a creative brief but no source video."""
    ),
    input_preamble=(
        "I am the pipeline entry point for story planning. I take a "
        "natural-language creative brief and turn it into a structured "
        "story blueprint."
    ),
)


DESCRIPTOR = SubAgentDescriptor.from_spec(
    SPEC,
    agent_factory=lambda llm: StoryAgent(llm_client=llm),
    evaluator_factory=StoryEvaluator,
    build_input=build_input,
    build_captions=build_captions,
)
