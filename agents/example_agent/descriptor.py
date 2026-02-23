"""ExamplePipelineAgent descriptor — self-describing manifest for the registry.

The descriptor is the glue between the agent and the orchestration layer.
It tells the registry:
  - How to create the agent (``agent_factory``)
  - How to create the evaluator (``evaluator_factory``)
  - How to build typed input from the shared asset cache (``build_input``)
  - What upstream data the evaluator needs (``build_upstream``)
  - Human-readable description for planning LLMs (``catalog_entry``)
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from agent_core.descriptor import SubAgentDescriptor
from .agent import ExamplePipelineAgent
from .schema import ExamplePipelineInput
from .evaluator import ExamplePipelineEvaluator


def build_input(
    project_id: str,
    draft_id: str,
    assets: dict[str, Any],
    config: Any,
) -> BaseModel:
    """Construct typed input from the shared asset cache.

    ``assets`` is the global asset dict maintained by the orchestration
    layer.  Extract the keys your agent needs and map them to the
    Pydantic input model.
    """
    return ExamplePipelineInput(
        project_id=project_id,
        draft_id=draft_id,
        source_text=assets.get("source_text", ""),
    )


def build_upstream(assets: dict[str, Any]) -> dict[str, Any] | None:
    """Extract upstream context for the evaluator's cross-checks."""
    return {
        "source_text": assets.get("source_text", ""),
    }


CATALOG_ENTRY = (
    "ExamplePipelineAgent\n"
    "  - Input: source_text (plain text to summarize)\n"
    "  - Output: example_summary (title, summary, key_points, word_count)\n"
    "  - Purpose: Demonstrate the pipeline agent pattern. Summarizes input text."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_name="ExamplePipelineAgent",
    asset_key="example_summary",
    asset_type="example_summary",
    upstream_keys=["source_text"],
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: ExamplePipelineAgent(llm_client=llm),
    evaluator_factory=ExamplePipelineEvaluator,
    build_input=build_input,
    build_upstream=build_upstream,
    materializer_factory=None,
)
