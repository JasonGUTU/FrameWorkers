"""Schema definitions for IntakeTextAgent input / output interfaces."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ...common_schema import ArtifactCaption, Meta


class IntakeTextContent(BaseModel):
    """Pass-through container for the raw user text plus an LLM/static summary."""

    text: str = Field("", description="The original user-uploaded text, verbatim")
    summary: str = Field(
        "",
        json_schema_extra={"creative": True},
        description=(
            "Short LLM-generated summary of long text uploads. "
            "Empty for short uploads (the raw text is used as-is)."
        ),
    )


class IntakeTextMetrics(BaseModel):
    char_count: int = 0


class IntakeTextInput(BaseModel):
    """Input payload for IntakeTextAgent.

    The InputResolver matches a placeholder ``[raw_text_upload]`` artifact
    and populates ``raw_text_path`` with the on-disk path of the raw user
    file (mirrors how IntakeImageAgent receives image paths). The agent
    reads the file lazily inside ``_generate`` so the InputResolver does
    not need to inline-load text payloads.
    """

    raw_text_path: str = ""
    user_intent: str = Field(
        default="",
        description=(
            "Free-form description from the user of what this text is for "
            "(e.g. 'creative brief for the project', 'user_story_outline', "
            "'screenplay revision request'). Stored verbatim in the output "
            "artifact's caption.why field."
        ),
    )


class IntakeTextOutput(BaseModel):
    """Caption-rich artifact wrapping a raw user text upload."""

    meta: Meta = Field(default_factory=Meta)
    content: IntakeTextContent = Field(default_factory=IntakeTextContent)
    metrics: IntakeTextMetrics = Field(default_factory=IntakeTextMetrics)
    artifact_caption: ArtifactCaption = Field(default_factory=ArtifactCaption)
