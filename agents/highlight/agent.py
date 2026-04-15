"""HighlightAgent — select and compile highlight clips from video.

Input:  HighlightAgentInput (source video + optional analysis + criteria)
Output: HighlightAgentOutput (selected clips + compiled highlight reel)

The LLM analyzes the video (using analysis data if available) and selects
the best segments matching the given criteria.  The materializer then
clips and compiles them into a highlight reel.
"""

from __future__ import annotations

from typing import Any

from ..base_agent import BaseAgent
from .schema import HighlightAgentInput, HighlightAgentOutput


HIGHLIGHT_OUTPUT_TEMPLATE = """{
  "content": {
    "criteria": "<the selection criteria applied>",
    "clips": [
      {
        "clip_id": "clip_001",
        "start_time": 5.0,
        "end_time": 12.5,
        "reason": "<why this segment is a highlight>",
        "score": 0.9
      }
    ],
    "compiled_video": {
      "asset_id": "highlight_reel",
      "uri": "placeholder",
      "format": "mp4"
    }
  }
}"""


class HighlightAgent(BaseAgent[HighlightAgentInput, HighlightAgentOutput]):

    async def generate(
        self,
        input_data: HighlightAgentInput,
        *,
        rework_notes: str = "",
    ) -> HighlightAgentOutput:
        output = await self._llm_fill_full(input_data, rework_notes)
        self.recompute_metrics(output)
        return output

    def system_prompt(self) -> str:
        return (
            "You are HighlightAgent: select the best highlight segments "
            "from a video based on given criteria.\n\n"
            "=== YOUR TASK ===\n"
            "Given a video (and optionally a structured analysis), select "
            "the segments that best match the criteria. For each clip:\n"
            "1. clip_id: clip_NNN (3-digit zero-padded, starting at "
            "clip_001).\n"
            "2. start_time / end_time: in seconds. Each clip should be "
            "at least 2 seconds and at most 30 seconds.\n"
            "3. reason: explain why this segment is a highlight.\n"
            "4. score: 0.0-1.0 relevance score for the criteria.\n\n"
            "=== SELECTION RULES ===\n"
            "- Select 3-10 clips typically, sorted by position in video.\n"
            "- Clips should not overlap.\n"
            "- Prefer clips that are self-contained and visually "
            "interesting.\n"
            "- compiled_video asset_id is always 'highlight_reel', "
            "uri is always 'placeholder'.\n\n"
            "=== OUTPUT FORMAT ===\n"
            "JSON only; no markdown; match the user-message template "
            "exactly.\n\n"
            "Do NOT include an artifact_caption block — the system "
            "generates it automatically."
        )

    def build_user_prompt(self, input_data: HighlightAgentInput) -> str:
        parts = [
            f"Source video: {input_data.source_video_path}\n"
            f"Criteria: {input_data.criteria or 'best/most interesting moments'}\n\n"
        ]

        if input_data.analysis_json_text:
            parts.append(
                "=== VIDEO ANALYSIS (use for informed selection) ===\n"
                f"{input_data.analysis_json_text}\n"
                "=== END ANALYSIS ===\n\n"
            )

        parts.append(
            "Select highlight clips in EXACTLY this shape:\n\n"
            f"{HIGHLIGHT_OUTPUT_TEMPLATE}\n\n"
            "Return JSON only."
        )

        return "".join(parts)

    def parse_output(self, raw: dict[str, Any]) -> HighlightAgentOutput:
        return HighlightAgentOutput.model_validate(raw)

    def recompute_metrics(self, output: HighlightAgentOutput) -> None:
        c = output.content
        output.metrics.clip_count = len(c.clips)
        output.metrics.total_highlight_seconds = sum(
            max(0, clip.end_time - clip.start_time) for clip in c.clips
        )
