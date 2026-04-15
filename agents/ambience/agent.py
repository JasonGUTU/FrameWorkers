"""AmbienceAgent — per-scene ambient sound from screenplay setting."""

from __future__ import annotations

from typing import Any

from ..base_agent import BaseAgent
from .schema import AmbienceAgentInput, AmbienceAgentOutput


AMBIENCE_OUTPUT_TEMPLATE = """{
  "content": {
    "beds": [
      {
        "ambience_id": "amb_sc_001",
        "scene_id": "sc_001",
        "description": "<short description of ambient sounds for this scene>",
        "duration_seconds": 45.0,
        "audio_asset": {"asset_id": "aud_amb_sc_001", "uri": "placeholder", "format": "wav"}
      }
    ]
  }
}"""


class AmbienceAgent(BaseAgent[AmbienceAgentInput, AmbienceAgentOutput]):

    async def generate(self, input_data: AmbienceAgentInput, *, rework_notes: str = "") -> AmbienceAgentOutput:
        output = await self._llm_fill_full(input_data, rework_notes)
        self.recompute_metrics(output)
        return output

    def system_prompt(self) -> str:
        return (
            "You are AmbienceAgent: read a screenplay and produce one "
            "ambient sound bed per scene.\n\n"
            "For each scene:\n"
            "1. Derive ambient sounds from the scene's location, heading, "
            "and environment (e.g. 'ocean waves, distant seagulls, wind').\n"
            "2. Set duration_seconds = the scene's pre-computed "
            "`estimated_duration_seconds` field (ScreenplayAgent owns the "
            "duration estimate — it sees both dialogue word counts and "
            "action shot counts, so it is the single source of truth "
            "shared with MusicAgent). Do NOT re-derive this from word "
            "counts yourself; just copy the number. If the field is "
            "missing or zero, emit 0 for duration_seconds — the pipeline "
            "will surface the bad screenplay output instead of hiding it "
            "behind a drifting local estimate.\n\n"
            "IDs: ambience_id = amb_{scene_id}, asset_id = aud_amb_{scene_id}.\n"
            "uri: always 'placeholder'.\n\n"
            "JSON only; no markdown.\n"
            "Do NOT include an artifact_caption block."
        )

    def build_user_prompt(self, input_data: AmbienceAgentInput) -> str:
        return (
            "Generate ambient sound descriptions for this screenplay:\n\n"
            f"=== SCREENPLAY ===\n{input_data.screenplay_json_text}\n=== END ===\n\n"
            "Remember: read each scene's estimated_duration_seconds "
            "field verbatim — do not re-estimate.\n\n"
            f"Output:\n{AMBIENCE_OUTPUT_TEMPLATE}\n\nReturn JSON only."
        )

    def parse_output(self, raw: dict[str, Any]) -> AmbienceAgentOutput:
        return AmbienceAgentOutput.model_validate(raw)

    def recompute_metrics(self, output: AmbienceAgentOutput) -> None:
        output.metrics.bed_count = len(output.content.beds)
