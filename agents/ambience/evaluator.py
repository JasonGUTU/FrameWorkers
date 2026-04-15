"""Evaluator for AmbienceAgent output."""

from __future__ import annotations

from ..base_evaluator import BaseEvaluator
from .schema import AmbienceAgentOutput


class AmbienceEvaluator(BaseEvaluator[AmbienceAgentOutput]):

    creative_dimensions: list[tuple[str, str]] = []

    def check_structure(self, output: AmbienceAgentOutput) -> list[str]:
        errors: list[str] = []
        if not output.content.beds:
            errors.append("beds list is empty")
            return errors
        for i, bed in enumerate(output.content.beds):
            p = f"beds[{i}]"
            if not bed.ambience_id:
                errors.append(f"{p}.ambience_id is empty")
            if not bed.scene_id:
                errors.append(f"{p}.scene_id is empty")
            if not bed.description:
                errors.append(f"{p}.description is empty")
        return errors
