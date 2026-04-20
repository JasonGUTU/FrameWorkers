"""Schema definitions for TranslationAgent input / output interfaces."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..common_schema import Meta


# ---------------------------------------------------------------------------
# Output sub-models
# ---------------------------------------------------------------------------

class TranslationContent(BaseModel):
    """Translated text preserving the original structure."""

    source_language: str = Field("", description="Detected source language code (e.g. zh, en, ja)")
    target_language: str = Field("", description="Target language code")
    translated_payload: dict = Field(default_factory=dict, description="Translated structured document preserving original JSON shape")


class TranslationMetrics(BaseModel):
    source_language: str = ""
    target_language: str = ""
    has_payload: bool = False


# ---------------------------------------------------------------------------
# Top-level I/O
# ---------------------------------------------------------------------------

class TranslationAgentInput(BaseModel):
    """Input payload for TranslationAgent.

    ``source_json_text`` is the upstream artifact payload (screenplay,
    transcript, or any structured text) serialized as a raw JSON text
    blob.  The LLM reads whatever shape it has and translates all
    human-readable text fields while preserving structural keys, ids,
    and ordering.

    ``target_language`` is the ISO language code to translate into.
    """

    source_json_text: str = ""
    target_language: str = "en"


class TranslationAgentOutput(BaseModel):
    """Output payload for TranslationAgent."""

    meta: Meta = Field(default_factory=Meta)
    content: TranslationContent = Field(default_factory=TranslationContent)
    metrics: TranslationMetrics = Field(default_factory=TranslationMetrics)
