"""SubtitleAgent — generate timed subtitle tracks from screenplay + video timing.

Input:  SubtitleAgentInput (screenplay_json_text + optional video_json_text)
Output: SubtitleAgentOutput (subtitle tracks with SRT-formatted cues)

Single LLM call.  The LLM reads the screenplay to extract dialogue and
narration lines, uses video timing info (if available) to align cue
timestamps, and produces a complete SRT-formatted subtitle track.
"""

from __future__ import annotations

from typing import Any

from ..base_agent import BaseAgent
from .schema import SubtitleAgentInput, SubtitleAgentOutput


SUBTITLE_OUTPUT_TEMPLATE = """{
  "content": {
    "tracks": [
      {
        "language": "<ISO language code, e.g. en>",
        "cues": [
          {
            "cue_id": "cue_001",
            "start_time": "00:00:01,000",
            "end_time": "00:00:04,500",
            "text": "<subtitle text for this cue>"
          }
        ],
        "srt_text": "1\\n00:00:01,000 --> 00:00:04,500\\n<subtitle text>\\n\\n2\\n..."
      }
    ]
  }
}"""


class SubtitleAgent(BaseAgent[SubtitleAgentInput, SubtitleAgentOutput]):

    async def generate(
        self,
        input_data: SubtitleAgentInput,
        *,
        rework_notes: str = "",
    ) -> SubtitleAgentOutput:
        output = await self._llm_fill_full(input_data, rework_notes)
        self.recompute_metrics(output)
        return output

    def system_prompt(self) -> str:
        return (
            "You are SubtitleAgent: generate timed subtitle tracks from a "
            "screenplay and optional video timing information.\n\n"
            "=== WHEN TO REJECT UPSTREAM INPUT ===\n"
            "Use the shared input_rejection escape hatch (see the UPSTREAM "
            "INPUT REJECTION block above) ONLY if the screenplay makes "
            "subtitle generation impossible. Concretely, reject when ANY "
            "of these is true after you have read screenplay_json_text "
            "carefully:\n"
            "  * screenplay_json_text is empty, whitespace-only, or an "
            "empty JSON object — there is no source to subtitle.\n"
            "  * No spoken or narrated text anywhere: every shot's text "
            "field is empty / missing AND no dialogue / narration / "
            "monologue / transcript / cues field exists with non-empty "
            "content. A subtitle track must contain at least one cue, "
            "and cues come from spoken/narrated text.\n"
            "When you reject, populate the rejection fields like this:\n"
            "  * reason: the single most specific defect (e.g. "
            "'screenplay contains only action shots with empty text "
            "fields — no spoken or narrated lines to subtitle').\n"
            "  * missing_labels: ['screenplay'] (the video_package label "
            "is optional and only used for timing alignment).\n"
            "  * offending_fields: e.g. ['content.scenes[].shots[].text'].\n"
            "  * upstream_agent_hint: 'ScreenplayAgent' or "
            "'TranscriptionAgent' depending on whether this looks like a "
            "screenplay-style or transcript-style payload.\n"
            "If the screenplay has plenty of action shots mixed with a few "
            "dialogue lines — DO NOT reject; subtitle the dialogue lines "
            "and skip the action shots.\n"
            "=== END WHEN TO REJECT UPSTREAM INPUT ===\n\n"
            "=== INPUT FORMAT ===\n"
            "You will receive:\n"
            "1. A screenplay as a raw JSON text blob — extract dialogue and "
            "narration lines from it.\n"
            "2. Optionally a video package JSON — use shot durations/timing "
            "to align subtitle timestamps.\n\n"
            "=== SUBTITLE GENERATION RULES ===\n"
            "CRITICAL: Read every shot's TEXT content carefully. Do NOT "
            "rely only on block_type labels — the upstream screenplay may "
            "label all shots as 'action' even when the text contains "
            "spoken dialogue or narration. Instead, judge from the TEXT "
            "itself: if a shot's text describes what is SAID or NARRATED, "
            "it needs a subtitle cue. If it only describes visual action "
            "with no spoken words, skip it.\n"
            "The cues list MUST NOT be empty if the screenplay contains "
            "any spoken or narrated text.\n"
            "1. Extract every spoken or narrated line from the "
            "screenplay, in order.\n"
            "2. Purely visual action shots (no words spoken) get NO cue.\n"
            "3. Each cue should be 1-2 lines max, ~40 characters per line. "
            "Split long dialogue into multiple cues.\n"
            "4. Timestamps in SRT format: HH:MM:SS,mmm\n"
            "5. If video timing is available, align cues to shot boundaries. "
            "If not, estimate reasonable timing (~150 words/minute reading "
            "speed, minimum 1.5s per cue, maximum 7s per cue).\n"
            "6. Leave a small gap (100-200ms) between consecutive cues.\n"
            "7. cue_id format: cue_NNN (3-digit zero-padded, globally "
            "sequential starting at cue_001).\n"
            "8. The srt_text field must contain the COMPLETE, valid SRT file "
            "content — all cues numbered sequentially.\n\n"
            "=== OUTPUT FORMAT ===\n"
            "JSON only; no markdown; match the user-message template exactly.\n\n"
            "Do NOT include an artifact_caption block — the system generates "
            "it automatically."
        )

    def build_user_prompt(self, input_data: SubtitleAgentInput) -> str:
        parts = [
            "Generate a subtitle track from the following screenplay.\n\n"
            "=== SCREENPLAY (raw JSON) ===\n"
            f"{input_data.screenplay_json_text}\n"
            "=== END SCREENPLAY ===\n"
        ]

        if input_data.video_json_text:
            parts.append(
                "\n=== VIDEO PACKAGE (raw JSON — use for timing) ===\n"
                f"{input_data.video_json_text}\n"
                "=== END VIDEO PACKAGE ===\n"
            )

        parts.append(
            "\nProduce the subtitle track in EXACTLY this shape:\n\n"
            f"{SUBTITLE_OUTPUT_TEMPLATE}\n\n"
            "Return JSON only."
        )

        return "".join(parts)

    def parse_output(self, raw: dict[str, Any]) -> SubtitleAgentOutput:
        return SubtitleAgentOutput.model_validate(raw)

    def recompute_metrics(self, output: SubtitleAgentOutput) -> None:
        c = output.content
        output.metrics.track_count = len(c.tracks)
        output.metrics.total_cue_count = sum(
            len(t.cues) for t in c.tracks
        )
