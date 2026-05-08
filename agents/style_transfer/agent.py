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
            "  * style_description is empty AND style_reference_path is "
            "empty AND creative_brief_json_text contains no recognisable "
            "style cue (no aesthetic / art-style / look / mood phrase "
            "anywhere in the brief text). Only then do I have no idea "
            "what style to apply, and inventing one would override the "
            "user's intent.\n"
            "When the brief mentions ANY style cue (named style like "
            "'Studio Ghibli' / 'ink-wash' / 'anime' / 'oil painting', or "
            "a descriptive phrase like 'animated-drama look' / 'cyberpunk "
            "neon'), DO NOT reject — extract that cue and use it as the "
            "style_description.\n"
            "When you reject, populate the rejection fields like this:\n"
            "  * reason: the single most specific defect (e.g. 'no "
            "style description, style reference image, or style cue in "
            "creative brief — cannot decide what visual style to apply').\n"
            "  * missing_labels: whichever of ['source_video', "
            "'style_reference', 'creative_brief'] is unusable.\n"
            "  * offending_fields: e.g. ['source_video_path'] or "
            "['style_description', 'style_reference_path', "
            "'creative_brief_json_text'].\n"
            "If the style description is short or vague (e.g. just "
            "'anime') — DO NOT reject; that is a perfectly usable "
            "style cue, just optimize the prompt around it.\n"
            "=== END WHEN TO REJECT UPSTREAM INPUT ===\n\n"
            "=== YOUR TASK ===\n"
            "Given a style description, optional style reference, and the "
            "user's creative brief, produce:\n"
            "1. A detailed style_description that captures the visual "
            "qualities to apply.\n"
            "2. An optimized style_prompt suitable for a video style "
            "transfer model (concise, keyword-rich, focused on visual "
            "attributes like color palette, texture, rendering technique, "
            "lighting).\n"
            "3. preserve_motion: usually true (keep original camera and "
            "subject motion). Set false only if the style inherently "
            "changes motion (e.g. stop-motion, timelapse).\n"
            "4. style_strength: lower (0.3-0.6) for stylistic touch-ups "
            "that preserve the photographic look; higher (0.7-1.0) when "
            "the source must be transformed into a markedly different "
            "medium.\n\n"
            "=== OUTPUT FORMAT ===\n"
            "JSON only; no markdown; match the user-message template "
            "exactly.\n\n"
            "Do NOT include an artifact_caption block — the system "
            "generates it automatically."
        )

    def build_user_prompt(self, input_data: StyleTransferAgentInput) -> str:
        parts = [
            f"Apply a style transfer to a video.\n\n"
            f"Source video: {input_data.source_video_path}\n"
        ]

        if input_data.style_description:
            parts.append(
                f"Style cue derived from upstream style_reference "
                f"(caption or payload): **{input_data.style_description}**\n"
            )

        if input_data.style_reference_path:
            parts.append(
                f"Style reference image: {input_data.style_reference_path}\n"
            )

        if input_data.creative_brief_json_text:
            parts.append(
                "\n=== CREATIVE BRIEF (raw JSON — read the user's verbatim "
                "request from it; the style cue may be in plain text) ===\n"
                f"{input_data.creative_brief_json_text}\n"
                "=== END CREATIVE BRIEF ===\n"
                "If the upstream style_description above is empty, extract "
                "the visual-style cue from the brief above and use it.\n"
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
