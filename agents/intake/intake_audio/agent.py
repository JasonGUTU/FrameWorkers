"""IntakeAudioAgent — runs an audio-understanding LLM on a raw user audio upload."""

from __future__ import annotations

from ...base_agent import BaseAgent
from ...common_schema import ArtifactCaption
from .schema import IntakeAudioAsset, IntakeAudioContent, IntakeAudioInput, IntakeAudioOutput


class IntakeAudioAgent(BaseAgent[IntakeAudioInput, IntakeAudioOutput]):

    def system_prompt(self) -> str:
        return (
            "You are IntakeAudioAgent. A user has uploaded an audio file. "
            "Produce a single objective sentence (<= 240 chars) describing "
            "what is audible: speech / music / ambience, mood, instruments "
            "if relevant. Do NOT speculate about the user's intent. Return "
            "JSON with field `auditory_summary`."
        )

    def build_user_prompt(self, input_data: IntakeAudioInput) -> str:
        return (
            "Audio is provided as a multimodal attachment.\n"
            f"User-stated intent (do not echo): {input_data.user_intent[:200] or '(none)'}\n\n"
            "Return JSON: {\"auditory_summary\": \"...\"}"
        )

    def fill_creative(self, skeleton: IntakeAudioOutput, creative: dict) -> IntakeAudioOutput:
        summary = ""
        if isinstance(creative, dict):
            summary = str(creative.get("auditory_summary") or "").strip()
        skeleton.content.auditory_summary = summary
        return skeleton

    def build_skeleton(self, input_data: IntakeAudioInput) -> IntakeAudioOutput | None:
        skeleton = IntakeAudioOutput()
        skeleton.content = IntakeAudioContent(
            auditory_summary="",
            audio_asset=IntakeAudioAsset(uri=input_data.raw_audio_path),
        )
        intent = (input_data.user_intent or "").strip()
        skeleton.artifact_caption = ArtifactCaption(
            what="",
            why=intent or "(no user intent provided)",
            scope="global",
        )
        return skeleton
