"""AudioAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from ..descriptor import SubAgentDescriptor
from ..contracts import InputBundleV2
from .agent import AudioAgent
from .labels import INPUT_LABEL_FINAL_VIDEO, INPUT_LABEL_SCREENPLAY
from .schema import AudioAgentInput
from .evaluator import AudioEvaluator
from .materializer import AudioMaterializer
from inference.generation.audio_generators.service import FalAudioService


def build_input(
    _task_id: str,
    input_bundle_v2: InputBundleV2,
) -> BaseModel:
    resolved = input_bundle_v2.resolved_artifacts

    sp = resolved.get(INPUT_LABEL_SCREENPLAY, {})
    sp_payload = sp.get("payload", {}) if isinstance(sp, dict) else {}

    fv = resolved.get(INPUT_LABEL_FINAL_VIDEO, {})
    fv_payload = fv.get("payload", {}) if isinstance(fv, dict) else {}

    return AudioAgentInput(
        screenplay=sp_payload,
        final_video=fv_payload,
    )


def materializer_factory(services: dict[str, Any]) -> AudioMaterializer:
    return AudioMaterializer(audio_service=services["audio_service"])


CATALOG_ENTRY = (
    "AudioAgent\n"
    "  - Input: screenplay + video package\n"
    "  - Output: audio_package (narration, music, ambience, scene mix, final audio)\n"
    "  - Purpose: Plan audio aligned with video timing."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_id="AudioAgent",
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: AudioAgent(llm_client=llm),
    evaluator_factory=AudioEvaluator,
    build_input=build_input,
    service_factories={
        "audio_service": lambda ctx: FalAudioService(),
    },
    materializer_factory=materializer_factory,
    input_needs_description=(
        "I plan and produce the audio side of the video: per-scene narration, music, "
        "ambience, and the final mixed audio aligned to the video timeline.\n\n"
        "For each [label] below, find every artifact in the registry whose caption "
        "describes the same kind of thing. Use the natural-language caption only — "
        "do not match by filename or by any tag.\n\n"
        f"[{INPUT_LABEL_SCREENPLAY}] (single)\n"
        "The unified screenplay document for the story: scenes broken into shots "
        "with dialogue lines, emotional beats, and creative direction. I read "
        "this to know what to say (narration) and what mood to score (music). "
        "Choose at most one.\n\n"
        f"[{INPUT_LABEL_FINAL_VIDEO}] (single)\n"
        "The single complete finished video file for the whole story (one continuous "
        "video, not per-shot or per-scene fragments). It is the visual side of the "
        "deliverable, against which I will mux the final audio. This is a JSON "
        "manifest describing the assembled video, not the raw video file itself. "
        "Choose at most one — and only the document describing the complete final "
        "video, not intermediate per-shot or per-scene assemblies."
    ),
)
