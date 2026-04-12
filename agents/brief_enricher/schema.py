"""Schema definitions for BriefEnricherAgent input / output interfaces."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..common_schema import Meta


class ImageClassification(BaseModel):
    """LLM-authored classification of one uploaded image's role."""

    image_index: int = 0
    role: str = ""  # character | location | prop | style
    entity_hint: str = ""  # e.g. "the protagonist", "the workshop"


class BriefEnricherContent(BaseModel):
    enriched_brief: str = Field("", json_schema_extra={"creative": True})
    image_classifications: list[ImageClassification] = Field(default_factory=list)
    # Runtime file paths copied from input_data — NOT LLM-authored.
    # Used by build_captions to register role-specific caption entries
    # for each classified image.
    image_paths: list[str] = Field(default_factory=list)


class BriefEnricherMetrics(BaseModel):
    image_count: int = 0
    classified_count: int = 0


class BriefEnricherOutput(BaseModel):
    meta: Meta = Field(default_factory=Meta)
    content: BriefEnricherContent = Field(default_factory=BriefEnricherContent)
    metrics: BriefEnricherMetrics = Field(default_factory=BriefEnricherMetrics)


class BriefEnricherInput(BaseModel):
    """Input payload for BriefEnricherAgent — JSON-text pass-through.

    ``raw_brief_json_text``: the IntakeTextAgent payload (has content.text).
    ``image_payloads_json_text``: JSON array of IntakeImageAgent payloads
        (each has content.visual_description). The LLM reads both blobs
        and merges visual descriptions into the brief text.
    ``image_paths``: runtime file paths of the uploaded images, parallel
        to the payloads array. The LLM never sees these; they are copied
        into the output so build_captions can register role-specific
        captions pointing at the original image files.
    """

    raw_brief_json_text: str = ""
    image_payloads_json_text: str = ""
    image_paths: list[str] = Field(default_factory=list)
