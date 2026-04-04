"""VideoAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

import os
from typing import Any

from pydantic import BaseModel

from ..descriptor import SubAgentDescriptor
from ..contracts import InputBundleV2
from .agent import VideoAgent
from .schema import VideoAgentInput
from .evaluator import VideoEvaluator
from .materializer import VideoMaterializer
from inference.generation.video_generators.service import FalVideoService, WavespeedVideoService

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
        screenplay=resolved.get("screenplay", {}),
        keyframes=resolved.get("keyframes", {}),
    )


def materializer_factory(services: dict[str, Any]) -> VideoMaterializer:
    return VideoMaterializer(video_service=services["video_service"])


def _video_service_factory(_ctx: dict[str, Any] | None = None) -> FalVideoService | WavespeedVideoService:
    """Select pipeline video backend (Layer A: alternate provider inside inference).

    - ``FW_VIDEO_BACKEND=fal`` (default): ``FalVideoService`` + fal env vars.
    - ``FW_VIDEO_BACKEND=wavespeed``: ``WavespeedVideoService`` + ``WAVESPEED_*`` env vars.

    Sidecar UniVA HTTP (Layer B) and MCP tool processes (Layer C) stay out of this
    factory; see ``inference/README.md`` (UniVA integration).
    """
    backend = os.getenv("FW_VIDEO_BACKEND", "fal").strip().lower()
    if backend in ("wavespeed", "wave_speed", "ws"):
        return WavespeedVideoService()
    return FalVideoService()


CATALOG_ENTRY = (
    "VideoAgent\n"
    "  - Input: screenplay + keyframes\n"
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
        "video_service": lambda ctx: _video_service_factory(ctx),
    },
    materializer_factory=materializer_factory,
)
