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

from typing import Any

from ..base_agent import BaseAgent
from .schema import StoryAgentInput, StoryAgentOutput

STORY_OUTPUT_TEMPLATE = """{
  "artifact_caption": {
    "what": "<1-2 sentences: genre, characters, scene count>",
    "why": "<key creative choices: tone, style, structure>",
    "scope": "global"
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
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    # ------------------------------------------------------------------
    # Prompts
    # ------------------------------------------------------------------

    def system_prompt(self) -> str:
        return (
            "You are StoryAgent: produce a Story Blueprint (top-level keys `content` and `artifact_caption`).\n"
            "No dialogue/screenplay prose, shots, camera, keyframes, audio, or editing.\n"
            "IDs: char_001, loc_001, arc_001, sc_001, … — JSON only per user template; "
            "use empty string/list for unknowns, not null; no meta/metrics.\n\n"
            "Length budget: this pipeline produces SHORT cinematic videos (typically "
            "30 seconds, never longer than ~60 seconds). Stay tightly within that budget:\n"
            "  * scene_outline: 1 scene by default; use 2 only when the story genuinely needs a setting change.\n"
            "  * Never exceed 2 scenes total.\n"
            "  * Use the scene's `goal / conflict / turn` fields to carry beats — do NOT manufacture\n"
            "    extra scenes just to subdivide the action.\n"
            "  * cast: 1-2 characters; locations: 1-2; story_arc: 3-5 steps.\n\n"
            "artifact_caption: fill all three fields to describe what you produced:\n"
            "  what — 1-2 sentences on the story (genre, characters, scenes).\n"
            "  why  — key creative choices (tone, style, structure decisions).\n"
            "  scope — always \"global\" for StoryAgent."
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
        return (
            "Creative brief (may be a brief idea or a detailed outline):\n"
            "=== CREATIVE BRIEF ===\n"
            f"{input_data.creative_brief}\n"
            "=== END ===\n\n"
            "Read the brief carefully:\n"
            "- If it is a SHORT or VAGUE prompt (e.g. 'make a 30s film about a "
            "cat chasing a butterfly'), expand it creatively into a full "
            "blueprint with cast, locations, arc, and scene outline.\n"
            "- If it is a DETAILED OUTLINE with specific characters, locations, "
            "or plot beats, PRESERVE those elements verbatim. Map the beats "
            "into story_arc (setup/inciting/turn/crisis/climax/resolution). "
            "Fill in any missing structural fields (motivation, flaw, conflict, "
            "turning_point, scene goal/conflict/turn) WITHOUT rewriting what "
            "the brief already specified.\n\n"
            "Infer language from the brief; default to English if unspecified. "
            "Cast size, arc, and scene count must fit the SHORT-video budget defined "
            "in the system prompt: prefer 1 scene, never more than 2.\n\n"
            f"Output JSON exactly like this template (replace placeholders):\n"
            f"{STORY_OUTPUT_TEMPLATE}\n\n"
            "Verify: scene_outline location_ids ⊆ locations; referenced character_ids "
            "⊆ cast; story_arc and scene_outline orders start at 1 and are contiguous. "
            "IDs: char_001, loc_001, arc_001, sc_001.\n"
            "Return JSON only."
        )

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
        c = output.content
        self._normalize_order(c.story_arc)
        self._normalize_order(c.scene_outline)
        output.metrics.character_count = len(c.cast)
        output.metrics.location_count = len(c.locations)
        output.metrics.scene_count = len(c.scene_outline)

    # Quality evaluation has been moved to StoryEvaluator
    # (see evaluator.py in this package).
