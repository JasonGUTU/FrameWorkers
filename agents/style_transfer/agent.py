"""StyleTransferAgent — apply visual style transfer to video.

Input:  StyleTransferAgentInput (source video + style description/reference)
Output: StyleTransferAgentOutput (style spec + output video asset)

The LLM reads the style description (and optionally a style reference image
description) and produces an optimized prompt for the video edit model.
The materializer then calls the video edit service to apply the style.
"""

from __future__ import annotations

from typing import Any

from ..base_agent import BaseAgent
from .schema import StyleTransferAgentInput, StyleTransferAgentOutput


STYLE_TRANSFER_OUTPUT_TEMPLATE = """{
  "content": {
    "style_spec": {
      "style_description": "<detailed description of the target visual style>",
      "style_prompt": "<optimized prompt for the video style transfer model>",
      "preserve_motion": true,
      "style_strength": 0.7
    },
    "output_video": {
      "asset_id": "style_transfer_output",
      "uri": "placeholder",
      "format": "mp4"
    }
  }
}"""


class StyleTransferAgent(BaseAgent[StyleTransferAgentInput, StyleTransferAgentOutput]):

    async def generate(
        self,
        input_data: StyleTransferAgentInput,
        *,
        rework_notes: str = "",
    ) -> StyleTransferAgentOutput:
        output = await self._llm_fill_full(input_data, rework_notes)
        self.recompute_metrics(output)
        return output

    def system_prompt(self) -> str:
        return (
            "You are StyleTransferAgent: plan a visual style transfer for "
            "a video.\n\n"
            "=== WHEN TO REJECT UPSTREAM INPUT ===\n"
            "Use the shared input_rejection escape hatch (see the UPSTREAM "
            "INPUT REJECTION block above) ONLY if the inputs make style "
            "transfer impossible. Concretely, reject when ANY of these is "
            "true:\n"
            "  * source_video_path is empty / whitespace-only — there is "
            "no video to restyle.\n"
            "  * Both style_description AND style_reference_path are "
            "empty — I have no idea what style to apply, and inventing a "
            "style would override the user's intent.\n"
            "When you reject, populate the rejection fields like this:\n"
            "  * reason: the single most specific defect (e.g. 'no "
            "style description or style reference image provided — cannot "
            "decide what visual style to apply').\n"
            "  * missing_labels: whichever of ['source_video', "
            "'style_reference'] is unusable.\n"
            "  * offending_fields: e.g. ['source_video_path'] or "
            "['style_description', 'style_reference_path'].\n"
            "  * upstream_agent_hint: 'IntakeVideoAgent' for missing "
            "video, 'IntakeImageAgent' / 'IntakeTextAgent' for missing "
            "style reference.\n"
            "If the style description is short or vague (e.g. just "
            "'anime') — DO NOT reject; that is a perfectly usable "
            "style cue, just optimize the prompt around it.\n"
            "=== END WHEN TO REJECT UPSTREAM INPUT ===\n\n"
            "=== YOUR TASK ===\n"
            "Given a style description (and optionally a style reference), "
            "produce:\n"
            "1. A detailed style_description that captures the visual "
            "qualities to apply.\n"
            "2. An optimized style_prompt suitable for a video style "
            "transfer model (concise, keyword-rich, focused on visual "
            "attributes like color palette, texture, rendering technique, "
            "lighting).\n"
            "3. preserve_motion: usually true (keep original camera and "
            "subject motion). Set false only if the style inherently "
            "changes motion (e.g. stop-motion, timelapse).\n"
            "4. style_strength: 0.5-0.8 for subtle styles, 0.8-1.0 for "
            "dramatic transformations (anime, oil painting, etc.).\n\n"
            "=== OUTPUT FORMAT ===\n"
            "JSON only; no markdown; match the user-message template "
            "exactly. asset_id is always 'style_transfer_output', "
            "uri is always 'placeholder'.\n\n"
            "Do NOT include an artifact_caption block — the system "
            "generates it automatically."
        )

    def build_user_prompt(self, input_data: StyleTransferAgentInput) -> str:
        parts = [
            f"Apply this style to a video: **{input_data.style_description}**\n\n"
            f"Source video: {input_data.source_video_path}\n"
        ]

        if input_data.style_reference_path:
            parts.append(
                f"Style reference image: {input_data.style_reference_path}\n"
            )

        parts.append(
            "\nProduce the style transfer plan in EXACTLY this shape:\n\n"
            f"{STYLE_TRANSFER_OUTPUT_TEMPLATE}\n\n"
            "Return JSON only."
        )

        return "".join(parts)

    def parse_output(self, raw: dict[str, Any]) -> StyleTransferAgentOutput:
        return StyleTransferAgentOutput.model_validate(raw)

    def recompute_metrics(self, output: StyleTransferAgentOutput) -> None:
        spec = output.content.style_spec
        output.metrics.style_strength = spec.style_strength
        output.metrics.preserve_motion = spec.preserve_motion
