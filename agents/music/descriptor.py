"""MusicAgent descriptor."""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import SubAgentDescriptor
from .agent import MusicAgent
from .labels import INPUT_LABEL_SCREENPLAY
from .schema import MusicAgentInput
from .evaluator import MusicEvaluator
from .materializer import MusicMaterializer

from inference.generation import select_audio_service


def build_input(_step_id: str, resolved_artifacts: dict) -> BaseModel:
    entry = ResolvedArtifactEntry.coerce(resolved_artifacts.get(INPUT_LABEL_SCREENPLAY))
    return MusicAgentInput(
        screenplay_json_text=json.dumps(entry.payload or {}, ensure_ascii=False, indent=2),
    )


def build_captions(agent_id: str, output_dict: dict) -> dict:
    cues = output_dict.get("content", {}).get("cues", [])
    moods = ", ".join(c.get("mood", "") for c in cues[:3])
    return {
        agent_id: {
            "caption": f"Background music: {len(cues)} cue(s). Moods: {moods}.",
            "scope": "global",
        },
    }


def materializer_factory(services: dict) -> MusicMaterializer:
    return MusicMaterializer(audio_service=services["audio_service"])


CATALOG_ENTRY = (
    "MusicAgent\n"
    "  - Input: screenplay (scene mood/tone).\n"
    "  - Output: music_cues (per-scene background music).\n"
    "  - Purpose: Generate background music / BGM / soundtrack. I am one of THREE OPTIONAL "
    "audio tracks (narration / music / ambience) — pick whichever subset the user actually asked "
    "for; do NOT auto-run all three. Run me only when the user wants music / BGM / soundtrack / "
    "a scored film. SKIP me when the user only asks for transcription / dialogue / "
    "ambience-only. I run AFTER VideoAgent (parallel with other audio tracks is fine) and "
    "BEFORE AudioMixAgent."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_id="MusicAgent",
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: MusicAgent(llm_client=llm),
    evaluator_factory=MusicEvaluator,
    build_input=build_input,
    build_captions=build_captions,
    service_factories={"audio_service": lambda ctx: select_audio_service()},
    materializer_factory=materializer_factory,
    input_needs_description=(
        "I generate background music for each scene based on its mood/tone.\n\n"
        f"[{INPUT_LABEL_SCREENPLAY}] (single)\n"
        "The screenplay — I read each scene's mood/tone to pick a music "
        "style and each scene's pre-computed estimated_duration_seconds "
        "to size the cue (single source of truth for scene duration, "
        "shared with Ambience so the two stay in sync)."
    ),
)
