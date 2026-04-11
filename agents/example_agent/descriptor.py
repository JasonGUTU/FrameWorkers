"""ExamplePipelineAgent descriptor — self-describing manifest for the registry.

The descriptor is the glue between the agent and the orchestration layer.
It tells the registry:
  - How to create the agent (``agent_factory``)
  - How to create the evaluator (``evaluator_factory``)
  - How to build typed input from the pipeline bundle (``build_input``)
  - Human-readable description for planning LLMs (``catalog_entry``)
"""

from __future__ import annotations

from pydantic import BaseModel

from ..descriptor import SubAgentDescriptor
from .agent import ExamplePipelineAgent
from .schema import ExamplePipelineInput
from .evaluator import ExamplePipelineEvaluator


def build_input(
    _task_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    """Construct typed input from the resolved artifact dict.

    NOTE: example_agent is no longer registered in AGENT_REGISTRY (it is kept
    only as a development template). It still illustrates the canonical
    label-based input pattern: read from ``resolved_artifacts[label]`` only,
    never from any hint slot.
    """
    entry = resolved_artifacts.get("creative_brief", {})
    payload = entry.get("payload", {}) if isinstance(entry, dict) else {}
    raw = ""
    if isinstance(payload, dict):
        raw = str(payload.get("text", "") or "")
    if not raw and isinstance(entry, dict):
        raw = str(entry.get("caption", "") or "")
    return ExamplePipelineInput(source_text=raw)


def build_captions(agent_id: str, output_dict: dict) -> dict:
    return {
        agent_id: {
            "caption": "Example text summary. Pipeline demo output.",
            "scope": "global",
        },
    }


CATALOG_ENTRY = (
    "ExamplePipelineAgent\n"
    "  - Input: source_text (plain text to summarize)\n"
    "  - Output: example_summary (title, summary, key_points, word_count)\n"
    "  - Purpose: Demonstrate the pipeline agent pattern. Summarizes input text."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_id="ExamplePipelineAgent",
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: ExamplePipelineAgent(llm_client=llm),
    evaluator_factory=ExamplePipelineEvaluator,
    build_input=build_input,
    build_captions=build_captions,
    materializer_factory=None,
    input_needs_description=(
        "Only needs the user-provided source_text to summarize. "
        "No prior workspace artifacts are required."
    ),
)
