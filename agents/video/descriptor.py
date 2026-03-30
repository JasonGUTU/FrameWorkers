"""VideoAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from ..descriptor import SubAgentDescriptor
from ..contracts import InputBundleV2
from .agent import VideoAgent
from .schema import VideoAgentInput
from .evaluator import VideoEvaluator
from .materializer import VideoMaterializer
from inference.generation.video_generators.service import FalVideoService

OUTPUT_ASSET_KEY = "video"


def build_input(
    _task_id: str,
    input_bundle_v2: InputBundleV2,
) -> BaseModel:
    resolved = (
        input_bundle_v2.context.get("resolved_inputs", {})
        if isinstance(getattr(input_bundle_v2, "context", None), dict)
        else {}
    )
    return VideoAgentInput(
        storyboard=resolved.get("storyboard", {}),
        keyframes=resolved.get("keyframes", {}),
    )


def materializer_factory(services: dict[str, Any]) -> VideoMaterializer:
    return VideoMaterializer(video_service=services["video_service"])


CATALOG_ENTRY = (
    "VideoAgent\n"
    "  - Input: storyboard + keyframes\n"
    "  - Output: video_package (shot segments, scene clips, final video)\n"
    "  - Purpose: Plan video clip generation from keyframe images."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_id="VideoAgent",
    asset_key=OUTPUT_ASSET_KEY,
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: VideoAgent(llm_client=llm),
    evaluator_factory=VideoEvaluator,
    build_input=build_input,
    service_factories={
        "video_service": lambda ctx: FalVideoService(),
    },
    materializer_factory=materializer_factory,
)
