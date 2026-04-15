"""VideoExtendAgent — extend/continue a video clip.

Input:  VideoExtendAgentInput (source video + continuation description)
Output: VideoExtendAgentOutput (extension spec + output video asset)

The LLM plans the continuation: what happens next, motion description,
duration.  The materializer calls the video generation service in
video-extension mode to produce the continuation clip.
"""

from __future__ import annotations

from typing import Any

from ..base_agent import BaseAgent
from .schema import VideoExtendAgentInput, VideoExtendAgentOutput


VIDEO_EXTEND_OUTPUT_TEMPLATE = """{
  "content": {
    "extension_spec": {
      "continuation_prompt": "<detailed description of what happens next>",
      "target_duration_seconds": 5.0,
      "maintain_style": true,
      "motion_description": "<camera and subject motion for the extension>"
    },
    "output_video": {
      "asset_id": "video_extend_output",
      "uri": "placeholder",
      "format": "mp4"
    }
  }
}"""


class VideoExtendAgent(BaseAgent[VideoExtendAgentInput, VideoExtendAgentOutput]):

    async def generate(
        self,
        input_data: VideoExtendAgentInput,
        *,
        rework_notes: str = "",
    ) -> VideoExtendAgentOutput:
        output = await self._llm_fill_full(input_data, rework_notes)
        self.recompute_metrics(output)
        return output

    def system_prompt(self) -> str:
        return (
            "You are VideoExtendAgent: plan a continuation for an existing "
            "video clip.\n\n"
            "=== YOUR TASK ===\n"
            "Given a source video and a description of what should happen "
            "next, produce:\n"
            "1. continuation_prompt: a detailed, visually specific prompt "
            "for the video generation model. Describe the scene, subjects, "
            "lighting, and what changes from the last frame.\n"
            "2. motion_description: specific camera and subject motion "
            "(e.g. 'camera slowly pans right as the character walks toward "
            "the door').\n"
            "3. target_duration_seconds: typically 3-10 seconds. Match the "
            "pacing of the original.\n"
            "4. maintain_style: true unless the user explicitly wants a "
            "visual change.\n\n"
            "=== OUTPUT FORMAT ===\n"
            "JSON only; no markdown; match the user-message template "
            "exactly. asset_id is always 'video_extend_output', uri is "
            "always 'placeholder'.\n\n"
            "Do NOT include an artifact_caption block — the system "
            "generates it automatically."
        )

    def build_user_prompt(self, input_data: VideoExtendAgentInput) -> str:
        return (
            f"Extend this video: {input_data.source_video_path}\n\n"
            f"What should happen next: {input_data.continuation_description}\n\n"
            "Produce the extension plan in EXACTLY this shape:\n\n"
            f"{VIDEO_EXTEND_OUTPUT_TEMPLATE}\n\n"
            "Return JSON only."
        )

    def parse_output(self, raw: dict[str, Any]) -> VideoExtendAgentOutput:
        return VideoExtendAgentOutput.model_validate(raw)

    def recompute_metrics(self, output: VideoExtendAgentOutput) -> None:
        spec = output.content.extension_spec
        output.metrics.target_duration_seconds = spec.target_duration_seconds
