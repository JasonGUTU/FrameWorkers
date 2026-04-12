"""Evaluator for VideoAgent output (Video Package).

All three layers (output-internal only — no cross-validation against
upstream artifacts):

Layer 1 -- structural checks:
  - shot_id format ``^sh_\\d{3}$`` and global-sequential numbering
    (sh_001, sh_002, … across the whole video package, no gaps, no
    restarts at scene boundaries). These are owned by the LLM via the
    template + system prompt and enforced here so rework surfaces any
    drift instead of a silent Python-side patch-up.
  - Transition plan from/to shot_ids exist in scene
  - Metrics consistency (scene_count, shot_segment_count)
  - Shot order continuity per scene (1, 2, 3, … per scene)
  - Temporal/transition validation (type)
  - Required content (non-empty scenes and shot_segments)

Layer 2 -- creative assessment:
  Not applicable. VideoAgent output is entirely structural (IDs,
  asset pointers, transition types, mirrored semantic_context). All
  quality dimensions that matter are checked in Layer 1 (structural)
  or Layer 3 (asset).

Layer 3 -- post-materialization asset checks:
  - clip_generation_success: shot-level clip success rate
  - assembly_completeness: scene clips + final video
  - motion_quality: (TODO) video analysis model
"""

from __future__ import annotations

import re
from typing import Any

from ..base_evaluator import BaseEvaluator, check_uri
from .schema import VideoAgentOutput


_SHOT_ID_PATTERN = re.compile(r"^sh_\d{3}$")


