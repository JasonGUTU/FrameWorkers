"""IntakeImageAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

from pydantic import BaseModel

from ...common_schema import ResolvedArtifactEntry
from ...descriptor import SubAgentDescriptor
from .agent import IntakeImageAgent
from .labels import INPUT_LABEL_RAW_IMAGE_UPLOAD
from .schema import IntakeImageInput
from .evaluator import IntakeImageEvaluator


def build_input(
    _task_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    raw = resolved_artifacts.get(INPUT_LABEL_RAW_IMAGE_UPLOAD)
    if isinstance(raw, list):
        raw = raw[0] if raw else None
    entry = ResolvedArtifactEntry.coerce(raw)
    return IntakeImageInput(raw_image_path=entry.path)


def build_captions(agent_id: str, output_dict: dict) -> dict:
    content = output_dict.get("content", {})
    visual = content.get("visual_description", "") if isinstance(content, dict) else ""
    cap_parts = ["User-uploaded image reference."]
    if visual:
        cap_parts.append(f"Shows: {visual}.")
    cap_parts.append("Available for downstream keyframe and video agents.")
    return {
        agent_id: {"caption": " ".join(cap_parts), "scope": "global"},
    }


CATALOG_ENTRY = (
    "IntakeImageAgent\n"
    "  - Input: raw_image_upload (placeholder caption pointing at a raw image file)\n"
    "  - Output: a caption-rich image artifact suitable for downstream agents to discover\n"
    "    via their semantic-typed image labels (e.g. [character_reference]).\n"
    "  - Purpose: Run a vision LLM over a freshly-uploaded user image and emit a workspace\n"
    "    artifact whose caption describes what the image visually shows together with the\n"
    "    user's stated intent."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_id="IntakeImageAgent",
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: IntakeImageAgent(llm_client=llm),
    evaluator_factory=IntakeImageEvaluator,
    build_input=build_input,
    build_captions=build_captions,
    materializer_factory=None,
    input_needs_description=(
        "I convert raw user-uploaded images into caption-rich workspace "
        "artifacts. I am invoked once per upload, before any content "
        "agent runs.\n\n"
        f"[{INPUT_LABEL_RAW_IMAGE_UPLOAD}] (single)\n"
        "A raw user-uploaded image artifact whose caption starts with "
        "'Raw user upload (mime=image/' and has scope 'raw_pending'. "
        "Pick the single most recent such pending image upload."
    ),
)
