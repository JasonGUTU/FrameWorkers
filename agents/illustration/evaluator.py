"""Evaluator for IllustrationAgent output.

Layer 1 — structural:
  - illustrations list mirrors upstream segments non-empty
  - segment_ids match seg_NNN and are sequential
  - image_prompt + overall_style non-empty (both mirrored — if empty it
    means NarrationAgent dropped them)

Note: post-materialization asset eval has been removed; per-illustration
binary failures are raised by IllustrationMaterializer after exhausting
its internal partial-resume retries (see Pattern B + materializer-raise
refactor). The output schema no longer carries per-entry image URI
fields — illustrations are registered as standalone artifacts under
sys_id ``illustration_<segment_id>``.
"""

from __future__ import annotations

import re

from ..base_evaluator import BaseEvaluator
from .schema import IllustrationAgentOutput


_SEGMENT_ID_RE = re.compile(r"^seg_\d{3}$")


class IllustrationEvaluator(BaseEvaluator[IllustrationAgentOutput]):

    # L2 skipped: IllustrationAgent is structurally a mirror — image_prompt
    # and overall_style are LLM-extracted/copied from NarrationAgent's
    # output (see schema.py docstrings; agent.py system_prompt instructs
    # "copy verbatim if upstream provides"). NarrationAgent's L2 already
    # evaluates the same prompts under "coherence" (does each image_prompt
    # visually match its narrated lines?). No creative=True fields exist
    # on IllustrationContent, so an attempted L2 here gives the judge
    # empty content. Re-evaluating would double-count NarrationAgent's L2.
    creative_dimensions: list[tuple[str, str]] = []

    def check_structure(self, output: IllustrationAgentOutput) -> list[str]:
        errors: list[str] = []
        c = output.content

        if not c.overall_style.strip():
            errors.append(
                "content.overall_style is empty (mirrored from NarrationAgent — "
                "if empty, the upstream script is missing the cross-segment "
                "art-style anchor)"
            )
        if not c.illustrations:
            errors.append("content.illustrations is empty")
            return errors

        # Set of character_ids declared as recurring anchors. Used to
        # validate the "characters_in_segment ⊆ character_anchors"
        # subset rule from system_prompt's STRUCTURAL REQUIREMENTS.
        anchor_ids = {a.character_id for a in c.character_anchors}

        for i, entry in enumerate(c.illustrations, start=1):
            expected_sid = f"seg_{i:03d}"
            if not _SEGMENT_ID_RE.match(entry.segment_id or ""):
                errors.append(
                    f"illustrations[{i-1}].segment_id={entry.segment_id!r} "
                    "must match seg_NNN"
                )
            elif entry.segment_id != expected_sid:
                errors.append(
                    f"illustrations[{i-1}].segment_id={entry.segment_id} "
                    f"expected {expected_sid} (must mirror NarrationAgent segment order)"
                )
            if not entry.image_prompt.strip():
                errors.append(
                    f"illustrations[{i-1}].image_prompt is empty"
                )
            # characters_in_segment subset check (mirrors prompt MUST rule).
            unknown = [cid for cid in entry.characters_in_segment
                       if cid not in anchor_ids]
            if unknown:
                errors.append(
                    f"illustrations[{i-1}] ({entry.segment_id}) "
                    f"characters_in_segment references {unknown!r} not in "
                    "character_anchors"
                )

        return errors
