"""Schema definitions for ExamplePipelineAgent.

This is a **template** -- copy this package and modify it to create a new
pipeline agent.  The schema defines the Pydantic input/output contract.

Key conventions:
  - Input class: <Agent>Input(BaseModel)
  - Output class: <Agent>Output(BaseModel) with a content sub-model
  - meta field uses common_schema.Meta (system-injected, never LLM-generated)
  - All string fields default to "" (not None) per JSON output rules
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..common_schema import Meta


# ---------------------------------------------------------------------------
# Output sub-models
# ---------------------------------------------------------------------------

class SummaryContent(BaseModel):
    """The creative content produced by the agent."""

    title: str = Field("", description="A short title for the summary")
    summary: str = Field("", description="The generated summary text")
    key_points: list[str] = Field(
        default_factory=list,
        description="Extracted key points from the input",
    )
    word_count: int = Field(0, description="Word count of the summary")


# ---------------------------------------------------------------------------
# Top-level I/O
# ---------------------------------------------------------------------------

class ExamplePipelineInput(BaseModel):
    """Input payload for ExamplePipelineAgent.

    project_id and draft_id are standard pipeline fields.
    source_text is the domain-specific input this agent processes.
    """

    project_id: str = ""
    draft_id: str = ""
    source_text: str = Field("", description="The text to summarize")


class ExamplePipelineOutput(BaseModel):
    """Output payload for ExamplePipelineAgent."""

    meta: Meta = Field(default_factory=Meta)
    content: SummaryContent = Field(default_factory=SummaryContent)
