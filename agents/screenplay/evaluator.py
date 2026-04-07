"""Evaluator for ScreenplayAgent output (unified screenplay + shots).

Layer 1 — structural checks (output-internal only):
  - Global unique shot_id; shot order continuity per scene
  - Dialogue-type shots: character_id + text
  - keyframe_plan.keyframe_count == 1 per shot
  - Metrics consistency
  - Non-empty scenes and shots

Layer 2 — creative assessment (output-internal only).

Evaluators do NOT cross-validate against upstream artifacts.
"""

from __future__ import annotations

from ..base_evaluator import BaseEvaluator
from .schema import ScreenplayAgentOutput


class ScreenplayEvaluator(BaseEvaluator[ScreenplayAgentOutput]):

    creative_dimensions = [
        (
            "character_consistency",
            "Are character voices distinct and consistent? Do shots honor who is on screen?",
        ),
        (
            "dramatic_flow",
            "Do dialogue/action and shot rhythm flow naturally? Effective scene turns?",
        ),
        (
            "visual_coherence",
            "Are shot types, camera choices, and visual goals coherent per scene?",
        ),
    ]

    def check_structure(self, output: ScreenplayAgentOutput) -> list[str]:
        errors: list[str] = []
        c = output.content

        all_shot_ids: list[str] = []
        for scene in c.scenes:
            for sh in scene.shots:
                all_shot_ids.append(sh.shot_id)
        dup = [sid for sid in all_shot_ids if all_shot_ids.count(sid) > 1]
        if dup:
            errors.append(f"duplicate shot_ids: {sorted(set(dup))}")

        for scene in c.scenes:
            for sh in scene.shots:
                if sh.block_type == "dialogue":
                    if not sh.character_id:
                        errors.append(
                            f"dialogue shot {sh.shot_id} missing character_id"
                        )
                    if not sh.text:
                        errors.append(
                            f"dialogue shot {sh.shot_id} has empty text"
                        )
                if sh.keyframe_plan.keyframe_count != 1:
                    errors.append(
                        f"shot {sh.shot_id} must have keyframe_count == 1 "
                        f"(got {sh.keyframe_plan.keyframe_count})"
                    )

        self._check_metric(errors, "scene_count", output.metrics.scene_count, len(c.scenes))
        shot_total = sum(len(s.shots) for s in c.scenes)
        self._check_metric(
            errors, "shot_count_total", output.metrics.shot_count_total, shot_total,
        )
        self._check_metric(
            errors, "dialogue_block_count", output.metrics.dialogue_block_count,
            sum(1 for s in c.scenes for sh in s.shots if sh.block_type == "dialogue"),
        )
        self._check_metric(
            errors, "action_block_count", output.metrics.action_block_count,
            sum(1 for s in c.scenes for sh in s.shots if sh.block_type == "action"),
        )

        self._check_order_continuous(errors, "scene", [s.order for s in c.scenes])
        for scene in c.scenes:
            self._check_order_continuous(
                errors, f"scene {scene.scene_id} shot",
                [sh.order for sh in scene.shots],
            )

        if not c.scenes:
            errors.append("scenes list is empty")
        for scene in c.scenes:
            if not scene.shots:
                errors.append(f"scene {scene.scene_id} has no shots")

        return errors
