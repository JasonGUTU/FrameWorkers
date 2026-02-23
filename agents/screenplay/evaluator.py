"""Evaluator for ScreenplayAgent output (Screenplay).

Layers 1+2 only (no binary assets to evaluate).

Layer 1 — structural checks:
  - Upstream cross-check (scene_ids match story_blueprint)
  - Block ID uniqueness
  - Dialogue blocks have character_id + text
  - Metrics consistency (scene_count, dialogue/action block counts)
  - Scene order continuity
  - Required content (non-empty scenes and blocks)

Layer 2 — creative assessment:
  - alignment_with_story: screenplay faithfully realizes the story blueprint
  - character_consistency: distinct, consistent character voices
  - dramatic_flow: natural dialogue/action flow with effective scene turns
"""

from __future__ import annotations

import json
from typing import Any

from ..base_evaluator import BaseEvaluator
from .schema import ScreenplayAgentOutput


class ScreenplayEvaluator(BaseEvaluator[ScreenplayAgentOutput]):

    creative_dimensions = [
        ("alignment_with_story", "Does the screenplay faithfully realize the story blueprint's intent, arc, and scene goals?"),
        ("character_consistency", "Are character voices distinct and consistent with their profiles, motivations, and flaws?"),
        ("dramatic_flow", "Does the dialogue/action flow naturally? Are scene turns and emotional shifts effective?"),
    ]

    def _build_creative_context(self, output, upstream):
        story_data = (upstream or {}).get("story_blueprint", {})
        if story_data:
            return f"Story Blueprint:\n{json.dumps(story_data, ensure_ascii=False, indent=2)}"
        return ""

    # ------------------------------------------------------------------
    # Layer 1 — Rule-based structural validation
    # ------------------------------------------------------------------

    def check_structure(
        self,
        output: ScreenplayAgentOutput,
        upstream: dict[str, Any] | None = None,
    ) -> list[str]:
        """Rule-based structural validation for Screenplay."""
        errors: list[str] = []
        c = output.content

        # --- Upstream cross-check: scene_ids must match story_blueprint ---
        bp = (upstream or {}).get("story_blueprint", {})
        bp_content = bp.get("content", {}) if isinstance(bp, dict) else {}
        bp_scenes = bp_content.get("scene_outline", [])
        if bp_scenes:
            story_scene_ids = {s.get("scene_id", "") for s in bp_scenes}
            sp_scene_ids = {s.scene_id for s in c.scenes}
            self._check_id_coverage(
                errors, "screenplay vs story_blueprint scenes",
                story_scene_ids, sp_scene_ids,
            )

        # --- Block ID uniqueness ---
        all_block_ids: list[str] = []
        for scene in c.scenes:
            for block in scene.blocks:
                all_block_ids.append(block.block_id)
        dup_blocks = [
            bid for bid in all_block_ids if all_block_ids.count(bid) > 1
        ]
        if dup_blocks:
            errors.append(f"duplicate block_ids: {sorted(set(dup_blocks))}")

        # --- Dialogue blocks must have character_id + text ---
        for scene in c.scenes:
            for block in scene.blocks:
                if block.block_type == "dialogue":
                    if not block.character_id:
                        errors.append(
                            f"dialogue block {block.block_id} missing character_id"
                        )
                    if not block.text:
                        errors.append(
                            f"dialogue block {block.block_id} has empty text"
                        )

        # --- Metrics consistency ---
        self._check_metric(errors, "scene_count", output.metrics.scene_count, len(c.scenes))
        self._check_metric(
            errors, "dialogue_block_count", output.metrics.dialogue_block_count,
            sum(1 for s in c.scenes for b in s.blocks if b.block_type == "dialogue"),
        )
        self._check_metric(
            errors, "action_block_count", output.metrics.action_block_count,
            sum(1 for s in c.scenes for b in s.blocks if b.block_type == "action"),
        )

        # --- Scene order continuity ---
        self._check_order_continuous(errors, "scene", [s.order for s in c.scenes])

        # --- Required content ---
        if not c.scenes:
            errors.append("scenes list is empty")
        for scene in c.scenes:
            if not scene.blocks:
                errors.append(f"scene {scene.scene_id} has no blocks")

        return errors

