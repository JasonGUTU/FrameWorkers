"""IntakeAudioAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

from pydantic import BaseModel

from ...descriptor import SubAgentDescriptor
from ...contracts import InputBundleV2
from .agent import IntakeAudioAgent
from .labels import INPUT_LABEL_RAW_AUDIO_UPLOAD
from .schema import IntakeAudioInput
from .evaluator import IntakeAudioEvaluator

OUTPUT_ASSET_KEY = "user_audio"


def build_input(
    _task_id: str,
    input_bundle_v2: InputBundleV2,
) -> BaseModel:
    resolved = input_bundle_v2.resolved_artifacts
    entry = resolved.get(INPUT_LABEL_RAW_AUDIO_UPLOAD, {})
    if isinstance(entry, list):
        entry = entry[0] if entry else {}
    raw_audio_path = ""
    user_intent = ""
    if isinstance(entry, dict):
        raw_audio_path = str(entry.get("path", "") or "")
        user_intent = str(entry.get("why", "") or "")
    return IntakeAudioInput(raw_audio_path=raw_audio_path, user_intent=user_intent)


CATALOG_ENTRY = (
    "IntakeAudioAgent\n"
    "  - Input: raw_audio_upload (placeholder caption pointing at a raw audio file)\n"
    "  - Output: a caption-rich audio artifact for downstream content agents.\n"
    "  - Purpose: Run an audio-understanding LLM over a freshly-uploaded user audio file."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_id="IntakeAudioAgent",
    asset_key=OUTPUT_ASSET_KEY,
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: IntakeAudioAgent(llm_client=llm),
    evaluator_factory=IntakeAudioEvaluator,
    build_input=build_input,
    materializer_factory=None,
    input_needs_description=(
        "I convert raw user-uploaded audio into a caption-rich workspace "
        "artifact.\n\n"
        f"[{INPUT_LABEL_RAW_AUDIO_UPLOAD}] (single)\n"
        "A raw user-uploaded audio file that has not yet been semantically "
        "analyzed. The placeholder caption marks it as 'raw user upload, "
        "mime=audio/*, awaiting semantic analysis'. Pick the single most "
        "recent such pending audio upload."
    ),
)
