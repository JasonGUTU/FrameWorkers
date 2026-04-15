"""Evaluator for InpaintAgent output."""

from __future__ import annotations

from ..base_evaluator import BaseEvaluator
from .schema import InpaintAgentOutput


_VALID_MASK_MODES = {"manual", "depth_foreground", "depth_background", "object_track"}


class InpaintEvaluator(BaseEvaluator[InpaintAgentOutput]):

    creative_dimensions: list[tuple[str, str]] = []  # L2 skipped — structural checks are sufficient

    def check_structure(self, output: InpaintAgentOutput) -> list[str]:
        errors: list[str] = []
        spec = output.content.inpaint_spec

        if spec.mask_mode not in _VALID_MASK_MODES:
            errors.append(
                f"inpaint_spec.mask_mode '{spec.mask_mode}' must be one of "
                f"{_VALID_MASK_MODES}"
            )

        if not spec.replacement_description:
            errors.append("inpaint_spec.replacement_description is empty")

        if not spec.inpaint_prompt:
            errors.append("inpaint_spec.inpaint_prompt is empty")

        if len(spec.inpaint_prompt) < 10:
            errors.append(
                "inpaint_spec.inpaint_prompt is too short — needs more "
                "detail for the model"
            )

        if spec.blend_edge_px < 0:
            errors.append(
                f"inpaint_spec.blend_edge_px ({spec.blend_edge_px}) must "
                "be non-negative"
            )

        da = output.content.output_video
        if da.asset_id != "inpaint_output":
            errors.append(
                f"output_video.asset_id must be 'inpaint_output', "
                f"got '{da.asset_id}'"
            )

        return errors
