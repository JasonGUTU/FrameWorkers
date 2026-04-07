"""Evaluator for UnivaStoryboardAgent output (output-internal only)."""

from __future__ import annotations

from ..base_evaluator import BaseEvaluator
from .schema import UnivaStoryboardOutput


class UnivaStoryboardEvaluator(BaseEvaluator[UnivaStoryboardOutput]):

    creative_dimensions = [
        ("coherence", "Do the shots flow logically as a continuous narrative within this storyboard?"),
    ]

    def check_structure(self, output: UnivaStoryboardOutput) -> list[str]:
        errors: list[str] = []
        c = output.content

        if not c.characters:
            errors.append("characters list is empty")

        if not c.shots:
            errors.append("shots list is empty")

        if not c.style:
            errors.append("style is empty")

        # Validate character IDs are unique
        char_ids = [ch.id for ch in c.characters]
        if len(char_ids) != len(set(char_ids)):
            errors.append("duplicate character IDs found")

        # Validate shot IDs are contiguous from 1
        shot_ids = [s.id for s in c.shots]
        expected = list(range(1, len(c.shots) + 1))
        if shot_ids != expected:
            errors.append(
                f"shot IDs should be contiguous 1..{len(c.shots)}, got {shot_ids}"
            )

        # Validate onstage_characters reference valid char IDs
        valid_ids = set(char_ids)
        for shot in c.shots:
            for cid in shot.onstage_characters:
                if cid not in valid_ids:
                    errors.append(
                        f"shot {shot.id} references unknown character '{cid}'"
                    )

        return errors
