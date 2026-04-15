"""VoiceCloneAgent — clone a voice from reference audio and generate narration.

Input:  VoiceCloneAgentInput (reference audio + transcript)
Output: VoiceCloneAgentOutput (voice profile + narration segments)

The LLM reads the transcript and plans the narration segments. The
materializer calls a voice cloning service to first extract a voice
profile from the reference audio, then generate each segment using
the cloned voice.
"""

from __future__ import annotations

from typing import Any

from ..base_agent import BaseAgent
from .schema import VoiceCloneAgentInput, VoiceCloneAgentOutput


VOICE_CLONE_OUTPUT_TEMPLATE = """{
  "content": {
    "voice_profile": {
      "voice_id": "voice_001",
      "description": "<description of the cloned voice>",
      "gender": "<male | female | neutral>",
      "age_range": "<child | young | adult | elderly>",
      "tone": "<voice tone keywords>"
    },
    "segments": [
      {
        "segment_id": "vc_seg_001",
        "text": "<text to speak>",
        "audio_asset_id": "vc_aud_001",
        "uri": "placeholder"
      }
    ],
    "final_audio": {
      "asset_id": "vc_final",
      "uri": "placeholder",
      "format": "wav"
    }
  }
}"""


class VoiceCloneAgent(BaseAgent[VoiceCloneAgentInput, VoiceCloneAgentOutput]):

    async def generate(
        self,
        input_data: VoiceCloneAgentInput,
        *,
        rework_notes: str = "",
    ) -> VoiceCloneAgentOutput:
        output = await self._llm_fill_full(input_data, rework_notes)
        self.recompute_metrics(output)
        return output

    def system_prompt(self) -> str:
        return (
            "You are VoiceCloneAgent: plan narration using a cloned voice.\n\n"
            "=== YOUR TASK ===\n"
            "Given a reference audio description and a transcript, produce:\n"
            "1. voice_profile: describe the voice from the reference audio "
            "(gender, age, tone). voice_id is always 'voice_001'.\n"
            "2. segments: break the transcript into individual narration "
            "segments. Each segment should be a natural speaking unit "
            "(one sentence or short phrase).\n"
            "   - segment_id: vc_seg_NNN (3-digit zero-padded)\n"
            "   - audio_asset_id: vc_aud_NNN (matching number)\n"
            "   - text: the exact text to speak\n"
            "   - uri: always 'placeholder'\n"
            "3. final_audio: asset_id is always 'vc_final'.\n\n"
            "=== OUTPUT FORMAT ===\n"
            "JSON only; no markdown; match the user-message template "
            "exactly.\n\n"
            "Do NOT include an artifact_caption block — the system "
            "generates it automatically."
        )

    def build_user_prompt(self, input_data: VoiceCloneAgentInput) -> str:
        return (
            f"Reference audio: {input_data.reference_audio_path}\n\n"
            "=== TRANSCRIPT (text to speak in the cloned voice) ===\n"
            f"{input_data.transcript_json_text}\n"
            "=== END TRANSCRIPT ===\n\n"
            "Plan the narration segments in EXACTLY this shape:\n\n"
            f"{VOICE_CLONE_OUTPUT_TEMPLATE}\n\n"
            "Return JSON only."
        )

    def parse_output(self, raw: dict[str, Any]) -> VoiceCloneAgentOutput:
        return VoiceCloneAgentOutput.model_validate(raw)

    def recompute_metrics(self, output: VoiceCloneAgentOutput) -> None:
        c = output.content
        output.metrics.segment_count = len(c.segments)
        output.metrics.voice_gender = c.voice_profile.gender
