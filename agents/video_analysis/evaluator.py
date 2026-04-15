"""Evaluator for VideoAnalysisAgent output."""

from __future__ import annotations

import re

from ..base_evaluator import BaseEvaluator
from .schema import VideoAnalysisAgentOutput


class VideoAnalysisEvaluator(BaseEvaluator[VideoAnalysisAgentOutput]):

    creative_dimensions: list[tuple[str, str]] = []  # L2 skipped — structural checks are sufficient

    def check_structure(self, output: VideoAnalysisAgentOutput) -> list[str]:
        errors: list[str] = []
        c = output.content

        # Summary checks
        s = c.video_summary
        if not s.title:
            errors.append("video_summary.title is empty")
        if not s.summary:
            errors.append("video_summary.summary is empty")
        if not s.genre:
            errors.append("video_summary.genre is empty")

        # Scene checks
        if not c.scenes:
            errors.append("scenes list is empty — must have at least one scene")
            return errors

        prev_end = -1.0
        prev_id_num = 0
        for i, scene in enumerate(c.scenes):
            prefix = f"scenes[{i}]"

            if not scene.scene_id:
                errors.append(f"{prefix}.scene_id is empty")
            else:
                m = re.match(r"^scene_(\d{3})$", scene.scene_id)
                if not m:
                    errors.append(
                        f"{prefix}.scene_id '{scene.scene_id}' does not "
                        "match scene_NNN format"
                    )
                else:
                    cur_num = int(m.group(1))
                    if cur_num <= prev_id_num:
                        errors.append(
                            f"{prefix}.scene_id '{scene.scene_id}' not "
                            "strictly increasing"
                        )
                    prev_id_num = cur_num

            if scene.end_time <= scene.start_time:
                errors.append(
                    f"{prefix}.end_time ({scene.end_time}) must be > "
                    f"start_time ({scene.start_time})"
                )

            if scene.start_time < prev_end - 0.5:
                errors.append(
                    f"{prefix}.start_time ({scene.start_time}) significantly "
                    f"overlaps previous scene end ({prev_end})"
                )
            prev_end = scene.end_time

            if not scene.description:
                errors.append(f"{prefix}.description is empty")

        return errors
