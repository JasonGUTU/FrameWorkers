"""Evaluator for ExamplePipelineAgent output.

Demonstrates the evaluator pattern:
  - check_structure() -- L1 rule-based checks (fast, free, deterministic)
  - creative_dimensions -- L2 LLM-based creative assessment dimensions
  - _build_creative_context() -- context string for the L2 LLM prompt

No L3 (asset evaluation) since this agent produces no binary assets.
"""

from __future__ import annotations

from typing import Any

from agent_core.base_evaluator import BaseEvaluator
from .schema import ExamplePipelineOutput


class ExamplePipelineEvaluator(BaseEvaluator[ExamplePipelineOutput]):

    creative_dimensions = [
        ("accuracy", "Does the summary accurately reflect the source text?"),
        ("conciseness", "Is the summary concise without losing key information?"),
    ]

    def _build_creative_context(self, output, upstream):
        source_text = (upstream or {}).get("source_text", "")
        return f"Source text: {source_text[:500]}"

    # ------------------------------------------------------------------
    # Layer 1 -- Rule-based structural validation
    # ------------------------------------------------------------------

    def check_structure(
        self,
        output: ExamplePipelineOutput,
        upstream: dict[str, Any] | None = None,
    ) -> list[str]:
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
