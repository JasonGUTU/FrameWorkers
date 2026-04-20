"""Evaluator for CompositorAgent output."""

from __future__ import annotations

import re

from ..base_evaluator import BaseEvaluator
from .schema import CompositorAgentOutput


_RESOLUTION_RE = re.compile(r"^\d{3,5}x\d{3,5}$")


class CompositorEvaluator(BaseEvaluator[CompositorAgentOutput]):

    creative_dimensions: list[tuple[str, str]] = []  # no L2 — tool agent, not creative

    def check_structure(self, output: CompositorAgentOutput) -> list[str]:
        errors: list[str] = []
        plan = output.content.plan

        # Transitions
        valid_types = {"cut", "crossfade", "fade_black", "wipe"}
        for i, t in enumerate(plan.transitions):
            prefix = f"transitions[{i}]"
            if not t.from_shot_id:
                errors.append(f"{prefix}.from_shot_id is empty")
            if not t.to_shot_id:
                errors.append(f"{prefix}.to_shot_id is empty")
            if t.transition_type not in valid_types:
                errors.append(
                    f"{prefix}.transition_type '{t.transition_type}' must be "
                    f"one of {valid_types}"
                )
            if t.transition_type != "cut" and t.duration_ms <= 0:
                errors.append(
                    f"{prefix}.duration_ms must be > 0 for non-cut transitions"
                )

        # Resolution
        if not _RESOLUTION_RE.match(plan.output_resolution):
            errors.append(
                f"output_resolution '{plan.output_resolution}' does not match "
                "WxH format (e.g. 1920x1080)"
            )

        # FPS
        if plan.output_fps < 1 or plan.output_fps > 120:
            errors.append(
                f"output_fps {plan.output_fps} is out of range (1-120)"
            )

        # Color grade bounds
        cg = plan.color_grade
        for field_name in ("brightness", "contrast", "saturation"):
            val = getattr(cg, field_name)
            if val < -1.0 or val > 1.0:
                errors.append(
                    f"color_grade.{field_name} ({val}) out of range [-1.0, 1.0]"
                )

        return errors
