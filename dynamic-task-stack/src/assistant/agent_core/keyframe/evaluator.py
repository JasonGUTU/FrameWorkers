"""Evaluator for KeyFrameAgent output (Keyframes Package).

All three layers:

Layer 1 -- structural checks:
  - Global anchor completeness
  - Scene stability_keyframes reference global anchors
  - Upstream cross-check (scene/shot IDs match storyboard)
  - Every shot has at least 1 keyframe
  - Every prompt_summary is non-empty
  - Metrics consistency (scene_count, shot_count, keyframe_count_total)
  - Required content

Layer 2 -- creative assessment:
  - overall_consistency: three-layer prompts maintain visual identity
  - overall_visual_quality: prompt descriptions are specific enough

Layer 3 -- post-materialization asset checks:
  - image_generation_success: success rate across all layers
  - image_format_compliance: (TODO) file header / resolution check
  - visual_consistency: (TODO) vision-model cross-layer comparison
"""

from __future__ import annotations

import json
from typing import Any

from ..base_evaluator import BaseEvaluator, check_uri
from .schema import KeyFrameAgentOutput


class KeyframeEvaluator(BaseEvaluator[KeyFrameAgentOutput]):

    creative_dimensions = [
        ("overall_consistency", "Do the three-layer prompts (global -> scene -> shot) maintain visual identity continuity? Are character/location descriptions consistent across layers?"),
        ("overall_visual_quality", "Are the prompt descriptions specific enough to generate good images? Do they include composition, lighting, mood, and action details?"),
    ]

    def _build_creative_context(self, output, upstream):
        sb_data = (upstream or {}).get("storyboard", {})
        if sb_data:
            return f"Storyboard:\n{json.dumps(sb_data, ensure_ascii=False, indent=2)}"
        return ""

    # ------------------------------------------------------------------
    # Layer 1 -- Rule-based structural validation
    # ------------------------------------------------------------------

    def check_structure(
        self,
        output: KeyFrameAgentOutput,
        upstream: dict[str, Any] | None = None,
    ) -> list[str]:
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

        # --- Upstream cross-check: scene/shot IDs must match storyboard ---
        if upstream and "storyboard" in upstream:
            sb_content = upstream["storyboard"].get("content", {})
            sb_scene_ids = {
                s.get("scene_id", "") for s in sb_content.get("scenes", [])
            }
            kf_scene_ids = {s.scene_id for s in c.scenes}
            self._check_id_coverage(
                errors, "keyframes vs storyboard scenes",
                sb_scene_ids, kf_scene_ids,
            )

            sb_shot_ids: set[str] = set()
            for sb_scene in sb_content.get("scenes", []):
                for shot in sb_scene.get("shots", []):
                    sb_shot_ids.add(shot.get("shot_id", ""))
            kf_shot_ids = {
                shot.shot_id for scene in c.scenes for shot in scene.shots
            }
            self._check_id_coverage(
                errors, "keyframes vs storyboard shots",
                sb_shot_ids, kf_shot_ids,
            )

        # --- Every shot must have at least 1 keyframe ---
        for scene in c.scenes:
            for shot in scene.shots:
                if not shot.keyframes:
                    errors.append(
                        f"shot {shot.shot_id} has no keyframes"
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
                for kf in shot.keyframes:
                    if not kf.prompt_summary:
                        errors.append(
                            f"shot {shot.shot_id} keyframe {kf.keyframe_id} "
                            f"has empty prompt_summary"
                        )

        # --- Metrics consistency ---
        self._check_metric(errors, "scene_count", output.metrics.scene_count, len(c.scenes))
        self._check_metric(errors, "shot_count", output.metrics.shot_count, sum(len(s.shots) for s in c.scenes))
        self._check_metric(
            errors, "keyframe_count_total", output.metrics.keyframe_count_total,
            sum(len(sh.keyframes) for s in c.scenes for sh in s.shots),
        )

        # --- Required content ---
        if not c.scenes:
            errors.append("scenes list is empty")

        return errors

    # ------------------------------------------------------------------
    # Layer 3 -- Post-materialization asset evaluation
    # ------------------------------------------------------------------

    async def evaluate_asset(
        self,
        asset_data: dict[str, Any],
        upstream: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Check that the three-layer image pipeline produced actual images."""
        content = asset_data.get("content", {})
        scenes = content.get("scenes", [])
        global_anchors = content.get("global_anchors", {})

        total_planned = 0
        total_success = 0
        total_error = 0

        # --- Layer 1: global anchors ---
        for entity_list in [
            global_anchors.get("characters", []),
            global_anchors.get("locations", []),
            global_anchors.get("props", []),
        ]:
            for kf in entity_list:
                uri = kf.get("image_asset", {}).get("uri", "")
                total_planned += 1
                status = check_uri(uri)
                if status == "success":
                    total_success += 1
                elif status == "error":
                    total_error += 1

        # --- Layer 2: scene stability keyframes ---
        for scene in scenes:
            stab = scene.get("stability_keyframes", {})
            for entity_list in [
                stab.get("characters", []),
                stab.get("locations", []),
                stab.get("props", []),
            ]:
                for kf in entity_list:
                    uri = kf.get("image_asset", {}).get("uri", "")
                    total_planned += 1
                    status = check_uri(uri)
                    if status == "success":
                        total_success += 1
                    elif status == "error":
                        total_error += 1

        # --- Layer 3: shot keyframes ---
        for scene in scenes:
            for shot in scene.get("shots", []):
                for kf in shot.get("keyframes", []):
                    uri = kf.get("image_asset", {}).get("uri", "")
                    total_planned += 1
                    status = check_uri(uri)
                    if status == "success":
                        total_success += 1
                    elif status == "error":
                        total_error += 1

        # --- Compute scores ---
        success_rate = total_success / total_planned if total_planned else 0.0

        dimensions = {
            "image_generation_success": {
                "score": success_rate,
                "notes": [
                    f"{total_success}/{total_planned} images generated",
                    *(
                        [f"{total_error} images failed with errors"]
                        if total_error
                        else []
                    ),
                ],
            },
            "image_format_compliance": {
                "score": 1.0,
                "notes": ["format compliance check not yet implemented"],
            },
            "visual_consistency": {
                "score": 1.0,
                "notes": ["visual consistency check not yet implemented"],
            },
        }

        overall_pass = success_rate >= self.ASSET_PASS_THRESHOLD
        summary = (
            f"Keyframe asset eval: {total_success}/{total_planned} images "
            f"generated ({success_rate:.0%} success rate)."
        )
        if total_error:
            summary += f" {total_error} had generation errors."

        return {
            "dimensions": dimensions,
            "overall_pass": overall_pass,
            "summary": summary,
        }
