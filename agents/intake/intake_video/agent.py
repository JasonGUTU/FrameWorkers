"""IntakeVideoAgent — runs a video LLM on a raw user video upload."""

from __future__ import annotations

import os

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
            "Video is provided as a multimodal attachment.\n\n"
            "Return JSON: {\"visual_summary\": \"...\"}"
        )

    def fill_creative(self, skeleton: IntakeVideoOutput, creative: dict) -> IntakeVideoOutput:
        # Hard failure (LLM returned non-dict / no creative payload) is
        # raised so the outer rework loop sees the failure instead of
        # registering an artifact whose only signal — visual_summary — is
        # silently empty. A legitimate "model has nothing to say" path is
        # creative being a dict with empty visual_summary; that flows
        # through normally.
        if not isinstance(creative, dict):
            raise RuntimeError(
                f"[IntakeVideoAgent] vision LLM returned non-dict "
                f"({type(creative).__name__}); cannot extract visual_summary"
            )
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
        a multimodal call with the video file attached.
        """
        # Validate the upload exists on disk before paying for a vision
        # LLM call — otherwise the call returns plausible-looking
        # placeholder text on the missing input and we silently register
        # a useless artifact.
        if not input_data.raw_video_path or not os.path.isfile(input_data.raw_video_path):
            raise RuntimeError(
                f"[IntakeVideoAgent] raw_video_path not found on disk: "
                f"{input_data.raw_video_path!r}"
            )

        skeleton = self.build_skeleton(input_data)
        system = self.system_prompt()
        user = self.build_user_prompt(input_data)
        if rework_notes:
            user += self._rework_section(rework_notes)

        media = [{"type": "video", "path": input_data.raw_video_path}]

        creative = await self.llm.chat_json(
            system, user, media_attachments=media or None,
        )
        return self.fill_creative(skeleton, creative)
