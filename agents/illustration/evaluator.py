"""Evaluator for IllustrationAgent output.

Layer 1 — structural:
  - illustrations list mirrors upstream segments non-empty
  - segment_ids match seg_NNN and are sequential
  - image_prompt + overall_style non-empty (both mirrored — if empty it
    means NarrationAgent dropped them)
  - metrics consistency

Layer 3 — asset:
  - every image URI is a real file (handled by default asset check:
    check_uri on illustrations[*].image.uri)
"""

from __future__ import annotations

import re

from ..base_evaluator import BaseEvaluator, check_uri
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

        return errors

    # ------------------------------------------------------------------
    # Layer 3 — post-materialization asset check
    # ------------------------------------------------------------------

    async def evaluate_asset(self, asset_data: dict) -> dict:
        """Every illustration must have a real image URI after materialization."""
        content = asset_data.get("content", {})
        illustrations = content.get("illustrations", [])
        errors: list[str] = []
        successes = 0
        for i, entry in enumerate(illustrations):
            img = entry.get("image", {}) if isinstance(entry, dict) else {}
            uri = img.get("uri", "") if isinstance(img, dict) else ""
            kind = check_uri(uri)
            if kind == "success":
                successes += 1
            else:
                seg_id = entry.get("segment_id", f"#{i}") if isinstance(entry, dict) else f"#{i}"
                errors.append(f"illustrations[{seg_id}].image.uri is {kind}: {uri!r}")

        total = len(illustrations)
        all_pass = (successes == total) and (total > 0)
        return {
            "dimensions": {
                "image_generation_success": {
                    "score": (successes / total) if total else 0.0,
                    "notes": errors,
                },
            },
            "overall_pass": all_pass,
            "summary": (
                f"{successes}/{total} illustrations generated successfully"
                if total
                else "no illustrations to materialize"
            ),
        }
