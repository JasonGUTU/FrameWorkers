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

        if spec.target_duration_seconds <= 0:
            errors.append(
                f"extension_spec.target_duration_seconds "
                f"({spec.target_duration_seconds}) must be positive"
            )

        if spec.target_duration_seconds > 30:
            errors.append(
                f"extension_spec.target_duration_seconds "
                f"({spec.target_duration_seconds}) exceeds 30s maximum "
                "for a single extension"
            )

        da = output.content.output_video
        if da.asset_id != "video_extend_output":
            errors.append(
                f"output_video.asset_id must be 'video_extend_output', "
                f"got '{da.asset_id}'"
            )

        return errors
