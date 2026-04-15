"""IntakeAudioAgent — runs an audio-understanding LLM on a raw user audio upload."""

from __future__ import annotations

from ...base_agent import BaseAgent
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
            "Audio is provided as a multimodal attachment.\n\n"
            "Return JSON: {\"auditory_summary\": \"...\"}"
        )

    def fill_creative(self, skeleton: IntakeAudioOutput, creative: dict) -> IntakeAudioOutput:
        summary = ""
        if isinstance(creative, dict):
            summary = str(creative.get("auditory_summary") or "").strip()
        skeleton.content.auditory_summary = summary
        return skeleton

    def build_skeleton(self, input_data: IntakeAudioInput) -> IntakeAudioOutput:
        skeleton = IntakeAudioOutput()
        skeleton.content = IntakeAudioContent(
            auditory_summary="",
            audio_asset=IntakeAudioAsset(uri=input_data.raw_audio_path),
        )
        return skeleton

    async def generate(
        self,
        input_data: IntakeAudioInput,
        *,
        rework_notes: str = "",
    ) -> IntakeAudioOutput:
        """Build the skeleton, ask the LLM to fill ``auditory_summary`` via
        a multimodal call with the audio file attached.
        """
        skeleton = self.build_skeleton(input_data)
        system = self.system_prompt()
        user = self.build_user_prompt(input_data)
        if rework_notes:
            user += self._rework_section(rework_notes)

        media = []
        if input_data.raw_audio_path:
            media.append({"type": "audio", "path": input_data.raw_audio_path})

        creative = await self.llm.chat_json(
            system, user, media_attachments=media or None,
        )
        return self.fill_creative(skeleton, creative)
