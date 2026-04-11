"""IntakeTextAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

from pydantic import BaseModel

from ...common_schema import ResolvedArtifactEntry
from ...descriptor import SubAgentDescriptor
from .agent import IntakeTextAgent
from .labels import INPUT_LABEL_RAW_TEXT_UPLOAD
from .schema import IntakeTextInput
from .evaluator import IntakeTextEvaluator


def build_input(
    _task_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    raw = resolved_artifacts.get(INPUT_LABEL_RAW_TEXT_UPLOAD)
    if isinstance(raw, list):
        raw = raw[0] if raw else None
    entry = ResolvedArtifactEntry.coerce(raw)
    return IntakeTextInput(raw_text_path=entry.path)


def build_captions(agent_id: str, output_dict: dict) -> dict:
    content = output_dict.get("content", {})
    text = content.get("text", "")
    char_count = len(text)
    if not text:
        caption = "Empty user text upload — no usable content."
    else:
        caption = (
            f"User-submitted creative brief ({char_count} chars). "
            "Pipeline entry point — consumed by story and screenplay agents."
        )
    return {
        agent_id: {"caption": caption, "scope": "global"},
    }


CATALOG_ENTRY = (
    "IntakeTextAgent\n"
    "  - Input: raw_text_upload (placeholder caption pointing at a raw text file path).\n"
    "  - Output: a caption-rich text artifact suitable for downstream agents to find\n"
    "    via their semantic-typed labels (e.g. [creative_brief]).\n"
    "  - Purpose: Convert a freshly-uploaded raw user text into a workspace artifact\n"
    "    whose caption describes what the text is and what the user wanted it for."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_id="IntakeTextAgent",
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: IntakeTextAgent(llm_client=llm),
    evaluator_factory=IntakeTextEvaluator,
    build_input=build_input,
    build_captions=build_captions,
    materializer_factory=None,
    input_needs_description=(
        "I convert raw user-uploaded text into a caption-rich workspace "
        "artifact. I am invoked once per upload, before any content "
        "agent runs.\n\n"
        f"[{INPUT_LABEL_RAW_TEXT_UPLOAD}] (single)\n"
        "A raw user-uploaded text artifact whose caption starts with "
        "'Raw user upload (mime=text/plain)' and has scope 'raw_pending'. "
        "Pick the single most recent such pending text upload."
    ),
)
