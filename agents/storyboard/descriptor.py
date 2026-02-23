"""StoryboardAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from ..descriptor import SubAgentDescriptor
from .agent import StoryboardAgent
from .schema import (
    StoryboardAgentInput,
    StoryboardConstraints,
)
from .evaluator import StoryboardEvaluator


def build_input(
    project_id: str,
    draft_id: str,
    assets: dict[str, Any],
    config: Any,
) -> BaseModel:
    return StoryboardAgentInput(
        project_id=project_id,
        draft_id=draft_id,
        screenplay=assets.get("screenplay", {}),
        constraints=StoryboardConstraints(language=config.language),
    )


CATALOG_ENTRY = (
    "StoryboardAgent\n"
    "  - Input: screenplay\n"
    "  - Output: storyboard (scenes -> shots with camera, visual_goal, keyframe_plan)\n"
    "  - Purpose: Translate screenplay into visual shot-by-shot planning."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_name="StoryboardAgent",
    asset_key="storyboard",
    asset_type="storyboard",
    upstream_keys=["screenplay"],
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: StoryboardAgent(llm_client=llm),
    evaluator_factory=StoryboardEvaluator,
    build_input=build_input,
    materializer_factory=None,
)
