"""UnivaStoryboardAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

from pydantic import BaseModel

from ..descriptor import SubAgentDescriptor
from ..contracts import InputBundleV2
from .agent import UnivaStoryboardAgent
from .labels import INPUT_LABEL_CREATIVE_BRIEF
from .schema import UnivaStoryboardInput
from .evaluator import UnivaStoryboardEvaluator

OUTPUT_ASSET_KEY = "univa_storyboard"


def build_input(
    _task_id: str,
    input_bundle_v2: InputBundleV2,
) -> BaseModel:
    """Construct typed input from the unified workspace bundle.

    The creative brief is selected by InputResolver via the
    ``[creative_brief]`` label.
    """
    resolved = input_bundle_v2.resolved_artifacts
    brief_entry = resolved.get(INPUT_LABEL_CREATIVE_BRIEF, {})
    payload = brief_entry.get("payload", {}) if isinstance(brief_entry, dict) else {}
    user_prompt = ""
    if isinstance(payload, dict):
        user_prompt = str(payload.get("text", "") or "")
    if not user_prompt and isinstance(brief_entry, dict):
        user_prompt = str(brief_entry.get("why", "") or "")
    return UnivaStoryboardInput(user_prompt=user_prompt)


CATALOG_ENTRY = (
    "UnivaStoryboardAgent\n"
    "  - Input: creative_brief (a natural-language description of what to produce)\n"
    "  - Output: univa_storyboard (characters[], shots[], style)\n"
    "  - Purpose: Generate a complete storyboard with character definitions and\n"
    "    shot-by-shot breakdown using UniVA's storyboard planning approach."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_id="UnivaStoryboardAgent",
    asset_key=OUTPUT_ASSET_KEY,
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: UnivaStoryboardAgent(llm_client=llm),
    evaluator_factory=UnivaStoryboardEvaluator,
    build_input=build_input,
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
