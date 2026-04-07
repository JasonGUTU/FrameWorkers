"""StoryAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

from pydantic import BaseModel

from ..descriptor import SubAgentDescriptor
from ..contracts import InputBundleV2
from .agent import StoryAgent
from .labels import INPUT_LABEL_CREATIVE_BRIEF
from .schema import StoryAgentInput
from .evaluator import StoryEvaluator

OUTPUT_ASSET_KEY = "story"


def build_input(
    _task_id: str,
    input_bundle_v2: InputBundleV2,
) -> BaseModel:
    """Construct typed input from the unified workspace bundle.

    The creative brief is selected by InputResolver via the
    ``[creative_brief]`` label and arrives as a caption-rich artifact
    (a JSON file produced by IntakeTextAgent). The verbatim user text
    lives at ``payload.content.text``; older paths placed it at the
    top-level ``payload.text``; both are supported as fallbacks.
    """
    resolved = input_bundle_v2.resolved_artifacts
    brief_entry = resolved.get(INPUT_LABEL_CREATIVE_BRIEF, {})
    payload = brief_entry.get("payload", {}) if isinstance(brief_entry, dict) else {}
    creative_brief = ""
    if isinstance(payload, dict):
        # New shape: IntakeTextAgent JSON output → payload.content.text
        content = payload.get("content")
        if isinstance(content, dict):
            creative_brief = str(content.get("text") or "")
        # Legacy shape: top-level payload.text
        if not creative_brief:
            creative_brief = str(payload.get("text", "") or "")
    if not creative_brief and isinstance(brief_entry, dict):
        # Final fallback: caption.why (the user_intent string).
        creative_brief = str(brief_entry.get("why", "") or "")
    return StoryAgentInput(creative_brief=creative_brief)


CATALOG_ENTRY = (
    "StoryAgent\n"
    "  - Input: creative_brief (a natural-language description of what to produce)\n"
    "  - Output: story_blueprint (logline, cast, locations, story_arc, scene_outline)\n"
    "  - Purpose: Produce a structured story blueprint. Autonomously decides "
    "whether the input is a short prompt to expand or a detailed outline to structure."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_id="StoryAgent",
    asset_key=OUTPUT_ASSET_KEY,
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: StoryAgent(llm_client=llm),
    evaluator_factory=StoryEvaluator,
    build_input=build_input,
    materializer_factory=None,
    input_needs_description=(
        "I am the pipeline entry point for story planning. I take a "
        "natural-language creative brief and turn it into a structured "
        "story blueprint.\n\n"
        f"[{INPUT_LABEL_CREATIVE_BRIEF}] (single)\n"
        "A natural-language brief describing what kind of story / video to "
        "produce. This may be a short prompt ('make a 30s film about a cat "
        "chasing a butterfly') or a longer detailed outline / draft story "
        "text. The caption describes it as a creative brief / project "
        "intent description. Pick the single most recent / most "
        "authoritative such brief."
    ),
)
