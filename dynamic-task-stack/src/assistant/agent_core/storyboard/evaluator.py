"""Evaluator for StoryboardAgent output (Storyboard).

Layers 1+2 only (no binary assets to evaluate).

Layer 1 — structural checks:
  - Upstream cross-check (scene_ids match screenplay)
  - Shot ID uniqueness (global across all scenes)
  - linked_blocks reference existing block IDs from screenplay
  - Metrics consistency (scene_count, shot_count_total)
  - Shot order continuity per scene
  - keyframe_plan.keyframe_count >= 1 per shot
  - Required content (non-empty scenes and shots)

Layer 2 — creative assessment:
  - coverage_of_blocks: shots cover all important screenplay blocks
  - visual_coherence: consistent shot types, camera angles, visual goals
  - pacing_fit: appropriate pacing via shot durations and counts
"""

from __future__ import annotations

import json
from typing import Any

from ..base_evaluator import BaseEvaluator
from .schema import StoryboardAgentOutput


class StoryboardEvaluator(BaseEvaluator[StoryboardAgentOutput]):

    creative_dimensions = [
        ("coverage_of_blocks", "Do the shots cover all important screenplay blocks? Are any key moments missed?"),
        ("visual_coherence", "Are shot types, camera angles, and visual goals consistent within each scene?"),
        ("pacing_fit", "Do shot durations and shot count create appropriate pacing? Not too fast, not too slow?"),
    ]

    def _build_creative_context(self, output, upstream):
        sp_data = (upstream or {}).get("screenplay", {})
        if sp_data:
            return f"Screenplay:\n{json.dumps(sp_data, ensure_ascii=False, indent=2)}"
        return ""

    # ------------------------------------------------------------------
    # Layer 1 — Rule-based structural validation
    # ------------------------------------------------------------------

    def check_structure(
        self,
        output: StoryboardAgentOutput,
        upstream: dict[str, Any] | None = None,
    ) -> list[str]:
        """Rule-based structural validation for Storyboard."""
        errors: list[str] = []
        c = output.content

        # --- Upstream cross-check: scene_ids must match screenplay ---
        if upstream and "screenplay" in upstream:
            sp_content = upstream["screenplay"].get("content", {})
            sp_scene_ids = {
                s.get("scene_id", "") for s in sp_content.get("scenes", [])
            }
            sb_scene_ids = {s.scene_id for s in c.scenes}
            self._check_id_coverage(
                errors, "storyboard vs screenplay scenes",
                sp_scene_ids, sb_scene_ids,
            )

        # --- Shot ID uniqueness (global across all scenes) ---
        all_shot_ids: list[str] = []
        for scene in c.scenes:
            for shot in scene.shots:
                all_shot_ids.append(shot.shot_id)
        dup_shots = [sid for sid in all_shot_ids if all_shot_ids.count(sid) > 1]
        if dup_shots:
            errors.append(f"duplicate shot_ids: {sorted(set(dup_shots))}")

        # --- linked_blocks must reference existing block IDs from screenplay ---
        if upstream and "screenplay" in upstream:
            sp_content = upstream["screenplay"].get("content", {})
            all_block_ids: set[str] = set()
            for sp_scene in sp_content.get("scenes", []):
                for block in sp_scene.get("blocks", []):
                    all_block_ids.add(block.get("block_id", ""))
            for scene in c.scenes:
                for shot in scene.shots:
                    for bid in shot.linked_blocks:
                        if bid and bid not in all_block_ids:
                            errors.append(
                                f"shot {shot.shot_id} references unknown "
                                f"block {bid}"
                            )

        # --- Metrics consistency ---
        self._check_metric(errors, "scene_count", output.metrics.scene_count, len(c.scenes))
        self._check_metric(
            errors, "shot_count_total", output.metrics.shot_count_total,
            sum(len(s.shots) for s in c.scenes),
        )

        # --- Shot order continuity per scene ---
        for scene in c.scenes:
            self._check_order_continuous(
                errors, f"scene {scene.scene_id} shot",
                [sh.order for sh in scene.shots],
            )

        # --- Required: every shot needs keyframe_plan.keyframe_count >= 1 ---
        for scene in c.scenes:
            for shot in scene.shots:
                if shot.keyframe_plan.keyframe_count < 1:
                    errors.append(
                        f"shot {shot.shot_id} has keyframe_count < 1"
                    )

        # --- Required content ---
        if not c.scenes:
            errors.append("scenes list is empty")
        for scene in c.scenes:
            if not scene.shots:
                errors.append(f"scene {scene.scene_id} has no shots")

        return errors

