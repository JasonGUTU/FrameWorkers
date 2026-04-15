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
    _step_id: str,
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
    "  - Input: ANY user-provided text (creative brief, instruction, product/brand info, "
    "script, chat message content).\n"
    "  - Output: a caption-rich text artifact suitable for downstream agents to find\n"
    "    via their semantic-typed labels (e.g. [creative_brief]).\n"
    "  - Purpose: MANDATORY first step for every pipeline run. The user's text input "
    "(including chat instructions) must always be ingested here before any creative, "
    "post-production, or analysis agent can run. Even if the user also provides media "
    "(video/audio/image), run IntakeTextAgent BEFORE the corresponding Intake*Agent.\n"
    "  - When to skip: ONLY when the user's input is genuinely empty (empty string). "
    "For greetings, nonsense, unrelated questions — still run IntakeTextAgent to ingest "
    "the message, then the Director can emit done afterwards based on the ingested content."
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
