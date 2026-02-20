"""AudioAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from ..descriptor import SubAgentDescriptor
from .agent import AudioAgent
from .schema import AudioAgentInput
from .evaluator import AudioEvaluator
from .materializer import AudioMaterializer
from .service import AudioService


def build_input(
    project_id: str,
    draft_id: str,
    assets: dict[str, Any],
    config: Any,
) -> BaseModel:
    return AudioAgentInput(
        project_id=project_id,
        draft_id=draft_id,
        screenplay=assets.get("screenplay", {}),
        storyboard=assets.get("storyboard", {}),
        video=assets.get("video", {}),
    )


def materializer_factory(services: dict[str, Any]) -> AudioMaterializer:
    return AudioMaterializer(audio_service=services["audio_service"])


CATALOG_ENTRY = (
    "AudioAgent\n"
    "  - Input: screenplay + storyboard + video\n"
    "  - Output: audio_package (narration, music, ambience, scene mix, final audio)\n"
    "  - Purpose: Plan audio aligned with video timing."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_name="AudioAgent",
    asset_key="audio",
    asset_type="audio_package",
    upstream_keys=["screenplay", "storyboard", "video"],
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: AudioAgent(llm_client=llm),
    evaluator_factory=AudioEvaluator,
    build_input=build_input,
    service_factories={
        "audio_service": lambda ctx: AudioService(client=ctx["llm_client"].client),
    },
    materializer_factory=materializer_factory,
)
