"""CompositorAgent — plan and execute final video composition.

Input:  CompositorAgentInput (screenplay + video + audio + subtitle JSON texts
        and direct file paths)
Output: CompositorAgentOutput (composition plan + final delivery asset)

The LLM plans the composition: transitions between shots, color grading,
subtitle styling.  The materializer then executes the plan using FFmpeg
to produce the final deliverable video.
"""

from __future__ import annotations

from typing import Any

from ..base_agent import BaseAgent
from .schema import CompositorAgentInput, CompositorAgentOutput


COMPOSITOR_OUTPUT_TEMPLATE = """{
  "content": {
    "plan": {
      "transitions": [
        {
          "from_shot_id": "sh_001",
          "to_shot_id": "sh_002",
          "transition_type": "crossfade",
          "duration_ms": 500
        }
      ],
      "color_grade": {
        "brightness": 0.0,
        "contrast": 0.05,
        "saturation": 0.0,
        "tone": "cinematic warm"
      },
      "subtitle_style": {
        "font_size": 24,
        "font_color": "#FFFFFF",
        "outline_color": "#000000",
        "position": "bottom",
        "burn_in": true
      },
      "output_resolution": "1920x1080",
      "output_fps": 30,
      "output_format": "mp4"
    },
    "delivery_asset": {
      "asset_id": "compositor_final",
      "uri": "placeholder",
      "format": "mp4",
      "resolution": "1920x1080",
      "duration_seconds": 0
    }
  }
}"""


class CompositorAgent(BaseAgent[CompositorAgentInput, CompositorAgentOutput]):

    async def generate(
        self,
        input_data: CompositorAgentInput,
        *,
        rework_notes: str = "",
    ) -> CompositorAgentOutput:
        output = await self._llm_fill_full(input_data, rework_notes)
        self.recompute_metrics(output)
        return output

    def system_prompt(self) -> str:
        return (
            "You are CompositorAgent: plan the final video composition by "
            "reading the screenplay, video package, audio package, and "
            "subtitle tracks.\n\n"
            "=== INPUT FORMAT ===\n"
            "You will receive raw JSON text blobs for:\n"
            "- Screenplay (scene/shot structure)\n"
            "- Video package (shot clips and timing)\n"
            "- Audio package (narration, music, ambience)\n"
            "- Subtitle tracks (timed cues)\n\n"
            "=== COMPOSITION PLANNING RULES ===\n"
            "1. TRANSITIONS: For each pair of consecutive shots, decide the "
            "transition type. Use 'cut' for most shot-to-shot transitions "
            "within a scene. Use 'crossfade' (500-1000ms) for scene changes. "
            "Use 'fade_black' (800-1200ms) for dramatic scene endings.\n"
            "2. COLOR GRADE: Set a consistent color grade that matches the "
            "screenplay's overall mood. Keep adjustments subtle (-0.1 to 0.1).\n"
            "3. SUBTITLE STYLE: Choose appropriate font size and colors "
            "based on the video resolution. White with black outline is the "
            "default. Set burn_in=true for final delivery.\n"
            "4. RESOLUTION: Match the source video resolution. Default "
            "1920x1080.\n"
            "5. delivery_asset: asset_id is always 'compositor_final', "
            "uri is always 'placeholder'.\n\n"
            "=== OUTPUT FORMAT ===\n"
            "JSON only; no markdown; match the user-message template "
            "exactly.\n\n"
            "Do NOT include an artifact_caption block — the system generates "
            "it automatically."
        )

    def build_user_prompt(self, input_data: CompositorAgentInput) -> str:
        parts = [
            "Plan the final video composition from the following inputs.\n\n"
        ]

        if input_data.screenplay_json_text:
            parts.append(
                "=== SCREENPLAY ===\n"
                f"{input_data.screenplay_json_text}\n"
                "=== END SCREENPLAY ===\n\n"
            )

        if input_data.video_json_text:
            parts.append(
                "=== VIDEO PACKAGE ===\n"
                f"{input_data.video_json_text}\n"
                "=== END VIDEO PACKAGE ===\n\n"
            )

        if input_data.audio_json_text:
            parts.append(
                "=== AUDIO PACKAGE ===\n"
                f"{input_data.audio_json_text}\n"
                "=== END AUDIO PACKAGE ===\n\n"
            )

        if input_data.subtitle_json_text:
            parts.append(
                "=== SUBTITLE TRACKS ===\n"
                f"{input_data.subtitle_json_text}\n"
                "=== END SUBTITLE TRACKS ===\n\n"
            )

        parts.append(
            "Produce the composition plan in EXACTLY this shape:\n\n"
            f"{COMPOSITOR_OUTPUT_TEMPLATE}\n\n"
            "Return JSON only."
        )

        return "".join(parts)

    def parse_output(self, raw: dict[str, Any]) -> CompositorAgentOutput:
        return CompositorAgentOutput.model_validate(raw)

    def recompute_metrics(self, output: CompositorAgentOutput) -> None:
        plan = output.content.plan
        output.metrics.transition_count = len(plan.transitions)
        output.metrics.has_subtitles = plan.subtitle_style.burn_in
        output.metrics.has_audio = True  # always true if audio_package provided
