"""MusicAgent — per-scene background music from screenplay mood/tone."""

from __future__ import annotations

from typing import Any

from ..base_agent import BaseAgent
from .schema import MusicAgentInput, MusicAgentOutput


MUSIC_OUTPUT_TEMPLATE = """{
  "content": {
    "cues": [
      {
        "cue_id": "music_sc_001",
        "scene_id": "sc_001",
        "mood": "<3-6 keywords: musical mood + instrumentation>",
        "duration_seconds": 45.0,
        "audio_asset": {"asset_id": "aud_music_sc_001", "uri": "placeholder", "format": "wav"}
      }
    ]
  }
}"""


class MusicAgent(BaseAgent[MusicAgentInput, MusicAgentOutput]):

    async def generate(self, input_data: MusicAgentInput, *, rework_notes: str = "") -> MusicAgentOutput:
        output = await self._llm_fill_full(input_data, rework_notes)
        self.recompute_metrics(output)
        return output

    def system_prompt(self) -> str:
        return (
            "You are MusicAgent: read a screenplay and produce one "
            "background music cue per scene.\n\n"
            "For each scene:\n"
            "1. Derive a mood from the scene's tone, summary, and heading. "
            "Express as 3-6 keywords (e.g. 'melancholic, ambient, solo piano').\n"
            "2. Set duration_seconds = the scene's pre-computed "
            "`estimated_duration_seconds` field (ScreenplayAgent owns the "
            "duration estimate — it sees both dialogue word counts and "
            "action shot counts, so it is the single source of truth "
            "shared with AmbienceAgent). Do NOT re-derive this from word "
            "counts yourself; just copy the number. If the field is "
            "missing or zero, emit 0 for duration_seconds — the pipeline "
            "will surface the bad screenplay output instead of hiding it "
            "behind a drifting local estimate.\n\n"
            "IDs: cue_id = music_{scene_id}, asset_id = aud_music_{scene_id}.\n"
            "uri: always 'placeholder'.\n\n"
            "JSON only; no markdown.\n"
            "Do NOT include an artifact_caption block."
        )

    def build_user_prompt(self, input_data: MusicAgentInput) -> str:
        return (
            "Generate music cues for this screenplay:\n\n"
            f"=== SCREENPLAY ===\n{input_data.screenplay_json_text}\n=== END ===\n\n"
            "Remember: read each scene's estimated_duration_seconds "
            "field verbatim — do not re-estimate.\n\n"
            f"Output:\n{MUSIC_OUTPUT_TEMPLATE}\n\nReturn JSON only."
        )

    def parse_output(self, raw: dict[str, Any]) -> MusicAgentOutput:
        return MusicAgentOutput.model_validate(raw)

    def recompute_metrics(self, output: MusicAgentOutput) -> None:
        output.metrics.cue_count = len(output.content.cues)
