"""Evaluator for NarrationAgent output.

Layer 1 — structural:
  - ID format + continuity (seg_NNN, ln_NNN, both 3-digit zero-padded,
    segments 1-indexed per script, lines globally 1-indexed)
  - Required non-empty fields (language, overall_style, segments,
    per-segment image_prompt + non-empty lines)
  - Metrics consistency

Layer 2 — creative:
  - dramatic: narrator voice, rhythm, hook strength
  - coherence: story flows across segments, image_prompts match their
    narrated lines
"""

from __future__ import annotations

import re

from ..base_evaluator import BaseEvaluator
from .schema import NarrationAgentOutput


_SEGMENT_ID_RE = re.compile(r"^seg_\d{3}$")
_LINE_ID_RE = re.compile(r"^ln_\d{3}$")


class NarrationEvaluator(BaseEvaluator[NarrationAgentOutput]):

    creative_dimensions = [
        ("dramatic", "Is this narrator voice engaging — clear hook, rhythm suited to being read aloud?"),
        ("coherence", "Do the segments flow as a continuous story, and does each image_prompt visually match its narrated lines?"),
    ]

    # ------------------------------------------------------------------
    # Layer 1 — Rule-based structural validation
    # ------------------------------------------------------------------

    def check_structure(self, output: NarrationAgentOutput) -> list[str]:
        errors: list[str] = []
        c = output.content

        if not c.language.strip():
            errors.append("content.language is empty (expected IETF tag like 'zh-CN')")
        if not c.overall_style.strip():
            errors.append("content.overall_style is empty (cross-segment art-style anchor required)")
        if not c.segments:
            errors.append("content.segments is empty")
            return errors

        # segment_id format + continuity
        for i, seg in enumerate(c.segments, start=1):
            expected_sid = f"seg_{i:03d}"
            if not _SEGMENT_ID_RE.match(seg.segment_id or ""):
                errors.append(
                    f"segments[{i-1}].segment_id={seg.segment_id!r} must match seg_NNN"
                )
            elif seg.segment_id != expected_sid:
                errors.append(
                    f"segments[{i-1}].segment_id={seg.segment_id} expected {expected_sid} "
                    "(segment_ids must be 1-indexed and sequential)"
                )

            if not seg.image_prompt.strip():
                errors.append(f"segments[{i-1}].image_prompt is empty")
            if not seg.lines:
                errors.append(f"segments[{i-1}].lines is empty")

        # line_id globally sequential
        global_idx = 0
        for s_idx, seg in enumerate(c.segments):
            for l_idx, line in enumerate(seg.lines):
                global_idx += 1
                expected_lid = f"ln_{global_idx:03d}"
                if not _LINE_ID_RE.match(line.line_id or ""):
                    errors.append(
                        f"segments[{s_idx}].lines[{l_idx}].line_id="
                        f"{line.line_id!r} must match ln_NNN"
                    )
                elif line.line_id != expected_lid:
                    errors.append(
                        f"segments[{s_idx}].lines[{l_idx}].line_id="
                        f"{line.line_id} expected {expected_lid} "
                        "(line_ids are globally sequential across all segments, not reset per segment)"
                    )
                if not line.text.strip():
                    errors.append(
                        f"segments[{s_idx}].lines[{l_idx}].text is empty"
                    )
                if line.pause_after_ms < 0:
                    errors.append(
                        f"segments[{s_idx}].lines[{l_idx}].pause_after_ms "
                        f"must be >= 0 (got {line.pause_after_ms})"
                    )

        return errors
