"""IntakeTextAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

from pydantic import BaseModel

from ...descriptor import SubAgentDescriptor
from ...contracts import InputBundleV2
from .agent import IntakeTextAgent
from .labels import INPUT_LABEL_RAW_TEXT_UPLOAD
from .schema import IntakeTextInput
from .evaluator import IntakeTextEvaluator


def build_input(
    _task_id: str,
    input_bundle_v2: InputBundleV2,
) -> BaseModel:
    """Pull the raw text path and user_intent out of the placeholder artifact.

    The placeholder artifact is registered by ``workspace.persist_raw_upload``
    with ``ArtifactRef.path`` pointing at the on-disk file and ``why``
    carrying the user's free-text intent. The agent reads the file
    contents lazily during ``_generate``.
    """
    resolved = input_bundle_v2.resolved_artifacts
    entry = resolved.get(INPUT_LABEL_RAW_TEXT_UPLOAD, {})
    if isinstance(entry, list):
        entry = entry[0] if entry else {}
    raw_text_path = ""
    user_intent = ""
    if isinstance(entry, dict):
        raw_text_path = str(entry.get("path", "") or "")
        user_intent = str(entry.get("why", "") or "")
    return IntakeTextInput(raw_text_path=raw_text_path, user_intent=user_intent)


CATALOG_ENTRY = (
    "IntakeTextAgent\n"
    "  - Input: raw_text_upload (placeholder caption pointing at a raw text file path,\n"
    "    caption.why carrying the user's free-text intent).\n"
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
    materializer_factory=None,
    input_needs_description=(
        "I convert raw user-uploaded text into a caption-rich workspace "
        "artifact. I am invoked once per upload, before any content "
        "agent runs.\n\n"
        f"[{INPUT_LABEL_RAW_TEXT_UPLOAD}] (single)\n"
        "A raw user-uploaded text artifact that has not yet been "
        "semantically analyzed. The placeholder caption marks it as "
        "'raw user upload, mime=text/plain, awaiting semantic analysis'. "
        "Its payload contains the verbatim text and its caption.why "
        "carries the user's free-text description of what the upload is "
        "for. Pick the single most recent such pending upload."
    ),
)
