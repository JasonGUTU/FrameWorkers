"""ExamplePipelineAgent -- minimal pipeline agent template.

This agent demonstrates the full async pipeline agent pattern:
  - Inherits from BaseAgent[InputT, OutputT]
  - Implements system_prompt(), build_user_prompt(), and
    optionally recompute_metrics()
  - LLM generates JSON -> Pydantic validates -> evaluator checks quality

Copy this package and modify it to create a new pipeline agent.
"""

from __future__ import annotations

from agent_core.base_agent import BaseAgent
from .schema import ExamplePipelineInput, ExamplePipelineOutput


class ExamplePipelineAgent(BaseAgent[ExamplePipelineInput, ExamplePipelineOutput]):
    """Summarizes input text into a structured summary with key points.

    This is intentionally simple -- a real agent would have more detailed
    prompts, domain-specific output templates, and richer schemas.
    """

    def system_prompt(self) -> str:
        return (
            "You are a summarization agent.\n"
            "Task: Read the provided text and produce a structured summary.\n\n"
            "You MUST:\n"
            "- Write a short title (max 10 words)\n"
            "- Write a concise summary (2-4 sentences)\n"
            "- Extract 3-5 key points as a list\n"
            "- Count the words in your summary and set word_count\n\n"
            "Output Rules:\n"
            "- Return JSON only, no markdown, no code fences.\n"
            "- The output MUST have a single top-level key: content.\n"
            "- Do NOT include a 'meta' block -- it is injected by the system.\n"
        )

    def build_user_prompt(self, input_data: ExamplePipelineInput) -> str:
        return (
            f"Please summarize the following text:\n\n"
            f"{input_data.source_text}\n\n"
            f"project_id: {input_data.project_id}\n"
            f"draft_id: {input_data.draft_id}\n\n"
            "Return JSON matching this structure:\n"
            "{\n"
            '  "content": {\n'
            '    "title": "<short title>",\n'
            '    "summary": "<2-4 sentence summary>",\n'
            '    "key_points": ["<point 1>", "<point 2>", ...],\n'
            '    "word_count": <integer>\n'
            "  }\n"
            "}\n"
        )

    def recompute_metrics(self, output: ExamplePipelineOutput) -> None:
        """Fix word_count if the LLM got it wrong."""
        if output.content.summary:
            output.content.word_count = len(output.content.summary.split())
