"""Evaluator for IntakeImageAgent (output-internal only)."""

from __future__ import annotations

from ...base_evaluator import BaseEvaluator
from .schema import IntakeImageOutput


class IntakeImageEvaluator(BaseEvaluator[IntakeImageOutput]):

    creative_dimensions: list[tuple[str, str]] = []

    def check_structure(self, output: IntakeImageOutput) -> list[str]:
        errors: list[str] = []
        if not output.content.image_asset.uri:
            errors.append("content.image_asset.uri is empty")
        return errors
