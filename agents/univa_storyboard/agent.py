"""UnivaStoryboardAgent -- generates a full storyboard from a single prompt.

Faithfully reproduces UniVA's storyboard generation step using its original
``storyboard_gen.txt`` system prompt.  The LLM produces a JSON object with
``characters``, ``shots``, and ``style`` fields.
"""

from __future__ import annotations

from pathlib import Path

from ..base_agent import BaseAgent
from .schema import UnivaStoryboardInput, UnivaStoryboardOutput


_PROMPT_DIR = Path(__file__).with_name("prompts")


class UnivaStoryboardAgent(BaseAgent[UnivaStoryboardInput, UnivaStoryboardOutput]):
    """One-shot storyboard planner — mirrors UniVA's storyboard_generate()."""

    def system_prompt(self) -> str:
        prompt_file = _PROMPT_DIR / "storyboard_gen.txt"
        text = prompt_file.read_text(encoding="utf-8")
        # Append JSON output rules required by the BaseAgent framework.
        text += (
            "\n\n# Output Rules (system-injected)\n"
            "- Return JSON only, no markdown, no code fences.\n"
            "- The output MUST have top-level keys: content, artifact_caption.\n"
            "- Wrap the characters/shots/style inside a \"content\" object.\n"
            "- Do NOT include a 'meta' block -- it is injected by the system.\n\n"
            "artifact_caption: fill both fields:\n"
            "  caption -- one sentence: character count, shot count. "
            "State this is a storyboard for keyframe and video generation. "
            "No creative prose.\n"
            "  scope -- always \"global\".\n\n"
            "Example top-level structure:\n"
            "{\n"
            '  "content": { "characters": [...], "shots": [...], "style": "..." },\n'
            '  "artifact_caption": { "caption": "Univa storyboard: 2 characters, 5 shots. Input for keyframe and video generation.", "scope": "global" }\n'
            "}\n"
        )
        return text

    def build_user_prompt(self, input_data: UnivaStoryboardInput) -> str:
        return (
            "=== CREATIVE BRIEF (raw JSON — read the text from it) ===\n"
            f"{input_data.creative_brief_json_text}\n"
            "=== END CREATIVE BRIEF ===\n\n"
            "Read the JSON above, find the user's creative intent, and "
            "produce the storyboard."
        )

    async def generate(
        self,
        input_data: UnivaStoryboardInput,
        *,
        rework_notes: str = "",
    ) -> UnivaStoryboardOutput:
        """One LLM call generates the full storyboard from the user prompt."""
        output = await self._llm_fill_full(input_data, rework_notes)
        self.recompute_metrics(output)
        return output

    def recompute_metrics(self, output: UnivaStoryboardOutput) -> None:
        c = output.content
        output.metrics.character_count = len(c.characters)
        output.metrics.shot_count = len(c.shots)
