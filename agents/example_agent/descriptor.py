"""ExamplePipelineAgent descriptor — built from a single AgentSpec.

Kept as a development template (not registered in AGENT_REGISTRY). The
spec-based pattern below is the canonical shape new agents should follow:
``AgentSpec(inputs=[InputLabelSpec(...)], ...)`` → derive both the
planner-facing ``catalog_entry`` and the InputResolver-facing
``input_needs_description`` from the same source of truth via
``SubAgentDescriptor.from_spec``.
"""

from __future__ import annotations

from pydantic import BaseModel

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import AgentSpec, InputLabelSpec, SubAgentDescriptor
from .agent import ExamplePipelineAgent
from .evaluator import ExamplePipelineEvaluator
from .schema import ExamplePipelineInput


INPUT_LABEL_SOURCE_TEXT = "creative_brief"


def build_input(
    _step_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    """Read ONLY from ``resolved_artifacts[label]``. No other input channels."""
    entry = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_SOURCE_TEXT)
    )
    raw = ""
    if entry.payload:
        raw = str(entry.payload.get("text", "") or "")
    if not raw:
        raw = entry.caption
    return ExamplePipelineInput(source_text=raw)


def build_captions(agent_id: str, output_dict: dict) -> dict:
    return {
        agent_id: {
            "caption": "Example text summary. Pipeline demo output.",
            "scope": "global",
        },
    }


SPEC = AgentSpec(
    agent_id="ExamplePipelineAgent",
    inputs=[
        InputLabelSpec(
            name=INPUT_LABEL_SOURCE_TEXT,
            cardinality="single",
            description=(
                "Plain text to summarize (from a creative brief artifact, "
                "IntakeTextAgent output, or any text payload)."
            ),
        ),
    ],
    output_description=(
        "example_summary (title, summary, key_points, word_count)."
    ),
    purpose_and_routing=(
        "Demonstrate the pipeline agent pattern. Summarizes input text. "
        "Kept as a development template — not registered in "
        "AGENT_REGISTRY and not invoked by Director."
    ),
    input_preamble=(
        "I summarize a single source-text artifact. No other upstream "
        "artifacts are required."
    ),
)


DESCRIPTOR = SubAgentDescriptor.from_spec(
    SPEC,
    agent_factory=lambda llm: ExamplePipelineAgent(llm_client=llm),
    evaluator_factory=ExamplePipelineEvaluator,
    build_input=build_input,
    build_captions=build_captions,
)
