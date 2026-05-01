"""Evaluator for AmbienceAgent output — exactly one film-wide bed."""

from __future__ import annotations

from ..base_evaluator import BaseEvaluator
from .schema import AmbienceAgentOutput


class AmbienceEvaluator(BaseEvaluator[AmbienceAgentOutput]):

    creative_dimensions: list[tuple[str, str]] = []

    def check_structure(self, output: AmbienceAgentOutput) -> list[str]:
        errors: list[str] = []
        beds = output.content.beds
        if not beds:
            errors.append("beds list is empty")
            return errors
        if len(beds) != 1:
            errors.append(
                f"AmbienceAgent must emit exactly one film-wide bed; got "
                f"{len(beds)}. Collapse scene-specific beds into a single "
                "global room-tone underlay."
            )
        for i, bed in enumerate(beds):
            p = f"beds[{i}]"
            if not bed.ambience_id:
                errors.append(f"{p}.ambience_id is empty")
            if not bed.description:
                errors.append(f"{p}.description is empty")
        return errors
