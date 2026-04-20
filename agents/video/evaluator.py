"""Evaluator for VideoAgent output (Video Package).

Layers 1 + 3 (L2 intentionally not overridden — see below):

Layer 1 -- structural checks:
  - shot_id format ``^sh_\\d{3}$`` and global-sequential numbering
    (sh_001, sh_002, … across the whole video package, no gaps, no
    restarts at scene boundaries). These are owned by the LLM via the
    template + system prompt and enforced here so rework surfaces any
    drift instead of a silent Python-side patch-up.
  - Transition plan from/to shot_ids exist in scene
  - Metrics consistency (scene_count, shot_segment_count)
  - Temporal/transition validation (type)
  - Required content (non-empty scenes and shot_segments)

Layer 2 -- creative assessment:
  Not applicable. VideoAgent output is entirely structural (IDs,
  transition types, mirrored semantic_context). All quality dimensions
  that matter are checked in Layer 1.

Layer 3 -- post-materialization asset checks:
  Asset pointers were dropped from the schema (video_asset /
  scene_clip_asset / final_video_asset no longer exist on the output),
  so per-clip URI inspection is no longer possible from the asset dict
  alone. L3 returns a vacuous pass; per-clip generation failures are
  surfaced via ``MaterializeContext.report_failure`` into the workspace
  event log instead.
"""

from __future__ import annotations

import re
from typing import Any

from ..base_evaluator import BaseEvaluator
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
    # VideoAgent output is entirely structural (IDs, transition types).
    # All quality dimensions that matter are checked in Layer 1.

    # ------------------------------------------------------------------
    # Layer 3 -- Post-materialization asset evaluation
    # ------------------------------------------------------------------

    async def evaluate_asset(
        self,
        asset_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Vacuous pass: asset URIs are no longer carried on the schema.

        The slim schema does not persist per-shot ``video_asset``,
        per-scene ``scene_clip_asset``, or ``final_video_asset`` blocks,
        so the asset dict alone cannot distinguish a clip that generated
        vs. one that failed. Per-clip generation failures are surfaced
        by ``VideoMaterializer`` via
        ``MaterializeContext.report_failure`` into the workspace event
        log; L3 here is kept as a stub returning ``overall_pass=True``
        so the base pipeline's L3 hook remains wired.
        """
        content = asset_data.get("content", {})
        scenes = content.get("scenes", [])
        total_clips_planned = sum(
            len(s.get("shot_segments", []) or []) for s in scenes
        )

        dimensions = {
            "clip_generation_success": {
                "score": 1.0,
                "notes": [
                    f"{total_clips_planned} shot clips planned; per-clip "
                    f"failures are reported via the workspace event log, "
                    f"not the asset dict",
                ],
            },
        }
        summary = (
            f"Video asset eval: {total_clips_planned} shot clips planned "
            f"(URI-based L3 check disabled — see materializer failure "
            f"reports)."
        )
        return {
            "dimensions": dimensions,
            "overall_pass": True,
            "summary": summary,
        }
