"""KeyFrameAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from ..descriptor import SubAgentDescriptor
from ..contracts import InputBundleV2
from .agent import KeyFrameAgent
from .schema import KeyFrameAgentInput
from .evaluator import KeyframeEvaluator
from .materializer import KeyframeMaterializer
from inference.generation.image_generators.service import FalImageService

OUTPUT_ASSET_KEY = "keyframes"


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
    return KeyFrameAgentInput(
        storyboard=resolved.get("storyboard", {}),
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
    agent_id="KeyFrameAgent",
    asset_key=OUTPUT_ASSET_KEY,
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: KeyFrameAgent(llm_client=llm),
    evaluator_factory=KeyframeEvaluator,
    build_input=build_input,
    service_factories={
        "image_service": lambda ctx: FalImageService(),
    },
    materializer_factory=materializer_factory,
)
