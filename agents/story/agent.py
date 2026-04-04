"""StoryAgent — expands source text into a Story Blueprint.

Input:  StoryAgentInput  (draft_idea, constraints, user_provided_text)
Output: StoryAgentOutput (Story Blueprint with logline, cast, locations,
        story_arc, scene_outline, metrics)

Coupling: receives canonical `source_text` from orchestrator (mapped to
`StoryAgentInput.draft_idea` in descriptor); output feeds ScreenplayAgent.
"""

from __future__ import annotations

from typing import Any

from ..base_agent import BaseAgent
from .schema import StoryAgentInput, StoryAgentOutput

STORY_OUTPUT_TEMPLATE = """{
  "content": {
    "logline": "<one-sentence story hook>",
    "estimated_duration": { "seconds": 10.0, "confidence": 0.7 },
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
        self._target_duration_sec: float = 10.0

    # ------------------------------------------------------------------
    # Prompts
    # ------------------------------------------------------------------

    def system_prompt(self) -> str:
        return (
            "You are StoryAgent: produce a Story Blueprint (top-level key `content` only).\n"
            "No dialogue/screenplay prose, shots, camera, keyframes, audio, or editing.\n"
            "IDs: char_001, loc_001, arc_001, sc_001, … — JSON only per user template; "
            "use empty string/list for unknowns, not null; no meta/metrics; "
            "include content.estimated_duration."
        )

    def build_user_prompt(self, input_data: StoryAgentInput) -> str:
        if input_data.user_provided_text:
            return self._build_structuring_prompt(input_data)
        return self._build_generate_prompt(input_data)

    def _build_generate_prompt(self, input_data: StoryAgentInput) -> str:
        """User prompt for generation mode (brief draft idea → blueprint)."""
        self._target_duration_sec = 10.0
        return (
            f"Draft idea (raw): {input_data.draft_idea}\n\n"
            "Infer length and language from the draft only; if unspecified use ~10s and English. "
            "Scale cast, arc, and scene count to that length. "
            "Set content.estimated_duration.seconds to your total-runtime estimate.\n\n"
            f"Output JSON exactly like this template (replace placeholders):\n"
            f"{STORY_OUTPUT_TEMPLATE}\n\n"
            "Verify: scene_outline location_ids ⊆ locations; referenced character_ids ⊆ cast; "
            "story_arc and scene_outline orders start at 1 and are contiguous; estimated_duration > 0.\n"
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
        self._target_duration_sec = 10.0
        return (
            "STRUCTURING MODE: map the user's outline into the Story Blueprint JSON — "
            "preserve names, locations, and plot beats verbatim; do not rewrite the story.\n"
            "Map beats → story_arc (setup/inciting/turn/crisis/climax/resolution); "
            "scenes from the user or one per major beat if missing.\n"
            "Infer missing fields (logline, style, cast profile/motivation/flaw, "
            "location descriptions, arc conflict/turning_point, scene goal/conflict/turn). "
            "IDs: char_001, loc_001, arc_001, sc_001. Length/language from outline; else ~10s, English. "
            f"estimated_duration within ~±20% of {input_data.constraints.target_duration_sec}s.\n\n"
            "=== USER OUTLINE ===\n"
            f"{input_data.user_provided_text}\n"
            "=== END ===\n\n"
            f"Output JSON:\n{STORY_OUTPUT_TEMPLATE}\n\n"
            "Verify: IDs consistent; names preserved; orders from 1; estimated_duration in range.\n"
            "Return JSON only."
        )

    def recompute_metrics(self, output: StoryAgentOutput) -> None:
        c = output.content
        self._normalize_order(c.story_arc)
        self._normalize_order(c.scene_outline)
        est = getattr(c, "estimated_duration", None)
        if est is not None:
            sec = getattr(est, "seconds", None)
            if sec is not None:
                try:
                    s = float(sec)
                    if s > 0:
                        self._target_duration_sec = s
                except (TypeError, ValueError):
                    pass
        output.metrics.target_duration_sec = self._target_duration_sec
        output.metrics.character_count = len(c.cast)
        output.metrics.location_count = len(c.locations)
        output.metrics.scene_count = len(c.scene_outline)

    # Quality evaluation has been moved to StoryEvaluator
    # (see evaluator.py in this package).
