"""AudioMixAgent descriptor."""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import SubAgentDescriptor
from .agent import AudioMixAgent
from .labels import (
    INPUT_LABEL_AMBIENCE,
    INPUT_LABEL_MUSIC,
    INPUT_LABEL_NARRATION,
    INPUT_LABEL_SCREENPLAY,
)
from .schema import AudioMixAgentInput
from .evaluator import AudioMixEvaluator
from .materializer import AudioMixMaterializer

from inference.generation import select_audio_service


def build_input(_step_id: str, resolved_artifacts: dict) -> BaseModel:
    sp = ResolvedArtifactEntry.coerce(resolved_artifacts.get(INPUT_LABEL_SCREENPLAY))
    narr = ResolvedArtifactEntry.coerce(resolved_artifacts.get(INPUT_LABEL_NARRATION))
    music = ResolvedArtifactEntry.coerce(resolved_artifacts.get(INPUT_LABEL_MUSIC))
    amb = ResolvedArtifactEntry.coerce(resolved_artifacts.get(INPUT_LABEL_AMBIENCE))
    return AudioMixAgentInput(
        screenplay_json_text=json.dumps(sp.payload or {}, ensure_ascii=False, indent=2),
        narration_json_text=json.dumps(narr.payload or {}, ensure_ascii=False, indent=2),
        music_json_text=json.dumps(music.payload or {}, ensure_ascii=False, indent=2),
        ambience_json_text=json.dumps(amb.payload or {}, ensure_ascii=False, indent=2),
    )


def build_captions(agent_id: str, output_dict: dict) -> dict:
    mixes = output_dict.get("content", {}).get("scene_mixes", [])
    return {
        agent_id: {
            "caption": f"Audio mix: {len(mixes)} scene(s) mixed + final audio assembled.",
            "scope": "global",
        },
    }


def materializer_factory(services: dict) -> AudioMixMaterializer:
    return AudioMixMaterializer(audio_service=services["audio_service"])


CATALOG_ENTRY = (
    "AudioMixAgent\n"
    "  - Input: any non-empty subset of (narration_segments, music_cues, ambience_beds).\n"
    "  - Output: audio_mix (per-scene mix + final assembled audio).\n"
    "  - Purpose: Mix the available audio tracks into the final audio. I require AT LEAST ONE "
    "of NarrationAgent / MusicAgent / AmbienceAgent to have completed — NOT all three. "
    "Match the subset to the user's explicit ask: e.g. 'only background music' → run MusicAgent "
    "only and then me; 'fully voiced film' → run all three then me; 'transcribe + subtitles' → "
    "skip me entirely. I run BEFORE SubtitleAgent (if subtitles needed) and BEFORE CompositorAgent."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_id="AudioMixAgent",
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: AudioMixAgent(llm_client=llm),
    evaluator_factory=AudioMixEvaluator,
    build_input=build_input,
    build_captions=build_captions,
    service_factories={"audio_service": lambda ctx: select_audio_service()},
    materializer_factory=materializer_factory,
    input_needs_description=(
        "I mix narration, music, and ambience tracks into a final audio.\n\n"
        f"[{INPUT_LABEL_SCREENPLAY}] (single)\n"
        "The screenplay. I use it to map narration segments (tagged with "
        "linked_shot_id) back to their scene so I can sync per-scene music "
        "and ambience correctly.\n\n"
        f"[{INPUT_LABEL_NARRATION}] (single)\n"
        "Narration segments from NarrationAgent.\n\n"
        f"[{INPUT_LABEL_MUSIC}] (single)\n"
        "Music cues from MusicAgent.\n\n"
        f"[{INPUT_LABEL_AMBIENCE}] (single)\n"
        "Ambience beds from AmbienceAgent."
    ),
)
