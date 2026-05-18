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
  "meta": {
    "language": "<ISO 639-1 code: zh / en / ja / fr / es / ...>"
  },
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
            "=== SCENE BUDGET ===\n"
            "Produce 3-5 scenes in scene_outline by default for short-form work "
            "(mini-drama / trailer / ad / short narration / illustrated audiobook). "
            "Each scene must carry significant dramatic weight — don't split fragments "
            "into separate scenes. NEVER exceed 5 scenes unless the user EXPLICITLY "
            "asks for episodic / multi-act / long-form work (e.g. 'episode breakdown', "
            "'12-episode', 'feature-length'). 5 scenes × ~3 shots/scene aligns with "
            "the downstream screenplay's 15-shot ceiling.\n"
            "=== END SCENE BUDGET ===\n\n"
            "=== PRESERVE SETTING-SPECIFIC ANCHORS ===\n"
            "A creative brief usually pins the work to a specific setting — a real "
            "or fictional historical era, geographic region, cultural milieu, "
            "technology level, or subgenre. When such anchors exist in the brief, "
            "preserve them VERBATIM in the blueprint. Do NOT replace a specific "
            "term with a generic one (do not collapse a named era into 'ancient', "
            "a named region into 'the East', a named subgenre into 'futuristic'). "
            "Generic descriptors are losslessly upcastable from specifics, never "
            "the other way around — once dropped, downstream stages cannot recover "
            "the original anchor.\n"
            "Carry the anchor through at least:\n"
            "  * every relevant cast[].profile — name the setting the character "
            "belongs to, not just their archetype\n"
            "  * every relevant locations[].description — name the setting of the "
            "location, not just its type\n"
            "  * style.tone_keywords — include the anchor itself as a keyword\n"
            "Why this matters: downstream agents see only the blueprint, not your "
            "original brief. When the blueprint generalizes the setting away, the "
            "image and video stages have to re-imagine it from neutral terms, "
            "which collapses to whatever is most prevalent in their training "
            "distribution — usually a default that conflicts with the user's "
            "intent.\n"
            "=== END PRESERVE SETTING-SPECIFIC ANCHORS ===\n\n"
            "=== LANGUAGE ANCHOR ===\n"
            "Set meta.language to the ISO 639-1 code of the asset's primary "
            "language — the language in which the story will be told "
            "(dialogue, narration, on-screen titles). Source priority:\n"
            "  1. If the brief explicitly names a target language, honor "
            "that.\n"
            "  2. Otherwise, infer from the setting anchor you preserved "
            "above — the language naturally / historically associated "
            "with that era, region, or culture.\n"
            "  3. Default 'en' only when neither signal exists (the brief "
            "is modern / abstract / culturally-unmarked).\n"
            "This anchor flows downstream: the screenplay copies it "
            "verbatim, and the video / audio gen stages use it to keep "
            "all spoken content — including ambient voices the model may "
            "auto-generate — in one language. A wrong language here "
            "causes the same distribution-default drift that PRESERVE "
            "SETTING-SPECIFIC ANCHORS exists to prevent.\n"
            "=== END LANGUAGE ANCHOR ===\n\n"
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
            "JSON and find the user's creative intent from whatever shape it has.\n\n"
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
