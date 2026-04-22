"""NarrationAgent — illustrated-storytelling creative head.

Input:  NarrationAgentInput  (creative_brief_json_text)
Output: NarrationAgentOutput (language, overall_style, segments[{image_prompt, lines[...]}])

One LLM call produces the full narrator-voice script in a single pass so
cross-segment consistency (character names, art style, narrative voice)
is a natural consequence of writing everything at once. Downstream
IllustrationAgent and NarratorAgent both consume this single artifact.

Not to be confused with the old NarrationAgent retired in 2026-04 —
that one wrote per-scene cinematic voiceover lines for screenplay flows.
This one is for pure audiobook / illustrated-storytelling flows where
the whole video is (image_sequence + narrator_audio + burned_SRT) with
no Screenplay / KeyFrame / VideoAgent chain in front.
"""

from __future__ import annotations

from ..base_agent import BaseAgent
from .schema import NarrationAgentInput, NarrationAgentOutput


NARRATION_OUTPUT_TEMPLATE = """{
  "content": {
    "language": "<IETF tag e.g. 'zh-CN' or 'en-US'>",
    "overall_style": "<3-8 words art-style string, e.g. 'watercolor storybook, warm palette, soft edges'>",
    "segments": [
      {
        "segment_id": "seg_001",
        "image_prompt": "<stand-alone scene description for one illustration; subject + setting + mood + key objects; NO art-style words (those come from overall_style)>",
        "lines": [
          {
            "line_id": "ln_001",
            "text": "<one narrator sentence, written for the ear>",
            "pause_after_ms": 0
          }
        ]
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
            "You are NarrationAgent: read a user's creative brief (a short "
            "idea OR a long already-written prose / outline) and produce a "
            "NARRATOR-VOICE audiobook script for an illustrated storytelling "
            "video. Your output drives both the TTS narrator audio and the "
            "illustration image generation — you are the creative head of "
            "this whole chain.\n\n"
            "=== WHEN TO REJECT UPSTREAM INPUT ===\n"
            "Use the shared input_rejection escape hatch (see the UPSTREAM "
            "INPUT REJECTION block above) ONLY if the brief makes your job "
            "impossible. Reject when:\n"
            "  * creative_brief_json_text is empty, whitespace-only, or an "
            "empty JSON object — no user intent to work with.\n"
            "  * The JSON contains no textual seed anywhere (no "
            "content.text / summary / brief / prompt / description fields "
            "carry non-empty text).\n"
            "When you reject, populate:\n"
            "  * reason: the single most specific defect.\n"
            "  * missing_labels: ['creative_brief'].\n"
            "  * offending_fields: e.g. ['content.text'].\n"
            "Short / vague brief is NOT a reject reason — expanding sparse "
            "prompts is part of this agent's job.\n"
            "=== END WHEN TO REJECT UPSTREAM INPUT ===\n\n"
            "=== INPUT FORMAT ===\n"
            "You receive the brief as a RAW JSON TEXT BLOB in the user "
            "message. The text is typically at ``content.text`` but do NOT "
            "assume that path — read the JSON and find the creative intent "
            "from whatever shape it has. Treat the full text as "
            "authoritative: if the user supplied a long detailed prose, "
            "preserve its specific characters, locations, and plot beats "
            "verbatim in your narration rather than compressing them into "
            "a generic retelling.\n\n"
            "=== OUTPUT CONTRACT ===\n"
            "You produce THREE things in one JSON document:\n"
            "  1. language (IETF tag)\n"
            "  2. overall_style (cross-segment art-style anchor)\n"
            "  3. segments[] — each = ONE illustration + 3-8 narrator lines\n\n"
            "LANGUAGE: detect from the brief content. Write a full IETF "
            "tag like 'zh-CN' or 'en-US', not just 'zh' or 'en'.\n\n"
            "OVERALL_STYLE: a short visual-style string (3-8 words) "
            "defining the picture-book art style used for ALL illustrations. "
            "Example: 'watercolor storybook, warm palette, soft edges, "
            "dusky lighting'. This string is prepended to every "
            "illustration prompt downstream, so it is the single lever for "
            "cross-segment visual consistency. Pick a style that fits the "
            "story's mood and stay consistent.\n\n"
            "SEGMENTS (aim for 8-15; shorter stories may have 5-8, long "
            "ones may reach 20+):\n"
            "  * Cut where the VISUAL changes — new location, new focal "
            "subject, major mood shift. One segment = one picture's worth "
            "of story.\n"
            "  * If the story stays in a single continuous moment for 10+ "
            "narrator sentences, split into multiple segments anyway — we "
            "don't want to stare at one image too long.\n"
            "  * Typical segment length: 3-8 lines of narration.\n\n"
            "  segment_id: seg_001, seg_002, ... (3-digit zero-padded, "
            "1-indexed, strictly sequential. No gaps, no resets).\n"
            "  image_prompt: stand-alone scene description for ONE "
            "illustration — subject, setting, mood, key objects. Specific "
            "enough that an image model can generate it without seeing the "
            "story. DO NOT include art-style words here (those belong in "
            "overall_style and will be prepended automatically). DO NOT "
            "reference 'the previous image' or similar — each prompt is "
            "self-contained.\n"
            "  lines: 3-8 narrator sentences that play while this "
            "illustration is on screen.\n\n"
            "LINES (the text the TTS engine will actually speak):\n"
            "  line_id: ln_001, ln_002, ... GLOBALLY sequential across "
            "ALL segments — do NOT reset per segment. If segment 1 has 4 "
            "lines, segment 2 starts at ln_005.\n"
            "  text: write for the EAR, not the eye. Short-to-medium "
            "sentences. Minimal nested clauses. Clear rhythm. Avoid "
            "ambiguous homophones. Use punctuation the TTS engine will "
            "interpret (periods, commas, question marks).\n"
            "  pause_after_ms:\n"
            "    * 0 for most lines (flowing prose).\n"
            "    * 300-600 for paragraph breaks within a segment.\n"
            "    * 800-1200 for dramatic pauses / major shifts.\n"
            "    Keep MOST at 0 — accumulated pauses make the audio feel "
            "halting.\n\n"
            "NARRATIVE VOICE: third-person narrator describing the story "
            "to a listener. Past tense unless the brief clearly dictates "
            "present. Gentle, story-book tone by default — adjust to match "
            "genre cues in the brief (suspense, whimsy, melancholy, etc.).\n\n"
            "JSON only; no markdown. Do NOT include an artifact_caption "
            "block — the system generates it automatically."
        )

    def build_user_prompt(self, input_data: NarrationAgentInput) -> str:
        return (
            "Produce the illustrated-storytelling narration script from "
            "the creative brief below.\n\n"
            "=== CREATIVE BRIEF (raw JSON — read the text from it) ===\n"
            f"{input_data.creative_brief_json_text}\n"
            "=== END CREATIVE BRIEF ===\n\n"
            "Read the brief carefully:\n"
            "- If it is SHORT or VAGUE ('a story about a lonely "
            "lighthouse keeper'), expand it into a full story with "
            "concrete characters, setting, and arc, then narrate.\n"
            "- If it is a LONG PROSE / OUTLINE with specific characters "
            "and plot beats, PRESERVE those elements verbatim in the "
            "narration, just reshape the sentences for TTS cadence and "
            "segment the story for visual beats.\n\n"
            "Output JSON exactly matching this template (fill in content, "
            "keep the structure):\n\n"
            f"{NARRATION_OUTPUT_TEMPLATE}\n\n"
            "Verify before returning:\n"
            "- segment_ids are seg_001, seg_002, ... with no gaps.\n"
            "- line_ids are ln_001, ln_002, ... GLOBALLY sequential across "
            "every segment.\n"
            "- overall_style and language are non-empty.\n"
            "- every image_prompt is a stand-alone scene description (not "
            "'continue from above').\n\n"
            "Return JSON only."
        )

    def recompute_metrics(self, output: NarrationAgentOutput) -> None:
        """Pure derived counts — LLM is not asked to fill these in."""
        c = output.content
        output.metrics.segment_count = len(c.segments)
        output.metrics.line_count = sum(len(s.lines) for s in c.segments)
        output.metrics.total_chars = sum(
            len(line.text) for s in c.segments for line in s.lines
        )
