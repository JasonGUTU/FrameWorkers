"""Evaluator for StoryAgent output (Story Blueprint).

Layers 1+2 only (no binary assets to evaluate).

Layer 1 — structural checks (output-internal only):
  - ID referential integrity (scene -> location, character, arc step)
  - Metrics consistency (character_count, location_count, scene_count)
  - Order continuity (story_arc, scene_outline)
  - Required content (logline, cast, scene_outline, story_arc)

Layer 2 — creative assessment (output-internal only):
  - dramatic: clear conflict, stakes, turning points, satisfying arc
  - coherence: characters, locations, scenes internally consistent

Evaluators do NOT cross-validate against upstream artifacts. Each layer
checks only the agent's own output for self-consistency.
"""

from __future__ import annotations

from ..base_evaluator import BaseEvaluator
from .schema import StoryAgentOutput


class StoryEvaluator(BaseEvaluator[StoryAgentOutput]):

    creative_dimensions = [
        ("dramatic", "Clear conflict, stakes, turning points, satisfying arc?"),
        ("coherence", "Characters, locations, scenes internally consistent and well-connected?"),
    ]

    # ------------------------------------------------------------------
    # Layer 1 — Rule-based structural validation
    # ------------------------------------------------------------------

    def check_structure(self, output: StoryAgentOutput) -> list[str]:
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

        # Hard cap to back the SCENE BUDGET section in the system prompt —
        # mirrors ScreenplayEvaluator's shot_total > 12 cap. Without this,
        # the prompt's "2-3 scenes default" is soft and the LLM drifts to
        # 6+ scenes uncapped, blowing up downstream cost (each scene
        # produces N shots → N keyframes → N video clips).
        scene_count = len(c.scene_outline)
        if scene_count > 3:
            errors.append(
                f"scene_count={scene_count} exceeds budget of 3 — "
                "consolidate fragments into fewer scenes carrying more "
                "dramatic weight (the SCENE BUDGET rule allows >3 only "
                "when the user explicitly asks for episodic / multi-act / "
                "long-form work)"
            )

        return errors

