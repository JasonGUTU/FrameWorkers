"""KeyFrameAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from ..descriptor import SubAgentDescriptor
from .agent import KeyFrameAgent
from .schema import KeyFrameAgentInput
from .evaluator import KeyframeEvaluator
from .materializer import KeyframeMaterializer
from .service import ImageService


def build_input(
    project_id: str,
    draft_id: str,
    assets: dict[str, Any],
    config: Any,
) -> BaseModel:
    return KeyFrameAgentInput(
        project_id=project_id,
        draft_id=draft_id,
        storyboard=assets.get("storyboard", {}),
    )


def materializer_factory(services: dict[str, Any]) -> KeyframeMaterializer:
    return KeyframeMaterializer(image_service=services["image_service"])


CATALOG_ENTRY = (
    "KeyFrameAgent\n"
    "  - Input: storyboard\n"
    "  - Output: keyframes_package (3-layer prompts: global anchors -> scene anchors -> shot keyframes)\n"
    "  - Purpose: Plan keyframe image prompts for visual consistency."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_name="KeyFrameAgent",
    asset_key="keyframes",
    asset_type="keyframes_package",
    upstream_keys=["storyboard"],
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: KeyFrameAgent(llm_client=llm),
    evaluator_factory=KeyframeEvaluator,
    build_input=build_input,
    service_factories={
        "image_service": lambda ctx: ImageService(),
    },
    materializer_factory=materializer_factory,
)
