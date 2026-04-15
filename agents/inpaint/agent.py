"""InpaintAgent — object replacement / depth-based video editing.

Input:  InpaintAgentInput (source video + mask mode + replacement description)
Output: InpaintAgentOutput (inpaint spec + output video asset)

Supports multiple mask modes:
- manual: user provides explicit mask
- depth_foreground: auto-mask foreground via depth estimation
- depth_background: auto-mask background via depth estimation
- object_track: track and mask a specific object

The LLM plans the inpainting prompt; the materializer executes it.
"""

from __future__ import annotations

from typing import Any

from ..base_agent import BaseAgent
from .schema import InpaintAgentInput, InpaintAgentOutput


INPAINT_OUTPUT_TEMPLATE = """{
  "content": {
    "inpaint_spec": {
      "mask_mode": "<manual | depth_foreground | depth_background | object_track>",
      "replacement_description": "<what to paint in the masked region>",
      "inpaint_prompt": "<optimized prompt for the inpainting model>",
      "preserve_unmasked": true,
      "blend_edge_px": 8
    },
    "output_video": {
      "asset_id": "inpaint_output",
      "uri": "placeholder",
      "format": "mp4"
    }
  }
}"""


class InpaintAgent(BaseAgent[InpaintAgentInput, InpaintAgentOutput]):

    async def generate(
        self,
        input_data: InpaintAgentInput,
        *,
        rework_notes: str = "",
    ) -> InpaintAgentOutput:
        output = await self._llm_fill_full(input_data, rework_notes)
        self.recompute_metrics(output)
        return output

    def system_prompt(self) -> str:
        return (
            "You are InpaintAgent: plan video inpainting / object "
            "replacement operations.\n\n"
            "=== MASK MODES ===\n"
            "- manual: An explicit mask image/video is provided.\n"
            "- depth_foreground: Automatically mask the foreground using "
            "depth estimation — use this to replace the foreground while "
            "keeping the background unchanged.\n"
            "- depth_background: Automatically mask the background using "
            "depth estimation — use this to replace the background while "
            "keeping the foreground (people, objects) unchanged.\n"
            "- object_track: Track a specific object across frames and "
            "mask it — describe what to track in the replacement.\n\n"
            "=== YOUR TASK ===\n"
            "Given the mask mode and replacement description, produce:\n"
            "1. inpaint_prompt: an optimized prompt for the inpainting "
            "model describing what should appear in the masked region. "
            "Be visually specific (colors, textures, lighting, style).\n"
            "2. replacement_description: a human-readable description of "
            "the intended change.\n"
            "3. blend_edge_px: feathering radius (4-16 px typical). "
            "Higher for organic edges, lower for sharp edges.\n\n"
            "=== OUTPUT FORMAT ===\n"
            "JSON only; no markdown; match the user-message template "
            "exactly. asset_id is always 'inpaint_output', uri is always "
            "'placeholder'.\n\n"
            "Do NOT include an artifact_caption block — the system "
            "generates it automatically."
        )

    def build_user_prompt(self, input_data: InpaintAgentInput) -> str:
        parts = [
            f"Mask mode: {input_data.mask_mode}\n"
            f"Replacement: {input_data.replacement_description}\n"
            f"Source video: {input_data.source_video_path}\n"
        ]

        if input_data.mask_path:
            parts.append(f"Mask file: {input_data.mask_path}\n")

        parts.append(
            "\nProduce the inpainting plan in EXACTLY this shape:\n\n"
            f"{INPAINT_OUTPUT_TEMPLATE}\n\n"
            "Return JSON only."
        )

        return "".join(parts)

    def parse_output(self, raw: dict[str, Any]) -> InpaintAgentOutput:
        return InpaintAgentOutput.model_validate(raw)

    def recompute_metrics(self, output: InpaintAgentOutput) -> None:
        spec = output.content.inpaint_spec
        output.metrics.mask_mode = spec.mask_mode
        output.metrics.has_replacement = bool(spec.replacement_description)
