"""IntakeVideoAgent — runs a video LLM on a raw user video upload."""

from __future__ import annotations

from ...base_agent import BaseAgent
from .schema import IntakeVideoAsset, IntakeVideoContent, IntakeVideoInput, IntakeVideoOutput


class IntakeVideoAgent(BaseAgent[IntakeVideoInput, IntakeVideoOutput]):

    def system_prompt(self) -> str:
        return (
            "You are IntakeVideoAgent. A user has uploaded a short video. "
            "Produce a single objective sentence (<= 240 chars) describing "
            "what is visible: subjects, action, setting, mood. Do NOT speculate "
            "about the user's intent. Return JSON with field `visual_summary`."
        )

    def build_user_prompt(self, input_data: IntakeVideoInput) -> str:
        return (
            "Video is provided as a multimodal attachment.\n"
            f"User-stated intent (do not echo): {input_data.user_intent[:200] or '(none)'}\n\n"
            "Return JSON: {\"visual_summary\": \"...\"}"
        )

    def fill_creative(self, skeleton: IntakeVideoOutput, creative: dict) -> IntakeVideoOutput:
        summary = ""
        if isinstance(creative, dict):
            summary = str(creative.get("visual_summary") or "").strip()
        skeleton.content.visual_summary = summary
        return skeleton

    def build_skeleton(self, input_data: IntakeVideoInput) -> IntakeVideoOutput:
        skeleton = IntakeVideoOutput()
        skeleton.content = IntakeVideoContent(
            visual_summary="",
            video_asset=IntakeVideoAsset(uri=input_data.raw_video_path),
        )
        return skeleton

    async def generate(
        self,
        input_data: IntakeVideoInput,
        *,
        rework_notes: str = "",
    ) -> IntakeVideoOutput:
        """Build the skeleton, ask the LLM to fill ``visual_summary`` via
        a one-shot multimodal call. NOTE: stub — relies on a multimodal
        video LLM endpoint that may not be wired up.
        """
        skeleton = self.build_skeleton(input_data)
        system = self.system_prompt()
        user = self.build_user_prompt(input_data)
        if rework_notes:
            user += self._rework_section(rework_notes)
        creative = await self.llm.chat_json(system, user)
        return self.fill_creative(skeleton, creative)
