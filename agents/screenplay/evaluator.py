"""Evaluator for ScreenplayAgent output (unified screenplay + shots).

Layer 1 — structural checks (output-internal only):
  - shot_id format ``^sh_\\d{3}$`` and global-sequential numbering
    (sh_001, sh_002, … across the whole screenplay, no gaps, no restarts
    at scene boundaries). These used to be force-rewritten in
    ScreenplayAgent.recompute_metrics; they are now owned by the LLM
    via the template + system prompt and enforced here so rework
    surfaces any drift instead of a silent Python-side patch-up.
  - Per-scene shot order continuity (1, 2, 3, … starting at 1 per scene).
  - Dialogue-type shots: character_id + text
  - keyframe_plan.keyframe_count == 1 per shot
  - Metrics consistency
  - Non-empty scenes and shots

Layer 2 — creative assessment (output-internal only).

Evaluators do NOT cross-validate against upstream artifacts.
"""

from __future__ import annotations

import re

from ..base_evaluator import BaseEvaluator
from .schema import ScreenplayAgentOutput


_SHOT_ID_PATTERN = re.compile(r"^sh_\d{3}$")


class ScreenplayEvaluator(BaseEvaluator[ScreenplayAgentOutput]):

    creative_dimensions = [
        (
            "character_consistency",
            "Are character voices distinct and consistent? Do shots honor who is on screen?",
        ),
        (
            "dramatic_flow",
            "Do dialogue/action and shot rhythm flow naturally? Effective scene turns?",
        ),
        (
            "visual_coherence",
            "Are shot types, camera choices, and visual goals coherent per scene?",
        ),
    ]

    def check_structure(self, output: ScreenplayAgentOutput) -> list[str]:
        errors: list[str] = []
        c = output.content

        # Shot id format + global sequential numbering. If any id is
        # malformed, skip the sequentiality check so the error message
        # stays specific ("wrong format" vs "wrong sequence").
        all_shot_ids: list[str] = []
        format_ok = True
        for scene in c.scenes:
            for sh in scene.shots:
                sid = sh.shot_id or ""
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

        for scene in c.scenes:
            for sh in scene.shots:
                if sh.block_type == "dialogue":
                    if not sh.character_id:
                        errors.append(
                            f"dialogue shot {sh.shot_id} missing character_id"
                        )
                    if not sh.text:
                        errors.append(
                            f"dialogue shot {sh.shot_id} has empty text"
                        )
                if sh.keyframe_plan.keyframe_count != 1:
                    errors.append(
                        f"shot {sh.shot_id} must have keyframe_count == 1 "
                        f"(got {sh.keyframe_plan.keyframe_count})"
                    )

        # Hard cap to back the SHOT BUDGET section in the system prompt — when
        # the LLM ignores the soft guidance, the rework loop forces it to
        # consolidate into denser shots.
        shot_total = sum(len(s.shots) for s in c.scenes)
        if shot_total > 12:
            errors.append(
                f"shot_count_total={shot_total} exceeds budget of 12 — "
                "consolidate into denser shots (each shot represents ~5s; "
                "merge cutaways and split-beats into single coherent shots)"
            )

        self._check_order_continuous(errors, "scene", [s.order for s in c.scenes])
        for scene in c.scenes:
            self._check_order_continuous(
                errors, f"scene {scene.scene_id} shot",
                [sh.order for sh in scene.shots],
            )

        if not c.scenes:
            errors.append("scenes list is empty")
        for scene in c.scenes:
            if not scene.shots:
                errors.append(f"scene {scene.scene_id} has no shots")

        return errors
