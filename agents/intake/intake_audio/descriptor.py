"""IntakeAudioAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

from pydantic import BaseModel

from ...common_schema import ResolvedArtifactEntry
from ...descriptor import SubAgentDescriptor
from .agent import IntakeAudioAgent
from .labels import INPUT_LABEL_RAW_AUDIO_UPLOAD
from .schema import IntakeAudioInput
from .evaluator import IntakeAudioEvaluator


def build_input(
    _task_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    raw = resolved_artifacts.get(INPUT_LABEL_RAW_AUDIO_UPLOAD)
    if isinstance(raw, list):
        raw = raw[0] if raw else None
    entry = ResolvedArtifactEntry.coerce(raw)
    return IntakeAudioInput(raw_audio_path=entry.path)


def build_captions(agent_id: str, output_dict: dict) -> dict:
    return {
        agent_id: {
            "caption": "User-uploaded audio reference. Available for downstream agents.",
            "scope": "global",
        },
    }


CATALOG_ENTRY = (
    "IntakeAudioAgent\n"
    "  - Input: raw_audio_upload (placeholder caption pointing at a raw audio file)\n"
    "  - Output: a caption-rich audio artifact for downstream content agents.\n"
    "  - Purpose: Run an audio-understanding LLM over a freshly-uploaded user audio file."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_id="IntakeAudioAgent",
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: IntakeAudioAgent(llm_client=llm),
    evaluator_factory=IntakeAudioEvaluator,
    build_input=build_input,
    build_captions=build_captions,
    materializer_factory=None,
    input_needs_description=(
        "I convert raw user-uploaded audio into a caption-rich workspace "
        "artifact.\n\n"
        f"[{INPUT_LABEL_RAW_AUDIO_UPLOAD}] (single)\n"
        "A raw user-uploaded audio file whose caption starts with "
        "'Raw user upload (mime=audio/' and has scope 'raw_pending'. "
        "Pick the single most recent such pending audio upload."
    ),
)
