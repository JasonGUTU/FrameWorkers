"""Evaluator for VideoAgent output (Video Package).

All three layers:

Layer 1 -- structural checks:
  - Upstream cross-check (scene/shot IDs match storyboard)
  - Transition plan from/to shot_ids exist in scene
  - Metrics consistency (scene_count, shot_segment_count)
  - Shot order continuity per scene
  - Temporal/transition validation (type, duration)
  - Shot duration sanity (positive actual_duration_sec)
  - Required content (non-empty scenes and shot_segments)

Layer 2 -- creative assessment:
  Not applicable. VideoAgent output is entirely structural (IDs,
  durations, asset pointers, transition types). All quality dimensions
  that matter are checked in Layer 1 (structural) or Layer 3 (asset).

Layer 3 -- post-materialization asset checks:
  - clip_generation_success: shot-level clip success rate
  - assembly_completeness: scene clips + final video
  - duration_compliance: (TODO) probe actual file durations
  - motion_quality: (TODO) video analysis model
"""

from __future__ import annotations

from typing import Any

from ..base_evaluator import BaseEvaluator, check_uri
from .schema import VideoAgentOutput


class VideoEvaluator(BaseEvaluator[VideoAgentOutput]):

    # ------------------------------------------------------------------
    # Layer 1 -- Rule-based structural validation
    # ------------------------------------------------------------------

    def check_structure(
        self,
        output: VideoAgentOutput,
        upstream: dict[str, Any] | None = None,
    ) -> list[str]:
        """Rule-based structural validation for Video Package."""
        errors: list[str] = []
        c = output.content

        # --- Upstream cross-check: scene/shot IDs must match storyboard ---
        if upstream and "storyboard" in upstream:
            sb_content = upstream["storyboard"].get("content", {})
            sb_scene_ids = {
                s.get("scene_id", "") for s in sb_content.get("scenes", [])
            }
            vid_scene_ids = {s.scene_id for s in c.scenes}
            self._check_id_coverage(
                errors, "video vs storyboard scenes",
                sb_scene_ids, vid_scene_ids,
            )

            sb_shot_ids: set[str] = set()
            for sb_scene in sb_content.get("scenes", []):
                for shot in sb_scene.get("shots", []):
                    sb_shot_ids.add(shot.get("shot_id", ""))
            vid_shot_ids = {
                seg.shot_id for scene in c.scenes
                for seg in scene.shot_segments
            }
            self._check_id_coverage(
                errors, "video vs storyboard shots",
                sb_shot_ids, vid_shot_ids,
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
                if tr.transition_type == "cut" and tr.duration_sec != 0.0:
                    errors.append(
                        f"scene {scene.scene_id} cut transition should have "
                        f"duration_sec=0, got {tr.duration_sec}"
                    )
                if tr.transition_type in ("dissolve", "fade", "soft") and tr.duration_sec <= 0:
                    errors.append(
                        f"scene {scene.scene_id} {tr.transition_type} transition "
                        f"should have positive duration_sec, got {tr.duration_sec}"
                    )

        # --- Shot duration sanity ---
        for scene in c.scenes:
            for seg in scene.shot_segments:
                if seg.actual_duration_sec <= 0:
                    errors.append(
                        f"shot {seg.shot_id} has non-positive "
                        f"actual_duration_sec ({seg.actual_duration_sec})"
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
    # VideoAgent output is entirely structural (IDs, durations, asset
    # pointers, transition types).  All quality dimensions that matter
    # are checked in Layer 1 (structural) or Layer 3 (asset).

    # ------------------------------------------------------------------
    # Layer 3 -- Post-materialization asset evaluation
    # ------------------------------------------------------------------

    async def evaluate_asset(
        self,
        asset_data: dict[str, Any],
        upstream: dict[str, Any] | None = None,
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
        clip_success_rate = (
            total_clips_success / total_clips_planned
            if total_clips_planned
            else 0.0
        )
        scene_assembly_rate = (
            scene_clips_success / scene_clips_planned
            if scene_clips_planned
            else 0.0
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
            "duration_compliance": {
                "score": 1.0,
                "notes": ["duration compliance check not yet implemented"],
            },
            "motion_quality": {
                "score": 1.0,
                "notes": ["motion quality check not yet implemented"],
            },
        }

        overall_pass = clip_success_rate >= self.ASSET_PASS_THRESHOLD
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
