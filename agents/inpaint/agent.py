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
            "=== WHEN TO REJECT UPSTREAM INPUT ===\n"
            "Use the shared input_rejection escape hatch (see the UPSTREAM "
            "INPUT REJECTION block above) ONLY if the inputs make "
            "inpainting impossible. Concretely, reject when ANY of these "
            "is true:\n"
            "  * source_video_path is empty / whitespace-only — there is "
            "no video to edit.\n"
            "  * replacement_description is empty AND mask_path is empty "
            "— I have no idea what to paint in the masked region, and "
            "without a manual mask there is nothing to derive intent "
            "from.\n"
            "  * mask_mode is 'manual' but mask_path is empty — manual "
            "mode requires an explicit mask file.\n"
            "When you reject, populate the rejection fields like this:\n"
            "  * reason: the single most specific defect (e.g. 'mask_mode "
            "is manual but mask_path is empty — cannot run manual "
            "inpainting without a mask file').\n"
            "  * missing_labels: whichever of ['source_video', 'mask'] "
            "is unusable.\n"
            "  * offending_fields: e.g. ['source_video_path'] or "
            "['replacement_description', 'mask_path'].\n"
            "  * upstream_agent_hint: 'IntakeVideoAgent' for missing "
            "video, 'IntakeImageAgent' / 'IntakeTextAgent' for missing "
            "mask spec.\n"
            "If the replacement_description is short or the mask_mode is "
            "depth/object-track without an explicit mask file — DO NOT "
            "reject; depth/object modes deliberately do not need a "
            "manual mask.\n"
            "=== END WHEN TO REJECT UPSTREAM INPUT ===\n\n"
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
