"""AudioMixAgent — mix narration + music + ambience into final audio.

Input:  AudioMixAgentInput (narration + music + ambience JSON text)
Output: AudioMixAgentOutput (per-scene mixes + final assembled audio)

The LLM plans the mix (which tracks per scene), the materializer
calls AudioService.mix_scene_audio() + assemble_final().
"""

from __future__ import annotations

from typing import Any

from ..base_agent import BaseAgent
from .schema import AudioMixAgentInput, AudioMixAgentOutput


AUDIOMIX_OUTPUT_TEMPLATE = """{
  "content": {
    "scene_mixes": [
      {
        "scene_id": "sc_001",
        "mix_asset": {"asset_id": "aud_mix_sc_001", "uri": "placeholder", "format": "wav"}
      }
    ],
    "final_audio": {"asset_id": "aud_final", "uri": "placeholder", "format": "wav"}
  }
}"""


class AudioMixAgent(BaseAgent[AudioMixAgentInput, AudioMixAgentOutput]):

    async def generate(self, input_data: AudioMixAgentInput, *, rework_notes: str = "") -> AudioMixAgentOutput:
        output = await self._llm_fill_full(input_data, rework_notes)
        self.recompute_metrics(output)
        return output

    def system_prompt(self) -> str:
        return (
            "You are AudioMixAgent: plan the final audio mix from "
            "narration, music, and ambience tracks.\n\n"
            "Read the three input packages and produce one scene_mix "
            "entry per scene. Each mix combines the narration segments, "
            "music cue, and ambience bed for that scene.\n\n"
            "IDs: mix_asset.asset_id = aud_mix_{scene_id}.\n"
            "final_audio.asset_id = 'aud_final'.\n"
            "All uri: 'placeholder'.\n\n"
            "JSON only; no markdown.\n"
            "Do NOT include an artifact_caption block."
        )

    def build_user_prompt(self, input_data: AudioMixAgentInput) -> str:
        parts = ["Mix these audio tracks:\n\n"]
        if input_data.narration_json_text:
            parts.append(f"=== NARRATION ===\n{input_data.narration_json_text}\n=== END ===\n\n")
        if input_data.music_json_text:
            parts.append(f"=== MUSIC ===\n{input_data.music_json_text}\n=== END ===\n\n")
        if input_data.ambience_json_text:
            parts.append(f"=== AMBIENCE ===\n{input_data.ambience_json_text}\n=== END ===\n\n")
        parts.append(f"Output:\n{AUDIOMIX_OUTPUT_TEMPLATE}\n\nReturn JSON only.")
        return "".join(parts)

    def parse_output(self, raw: dict[str, Any]) -> AudioMixAgentOutput:
        return AudioMixAgentOutput.model_validate(raw)

    def recompute_metrics(self, output: AudioMixAgentOutput) -> None:
        output.metrics.scene_count = len(output.content.scene_mixes)
