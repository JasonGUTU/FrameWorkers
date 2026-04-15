"""AmbienceAgent descriptor."""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import SubAgentDescriptor
from .agent import AmbienceAgent
from .labels import INPUT_LABEL_SCREENPLAY
from .schema import AmbienceAgentInput
from .evaluator import AmbienceEvaluator
from .materializer import AmbienceMaterializer

from inference.generation import select_audio_service


def build_input(_step_id: str, resolved_artifacts: dict) -> BaseModel:
    entry = ResolvedArtifactEntry.coerce(resolved_artifacts.get(INPUT_LABEL_SCREENPLAY))
    return AmbienceAgentInput(
        screenplay_json_text=json.dumps(entry.payload or {}, ensure_ascii=False, indent=2),
    )


def build_captions(agent_id: str, output_dict: dict) -> dict:
    beds = output_dict.get("content", {}).get("beds", [])
    descs = ", ".join(b.get("description", "") for b in beds[:3])
    return {
        agent_id: {
            "caption": f"Ambient sounds: {len(beds)} bed(s). {descs}.",
            "scope": "global",
        },
    }


def materializer_factory(services: dict) -> AmbienceMaterializer:
    return AmbienceMaterializer(audio_service=services["audio_service"])


CATALOG_ENTRY = (
    "AmbienceAgent\n"
    "  - Input: screenplay (scene location/setting).\n"
    "  - Output: ambience_beds (per-scene environmental sounds).\n"
    "  - Purpose: Generate ambient environmental sounds (room tone, wind, traffic, crowd, etc.). "
    "I am one of THREE OPTIONAL audio tracks (narration / music / ambience) — pick whichever "
    "subset the user actually asked for; do NOT auto-run all three. Run me only when the user "
    "explicitly wants ambience / environmental sound / immersive sound design. SKIP me when the "
    "user only asks for background music, dialogue, or transcription. I run AFTER VideoAgent "
    "(parallel with other audio tracks is fine) and BEFORE AudioMixAgent."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_id="AmbienceAgent",
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: AmbienceAgent(llm_client=llm),
    evaluator_factory=AmbienceEvaluator,
    build_input=build_input,
    build_captions=build_captions,
    service_factories={"audio_service": lambda ctx: select_audio_service()},
    materializer_factory=materializer_factory,
    input_needs_description=(
        "I generate ambient environmental sounds for each scene.\n\n"
        f"[{INPUT_LABEL_SCREENPLAY}] (single)\n"
        "The screenplay — I read each scene's location/heading to derive "
        "ambient sound content, and each scene's pre-computed "
        "estimated_duration_seconds to size the bed (single source of "
        "truth for scene duration, shared with Music so the two stay in "
        "sync)."
    ),
)
