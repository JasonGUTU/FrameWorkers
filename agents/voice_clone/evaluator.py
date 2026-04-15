"""Evaluator for VoiceCloneAgent output."""

from __future__ import annotations

import re

from ..base_evaluator import BaseEvaluator
from .schema import VoiceCloneAgentOutput


class VoiceCloneEvaluator(BaseEvaluator[VoiceCloneAgentOutput]):

    creative_dimensions: list[tuple[str, str]] = []  # L2 skipped — structural checks are sufficient

    def check_structure(self, output: VoiceCloneAgentOutput) -> list[str]:
        errors: list[str] = []
        c = output.content

        # Voice profile
        vp = c.voice_profile
        if not vp.voice_id:
            errors.append("voice_profile.voice_id is empty")
        if not vp.description:
            errors.append("voice_profile.description is empty")
        if vp.gender not in ("male", "female", "neutral", ""):
            errors.append(
                f"voice_profile.gender '{vp.gender}' must be "
                "male | female | neutral"
            )

        # Segments
        if not c.segments:
            errors.append("segments list is empty — must have narration segments")
            return errors

        prev_id_num = 0
        for i, seg in enumerate(c.segments):
            prefix = f"segments[{i}]"

            if not seg.segment_id:
                errors.append(f"{prefix}.segment_id is empty")
            else:
                m = re.match(r"^vc_seg_(\d{3})$", seg.segment_id)
                if not m:
                    errors.append(
                        f"{prefix}.segment_id '{seg.segment_id}' does not "
                        "match vc_seg_NNN format"
                    )
                else:
                    cur_num = int(m.group(1))
                    if cur_num <= prev_id_num:
                        errors.append(
                            f"{prefix}.segment_id '{seg.segment_id}' not "
                            "strictly increasing"
                        )
                    prev_id_num = cur_num

            if not seg.text.strip():
                errors.append(f"{prefix}.text is empty")

            if not seg.audio_asset_id:
                errors.append(f"{prefix}.audio_asset_id is empty")

        # Final audio
        if c.final_audio.asset_id != "vc_final":
            errors.append(
                f"final_audio.asset_id must be 'vc_final', "
                f"got '{c.final_audio.asset_id}'"
            )

        return errors
