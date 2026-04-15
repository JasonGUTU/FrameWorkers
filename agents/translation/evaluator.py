"""Evaluator for TranslationAgent output."""

from __future__ import annotations

from ..base_evaluator import BaseEvaluator
from .schema import TranslationAgentOutput


class TranslationEvaluator(BaseEvaluator[TranslationAgentOutput]):

    creative_dimensions: list[tuple[str, str]] = []  # no L2 — tool agent, not creative

    def check_structure(self, output: TranslationAgentOutput) -> list[str]:
        errors: list[str] = []
        c = output.content

        if not c.source_language:
            errors.append("source_language is empty — must detect the source language")

        if not c.target_language:
            errors.append("target_language is empty")

        if not c.translated_payload:
            errors.append("translated_payload is empty — must contain the translated structure")

        return errors
