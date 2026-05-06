"""Evaluator for NarratorAgent output.

Layer 1 — structural (pre-materialize):
  * ``lines`` worklist non-empty and well-formed (line_id + segment_id
    + text all non-empty per entry)

Note: post-materialize asset eval has been removed. Narrator's
materializer raises after exhausting its per-line partial-resume retry
budget, so failure of any TTS call is caught by the outer run loop
directly instead of being detected here. Timing-math invariants
previously checked here (clips count == lines count, monotonicity) are
guaranteed by the materializer's deterministic per-line cursor logic;
re-checking them was a belt-and-suspenders artifact of the old "silent
+ skip" failure model that no longer applies.
"""

from __future__ import annotations

import re

from ..base_evaluator import BaseEvaluator
from .schema import NarratorAgentOutput


_LINE_ID_RE = re.compile(r"^ln_\d{3}$")
_SEGMENT_ID_RE = re.compile(r"^seg_\d{3}$")


class NarratorEvaluator(BaseEvaluator[NarratorAgentOutput]):

    # L2 skipped: line.text mirrors upstream narration_script verbatim;
    # NarrationAgent's L2 already evaluates dramatic + coherence on the
    # same text. Re-evaluating here would double-count.
    creative_dimensions: list[tuple[str, str]] = []

    def check_structure(self, output: NarratorAgentOutput) -> list[str]:
        errors: list[str] = []
        c = output.content

        if not c.language.strip():
            errors.append("content.language is empty (mirrored from NarrationAgent)")
        if not c.lines:
            errors.append("content.lines is empty (no TTS worklist — upstream script may be empty)")
            return errors

        for i, line in enumerate(c.lines):
            if not _LINE_ID_RE.match(line.line_id or ""):
                errors.append(f"lines[{i}].line_id={line.line_id!r} must match ln_NNN")
            if not _SEGMENT_ID_RE.match(line.segment_id or ""):
                errors.append(
                    f"lines[{i}].segment_id={line.segment_id!r} must match seg_NNN "
                    "(mirrored from upstream NarrationAgent segment parent)"
                )
            if not line.text.strip():
                errors.append(f"lines[{i}].text is empty")
            if line.pause_after_ms < 0:
                errors.append(f"lines[{i}].pause_after_ms must be >= 0")

        return errors
