"""Evaluator for SubtitleAgent output."""

from __future__ import annotations

import re

from ..base_evaluator import BaseEvaluator
from .schema import SubtitleAgentOutput


_SRT_TIME_RE = re.compile(r"^\d{2}:\d{2}:\d{2},\d{3}$")


class SubtitleEvaluator(BaseEvaluator[SubtitleAgentOutput]):

    creative_dimensions: list[tuple[str, str]] = []  # no L2 — tool agent, not creative

    def check_structure(self, output: SubtitleAgentOutput) -> list[str]:
        errors: list[str] = []
        c = output.content

        if not c.tracks:
            errors.append("tracks list is empty — must have at least one subtitle track")
            return errors

        for ti, track in enumerate(c.tracks):
            prefix = f"tracks[{ti}]"

            if not track.language:
                errors.append(f"{prefix}.language is empty")

            if not track.cues:
                errors.append(f"{prefix}.cues is empty — track has no subtitle cues")
                continue

            if not track.srt_text.strip():
                errors.append(f"{prefix}.srt_text is empty — must contain valid SRT content")

            prev_id_num = 0
            for ci, cue in enumerate(track.cues):
                cue_prefix = f"{prefix}.cues[{ci}]"

                if not cue.cue_id:
                    errors.append(f"{cue_prefix}.cue_id is empty")
                else:
                    m = re.match(r"^cue_(\d{3})$", cue.cue_id)
                    if not m:
                        errors.append(
                            f"{cue_prefix}.cue_id '{cue.cue_id}' does not match "
                            "cue_NNN format"
                        )
                    else:
                        cur_num = int(m.group(1))
                        if cur_num <= prev_id_num:
                            errors.append(
                                f"{cue_prefix}.cue_id '{cue.cue_id}' is not "
                                "strictly increasing"
                            )
                        prev_id_num = cur_num

                if not _SRT_TIME_RE.match(cue.start_time):
                    errors.append(
                        f"{cue_prefix}.start_time '{cue.start_time}' is not "
                        "valid SRT time (HH:MM:SS,mmm)"
                    )

                if not _SRT_TIME_RE.match(cue.end_time):
                    errors.append(
                        f"{cue_prefix}.end_time '{cue.end_time}' is not "
                        "valid SRT time (HH:MM:SS,mmm)"
                    )

                if not cue.text.strip():
                    errors.append(f"{cue_prefix}.text is empty")

        return errors
