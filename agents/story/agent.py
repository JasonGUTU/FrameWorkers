"""StoryAgent — expands a draft idea into a Story Blueprint.

Input:  StoryAgentInput  (project_id, draft_id, draft_idea)
Output: StoryAgentOutput (Story Blueprint with logline, cast, locations,
        story_arc, scene_outline, metrics)

Coupling: receives draft_idea from Orchestrator; output feeds ScreenplayAgent.
"""

from __future__ import annotations

from typing import Any

from ..base_agent import BaseAgent
from .schema import StoryAgentInput, StoryAgentOutput

STORY_OUTPUT_TEMPLATE = """{
  "content": {
    "logline": "<one-sentence story hook>",
    "estimated_duration": { "seconds": 60.0, "confidence": 0.7 },
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
            "You are StoryAgent. "
            "Task: Expand a brief draft idea into a Story Blueprint (story_blueprint).\n"
            "The blueprint answers: what the story is, why it works, and how it unfolds at scene level.\n\n"
            "You MUST:\n"
            "- Keep scope and cast/location counts realistic.\n"
            "- Ensure dramatic viability: clear conflict, stakes, turning points, resolution.\n"
            "- Produce cast, locations, story_arc, and scene_outline with consistent IDs.\n"
            "- Use IDs: char_001, loc_001, arc_001, sc_001, etc.\n\n"
            "You MUST NOT:\n"
            "- Write dialogue lines or screenplay blocks.\n"
            "- Describe shots/camera, keyframes, audio, or editing.\n"
            "- Mention any agent names.\n\n"
            "Output Rules:\n"
            "- Return JSON only, no markdown, no code fences.\n"
            "- Do not include trailing comments.\n"
            "- If something is unknown, use empty string or empty list, not null.\n"
            "- You MUST follow EXACTLY the JSON structure template provided in the user prompt.\n"
            "- The output MUST have a single top-level key: content.\n"
            "- Do NOT include \"meta\" or \"metrics\" blocks — both are injected by the system.\n"
            "- You MUST include \"estimated_duration\" inside content with your best estimate."
        )

    def build_user_prompt(self, input_data: StoryAgentInput) -> str:
        if input_data.user_provided_text:
            return self._build_structuring_prompt(input_data)
        return self._build_generate_prompt(input_data)

    def _build_generate_prompt(self, input_data: StoryAgentInput) -> str:
        """User prompt for generation mode (brief draft idea → blueprint)."""
        return (
            f"Draft idea (raw): {input_data.draft_idea}\n\n"
            f"project_id: {input_data.project_id}\n"
            f"draft_id: {input_data.draft_id}\n\n"
            f"Constraints:\n"
            f"- Target duration: 60 seconds (estimate)\n"
            f"- Language: en\n\n"
            f"You MUST output JSON matching EXACTLY this structure (fill in real content):\n"
            f"{STORY_OUTPUT_TEMPLATE}\n\n"
            "Self-check before finalizing:\n"
            "- Every scene_outline[i].location_id exists in locations[]\n"
            "- Every character_id referenced exists in cast[]\n"
            "- story_arc order is continuous starting at 1\n"
            "- scene_outline order is continuous starting at 1\n\n"
            "Return JSON only."
        )

    def _build_structuring_prompt(self, input_data: StoryAgentInput) -> str:
        """User prompt for structuring mode (detailed outline → blueprint).

        The LLM maps the user's existing characters, locations, and plot
        points into the Story Blueprint schema while preserving them
        verbatim.  It fills in any missing structural fields (motivation,
        flaw, conflict, turning_point) but does NOT rewrite what the user
        already provided.
        """
        return (
            "=== STRUCTURING MODE ===\n"
            "You have received a DETAILED STORY OUTLINE from the user.  "
            "Your task is to STRUCTURE it into the Story Blueprint JSON "
            "schema — NOT to rewrite or reinvent the story.\n\n"
            "RULES:\n"
            "- PRESERVE the user's character names, locations, and plot "
            "points VERBATIM.  Do not rename, merge, or drop them.\n"
            "- Map the user's plot arc / beats into story_arc steps with "
            "appropriate step_type (setup / inciting / turn / crisis / "
            "climax / resolution).\n"
            "- Map the user's scene breakdown (if provided) into "
            "scene_outline entries.  If no explicit scenes are given, "
            "derive them from the plot arc (one scene per major beat).\n"
            "- Fill in any MISSING fields that the user did not provide:\n"
            "  - logline: summarise the story in one sentence\n"
            "  - style.genre, style.tone_keywords\n"
            "  - cast[].profile, cast[].motivation, cast[].flaw "
            "(infer from context)\n"
            "  - locations[].description (infer from context)\n"
            "  - story_arc[].conflict, story_arc[].turning_point\n"
            "  - scene_outline[].goal, scene_outline[].conflict, "
            "scene_outline[].turn\n"
            "- Assign stable IDs: char_001, loc_001, arc_001, sc_001, etc.\n"
            "- Keep scope realistic for a ~60 second video.\n\n"
            "=== USER-PROVIDED STORY OUTLINE ===\n"
            f"{input_data.user_provided_text}\n"
            "=== END USER OUTLINE ===\n\n"
            f"project_id: {input_data.project_id}\n"
            f"draft_id: {input_data.draft_id}\n\n"
            f"You MUST output JSON matching EXACTLY this structure:\n"
            f"{STORY_OUTPUT_TEMPLATE}\n\n"
            "Self-check before finalizing:\n"
            "- Every scene_outline[i].location_id exists in locations[]\n"
            "- Every character_id referenced exists in cast[]\n"
            "- story_arc order is continuous starting at 1\n"
            "- scene_outline order is continuous starting at 1\n"
            "- Character names match the user's original names exactly\n"
            "- Location names match the user's original names exactly\n\n"
            "Return JSON only."
        )

    def recompute_metrics(self, output: StoryAgentOutput) -> None:
        c = output.content
        self._normalize_order(c.story_arc)
        self._normalize_order(c.scene_outline)
        output.metrics.character_count = len(c.cast)
        output.metrics.location_count = len(c.locations)
        output.metrics.scene_count = len(c.scene_outline)

    # Quality evaluation has been moved to StoryEvaluator
    # (see evaluator.py in this package).
