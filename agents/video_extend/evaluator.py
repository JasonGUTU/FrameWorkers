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
        # exactly 5 or 10" rule. The fal / Kling extension backend
        # silently rounds non-{5,10} values; without this check that
        # silent rounding masks drift (CLAUDE.md §7 anti-pattern).
        if spec.target_duration_seconds not in (5, 5.0, 10, 10.0):
            errors.append(
                f"extension_spec.target_duration_seconds "
                f"({spec.target_duration_seconds}) must be exactly 5 or "
                "10 (Kling video extension only accepts 5s or 10s clips)"
            )

        return errors
