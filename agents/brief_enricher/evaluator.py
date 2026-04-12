"""Evaluator for BriefEnricherAgent output."""

from __future__ import annotations

from ..base_evaluator import BaseEvaluator
from .schema import BriefEnricherOutput


class BriefEnricherEvaluator(BaseEvaluator[BriefEnricherOutput]):

    creative_dimensions = [
        (
            "enrichment_quality",
            "Does the enriched brief naturally integrate the visual descriptions "
            "without losing the original creative intent?",
        ),
    ]

    def check_structure(self, output: BriefEnricherOutput) -> list[str]:
        errors: list[str] = []
        c = output.content
        if not c.enriched_brief.strip():
            errors.append("enriched_brief is empty")
        for i, cls in enumerate(c.image_classifications):
            if cls.role not in ("character", "location", "prop", "style"):
                errors.append(
                    f"image_classifications[{i}].role must be one of "
                    f"character/location/prop/style, got {cls.role!r}"
                )
        return errors
