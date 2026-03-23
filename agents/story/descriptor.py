"""StoryAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from ..descriptor import SubAgentDescriptor
from .agent import StoryAgent
from .schema import StoryAgentInput, StoryConstraints
from .evaluator import StoryEvaluator


def build_input(
    _project_id: str,
    _draft_id: str,
    assets: dict[str, Any],
    config: Any,
) -> BaseModel:
    return StoryAgentInput(
        draft_idea=assets.get("draft_idea", ""),
        constraints=StoryConstraints(
            target_duration_sec=config.target_total_duration_sec,
            language=config.language,
        ),
        user_provided_text=assets.get("user_story_outline", ""),
    )


def build_upstream(assets: dict[str, Any]) -> dict[str, Any] | None:
    return {
        "draft_idea": assets.get("draft_idea", ""),
    }


CATALOG_ENTRY = (
    "StoryAgent\n"
    "  - Input: draft_idea (text) OR user_story_outline (detailed outline text)\n"
    "  - Output: story_blueprint (logline, cast, locations, story_arc, scene_outline)\n"
    "  - Purpose: Produce a structured story blueprint. Structures user outline if provided."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_name="StoryAgent",
    asset_key="story_blueprint",
    asset_type="story_blueprint",
    upstream_keys=["draft_idea"],
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: StoryAgent(llm_client=llm),
    evaluator_factory=StoryEvaluator,
    build_input=build_input,
    build_upstream=build_upstream,
    materializer_factory=None,
    user_text_key="user_story_outline",
)
