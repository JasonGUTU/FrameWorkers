"""AudioMixAgent — plan the single film-wide final audio track.

Input:  AudioMixAgentInput (video + optional music + optional ambience JSON text + file paths)
Output: AudioMixAgentOutput (empty content envelope — all binary lives under sys_id ``aud_final``)

The LLM's only job here is the upstream-input rejection gate. The
materializer does the actual work: extract the video's audio track
(Kling's in-clip dialogue + foley), amix with the optional global
music / ambience tracks (duration=longest), and emit one final wav
registered under sys_id ``aud_final``.
"""

from __future__ import annotations

from typing import Any

from ..base_agent import BaseAgent
from .schema import AudioMixAgentInput, AudioMixAgentOutput


AUDIOMIX_OUTPUT_TEMPLATE = """{
  "content": {}
}"""


class AudioMixAgent(BaseAgent[AudioMixAgentInput, AudioMixAgentOutput]):

    async def generate(self, input_data: AudioMixAgentInput, *, rework_notes: str = "") -> AudioMixAgentOutput:
        output = await self._llm_fill_full(input_data, rework_notes)
        self.recompute_metrics(output, input_data)
        return output

    def system_prompt(self) -> str:
        return (
            "You are AudioMixAgent: gate the inputs for the final "
            "film-wide audio mix. The actual amix happens in the "
            "materializer; your JSON output is just an envelope.\n\n"
            "=== WHEN TO REJECT UPSTREAM INPUT ===\n"
            "Use the shared input_rejection escape hatch ONLY if the "
            "inputs make mixing impossible. Reject when ANY of these is "
            "true:\n"
            "  * video_json_text is empty or has no rendered scenes — "
            "without the Kling-baked video track (which carries dialogue "
            "+ foley), there is no base audio to mix.\n"
            "When you reject, populate the rejection fields like this:\n"
            "  * reason: a specific defect.\n"
            "  * missing_labels: ['video'] in this case.\n"
            "  * offending_fields: e.g. ['content.scenes'].\n"
            "  * upstream_agent_hint: 'VideoAgent'.\n"
            "If only music or only ambience is missing — DO NOT reject; "
            "mix whatever is available (both are optional global tracks; "
            "the video's own audio alone is a valid mix).\n"
            "=== END WHEN TO REJECT UPSTREAM INPUT ===\n\n"
            "=== OUTPUT SHAPE ===\n"
            "Emit exactly the envelope `{\"content\": {}}`. There are no "
            "per-scene mixes in the new architecture — dialogue + foley "
            "are baked into the video clips already, so this agent just "
            "lets the materializer layer any global music / ambience "
            "underlays on top. The final wav is registered as a separate "
            "artifact (sys_id 'aud_final') in workspace memory; do NOT "
            "include any audio asset / uri / file-path field in your "
            "JSON output.\n\n"
            "JSON only; no markdown.\n"
            "Do NOT include an artifact_caption block."
        )

    def build_user_prompt(self, input_data: AudioMixAgentInput) -> str:
        parts = ["Mix these source tracks into one film-wide audio track.\n\n"]
        parts.append(
            f"=== VIDEO (provides in-clip dialogue + foley) ===\n"
            f"{input_data.video_json_text}\n=== END ===\n\n"
        )
        if input_data.music_json_text:
            parts.append(
                f"=== MUSIC (global BGM) ===\n"
                f"{input_data.music_json_text}\n=== END ===\n\n"
            )
        if input_data.ambience_json_text:
            parts.append(
                f"=== AMBIENCE (global room-tone) ===\n"
                f"{input_data.ambience_json_text}\n=== END ===\n\n"
            )
        parts.append(f"Output:\n{AUDIOMIX_OUTPUT_TEMPLATE}\n\nReturn JSON only.")
        return "".join(parts)

    def parse_output(self, raw: dict[str, Any]) -> AudioMixAgentOutput:
        return AudioMixAgentOutput.model_validate(raw)

    def recompute_metrics(
        self,
        output: AudioMixAgentOutput,
        input_data: AudioMixAgentInput | None = None,
    ) -> None:
        count = 1  # video track is always present
        if input_data is not None:
            if input_data.music_json_text:
                count += 1
            if input_data.ambience_json_text:
                count += 1
        output.metrics.source_track_count = count
