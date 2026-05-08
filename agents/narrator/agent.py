"""NarratorAgent — LLM-driven extractor of TTS line worklist.

Generation model: ONE LLM call via ``_llm_fill_full``. Reads the upstream
NarrationAgent output as a raw JSON text blob (Postel's Law — zero
key-name assumptions on upstream shape) and emits its own structured
output containing language + a flat per-line TTS worklist
(line_id, segment_id, text, pause_after_ms). The actual TTS — per-line
synthesis, ffmpeg concat with pauses, per-segment timing aggregation,
SRT assembly — happens in ``NarratorMaterializer``; this layer only
owns the worklist.

Why an LLM instead of ``json.loads()``: the previous version hard-coded
``content.segments[].lines[].text`` access into the producer's schema,
violating the project-wide "对外宽进" (Postel's Law) rule. A single
upstream rename or restructure would silently produce an empty TTS
worklist. Routing the parse through this agent's own LLM lets the
system tolerate upstream drift the same way ScreenplayAgent tolerates
StoryAgent drift.
"""

from __future__ import annotations

from typing import Any

from ..base_agent import BaseAgent
from .schema import (
    NarratorAgentInput,
    NarratorAgentOutput,
)


# Output template the LLM follows. Shows only the fields the LLM should
# fill — clips / segment_timings / srt_text / total_duration_sec /
# speaker are post-materialize fields populated by NarratorMaterializer.
NARRATOR_OUTPUT_TEMPLATE = """{
  "content": {
    "language": "<ISO-ish language tag of the script, e.g. 'en' or 'zh'>",
    "lines": [
      {
        "line_id": "ln_001",
        "segment_id": "seg_001",
        "text": "<verbatim spoken line text>",
        "pause_after_ms": 0
      },
      {
        "line_id": "ln_002",
        "segment_id": "seg_001",
        "text": "...",
        "pause_after_ms": 500
      }
    ]
  },
  "metrics": {
    "line_count": 2,
    "segment_count": 1
  }
}"""


class NarratorAgent(BaseAgent[NarratorAgentInput, NarratorAgentOutput]):

    async def generate(
        self,
        input_data: NarratorAgentInput,
        *,
        rework_notes: str = "",
    ) -> NarratorAgentOutput:
        """Single full-output LLM call from the narration script JSON text blob."""
        output = await self._llm_fill_full(input_data, rework_notes)
        self.recompute_metrics(output)
        return output

    def system_prompt(self) -> str:
        return (
            "You are NarratorAgent: extract a flat TTS line worklist from "
            "an upstream narration script. The downstream materializer takes "
            "your output and synthesizes one audio clip per line via a TTS "
            "API, then concatenates them with the requested pauses.\n\n"
            "=== WHEN TO REJECT UPSTREAM INPUT ===\n"
            "Use the shared input_rejection escape hatch ONLY if the "
            "narration script is structurally unusable. Concretely, reject "
            "when ANY of these is true after reading "
            "narration_script_json_text carefully:\n"
            "  * narration_script_json_text is empty, whitespace-only, or "
            "an empty JSON object — there is literally nothing to read aloud.\n"
            "  * No segment-or-line structure anywhere: no segments / "
            "scenes / parts / chapters / pages array, AND no top-level "
            "lines / sentences / utterances array — there is no readable "
            "unit.\n"
            "  * No spoken text whatsoever: not a single field across the "
            "whole document carries narrator-readable prose (no text / "
            "narration_text / sentence / utterance or anything similar).\n"
            "When you reject, populate the rejection fields:\n"
            "  * reason: the single most specific defect.\n"
            "  * missing_labels: ['narration_script'].\n"
            "  * offending_fields: the field paths you looked at, e.g. "
            "['content.segments', 'content.lines', 'content.text'].\n"
            "If the script is merely sparse (e.g. a single segment with one "
            "line) — DO NOT reject; proceed and produce that one line.\n\n"
            "=== INPUT FORMAT ===\n"
            "You will receive the upstream NarrationAgent output as a RAW "
            "JSON TEXT BLOB inside the user message. Do NOT assume specific "
            "field names in advance. READ the JSON, understand whatever shape "
            "it happens to have, and extract:\n"
            "  1. The script's language tag (typical names: language / lang "
            "/ locale / target_language). If absent, infer from the prose "
            "text itself (Chinese characters → 'zh', English alphabet → 'en', "
            "etc.).\n"
            "  2. A flat list of TTS lines. Walk the segments / scenes / "
            "parts container; for each segment, walk its lines / sentences "
            "/ utterances container; for each line, capture line_id, "
            "segment_id (the parent segment), text (verbatim, the exact "
            "string the TTS engine should pronounce), and pause_after_ms "
            "(integer pause inserted AFTER this line; default 0).\n\n"
            "=== OUTPUT FORMAT ===\n"
            "JSON only; no markdown; match the user-message template "
            "exactly. Use empty string or empty list for unknowns, never "
            "null.\n\n"
            "=== ID CONVENTIONS ===\n"
            "line_id: ln_001, ln_002, ... GLOBALLY sequential across the "
            "entire script (never restart at segment boundary), 3-digit "
            "zero-padded. If upstream provides ln_NNN ids, REUSE them; "
            "otherwise number in declaration order.\n"
            "segment_id: seg_001, seg_002, ... matching the parent segment "
            "id, 3-digit zero-padded. Reuse upstream seg_NNN ids verbatim "
            "if present, else renumber.\n\n"
            "=== STRUCTURAL REQUIREMENTS ===\n"
            "content.language: non-empty short tag (e.g. 'en', 'zh', "
            "'es'); NOT a full sentence and NOT a placeholder.\n"
            "content.lines: at least one entry; every entry's text is a "
            "non-empty string the TTS engine will read verbatim.\n"
            "pause_after_ms: non-negative integer (use 0 if unspecified, "
            "common values 200-800 for natural beats).\n"
            "Do NOT include an artifact_caption block — the system generates "
            "it automatically."
        )

    def build_user_prompt(self, input_data: NarratorAgentInput) -> str:
        return (
            "Read the upstream narration script below and produce a flat "
            "TTS worklist (one entry per line).\n\n"
            "=== NARRATION SCRIPT (raw JSON — read the shape before writing) ===\n"
            f"{input_data.narration_script_json_text}\n"
            "=== END NARRATION SCRIPT ===\n\n"
            "Extract from the script:\n"
            "  - the script language\n"
            "  - per-line {line_id, segment_id (parent), text, pause_after_ms}\n\n"
            "Produce the full TTS worklist JSON in EXACTLY this shape:\n\n"
            f"{NARRATOR_OUTPUT_TEMPLATE}\n\n"
            "Return JSON only."
        )

    def parse_output(self, raw: dict[str, Any]) -> NarratorAgentOutput:
        return NarratorAgentOutput.model_validate(raw)

    def recompute_metrics(self, output: NarratorAgentOutput) -> None:
        """Pure derived counts; LLM is not asked to compute them independently."""
        lines = output.content.lines
        output.metrics.line_count = len(lines)
        output.metrics.segment_count = len({line.segment_id for line in lines if line.segment_id})
