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
    _step_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    raw = resolved_artifacts.get(INPUT_LABEL_RAW_IMAGE_UPLOAD)
    if isinstance(raw, list):
        raw = raw[0] if raw else None
    entry = ResolvedArtifactEntry.coerce(raw)
    return IntakeImageInput(raw_image_path=entry.path)


def build_captions(agent_id: str, output_dict: dict) -> dict:
    content = output_dict.get("content", {})
    image_uri = ""
    if isinstance(content, dict):
        asset = content.get("image_asset") or {}
        if isinstance(asset, dict):
            image_uri = str(asset.get("uri", "") or "").strip()
    visual = ""
    if isinstance(content, dict):
        visual = str(content.get("visual_description", "") or "").strip()
    caps: dict = {
        agent_id: {
            "caption": (
                f"User-uploaded reference image description. {visual}"
                if visual
                else "User-uploaded reference image description."
            ),
            "scope": "global",
        },
    }
    # Register the original image file so downstream agents can match
    # by mime=image/* and get the file path directly.
    # One entry only — BriefEnricherAgent will update this caption
    # with role-specific info via global_memory.update_caption_by_path().
    if image_uri:
        caps[f"{agent_id}_source_image"] = {
            "caption": (
                f"User-uploaded reference image file. {visual}"
                if visual
                else "User-uploaded reference image file."
            ),
            "scope": "global",
            "path": image_uri,
            "mime": "image/png",
        }
    return caps


CATALOG_ENTRY = (
    "IntakeImageAgent\n"
    "  - Input: raw_image_upload (placeholder caption pointing at a raw image file the user "
    "uploaded).\n"
    "  - Output: a caption-rich image artifact with vision-LLM caption, discoverable by "
    "downstream agents via semantic-typed image labels (e.g. [character_reference]).\n"
    "  - Purpose: Run a vision LLM over a freshly-uploaded user image so downstream agents "
    "can use it as a reference (character, location, style, etc.). Run me whenever the user "
    "has uploaded an image — always AFTER the user's text instruction has been ingested first. "
    "If the image is a creative reference (not a finished asset), a brief-enrichment step "
    "should usually follow to weave its visual description into the text brief."
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
