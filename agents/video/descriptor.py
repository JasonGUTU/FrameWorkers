"""VideoAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from ..descriptor import SubAgentDescriptor
from .agent import VideoAgent
from .schema import VideoAgentInput
from .evaluator import VideoEvaluator
from .materializer import VideoMaterializer
from inference.generation.video_generators.service import FalVideoService


def build_input(
    _project_id: str,
    _draft_id: str,
    assets: dict[str, Any],
    config: Any,
) -> BaseModel:
    return VideoAgentInput(
        storyboard=assets.get("storyboard", {}),
        keyframes=assets.get("keyframes", {}),
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
    agent_name="VideoAgent",
    asset_key="video",
    asset_type="video_package",
    upstream_keys=["storyboard", "keyframes"],
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: VideoAgent(llm_client=llm),
    evaluator_factory=VideoEvaluator,
    build_input=build_input,
    service_factories={
        "video_service": lambda ctx: FalVideoService(),
    },
    materializer_factory=materializer_factory,
)
