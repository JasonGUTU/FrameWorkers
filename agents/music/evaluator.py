"""Evaluator for MusicAgent output — exactly one film-wide cue."""

from __future__ import annotations

from ..base_evaluator import BaseEvaluator
from .schema import MusicAgentOutput


class MusicEvaluator(BaseEvaluator[MusicAgentOutput]):

    creative_dimensions: list[tuple[str, str]] = []

    def check_structure(self, output: MusicAgentOutput) -> list[str]:
        errors: list[str] = []
        cues = output.content.cues
        if not cues:
            errors.append("cues list is empty")
            return errors
        if len(cues) != 1:
            errors.append(
                f"MusicAgent must emit exactly one film-wide cue; got "
                f"{len(cues)}. Collapse scene-specific cues into a single "
                "global BGM bed."
            )
        for i, cue in enumerate(cues):
            p = f"cues[{i}]"
            if not cue.cue_id:
                errors.append(f"{p}.cue_id is empty")
            if not cue.mood:
                errors.append(f"{p}.mood is empty")
        return errors
