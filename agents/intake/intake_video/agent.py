"""IntakeVideoAgent — runs a video LLM on a raw user video upload."""

from __future__ import annotations

from ...base_agent import BaseAgent
from ...common_schema import ArtifactCaption
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

    def build_skeleton(self, input_data: IntakeVideoInput) -> IntakeVideoOutput | None:
        skeleton = IntakeVideoOutput()
        skeleton.content = IntakeVideoContent(
            visual_summary="",
            video_asset=IntakeVideoAsset(uri=input_data.raw_video_path),
        )
        intent = (input_data.user_intent or "").strip()
        skeleton.artifact_caption = ArtifactCaption(
            what="",
            why=intent or "(no user intent provided)",
            scope="global",
        )
        return skeleton
