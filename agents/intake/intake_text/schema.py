"""Schema definitions for IntakeTextAgent input / output interfaces."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ...common_schema import Meta


class IntakeTextContent(BaseModel):
    """Pass-through container for the raw user text."""

    text: str = Field("", description="The original user-uploaded text, verbatim")


class IntakeTextMetrics(BaseModel):
    char_count: int = 0


class IntakeTextInput(BaseModel):
    """Input payload for IntakeTextAgent.

    The InputResolver matches a placeholder ``[raw_text_upload]`` artifact
    and populates ``raw_text_path`` with the on-disk path of the raw user
    file (mirrors how the image-intake agent receives image paths). The
    agent reads the file lazily inside ``_generate`` so the InputResolver
    does not need to inline-load text payloads.
    """

    raw_text_path: str = ""


class IntakeTextOutput(BaseModel):
    """Caption-rich artifact wrapping a raw user text upload."""

    meta: Meta = Field(default_factory=Meta)
    content: IntakeTextContent = Field(default_factory=IntakeTextContent)
    metrics: IntakeTextMetrics = Field(default_factory=IntakeTextMetrics)
