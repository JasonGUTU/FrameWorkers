"""ScreenplayAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from ..descriptor import SubAgentDescriptor
from .agent import ScreenplayAgent
from .schema import (
    ScreenplayAgentInput,
    ScreenplayConstraints,
)
from .evaluator import ScreenplayEvaluator


def build_input(
    project_id: str,
    draft_id: str,
    assets: dict[str, Any],
    config: Any,
) -> BaseModel:
    story_dict = assets.get("story_blueprint", {})
    content = story_dict.get("content", {})
    return ScreenplayAgentInput(
        project_id=project_id,
        draft_id=draft_id,
        story_blueprint=content,
        constraints=ScreenplayConstraints(
            target_duration_sec=config.target_total_duration_sec,
            language=config.language,
        ),
        user_provided_text=assets.get("user_screenplay", ""),
    )


CATALOG_ENTRY = (
    "ScreenplayAgent\n"
    "  - Input: story_blueprint OR user_screenplay (raw screenplay text)\n"
    "  - Output: screenplay (scenes -> blocks with dialogue, action, narration)\n"
    "  - Purpose: Produce a structured screenplay JSON. Structures user text if provided."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_name="ScreenplayAgent",
    asset_key="screenplay",
    asset_type="screenplay",
    upstream_keys=["story_blueprint"],
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: ScreenplayAgent(llm_client=llm),
    evaluator_factory=ScreenplayEvaluator,
    build_input=build_input,
    materializer_factory=None,
    user_text_key="user_screenplay",
)
