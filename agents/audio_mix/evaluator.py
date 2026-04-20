"""Evaluator for AudioMixAgent output.

The agent's JSON output is now just an envelope — the wav lives under
sys_id ``aud_final`` in global_memory. The structural check here is
trivial; the real signal is whether the materializer produced a real
audio file, which is surfaced via the asset evaluation layer (L3).
"""

from __future__ import annotations

from ..base_evaluator import BaseEvaluator
from .schema import AudioMixAgentOutput


class AudioMixEvaluator(BaseEvaluator[AudioMixAgentOutput]):

    creative_dimensions: list[tuple[str, str]] = []

    def check_structure(self, output: AudioMixAgentOutput) -> list[str]:
        return []
