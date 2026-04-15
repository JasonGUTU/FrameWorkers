"""VoiceCloneAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

import json

from pydantic import BaseModel

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import SubAgentDescriptor
from .agent import VoiceCloneAgent
from .labels import INPUT_LABEL_REFERENCE_AUDIO, INPUT_LABEL_TRANSCRIPT
from .schema import VoiceCloneAgentInput
from .evaluator import VoiceCloneEvaluator
from .materializer import VoiceCloneMaterializer


def build_input(
    _step_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    ref_audio = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_REFERENCE_AUDIO)
    )
    transcript = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_TRANSCRIPT)
    )

    return VoiceCloneAgentInput(
        reference_audio_path=ref_audio.path,
        transcript_json_text=json.dumps(
            transcript.payload or {}, ensure_ascii=False, indent=2
        ),
    )


def build_captions(agent_id: str, output_dict: dict) -> dict:
    content = output_dict.get("content", {})
    profile = content.get("voice_profile", {})
    gender = profile.get("gender", "?")
    tone = profile.get("tone", "")
    seg_count = len(content.get("segments", []))
    return {
        agent_id: {
            "caption": (
                f"Voice clone narration ({gender}, {tone}): {seg_count} "
                f"segment(s). Cloned from reference audio."
            ),
            "scope": "global",
        },
    }


def materializer_factory(services: dict) -> VoiceCloneMaterializer:
    return VoiceCloneMaterializer(voice_clone_service=services["voice_clone_service"])


CATALOG_ENTRY = (
    "VoiceCloneAgent\n"
    "  - Input: a reference-audio artifact (the voice sample to clone) + a transcript or "
    "instruction text (what to say in the cloned voice). The script can be supplied directly "
    "by the user OR derived later from a screenplay / dialogue artifact in a creative chain.\n"
    "  - Output: voice_clone_narration (narration segments in the cloned voice).\n"
    "  - Purpose: Clone a user-supplied voice and generate narration in that voice. I am the "
    "voice-substitute equivalent of standard TTS narration: in a creative production chain "
    "where the user supplies a voice sample, prefer me OVER plain TTS narration — they are "
    "mutually exclusive (do NOT also run a generic narration agent for the same shot). Need "
    "both an ingested reference audio AND a script source before I can run."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_id="VoiceCloneAgent",
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: VoiceCloneAgent(llm_client=llm),
    evaluator_factory=VoiceCloneEvaluator,
    build_input=build_input,
    build_captions=build_captions,
    service_factories={
        "voice_clone_service": lambda ctx: __import__("inference.generation", fromlist=["select_voice_clone_service"]).select_voice_clone_service(),
    },
    materializer_factory=materializer_factory,
    input_needs_description=(
        "I clone a voice from reference audio and generate narration in "
        "that cloned voice.\n\n"
        f"[{INPUT_LABEL_REFERENCE_AUDIO}] (single)\n"
        "An audio file containing a voice sample to clone (at least a "
        "few seconds of clear speech).\n\n"
        f"[{INPUT_LABEL_TRANSCRIPT}] (single)\n"
        "The text to speak in the cloned voice. May be a transcript, "
        "screenplay excerpt, or plain text. Payload is forwarded as "
        "JSON text."
    ),
)
