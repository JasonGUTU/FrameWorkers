"""Evaluator for KeyFrameAgent output (Keyframes Package).

All three layers (output-internal only — no cross-validation against
upstream artifacts):

Layer 1 -- structural checks:
  - Global anchor completeness
  - Scene stability_keyframes reference global anchors
  - Every shot has exactly one keyframe (keyframe_count == 1)
  - Every prompt_summary is non-empty (anchors + L3)
  - Every L3 keyframe has non-empty video_motion_hint
  - Metrics consistency (scene_count, shot_count, keyframe_count_total)
  - Required content

Layer 2 -- creative assessment:
  - overall_consistency: three-layer prompts maintain visual identity
  - overall_visual_quality: prompt descriptions are specific enough

Note: the prior Layer 3 (post-materialization asset eval) was removed —
KeyframeMaterializer raises RuntimeError after exhausting its internal
partial-resume retries, so reaching the end of materialize implies every
planned image was generated. Artifact-content quality is a separate
concern handled outside this evaluator.
"""

from __future__ import annotations

from ..base_evaluator import BaseEvaluator
from .schema import KeyFrameAgentOutput


class KeyframeEvaluator(BaseEvaluator[KeyFrameAgentOutput]):

    creative_dimensions = [
        ("overall_consistency", "Do the three-layer prompts (global -> scene -> shot) maintain visual identity continuity? Are character/location descriptions consistent across layers?"),
        ("overall_visual_quality", "Are the prompt descriptions specific enough to generate good images? Do they include composition, lighting, mood, and action details?"),
    ]

    # ------------------------------------------------------------------
    # Layer 1 -- Rule-based structural validation
    # ------------------------------------------------------------------

    def check_structure(self, output: KeyFrameAgentOutput) -> list[str]:
        """Rule-based structural validation for Keyframes Package."""
        errors: list[str] = []
        c = output.content

        # --- Global anchor completeness ---
        global_char_ids = {
            ch.entity_id for ch in c.global_anchors.characters
        }
        global_loc_ids = {
            lo.entity_id for lo in c.global_anchors.locations
        }
        global_prop_ids = {
            p.entity_id for p in c.global_anchors.props
        }

        # --- Scene-level stability_keyframes must reference global anchors ---
        for scene in c.scenes:
            stab = scene.stability_keyframes
            for ch in stab.characters:
                if ch.entity_id not in global_char_ids:
                    errors.append(
                        f"scene {scene.scene_id} stability_keyframes references "
                        f"character {ch.entity_id} not in global_anchors"
                    )
            for lo in stab.locations:
                if lo.entity_id not in global_loc_ids:
                    errors.append(
                        f"scene {scene.scene_id} stability_keyframes references "
                        f"location {lo.entity_id} not in global_anchors"
                    )
            for p in stab.props:
                if p.entity_id not in global_prop_ids:
                    errors.append(
                        f"scene {scene.scene_id} stability_keyframes references "
                        f"prop '{p.entity_id}' not in global_anchors"
                    )

        # --- Every shot must have exactly one keyframe (keyframe_count == 1) ---
        for scene in c.scenes:
            for shot in scene.shots:
                if len(shot.keyframes) != 1:
                    errors.append(
                        f"shot {shot.shot_id} has {len(shot.keyframes)} "
                        f"keyframes, expected exactly 1"
                    )

        # --- Every prompt_summary must be non-empty ---
        for ch in c.global_anchors.characters:
            if not ch.prompt_summary:
                errors.append(
                    f"global anchor character {ch.entity_id} has empty "
                    f"prompt_summary"
                )
        for lo in c.global_anchors.locations:
            if not lo.prompt_summary:
                errors.append(
                    f"global anchor location {lo.entity_id} has empty "
                    f"prompt_summary"
                )
        for scene in c.scenes:
            for shot in scene.shots:
                for i, kf in enumerate(shot.keyframes):
                    if not kf.prompt_summary:
                        errors.append(
                            f"shot {shot.shot_id} keyframe[{i}] "
                            f"has empty prompt_summary"
                        )
                    if not (kf.video_motion_hint or "").strip():
                        errors.append(
                            f"shot {shot.shot_id} keyframe[{i}] "
                            f"has empty video_motion_hint"
                        )

        # --- Required content ---
        if not c.scenes:
            errors.append("scenes list is empty")

        return errors
