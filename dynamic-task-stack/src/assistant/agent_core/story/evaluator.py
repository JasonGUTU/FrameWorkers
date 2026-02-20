"""Evaluator for StoryAgent output (Story Blueprint).

Layers 1+2 only (no binary assets to evaluate).

Layer 1 — structural checks:
  - ID referential integrity (scene -> location, character, arc step)
  - Metrics consistency (character_count, location_count, scene_count)
  - Order continuity (story_arc, scene_outline)
  - Required content (logline, cast, scene_outline, story_arc)

Layer 2 — creative assessment:
  - alignment: blueprint faithfully expands the draft idea
  - dramatic: clear conflict, stakes, turning points, satisfying arc
  - coherence: characters, locations, scenes internally consistent
"""

from __future__ import annotations

from typing import Any

from ..base_evaluator import BaseEvaluator
from .schema import StoryAgentOutput


class StoryEvaluator(BaseEvaluator[StoryAgentOutput]):

    creative_dimensions = [
        ("alignment", "Does the blueprint faithfully expand the draft idea?"),
        ("dramatic", "Clear conflict, stakes, turning points, satisfying arc?"),
        ("coherence", "Characters, locations, scenes internally consistent and well-connected?"),
    ]

    def _build_creative_context(self, output, upstream):
        draft_idea = (upstream or {}).get("draft_idea", "")
        return f"Draft idea: {draft_idea}"

    # ------------------------------------------------------------------
    # Layer 1 — Rule-based structural validation
    # ------------------------------------------------------------------

    def check_structure(
        self,
        output: StoryAgentOutput,
        upstream: dict[str, Any] | None = None,
    ) -> list[str]:
        """Rule-based structural validation for Story Blueprint."""
        errors: list[str] = []
        c = output.content

        # --- ID referential integrity ---
        char_ids = {m.character_id for m in c.cast}
        loc_ids = {loc.location_id for loc in c.locations}
        arc_ids = {s.step_id for s in c.story_arc}

        for scene in c.scene_outline:
            if scene.location_id and scene.location_id not in loc_ids:
                errors.append(
                    f"scene {scene.scene_id} references unknown location "
                    f"{scene.location_id}"
                )
            if scene.linked_step_id and scene.linked_step_id not in arc_ids:
                errors.append(
                    f"scene {scene.scene_id} references unknown arc step "
                    f"{scene.linked_step_id}"
                )
            for cid in scene.characters_present:
                if cid not in char_ids:
                    errors.append(
                        f"scene {scene.scene_id} references unknown character "
                        f"{cid}"
                    )

        # --- Metrics consistency ---
        self._check_metric(errors, "character_count", output.metrics.character_count, len(c.cast))
        self._check_metric(errors, "location_count", output.metrics.location_count, len(c.locations))
        self._check_metric(errors, "scene_count", output.metrics.scene_count, len(c.scene_outline))

        # --- Order continuity ---
        self._check_order_continuous(errors, "story_arc", [s.order for s in c.story_arc])
        self._check_order_continuous(errors, "scene_outline", [s.order for s in c.scene_outline])

        # --- Required content ---
        if not c.logline:
            errors.append("logline is empty")
        if not c.cast:
            errors.append("cast is empty")
        if not c.scene_outline:
            errors.append("scene_outline is empty")
        if not c.story_arc:
            errors.append("story_arc is empty")

        return errors

