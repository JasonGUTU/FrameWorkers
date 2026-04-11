"""UnivaStoryboardAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

from pydantic import BaseModel

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import SubAgentDescriptor
from .agent import UnivaStoryboardAgent
from .labels import INPUT_LABEL_CREATIVE_BRIEF
from .schema import UnivaStoryboardInput
from .evaluator import UnivaStoryboardEvaluator


def build_input(
    _task_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    """Construct typed input from the resolved artifact dict.

    The creative brief is selected by InputResolver via the
    ``[creative_brief]`` label.
    """
    brief = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_CREATIVE_BRIEF)
    )
    user_prompt = ""
    if brief.payload:
        user_prompt = str(brief.payload.get("text", "") or "")
    if not user_prompt:
        user_prompt = brief.caption
    return UnivaStoryboardInput(user_prompt=user_prompt)


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


CATALOG_ENTRY = (
    "UnivaStoryboardAgent\n"
    "  - Input: creative_brief (a natural-language description of what to produce)\n"
    "  - Output: univa_storyboard (characters[], shots[], style)\n"
    "  - Purpose: Generate a complete storyboard with character definitions and\n"
    "    shot-by-shot breakdown using UniVA's storyboard planning approach."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_id="UnivaStoryboardAgent",
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: UnivaStoryboardAgent(llm_client=llm),
    evaluator_factory=UnivaStoryboardEvaluator,
    build_input=build_input,
    build_captions=build_captions,
    materializer_factory=None,
    input_needs_description=(
        "I am the pipeline entry point for UniVA-style storyboard planning. "
        "I take a natural-language creative brief and produce a storyboard "
        "with character definitions and a shot-by-shot breakdown.\n\n"
        f"[{INPUT_LABEL_CREATIVE_BRIEF}] (single)\n"
        "A natural-language brief describing the story / video concept to "
        "be produced. The caption describes it as a creative brief / project "
        "intent description. Pick the single most recent / most authoritative "
        "such brief."
    ),
)
