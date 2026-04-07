"""Evaluator for IntakeAudioAgent (output-internal only)."""

from __future__ import annotations

from ...base_evaluator import BaseEvaluator
from .schema import IntakeAudioOutput


class IntakeAudioEvaluator(BaseEvaluator[IntakeAudioOutput]):

    creative_dimensions: list[tuple[str, str]] = []

    def check_structure(self, output: IntakeAudioOutput) -> list[str]:
        errors: list[str] = []
        if not output.content.audio_asset.uri:
            errors.append("content.audio_asset.uri is empty")
        return errors
