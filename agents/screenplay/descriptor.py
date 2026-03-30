"""ScreenplayAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

from pydantic import BaseModel

from ..descriptor import SubAgentDescriptor
from ..contracts import InputBundleV2
from .agent import ScreenplayAgent
from .schema import (
    ScreenplayAgentInput,
    ScreenplayConstraints,
)
from .evaluator import ScreenplayEvaluator

OUTPUT_ASSET_KEY = "screenplay"
USER_TEXT_KEY = "user_screenplay"


def build_input(
    _task_id: str,
    input_bundle_v2: InputBundleV2,
) -> BaseModel:
    resolved = (
        input_bundle_v2.context.get("resolved_inputs", {})
        if isinstance(getattr(input_bundle_v2, "context", None), dict)
        else {}
    )
    story_dict = resolved.get("story_blueprint", {}) if isinstance(resolved, dict) else {}
    content = story_dict.get("content", {}) if isinstance(story_dict, dict) else {}
    return ScreenplayAgentInput(
        story_blueprint=content,
        constraints=ScreenplayConstraints(),
        user_provided_text=(resolved.get(USER_TEXT_KEY, "") if isinstance(resolved, dict) else ""),
    )


CATALOG_ENTRY = (
    "ScreenplayAgent\n"
    "  - Input: story_blueprint OR user_screenplay (raw screenplay text)\n"
    "  - Output: screenplay (scenes -> blocks with dialogue, action, narration)\n"
    "  - Purpose: Produce a structured screenplay JSON. Structures user text if provided."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_id="ScreenplayAgent",
    asset_key=OUTPUT_ASSET_KEY,
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: ScreenplayAgent(llm_client=llm),
    evaluator_factory=ScreenplayEvaluator,
    build_input=build_input,
    materializer_factory=None,
    user_text_key=USER_TEXT_KEY,
)
