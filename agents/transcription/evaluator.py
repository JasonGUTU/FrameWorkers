"""Evaluator for TranscriptionAgent output."""

from __future__ import annotations

import re

from ..base_evaluator import BaseEvaluator
from .schema import TranscriptionAgentOutput


class TranscriptionEvaluator(BaseEvaluator[TranscriptionAgentOutput]):

    creative_dimensions: list[tuple[str, str]] = []  # no L2 — tool agent, not creative

    def check_structure(self, output: TranscriptionAgentOutput) -> list[str]:
        errors: list[str] = []
        c = output.content

        if not c.language:
            errors.append("language is empty — must detect source language")

        if not c.segments:
            errors.append("segments list is empty — no transcription produced")
            return errors

        if not c.full_text.strip():
            errors.append("full_text is empty")

        prev_end = -1.0
        prev_id_num = 0
        for i, seg in enumerate(c.segments):
            prefix = f"segments[{i}]"

            if not seg.segment_id:
                errors.append(f"{prefix}.segment_id is empty")
            else:
                m = re.match(r"^seg_(\d{3})$", seg.segment_id)
                if not m:
                    errors.append(
                        f"{prefix}.segment_id '{seg.segment_id}' does not "
                        "match seg_NNN format"
                    )
                else:
                    cur_num = int(m.group(1))
                    if cur_num <= prev_id_num:
                        errors.append(
                            f"{prefix}.segment_id '{seg.segment_id}' is not "
                            "strictly increasing"
                        )
                    prev_id_num = cur_num

            if seg.start_time < 0:
                errors.append(f"{prefix}.start_time is negative")

            if seg.end_time <= seg.start_time:
                errors.append(
                    f"{prefix}.end_time ({seg.end_time}) must be > "
                    f"start_time ({seg.start_time})"
                )

            if seg.start_time < prev_end - 0.01:
                errors.append(
                    f"{prefix}.start_time ({seg.start_time}) overlaps "
                    f"previous segment end ({prev_end})"
                )
            prev_end = seg.end_time

            if not seg.text.strip():
                errors.append(f"{prefix}.text is empty")

        return errors
