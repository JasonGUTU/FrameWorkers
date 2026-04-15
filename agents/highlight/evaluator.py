"""Evaluator for HighlightAgent output."""

from __future__ import annotations

import re

from ..base_evaluator import BaseEvaluator
from .schema import HighlightAgentOutput


class HighlightEvaluator(BaseEvaluator[HighlightAgentOutput]):

    creative_dimensions: list[tuple[str, str]] = []  # L2 skipped — structural checks are sufficient

    def check_structure(self, output: HighlightAgentOutput) -> list[str]:
        errors: list[str] = []
        c = output.content

        if not c.criteria:
            errors.append("criteria is empty — must state the selection criteria")

        if not c.clips:
            errors.append("clips list is empty — must select at least one highlight")
            return errors

        prev_end = -1.0
        prev_id_num = 0
        for i, clip in enumerate(c.clips):
            prefix = f"clips[{i}]"

            if not clip.clip_id:
                errors.append(f"{prefix}.clip_id is empty")
            else:
                m = re.match(r"^clip_(\d{3})$", clip.clip_id)
                if not m:
                    errors.append(
                        f"{prefix}.clip_id '{clip.clip_id}' does not match "
                        "clip_NNN format"
                    )
                else:
                    cur_num = int(m.group(1))
                    if cur_num <= prev_id_num:
                        errors.append(
                            f"{prefix}.clip_id '{clip.clip_id}' not strictly "
                            "increasing"
                        )
                    prev_id_num = cur_num

            if clip.end_time <= clip.start_time:
                errors.append(
                    f"{prefix}.end_time ({clip.end_time}) must be > "
                    f"start_time ({clip.start_time})"
                )

            duration = clip.end_time - clip.start_time
            if duration < 1.0:
                errors.append(
                    f"{prefix} duration ({duration:.1f}s) is too short — "
                    "minimum 1 second"
                )

            if clip.start_time < prev_end - 0.01:
                errors.append(
                    f"{prefix}.start_time ({clip.start_time}) overlaps "
                    f"previous clip end ({prev_end})"
                )
            prev_end = clip.end_time

            if not clip.reason:
                errors.append(f"{prefix}.reason is empty")

        da = c.compiled_video
        if da.asset_id != "highlight_reel":
            errors.append(
                f"compiled_video.asset_id must be 'highlight_reel', "
                f"got '{da.asset_id}'"
            )

        return errors
