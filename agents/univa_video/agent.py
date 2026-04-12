"""UnivaVideoAgent — per-shot I2V plan from a storyboard JSON text blob.

Input:  UnivaVideoInput (storyboard_json_text + shot_keyframes image refs)
Output: UnivaVideoOutput (per-shot video_prompt + asset placeholders +
        final_video_asset)

Generation model: ONE LLM call via ``_llm_fill_full``. The LLM reads the
upstream storyboard as an indented JSON text blob and composes a
video-generation prompt for each shot by combining the shot's visual
description, setting, plot, and camera design fields. Zero Python-side
string-key access on the upstream storyboard. See CLAUDE.md §7.
"""

from __future__ import annotations

from typing import Any

from ..base_agent import BaseAgent
from .schema import (
    UnivaVideoInput,
    UnivaVideoOutput,
)


UNIVA_VIDEO_OUTPUT_TEMPLATE = """{
  "content": {
    "shot_videos": [
      {
        "shot_id": 0,
        "video_prompt": "<composed from the shot's setting + plot + visual description + camera distance/angle/lens, concatenated into one I2V motion prompt>",
        "video_asset": {"asset_id": "", "uri": "placeholder", "format": "mp4"}
      }
    ],
    "final_video_asset": {"asset_id": "", "uri": "placeholder", "format": "mp4"}
  }
}"""


class UnivaVideoAgent(BaseAgent[UnivaVideoInput, UnivaVideoOutput]):

    async def generate(
        self,
        input_data: UnivaVideoInput,
        *,
        rework_notes: str = "",
    ) -> UnivaVideoOutput:
        """Single full-output LLM call from the storyboard JSON text blob."""
        output = await self._llm_fill_full(input_data, rework_notes)
        self.recompute_metrics(output)
        return output

    def system_prompt(self) -> str:
        return (
            "You are UnivaVideoAgent: read a storyboard and produce "
            "per-shot video-generation prompts.\n\n"
            "=== INPUT FORMAT ===\n"
            "You will receive the upstream storyboard as a RAW JSON TEXT "
            "BLOB. Do NOT assume specific field names. READ the JSON and "
            "find the ordered list of shots with their visual "
            "descriptions, settings, plot beats, and camera/perspective "
            "design. Reason from the text.\n\n"
            "=== YOUR JOB ===\n"
            "For each SHOT in the storyboard, compose a ``video_prompt`` "
            "by concatenating the shot's description fields (setting, "
            "plot, static visual description, camera distance/angle/lens) "
            "into one continuous image-to-video motion prompt. This is "
            "the text that will accompany the shot's starting-frame "
            "keyframe image when calling the I2V model.\n\n"
            "=== ID CONVENTIONS ===\n"
            "shot_id: reuse the storyboard's shot id (integer).\n"
            "video_asset: leave as placeholder.\n"
            "final_video_asset: leave as placeholder.\n\n"
            "=== OUTPUT FORMAT ===\n"
            "JSON only; no markdown; match the template exactly.\n\n"
            "Do NOT include an artifact_caption block — the system "
            "generates it automatically."
        )

    def build_user_prompt(self, input_data: UnivaVideoInput) -> str:
        return (
            "=== STORYBOARD (raw JSON — read before writing) ===\n"
            f"{input_data.storyboard_json_text}\n"
            "=== END STORYBOARD ===\n\n"
            "Produce the full video plan in this shape:\n\n"
            f"{UNIVA_VIDEO_OUTPUT_TEMPLATE}\n\n"
            "Return JSON only."
        )

    def parse_output(self, raw: dict[str, Any]) -> UnivaVideoOutput:
        return UnivaVideoOutput.model_validate(raw)

    def recompute_metrics(self, output: UnivaVideoOutput) -> None:
        c = output.content
        output.metrics.shot_count = len(c.shot_videos)
