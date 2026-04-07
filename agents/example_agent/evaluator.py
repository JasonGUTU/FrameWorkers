"""Evaluator for ExamplePipelineAgent output (output-internal only).

NOTE: example_agent is no longer registered in AGENT_REGISTRY (it is kept
only as a development template). Its evaluator follows the same rules as
all other evaluators: only check the agent's own output, never read any
upstream artifact.
"""

from __future__ import annotations

from ..base_evaluator import BaseEvaluator
from .schema import ExamplePipelineOutput


class ExamplePipelineEvaluator(BaseEvaluator[ExamplePipelineOutput]):

    creative_dimensions = [
        ("accuracy", "Is the summary internally well-formed (clear title, coherent summary)?"),
        ("conciseness", "Is the summary concise without losing key information?"),
    ]

    # ------------------------------------------------------------------
    # Layer 1 -- Rule-based structural validation
    # ------------------------------------------------------------------

    def check_structure(self, output: ExamplePipelineOutput) -> list[str]:
        errors: list[str] = []
        c = output.content

        if not c.title:
            errors.append("title is empty")

        if not c.summary:
            errors.append("summary is empty")

        if len(c.key_points) < 1:
            errors.append("key_points must have at least 1 item")

        if c.word_count < 0:
            errors.append("word_count must be non-negative")

        return errors
