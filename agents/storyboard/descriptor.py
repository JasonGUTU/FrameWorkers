"""StoryboardAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from ..descriptor import SubAgentDescriptor
from ..contracts import InputBundleV2
from .agent import StoryboardAgent
from .schema import (
    StoryboardAgentInput,
    StoryboardConstraints,
)
from .evaluator import StoryboardEvaluator

OUTPUT_ASSET_KEY = "storyboard"


def build_input(
    _task_id: str,
    input_bundle_v2: InputBundleV2,
    config: Any,
) -> BaseModel:
    resolved = (
        input_bundle_v2.context.get("resolved_inputs", {})
        if isinstance(getattr(input_bundle_v2, "context", None), dict)
        else {}
    )
    return StoryboardAgentInput(
        screenplay=resolved.get("screenplay", {}),
        constraints=StoryboardConstraints(language=config.language),
    )


CATALOG_ENTRY = (
    "StoryboardAgent\n"
    "  - Input: screenplay\n"
    "  - Output: storyboard (scenes -> shots with camera, visual_goal, keyframe_plan)\n"
    "  - Purpose: Translate screenplay into visual shot-by-shot planning."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_id="StoryboardAgent",
    asset_key=OUTPUT_ASSET_KEY,
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: StoryboardAgent(llm_client=llm),
    evaluator_factory=StoryboardEvaluator,
    build_input=build_input,
    materializer_factory=None,
)
