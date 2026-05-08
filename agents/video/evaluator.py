"""Evaluator for VideoAgent output (Video Package).

Layer 1 only (L2 intentionally not overridden — see below).

Layer 1 -- structural checks:
  - shot_id format ``^sh_\\d{3}$`` and global-sequential numbering
    (sh_001, sh_002, … across the whole video package, no gaps, no
    restarts at scene boundaries). These are owned by the LLM via the
    template + system prompt and enforced here so rework surfaces any
    drift instead of a silent Python-side patch-up.
  - Transition plan from/to shot_ids exist in scene
  - Metrics consistency (scene_count, shot_segment_count)
  - Order continuity (scene.order is [1, 2, ..., N])
  - Temporal/transition validation (type)
  - Required content (non-empty scenes and shot_segments)

Layer 2 -- creative assessment:
  Not applicable. VideoAgent output is entirely structural (IDs,
  transition types, mirrored semantic_context). All quality dimensions
  that matter are checked in Layer 1.

Note: a previous Layer 3 (post-materialization asset eval) has been
removed; per-clip / scene / final assembly failures are raised by
VideoMaterializer after exhausting its internal partial-resume retry
budget, so the outer run loop catches them directly.
"""

from __future__ import annotations

import re

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

        # --- duration_sec must be in Kling's accepted enum {5, 10} ---
        # Mirror of system_prompt's PER-SHOT DURATION rule. The fal /
        # Kling backend silently rounds non-{5,10} values; without this
        # check that silent rounding masks drift (CLAUDE.md §7 anti-pattern).
        for scene in c.scenes:
            for seg in scene.shot_segments:
                if seg.duration_sec not in (5, 5.0, 10, 10.0):
                    errors.append(
                        f"shot {seg.shot_id} duration_sec="
                        f"{seg.duration_sec} is not in the allowed set "
                        "{5, 10} (Kling i2v only accepts 5s or 10s clips)"
                    )

        # --- semantic_context.visual_goal must be non-empty ---
        # Mirror of system_prompt's STRUCTURAL REQUIREMENTS line:
        # "Every shot MUST have a semantic_context with ... visual_goal
        # non-empty." Without this check the prompt rule is placebo.
        for scene in c.scenes:
            for seg in scene.shot_segments:
                if not (seg.semantic_context.visual_goal or "").strip():
                    errors.append(
                        f"shot {seg.shot_id} semantic_context.visual_goal "
                        "is empty"
                    )

        # --- Order continuity ---
        self._check_order_continuous(errors, "scenes", [s.order for s in c.scenes])

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
