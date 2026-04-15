"""NarrationAgent — per-shot TTS narration from screenplay dialogue.

Input:  NarrationAgentInput (screenplay_json_text)
Output: NarrationAgentOutput (narration segments with per-shot audio)

Extracts dialogue/narration/monologue shots from the screenplay and
produces one narration segment per spoken line. The materializer calls
AudioService.generate_speech() for each segment.
"""

from __future__ import annotations

from typing import Any

from ..base_agent import BaseAgent
from .schema import NarrationAgentInput, NarrationAgentOutput


NARRATION_OUTPUT_TEMPLATE = """{
  "content": {
    "segments": [
      {
        "segment_id": "narr_001",
        "linked_shot_id": "sh_001",
        "speaker": "<character_name or Narrator>",
        "text": "<VERBATIM spoken line from the screenplay>",
        "audio_asset": {
          "asset_id": "aud_narr_001",
          "uri": "placeholder",
          "format": "wav"
        }
      }
    ]
  }
}"""


class NarrationAgent(BaseAgent[NarrationAgentInput, NarrationAgentOutput]):

    async def generate(
        self,
        input_data: NarrationAgentInput,
        *,
        rework_notes: str = "",
    ) -> NarrationAgentOutput:
        output = await self._llm_fill_full(input_data, rework_notes)
        self.recompute_metrics(output)
        return output

    def system_prompt(self) -> str:
        return (
            "You are NarrationAgent: extract spoken lines from a screenplay "
            "and prepare them for text-to-speech synthesis.\n\n"
            "=== EXTRACTION RULES ===\n"
            "Walk every scene's shots IN ORDER. For each shot whose "
            "block_type is 'dialogue', 'narration', or 'monologue', "
            "produce ONE segment. Skip 'action' shots.\n\n"
            "For each segment:\n"
            "  * text: copy the shot's spoken line VERBATIM.\n"
            "  * speaker: copy character_name. For narration with empty "
            "character_name, use 'Narrator'.\n"
            "  * linked_shot_id: the shot's shot_id.\n"
            "  * segment_id: narr_NNN (3-digit, globally sequential).\n"
            "  * audio_asset.asset_id: aud_narr_NNN.\n"
            "  * audio_asset.uri: always 'placeholder'.\n\n"
            "=== OUTPUT FORMAT ===\n"
            "JSON only; no markdown.\n\n"
            "Do NOT include an artifact_caption block."
        )

    def build_user_prompt(self, input_data: NarrationAgentInput) -> str:
        return (
            "Extract all spoken lines from this screenplay:\n\n"
            "=== SCREENPLAY ===\n"
            f"{input_data.screenplay_json_text}\n"
            "=== END ===\n\n"
            f"Output in this shape:\n{NARRATION_OUTPUT_TEMPLATE}\n\n"
            "Return JSON only."
        )

    def parse_output(self, raw: dict[str, Any]) -> NarrationAgentOutput:
        return NarrationAgentOutput.model_validate(raw)

    def recompute_metrics(self, output: NarrationAgentOutput) -> None:
        output.metrics.segment_count = len(output.content.segments)
