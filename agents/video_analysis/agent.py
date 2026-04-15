"""VideoAnalysisAgent — deep structured analysis of video content.

Input:  VideoAnalysisAgentInput (source_video_path)
Output: VideoAnalysisAgentOutput (scene segments + summary + entities)

Uses a vision-capable LLM to analyze video content: detect scene
boundaries, describe each scene, identify entities, and produce an
overall summary.  This is a pure LLM + vision agent with no
materializer — the structured analysis is the output.
"""

from __future__ import annotations

from typing import Any

from ..base_agent import BaseAgent
from .schema import VideoAnalysisAgentInput, VideoAnalysisAgentOutput


VIDEO_ANALYSIS_OUTPUT_TEMPLATE = """{
  "content": {
    "video_summary": {
      "title": "<suggested title>",
      "summary": "<2-4 sentence overall summary>",
      "genre": "<genre/category>",
      "language": "<detected spoken language or empty>",
      "duration_seconds": 0
    },
    "scenes": [
      {
        "scene_id": "scene_001",
        "start_time": 0.0,
        "end_time": 10.5,
        "description": "<visual description of what happens in this scene>",
        "setting": "<location / environment>",
        "mood": "<emotional tone>",
        "entities": ["<person/object 1>", "<person/object 2>"]
      }
    ]
  }
}"""


class VideoAnalysisAgent(BaseAgent[VideoAnalysisAgentInput, VideoAnalysisAgentOutput]):

    async def generate(
        self,
        input_data: VideoAnalysisAgentInput,
        *,
        rework_notes: str = "",
    ) -> VideoAnalysisAgentOutput:
        system = self.system_prompt()
        user = self.build_user_prompt(input_data)
        if rework_notes:
            user += self._rework_section(rework_notes)

        media = []
        if input_data.source_video_path:
            media.append({"type": "video", "path": input_data.source_video_path})

        raw = await self.llm.chat_json(
            system, user, media_attachments=media or None,
        )
        output = self.parse_output(raw)
        self.recompute_metrics(output)
        return output

    def system_prompt(self) -> str:
        return (
            "You are VideoAnalysisAgent: analyze video content and produce "
            "a structured breakdown.\n\n"
            "=== YOUR TASK ===\n"
            "Watch/analyze the provided video and produce:\n"
            "1. A high-level video_summary with title, summary, genre, and "
            "language detection.\n"
            "2. A list of scene segments with detected boundaries, visual "
            "descriptions, settings, mood, and entities.\n\n"
            "=== SCENE DETECTION RULES ===\n"
            "1. A scene changes when there's a significant shift in "
            "location, time, or visual content (not just camera angle).\n"
            "2. scene_id format: scene_NNN (3-digit zero-padded, starting "
            "at scene_001).\n"
            "3. Timestamps should be in seconds with one decimal place.\n"
            "4. Description should capture WHAT HAPPENS visually, not just "
            "what's there (actions, movements, interactions).\n"
            "5. Entities: list specific people (by appearance if name "
            "unknown), objects, animals that are prominent in the scene.\n\n"
            "=== OUTPUT FORMAT ===\n"
            "JSON only; no markdown; match the user-message template "
            "exactly.\n\n"
            "Do NOT include an artifact_caption block — the system "
            "generates it automatically."
        )

    def build_user_prompt(self, input_data: VideoAnalysisAgentInput) -> str:
        return (
            f"Analyze this video: {input_data.source_video_path}\n\n"
            "Produce a structured analysis in EXACTLY this shape:\n\n"
            f"{VIDEO_ANALYSIS_OUTPUT_TEMPLATE}\n\n"
            "Return JSON only."
        )

    def parse_output(self, raw: dict[str, Any]) -> VideoAnalysisAgentOutput:
        return VideoAnalysisAgentOutput.model_validate(raw)

    def recompute_metrics(self, output: VideoAnalysisAgentOutput) -> None:
        c = output.content
        output.metrics.scene_count = len(c.scenes)
        output.metrics.duration_seconds = c.video_summary.duration_seconds
        output.metrics.entity_count = sum(
            len(s.entities) for s in c.scenes
        )
