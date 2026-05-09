"""Evaluator for VideoExtendAgent output."""

from __future__ import annotations

from ..base_evaluator import BaseEvaluator
from .schema import VideoExtendAgentOutput


class VideoExtendEvaluator(BaseEvaluator[VideoExtendAgentOutput]):

    creative_dimensions: list[tuple[str, str]] = []  # L2 skipped — structural checks are sufficient

    def check_structure(self, output: VideoExtendAgentOutput) -> list[str]:
        errors: list[str] = []
        spec = output.content.extension_spec

        if not spec.continuation_prompt:
            errors.append("extension_spec.continuation_prompt is empty")

        if len(spec.continuation_prompt) < 15:
            errors.append(
                "extension_spec.continuation_prompt is too short — needs "
                "more visual detail"
            )

        if not spec.motion_description:
            errors.append("extension_spec.motion_description is empty")

        # Mirror of system_prompt's "target_duration_seconds MUST be
        # exactly 5" rule. Both Kling and HunyuanVideo accept 5s clips;
        # HunyuanVideo I2V does not support 10s natively (training cap
        # at 129 frames ≈ 5.4s) so we standardize on 5 across backends.
        # Without this check, backends silently round mismatched values
        # (CLAUDE.md §7 anti-pattern).
        if spec.target_duration_seconds not in (5, 5.0):
            errors.append(
                f"extension_spec.target_duration_seconds "
                f"({spec.target_duration_seconds}) must be exactly 5 "
                "(downstream i2v backends standardize on 5s clips)"
            )

        return errors
