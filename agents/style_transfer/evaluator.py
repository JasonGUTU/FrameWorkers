"""Evaluator for StyleTransferAgent output."""

from __future__ import annotations

from ..base_evaluator import BaseEvaluator
from .schema import StyleTransferAgentOutput


class StyleTransferEvaluator(BaseEvaluator[StyleTransferAgentOutput]):

    creative_dimensions: list[tuple[str, str]] = []  # L2 skipped — structural checks are sufficient

    def check_structure(self, output: StyleTransferAgentOutput) -> list[str]:
        errors: list[str] = []
        spec = output.content.style_spec

        if not spec.style_description:
            errors.append("style_spec.style_description is empty")

        if not spec.style_prompt:
            errors.append("style_spec.style_prompt is empty")

        if len(spec.style_prompt) < 10:
            errors.append(
                "style_spec.style_prompt is too short — needs more detail "
                "for the model"
            )

        # NOTE: style_strength range is enforced by Pydantic
        # (Field(ge=0.0, le=1.0) on schema) — not re-checked here.

        da = output.content.output_video
        if da.asset_id != "style_transfer_output":
            errors.append(
                f"output_video.asset_id must be 'style_transfer_output', "
                f"got '{da.asset_id}'"
            )

        return errors
