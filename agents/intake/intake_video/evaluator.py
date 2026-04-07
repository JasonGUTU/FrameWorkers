"""Evaluator for IntakeVideoAgent (output-internal only)."""

from __future__ import annotations

from ...base_evaluator import BaseEvaluator
from .schema import IntakeVideoOutput


class IntakeVideoEvaluator(BaseEvaluator[IntakeVideoOutput]):

    creative_dimensions: list[tuple[str, str]] = []

    def check_structure(self, output: IntakeVideoOutput) -> list[str]:
        errors: list[str] = []
        if not output.content.video_asset.uri:
            errors.append("content.video_asset.uri is empty")
        return errors
