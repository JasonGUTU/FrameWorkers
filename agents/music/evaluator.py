"""Evaluator for MusicAgent output."""

from __future__ import annotations

from ..base_evaluator import BaseEvaluator
from .schema import MusicAgentOutput


class MusicEvaluator(BaseEvaluator[MusicAgentOutput]):

    creative_dimensions: list[tuple[str, str]] = []

    def check_structure(self, output: MusicAgentOutput) -> list[str]:
        errors: list[str] = []
        if not output.content.cues:
            errors.append("cues list is empty")
            return errors
        for i, cue in enumerate(output.content.cues):
            p = f"cues[{i}]"
            if not cue.cue_id:
                errors.append(f"{p}.cue_id is empty")
            if not cue.scene_id:
                errors.append(f"{p}.scene_id is empty")
            if not cue.mood:
                errors.append(f"{p}.mood is empty")
        return errors
