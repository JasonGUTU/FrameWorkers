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
        "reason": "<why this segment is a highlight>"
      }
    ]
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
            "=== WHEN TO REJECT UPSTREAM INPUT ===\n"
            "Use the shared input_rejection escape hatch (see the UPSTREAM "
            "INPUT REJECTION block above) ONLY if the inputs make "
            "highlight selection impossible. Concretely, reject when:\n"
            "  * source_video_path is empty / whitespace-only — there is "
            "no video to extract highlights from.\n"
            "When you reject, populate the rejection fields like this:\n"
            "  * reason: e.g. 'source_video_path is empty — no video to "
            "extract highlights from'.\n"
            "  * missing_labels: ['source_video'] (the video_analysis "
            "label is optional).\n"
            "  * offending_fields: ['source_video_path'].\n"
            "If the criteria is empty or vague (e.g. 'best moments') — "
            "DO NOT reject; default to selecting the most visually "
            "interesting segments. If the analysis_json_text is empty — "
            "DO NOT reject; the analysis is purely an optional "
            "augmentation, you can select highlights from the video "
            "directly.\n"
            "=== END WHEN TO REJECT UPSTREAM INPUT ===\n\n"
            "=== YOUR TASK ===\n"
            "Given a video (and optionally a structured analysis), select "
            "the segments that best match the criteria. For each clip:\n"
            "1. clip_id: clip_NNN (3-digit zero-padded, starting at "
            "clip_001).\n"
            "2. start_time / end_time: in seconds. Each clip should be "
            "at least 2 seconds and at most 30 seconds.\n"
            "3. reason: explain why this segment is a highlight.\n\n"
            "=== SELECTION RULES ===\n"
            "- Select 3-10 clips typically, sorted by position in video.\n"
            "- Clips should not overlap.\n"
            "- Prefer clips that are self-contained and visually "
            "interesting.\n"
            "- If VIDEO ANALYSIS was provided AND the criteria targets "
            "narrative / content concepts (plot beats, reversals, "
            "emotional peaks, character interactions), FIRST consider "
            "scenes where `is_climax_candidate` is true, then sort "
            "remaining candidates by `tension_score` descending. Don't "
            "blindly pick top-N by tension for purely visual criteria "
            "(action choreography, VFX, kinetic B-roll) — those can come "
            "from anywhere in the video.\n\n"
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
