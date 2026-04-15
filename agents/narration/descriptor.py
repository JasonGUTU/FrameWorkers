"""NarrationAgent descriptor."""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import SubAgentDescriptor
from .agent import NarrationAgent
from .labels import INPUT_LABEL_SCREENPLAY
from .schema import NarrationAgentInput
from .evaluator import NarrationEvaluator
from .materializer import NarrationMaterializer

from inference.generation import select_audio_service


def build_input(_step_id: str, resolved_artifacts: dict) -> BaseModel:
    entry = ResolvedArtifactEntry.coerce(resolved_artifacts.get(INPUT_LABEL_SCREENPLAY))
    return NarrationAgentInput(
        screenplay_json_text=json.dumps(entry.payload or {}, ensure_ascii=False, indent=2),
    )


def build_captions(agent_id: str, output_dict: dict) -> dict:
    segs = output_dict.get("content", {}).get("segments", [])
    return {
        agent_id: {
            "caption": f"Narration audio: {len(segs)} segment(s) of TTS speech from screenplay dialogue.",
            "scope": "global",
        },
    }


def materializer_factory(services: dict) -> NarrationMaterializer:
    return NarrationMaterializer(audio_service=services["audio_service"])


CATALOG_ENTRY = (
    "NarrationAgent\n"
    "  - Input: screenplay (dialogue/narration text).\n"
    "  - Output: narration_segments (per-shot TTS audio).\n"
    "  - Purpose: Generate TTS speech (dialogue / voiceover). I am one of THREE OPTIONAL "
    "audio tracks (narration / music / ambience) — pick whichever subset the user actually asked "
    "for; do NOT auto-run all three. Run me only when the user wants dialogue / voiceover / "
    "narration / a voice-acted film. SKIP me when the user only asks for background music, "
    "ambience-only, or transcription. I run AFTER VideoAgent (parallel with other audio tracks "
    "is fine) and BEFORE AudioMixAgent."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_id="NarrationAgent",
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: NarrationAgent(llm_client=llm),
    evaluator_factory=NarrationEvaluator,
    build_input=build_input,
    build_captions=build_captions,
    service_factories={"audio_service": lambda ctx: select_audio_service()},
    materializer_factory=materializer_factory,
    input_needs_description=(
        "I generate TTS narration audio for each spoken line in the screenplay.\n\n"
        f"[{INPUT_LABEL_SCREENPLAY}] (single)\n"
        "The screenplay containing dialogue and narration text."
    ),
)
