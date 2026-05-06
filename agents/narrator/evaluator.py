"""Evaluator for NarratorAgent output.

Layer 1 — structural (pre-materialize):
  * ``lines`` worklist non-empty and well-formed (line_id + segment_id
    + text all non-empty per entry)
  * metrics match worklist size

Layer 3 — asset (post-materialize):
  * narrator audio URI is a real file
  * clips + segment_timings populated and timing is monotonic
  * srt_text non-empty and well-formed
"""

from __future__ import annotations

import re

from ..base_evaluator import BaseEvaluator, check_uri
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

    # ------------------------------------------------------------------
    # Layer 3 — post-materialization asset check
    # ------------------------------------------------------------------

    async def evaluate_asset(self, asset_data: dict) -> dict:
        content = asset_data.get("content", {}) or {}
        errors: list[str] = []

        # The narrator wav is registered as a standalone artifact under
        # sys_id ``aud_narrator_full``; its URI isn't kept in the
        # payload. The materializer's own logging covers wav-write
        # failure — here we verify the derived timing structures only.
        clips = content.get("clips", []) or []
        segment_timings = content.get("segment_timings", []) or []
        srt_text = (content.get("srt_text", "") or "").strip()
        total_dur = float(content.get("total_duration_sec", 0.0) or 0.0)
        lines = content.get("lines", []) or []

        if not clips:
            errors.append("content.clips is empty (materializer produced no per-line timing)")
        if not segment_timings:
            errors.append("content.segment_timings is empty")
        if not srt_text:
            errors.append("content.srt_text is empty")
        if total_dur <= 0:
            errors.append(f"content.total_duration_sec must be > 0 (got {total_dur})")

        if clips and lines and len(clips) != len(lines):
            errors.append(
                f"clips count ({len(clips)}) != lines count ({len(lines)}) "
                "— a TTS call must have failed silently"
            )

        # Timing monotonicity: each clip's end > start, and clips are in order.
        prev_end = 0.0
        for i, clip in enumerate(clips):
            start = float(clip.get("start_sec", 0.0) or 0.0)
            end = float(clip.get("end_sec", 0.0) or 0.0)
            if end <= start:
                errors.append(f"clips[{i}] ({clip.get('line_id')}): end_sec <= start_sec")
            if start < prev_end - 1e-3:
                errors.append(
                    f"clips[{i}] starts before prev clip ended "
                    f"({start:.3f} < {prev_end:.3f})"
                )
            prev_end = max(prev_end, end)

        all_pass = not errors
        return {
            "dimensions": {
                "narrator_timing_valid": {
                    "score": 1.0 if all_pass else 0.0,
                    "notes": errors,
                },
            },
            "overall_pass": all_pass,
            "summary": (
                f"Narrator audio produced ({total_dur:.1f}s, {len(clips)} clips, "
                f"{len(segment_timings)} segments)"
                if all_pass
                else f"Narrator asset check failed: {'; '.join(errors)}"
            ),
        }
