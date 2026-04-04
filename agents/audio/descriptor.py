"""AudioAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from ..descriptor import SubAgentDescriptor
from ..contracts import InputBundleV2
from .agent import AudioAgent
from .schema import AudioAgentInput
from .evaluator import AudioEvaluator
from .materializer import AudioMaterializer
from inference.generation.audio_generators.service import FalAudioService

OUTPUT_ASSET_KEY = "audio"


def build_input(
    _task_id: str,
    input_bundle_v2: InputBundleV2,
) -> BaseModel:
    resolved = (
        input_bundle_v2.context.get("resolved_inputs", {})
        if isinstance(getattr(input_bundle_v2, "context", None), dict)
        else {}
    )
    return AudioAgentInput(
        screenplay=resolved.get("screenplay", {}),
        video=resolved.get("video", {}),
    )


def materializer_factory(services: dict[str, Any]) -> AudioMaterializer:
    return AudioMaterializer(audio_service=services["audio_service"])


CATALOG_ENTRY = (
    "AudioAgent\n"
    "  - Input: screenplay + video\n"
    "  - Output: audio_package (narration, music, ambience, scene mix, final audio)\n"
    "  - Purpose: Plan audio aligned with video timing."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_id="AudioAgent",
    asset_key=OUTPUT_ASSET_KEY,
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: AudioAgent(llm_client=llm),
    evaluator_factory=AudioEvaluator,
    build_input=build_input,
    service_factories={
        "audio_service": lambda ctx: FalAudioService(),
    },
    materializer_factory=materializer_factory,
)
