"""Evaluator for AudioMixAgent output."""

from __future__ import annotations

from ..base_evaluator import BaseEvaluator
from .schema import AudioMixAgentOutput


class AudioMixEvaluator(BaseEvaluator[AudioMixAgentOutput]):

    creative_dimensions: list[tuple[str, str]] = []

    def check_structure(self, output: AudioMixAgentOutput) -> list[str]:
        errors: list[str] = []
        if not output.content.scene_mixes:
            errors.append("scene_mixes list is empty")
        for i, m in enumerate(output.content.scene_mixes):
            if not m.scene_id:
                errors.append(f"scene_mixes[{i}].scene_id is empty")
            if not m.mix_asset.asset_id:
                errors.append(f"scene_mixes[{i}].mix_asset.asset_id is empty")
        if output.content.final_audio.asset_id != "aud_final":
            errors.append(f"final_audio.asset_id must be 'aud_final', got '{output.content.final_audio.asset_id}'")
        return errors
