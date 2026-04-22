"""StoryAgent — expands a natural-language creative brief into a Story Blueprint.

Input:  StoryAgentInput  (creative_brief)
Output: StoryAgentOutput (Story Blueprint with logline, cast, locations,
        story_arc, scene_outline, metrics)

Single unified input path: ``creative_brief`` arrives via the
InputResolver-selected ``[creative_brief]`` label.  The LLM
autonomously decides whether the input is a short prompt to expand
creatively or a detailed outline to structure faithfully — both cases
use the same prompt.
"""

from __future__ import annotations

from ..base_agent import BaseAgent
from .schema import StoryAgentInput, StoryAgentOutput

STORY_OUTPUT_TEMPLATE = """{
  "content": {
    "logline": "<one-sentence story hook>",
    "style": {
      "genre": ["<genre1>", "<genre2>"],
      "tone_keywords": ["<tone1>", "<tone2>"]
    },
    "cast": [
      {
        "character_id": "char_001",
        "name": "<name>",
        "role": "protagonist|antagonist|support",
        "profile": "<narrative portrait>",
        "motivation": "<what drives them>",
        "flaw": "<what holds them back>"
      }
    ],
    "locations": [
      {
        "location_id": "loc_001",
        "name": "<name>",
        "description": "<description>"
      }
    ],
    "story_arc": [
      {
        "step_id": "arc_001",
        "order": 1,
        "step_type": "setup|inciting|turn|crisis|climax|resolution",
        "summary": "<what happens>",
        "conflict": "<core tension>",
        "turning_point": "<what changes>"
      }
    ],
    "scene_outline": [
      {
        "scene_id": "sc_001",
        "order": 1,
        "linked_step_id": "arc_001",
        "location_id": "loc_001",
        "time_of_day_hint": "DAY|NIGHT|CUSTOM",
        "characters_present": ["char_001"],
        "goal": "<scene goal>",
        "conflict": "<scene conflict>",
        "turn": "<scene turn>"
      }
    ]
  }
}"""


