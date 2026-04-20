"""TranscriptionAgent — speech-to-text from audio/video files.

Input:  TranscriptionAgentInput (source_media_path)
Output: TranscriptionAgentOutput (timestamped transcript segments + full text)

This agent uses a two-phase approach:
1. The materializer calls a transcription service (e.g. Whisper) to get
   raw timestamped segments.
2. The LLM post-processes the raw segments: cleans up text, infers
   speaker labels, and produces the final structured output.

The LLM phase is optional — if the transcription service already produces
clean output, the materializer can populate the output directly.
"""

from __future__ import annotations

from typing import Any

from ..base_agent import BaseAgent
from .schema import TranscriptionAgentInput, TranscriptionAgentOutput


TRANSCRIPTION_OUTPUT_TEMPLATE = """{
  "content": {
    "language": "<detected language code, e.g. zh>",
    "segments": [
      {
        "segment_id": "seg_001",
        "start_time": 0.0,
        "end_time": 3.5,
        "text": "<transcribed text>"
      }
    ],
    "full_text": "<complete transcript as continuous text>"
  }
}"""


class TranscriptionAgent(BaseAgent[TranscriptionAgentInput, TranscriptionAgentOutput]):

    async def generate(
        self,
        input_data: TranscriptionAgentInput,
        *,
        rework_notes: str = "",
    ) -> TranscriptionAgentOutput:
        output = await self._llm_fill_full(input_data, rework_notes)
        self.recompute_metrics(output)
        return output

    def system_prompt(self) -> str:
        return (
            "You are TranscriptionAgent: clean up and structure raw "
            "speech-to-text output into a polished transcript.\n\n"
            "=== WHEN TO REJECT UPSTREAM INPUT ===\n"
            "Use the shared input_rejection escape hatch (see the UPSTREAM "
            "INPUT REJECTION block above) ONLY if the source media is "
            "unusable. Concretely, reject when:\n"
            "  * source_media_path is empty / whitespace-only — there is "
            "no file to transcribe.\n"
            "When you reject, populate the rejection fields like this:\n"
            "  * reason: e.g. 'source_media_path is empty — no media "
            "file to transcribe'.\n"
            "  * missing_labels: ['source_media'] (my only input label).\n"
            "  * offending_fields: ['source_media_path'].\n"
            "If the path looks unusual but is non-empty — DO NOT reject; "
            "the materializer (which actually invokes the ASR service) "
            "will surface a real failure if the file does not exist or is "
            "not decodable. Speech-light or noisy media is not a reason "
            "to reject.\n"
            "=== END WHEN TO REJECT UPSTREAM INPUT ===\n\n"
            "=== INPUT FORMAT ===\n"
            "You will receive raw transcription segments from an ASR "
            "(Automatic Speech Recognition) system. Each segment has "
            "a timestamp and raw text.\n\n"
            "=== POST-PROCESSING RULES ===\n"
            "1. Clean up transcription artifacts: fix obvious typos, "
            "normalize punctuation, remove filler words (um, uh) unless "
            "they are meaningful.\n"
            "2. Merge very short adjacent segments that are clearly part "
            "of the same sentence.\n"
            "3. segment_id format: seg_NNN (3-digit zero-padded, globally "
            "sequential starting at seg_001).\n"
            "4. Detect the language from the content.\n"
            "5. full_text: concatenate all segment texts in order, separated "
            "by spaces.\n\n"
            "=== OUTPUT FORMAT ===\n"
            "JSON only; no markdown; match the user-message template "
            "exactly.\n\n"
            "Do NOT include an artifact_caption block — the system generates "
            "it automatically."
        )

    def build_user_prompt(self, input_data: TranscriptionAgentInput) -> str:
        return (
            "Process the raw transcription segments below into a clean, "
            "structured transcript.\n\n"
            f"Source media: {input_data.source_media_path}\n\n"
            "NOTE: The actual transcription was performed by the "
            "materializer before this LLM call. If raw segments are "
            "provided in the rework notes, process them. Otherwise, "
            "produce a minimal placeholder output.\n\n"
            "Produce the transcript in EXACTLY this shape:\n\n"
            f"{TRANSCRIPTION_OUTPUT_TEMPLATE}\n\n"
            "Return JSON only."
        )

    def parse_output(self, raw: dict[str, Any]) -> TranscriptionAgentOutput:
        return TranscriptionAgentOutput.model_validate(raw)

    def recompute_metrics(self, output: TranscriptionAgentOutput) -> None:
        c = output.content
        output.metrics.language = c.language
        output.metrics.segment_count = len(c.segments)
        if c.segments:
            output.metrics.duration_seconds = max(
                s.end_time for s in c.segments
            )