class VideoEvaluator(BaseEvaluator[VideoAgentOutput]):

    # ------------------------------------------------------------------
    # Layer 1 -- Rule-based structural validation
    # ------------------------------------------------------------------

    def check_structure(self, output: VideoAgentOutput) -> list[str]:
        """Rule-based structural validation for Video Package."""
        errors: list[str] = []
        c = output.content

        # --- Shot id format + global sequential numbering ---
        # Mirror of screenplay's contract: sh_001, sh_002, … across the
        # whole video package, no gaps, no restarts at scene boundaries.
        all_shot_ids: list[str] = []
        format_ok = True
        for scene in c.scenes:
            for seg in scene.shot_segments:
                sid = seg.shot_id or ""
                all_shot_ids.append(sid)
                if not _SHOT_ID_PATTERN.match(sid):
                    errors.append(
                        f"shot_id {sid!r} does not match required format "
                        f"^sh_NNN$ (e.g. sh_001, sh_002, sh_012)"
                    )
                    format_ok = False
        if format_ok and all_shot_ids:
            expected = [f"sh_{i:03d}" for i in range(1, len(all_shot_ids) + 1)]
            if all_shot_ids != expected:
                errors.append(
                    "shot_ids must be globally sequential starting at sh_001 "
                    f"with no gaps or restarts; got {all_shot_ids!r}"
                )

        # --- Transition plan: from/to shot_ids must exist in the scene ---
        for scene in c.scenes:
            scene_shot_ids = {seg.shot_id for seg in scene.shot_segments}
            for tr in scene.transition_plan:
                if tr.from_shot_id and tr.from_shot_id not in scene_shot_ids:
                    errors.append(
                        f"scene {scene.scene_id} transition references unknown "
                        f"from_shot_id {tr.from_shot_id}"
                    )
                if tr.to_shot_id and tr.to_shot_id not in scene_shot_ids:
                    errors.append(
                        f"scene {scene.scene_id} transition references unknown "
                        f"to_shot_id {tr.to_shot_id}"
                    )

        # --- Metrics consistency ---
        self._check_metric(errors, "scene_count", output.metrics.scene_count, len(c.scenes))
        self._check_metric(
            errors, "shot_segment_count", output.metrics.shot_segment_count,
            sum(len(s.shot_segments) for s in c.scenes),
        )

        # --- Shot order continuity per scene ---
        for scene in c.scenes:
            self._check_order_continuous(
                errors, f"scene {scene.scene_id} shot_segment",
                [seg.order for seg in scene.shot_segments],
            )

        # --- Temporal / transition checks ---
        VALID_TRANSITIONS = {"cut", "dissolve", "fade", "soft"}
        for scene in c.scenes:
            for tr in scene.transition_plan:
                if tr.transition_type and tr.transition_type not in VALID_TRANSITIONS:
                    errors.append(
                        f"scene {scene.scene_id} transition has unknown type "
                        f"'{tr.transition_type}'"
                    )

        # --- Required content ---
        if not c.scenes:
            errors.append("scenes list is empty")
        for scene in c.scenes:
            if not scene.shot_segments:
                errors.append(
                    f"scene {scene.scene_id} has no shot_segments"
                )

        return errors

    # Note: evaluate_creative is intentionally NOT overridden.
    # VideoAgent output is entirely structural (IDs, asset pointers,
    # transition types).  All quality dimensions that matter are checked
    # in Layer 1 (structural) or Layer 3 (asset).

    # ------------------------------------------------------------------
    # Layer 3 -- Post-materialization asset evaluation
    # ------------------------------------------------------------------

    async def evaluate_asset(
        self,
        asset_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Check that shot clips, scene clips, and final video were generated."""
        content = asset_data.get("content", {})
        scenes = content.get("scenes", [])

        total_clips_planned = 0
        total_clips_success = 0
        total_clips_error = 0

        # --- Shot clips ---
        for scene in scenes:
            for seg in scene.get("shot_segments", []):
                uri = seg.get("video_asset", {}).get("uri", "")
                total_clips_planned += 1
                status = check_uri(uri)
                if status == "success":
                    total_clips_success += 1
                elif status == "error":
                    total_clips_error += 1

        # --- Scene clips ---
        scene_clips_planned = 0
        scene_clips_success = 0
        for scene in scenes:
            clip = scene.get("scene_clip_asset", {})
            if clip:
                scene_clips_planned += 1
                uri = clip.get("uri", "")
                if check_uri(uri) == "success":
                    scene_clips_success += 1

        # --- Final video ---
        final = content.get("final_video_asset", {})
        final_ok = check_uri(final.get("uri", "")) == "success"

        # --- Compute scores ---
        # Vacuous case: empty plan → 1.0 (nothing to fail). A real "no
        # shots were planned" failure should be caught upstream by the
        # structural L1 check, not here.
        clip_success_rate = (
            total_clips_success / total_clips_planned
            if total_clips_planned
            else 1.0
        )
        scene_assembly_rate = (
            scene_clips_success / scene_clips_planned
            if scene_clips_planned
            else 1.0
        )

        dimensions = {
            "clip_generation_success": {
                "score": clip_success_rate,
                "notes": [
                    f"{total_clips_success}/{total_clips_planned} shot clips generated",
                    *(
                        [f"{total_clips_error} clips failed with errors"]
                        if total_clips_error
                        else []
                    ),
                ],
            },
            "assembly_completeness": {
                "score": (
                    (scene_assembly_rate + (1.0 if final_ok else 0.0)) / 2.0
                ),
                "notes": [
                    f"{scene_clips_success}/{scene_clips_planned} scene clips assembled",
                    f"final video: {'OK' if final_ok else 'MISSING'}",
                ],
            },
            "motion_quality": {
                "score": 1.0,
                "notes": ["motion quality check not yet implemented"],
            },
        }

        # final_ok is now load-bearing on overall_pass — previously it was
        # only mentioned in the summary string, so a run could miss the
        # final assembled video and still report overall_pass=True (which
        # let "0/N shot clips, final=MISSING" silently pass as COMPLETED).
        overall_pass = (
            clip_success_rate >= self.ASSET_PASS_THRESHOLD
            and final_ok
        )
        summary = (
            f"Video asset eval: {total_clips_success}/{total_clips_planned} "
            f"shot clips ({clip_success_rate:.0%}), "
            f"{scene_clips_success}/{scene_clips_planned} scene clips, "
            f"final={'OK' if final_ok else 'MISSING'}."
        )

        return {
            "dimensions": dimensions,
            "overall_pass": overall_pass,
            "summary": summary,
        }
