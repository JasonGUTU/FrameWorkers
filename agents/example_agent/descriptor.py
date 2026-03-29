"""ExamplePipelineAgent descriptor — self-describing manifest for the registry.

The descriptor is the glue between the agent and the orchestration layer.
It tells the registry:
  - How to create the agent (``agent_factory``)
  - How to create the evaluator (``evaluator_factory``)
  - How to build typed input from the pipeline bundle (``build_input``)
  - Human-readable description for planning LLMs (``catalog_entry``)
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from ..descriptor import SubAgentDescriptor
from ..contracts import InputBundleV2
from .agent import ExamplePipelineAgent
from .schema import ExamplePipelineInput
from .evaluator import ExamplePipelineEvaluator

OUTPUT_ASSET_KEY = "example_summary"


def build_input(
    _task_id: str,
    input_bundle_v2: InputBundleV2,
    config: Any,
) -> BaseModel:
    """Construct typed input from the pipeline bundle."""
    resolved = (
        input_bundle_v2.context.get("resolved_inputs", {})
        if isinstance(getattr(input_bundle_v2, "context", None), dict)
        else {}
    )
    return ExamplePipelineInput(
        source_text=resolved.get("source_text", ""),
    )


CATALOG_ENTRY = (
    "ExamplePipelineAgent\n"
    "  - Input: source_text (plain text to summarize)\n"
    "  - Output: example_summary (title, summary, key_points, word_count)\n"
    "  - Purpose: Demonstrate the pipeline agent pattern. Summarizes input text."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_id="ExamplePipelineAgent",
    asset_key=OUTPUT_ASSET_KEY,
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: ExamplePipelineAgent(llm_client=llm),
    evaluator_factory=ExamplePipelineEvaluator,
    build_input=build_input,
    materializer_factory=None,
)
