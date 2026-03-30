"""StoryAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

from pydantic import BaseModel

from ..descriptor import SubAgentDescriptor
from ..contracts import InputBundleV2
from .agent import StoryAgent
from .schema import StoryAgentInput, StoryConstraints
from .evaluator import StoryEvaluator

OUTPUT_ASSET_KEY = "story_blueprint"
USER_TEXT_KEY = "user_story_outline"


def build_input(
    _task_id: str,
    input_bundle_v2: InputBundleV2,
) -> BaseModel:
    resolved = (
        input_bundle_v2.context.get("resolved_inputs", {})
        if isinstance(getattr(input_bundle_v2, "context", None), dict)
        else {}
    )
    hints = getattr(input_bundle_v2, "hints", {}) or {}
    raw = resolved.get("source_text") or hints.get("source_text", "")
    source_text = raw if isinstance(raw, str) else str(raw)
    return StoryAgentInput(
        draft_idea=source_text,
        constraints=StoryConstraints(),
        user_provided_text=(resolved.get(USER_TEXT_KEY, "") if isinstance(resolved, dict) else ""),
    )


CATALOG_ENTRY = (
    "StoryAgent\n"
    "  - Input: source_text (text) OR user_story_outline (detailed outline text)\n"
    "  - Output: story_blueprint (logline, cast, locations, story_arc, scene_outline)\n"
    "  - Purpose: Produce a structured story blueprint. Structures user outline if provided."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_id="StoryAgent",
    asset_key=OUTPUT_ASSET_KEY,
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: StoryAgent(llm_client=llm),
    evaluator_factory=StoryEvaluator,
    build_input=build_input,
    materializer_factory=None,
    user_text_key=USER_TEXT_KEY,
)
