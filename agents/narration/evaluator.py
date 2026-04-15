"""Evaluator for NarrationAgent output."""

from __future__ import annotations

import re

from ..base_evaluator import BaseEvaluator
from .schema import NarrationAgentOutput


class NarrationEvaluator(BaseEvaluator[NarrationAgentOutput]):

    creative_dimensions: list[tuple[str, str]] = []

    def check_structure(self, output: NarrationAgentOutput) -> list[str]:
        errors: list[str] = []
        if not output.content.segments:
            # Valid when screenplay is all-action with no dialogue/narration.
            return errors

        prev = 0
        for i, seg in enumerate(output.content.segments):
            p = f"segments[{i}]"
            if not seg.segment_id:
                errors.append(f"{p}.segment_id is empty")
            else:
                m = re.match(r"^narr_(\d{3})$", seg.segment_id)
                if not m:
                    errors.append(f"{p}.segment_id '{seg.segment_id}' not narr_NNN")
                elif int(m.group(1)) <= prev:
                    errors.append(f"{p}.segment_id not increasing")
                else:
                    prev = int(m.group(1))
            if not seg.text.strip():
                errors.append(f"{p}.text is empty")
            if not seg.linked_shot_id:
                errors.append(f"{p}.linked_shot_id is empty")
        return errors
