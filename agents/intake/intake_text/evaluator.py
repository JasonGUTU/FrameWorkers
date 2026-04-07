"""Evaluator for IntakeTextAgent (output-internal only)."""

from __future__ import annotations

from ...base_evaluator import BaseEvaluator
from .schema import IntakeTextOutput


class IntakeTextEvaluator(BaseEvaluator[IntakeTextOutput]):

    creative_dimensions: list[tuple[str, str]] = []  # no L2 LLM eval needed

    def check_structure(self, output: IntakeTextOutput) -> list[str]:
        errors: list[str] = []
        if not output.content.text:
            errors.append("content.text is empty")
        if output.metrics.char_count <= 0:
            errors.append("metrics.char_count must be > 0")
        if not output.artifact_caption.what:
            errors.append("artifact_caption.what is empty")
        return errors