class StoryAgent(BaseAgent[StoryAgentInput, StoryAgentOutput]):

    # ------------------------------------------------------------------
    # Prompts
    # ------------------------------------------------------------------

    def system_prompt(self) -> str:
        return (
            "You are StoryAgent: produce a Story Blueprint (top-level key `content`).\n"
            "No dialogue/screenplay prose, shots, camera, keyframes, audio, or editing.\n"
            "IDs: char_001, loc_001, arc_001, sc_001, … — JSON only per user template; "
            "use empty string/list for unknowns, not null; no meta/metrics.\n\n"
            "=== WHEN TO REJECT UPSTREAM INPUT ===\n"
            "Use the shared input_rejection escape hatch (see the UPSTREAM "
            "INPUT REJECTION block above) ONLY if the creative brief makes "
            "your job impossible. Concretely, reject when ANY of these is "
            "true after you have read the creative_brief_json_text "
            "carefully:\n"
            "  * creative_brief_json_text is empty, whitespace-only, or "
            "an empty JSON object — there is literally no user intent to "
            "expand.\n"
            "  * No textual creative intent anywhere: no text / summary / "
            "content / brief / prompt / description fields are present "
            "with non-empty content. A story needs SOME seed of intent — "
            "even one sentence ('a film about a cat') is enough to "
            "proceed.\n"
            "When you reject, populate the rejection fields like this:\n"
            "  * reason: the single most specific defect (e.g. 'creative "
            "brief payload is empty — no story seed to expand').\n"
            "  * missing_labels: ['creative_brief'] (my only input label).\n"
            "  * offending_fields: the field paths you looked at and "
            "found empty, e.g. ['content.text'].\n"
            "If the brief is merely short or vague — DO NOT reject; "
            "expanding short prompts into rich blueprints is exactly what "
            "this agent is for.\n"
            "=== END WHEN TO REJECT UPSTREAM INPUT ===\n\n"
            "=== INPUT FORMAT ===\n"
            "You will receive the upstream creative brief as a RAW JSON TEXT BLOB "
            "inside the user message. The brief text is typically inside a "
            "``content.text`` field, but do NOT assume that exact path — READ the "
            "JSON and find the user's creative intent from whatever shape it has. "
            "Treat the full text as authoritative: if the user supplied a long "
            "detailed outline, read it in its entirety and preserve its specific "
            "elements verbatim rather than compressing into a generic blueprint.\n\n"
            "scene_outline.linked_step_id rule (CRITICAL — read carefully):\n"
            "  * `linked_step_id` MUST be a SINGLE arc step id (a string like \"arc_001\"),\n"
            "    NEVER a list. The schema only accepts one string per scene.\n"
            "  * If a scene dramatizes multiple arc steps in one continuous visual moment,\n"
            "    set `linked_step_id` to the SINGLE most central arc step — usually its\n"
            "    climactic beat (climax / turn) or its inciting moment, NOT its setup. The\n"
            "    other arc steps the scene also covers are still expressed via the scene's\n"
            "    `goal / conflict / turn` text fields.\n\n"
            "Do NOT include an artifact_caption block — the system generates it automatically."
        )

    def build_user_prompt(self, input_data: StoryAgentInput) -> str:
        """Single unified prompt — handles both brief prompts and detailed outlines.

        The LLM reads the user's instruction and autonomously decides:
          * If brief / vague → expand creatively into a full blueprint.
          * If a detailed outline (with named characters, scenes, beats) →
            preserve the user's specific elements verbatim and fill in
            structural fields (motivation, flaw, conflict, turning_point)
            without rewriting.
        """
        parts = [
            "=== CREATIVE BRIEF (raw JSON — read the text from it) ===\n"
            f"{input_data.creative_brief_json_text}\n"
            "=== END CREATIVE BRIEF ===\n\n"
        ]
        if input_data.reference_analysis_json_text:
            parts.append(
                "=== REFERENCE VIDEO ANALYSIS (inspiration — use as "
                "tone / genre / pacing seed, do NOT copy plot verbatim) ===\n"
                f"{input_data.reference_analysis_json_text}\n"
                "=== END REFERENCE ANALYSIS ===\n\n"
            )
        parts.append(
            "Read the brief JSON carefully and find the user's intent:\n"
            "- If the brief is short or vague (e.g. 'a film about a cat "
            "chasing a butterfly'), expand it creatively into a full "
            "blueprint with cast, locations, arc, and scene outline.\n"
            "- If it is a DETAILED OUTLINE with specific characters, locations, "
            "or plot beats, PRESERVE those elements verbatim. Map the beats "
            "into story_arc (setup/inciting/turn/crisis/climax/resolution). "
            "Fill in any missing structural fields (motivation, flaw, conflict, "
            "turning_point, scene goal/conflict/turn) WITHOUT rewriting what "
            "the brief already specified.\n"
            "- If a REFERENCE VIDEO ANALYSIS block is supplied, blend its "
            "genre / mood / entities / scene rhythm into the new blueprint "
            "as inspiration for tone and pacing; do NOT lift its plot "
            "verbatim — the new story must be a distinct work.\n\n"
            "Infer language from the brief; default to English if unspecified.\n\n"
            f"Output JSON exactly like this template (replace placeholders):\n"
            f"{STORY_OUTPUT_TEMPLATE}\n\n"
            "Verify: scene_outline location_ids ⊆ locations; referenced character_ids "
            "⊆ cast; story_arc and scene_outline orders start at 1 and are contiguous. "
            "IDs: char_001, loc_001, arc_001, sc_001.\n"
            "Return JSON only."
        )
        return "".join(parts)

    async def generate(
        self,
        input_data: StoryAgentInput,
        *,
        rework_notes: str = "",
    ) -> StoryAgentOutput:
        """One LLM call generates the full story blueprint from the brief."""
        output = await self._llm_fill_full(input_data, rework_notes)
        self.recompute_metrics(output)
        return output

    def recompute_metrics(self, output: StoryAgentOutput) -> None:
        """Derive summary metrics from content — pure derived data, zero rewrites.

        All LLM-authored fields (story_arc[].order, scene_outline[].order,
        ids, …) are left untouched; StoryEvaluator enforces their
        invariants via structural checks + rework. The ``metrics`` field
        is hidden from the user-message template, so populating it here
        is derivation, not a silent patch-up of LLM output.
        """
        c = output.content
        output.metrics.character_count = len(c.cast)
        output.metrics.location_count = len(c.locations)
        output.metrics.scene_count = len(c.scene_outline)

    # Quality evaluation has been moved to StoryEvaluator
    # (see evaluator.py in this package).
