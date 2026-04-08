"""KeyFrameAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from ..descriptor import SubAgentDescriptor
from ..contracts import InputBundleV2
from .agent import KeyFrameAgent
from .labels import (
    INPUT_LABEL_CHARACTER_REFERENCE,
    INPUT_LABEL_LOCATION_REFERENCE,
    INPUT_LABEL_SCREENPLAY,
    INPUT_LABEL_STYLE_REFERENCE,
)
from ..common_schema import ImageReferenceEntry
from .schema import KeyFrameAgentInput
from .evaluator import KeyframeEvaluator
from .materializer import KeyframeMaterializer
from inference.generation.image_generators.service import FalImageService


def _to_image_refs(resolved: dict, label: str) -> list[ImageReferenceEntry]:
    items = resolved.get(label, [])
    if not isinstance(items, list):
        return []
    out: list[ImageReferenceEntry] = []
    for it in items:
        if not isinstance(it, dict):
            continue
        path = str(it.get("path", "") or "").strip()
        if not path:
            continue
        out.append(
            ImageReferenceEntry(
                path=path,
                caption_what=str(it.get("what", "") or ""),
                caption_why=str(it.get("why", "") or ""),
                mime=str(it.get("mime", "") or ""),
            )
        )
    return out


def build_input(
    _task_id: str,
    input_bundle_v2: InputBundleV2,
) -> BaseModel:
    resolved = input_bundle_v2.resolved_artifacts

    sp = resolved.get(INPUT_LABEL_SCREENPLAY, {})
    payload = sp.get("payload", {}) if isinstance(sp, dict) else {}

    return KeyFrameAgentInput(
        screenplay=payload,
        character_references=_to_image_refs(resolved, INPUT_LABEL_CHARACTER_REFERENCE),
        location_references=_to_image_refs(resolved, INPUT_LABEL_LOCATION_REFERENCE),
        style_references=_to_image_refs(resolved, INPUT_LABEL_STYLE_REFERENCE),
    )


def materializer_factory(services: dict[str, Any]) -> KeyframeMaterializer:
    return KeyframeMaterializer(image_service=services["image_service"])


CATALOG_ENTRY = (
    "KeyFrameAgent\n"
    "  - Input: screenplay (unified shots + consistency packs)\n"
    "  - Output: keyframes_package (L1 global + L2 scene stability + L3 one still per shot); "
    "each L3 row has prompt_summary (image API) + video_motion_hint (I2V text only)\n"
    "  - Purpose: Anchor consistency, per-shot stills, and decoupled motion hints for video."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_id="KeyFrameAgent",
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: KeyFrameAgent(llm_client=llm),
    evaluator_factory=KeyframeEvaluator,
    build_input=build_input,
    service_factories={
        "image_service": lambda ctx: FalImageService(),
    },
    materializer_factory=materializer_factory,
    input_needs_description=(
        "I plan and render the visual reference images for a video: identity sheets "
        "for each character/location/prop, scene-level adaptations, and one starting "
        "frame per planned shot. I work primarily from a written screenplay.\n\n"
        "For each [label] below, find every artifact in the registry whose caption "
        "describes the same kind of thing. Use the natural-language caption only — "
        "do not match by filename or by any tag. Sources are irrelevant: an image "
        "may have come from a user upload or from another agent's run; both are "
        "treated identically once their captions semantically match.\n\n"
        f"[{INPUT_LABEL_SCREENPLAY}] (single)\n"
        "The full unified screenplay document for the story: scenes broken into "
        "ordered shots with camera direction, action description, "
        "and per-scene consistency information (visual style, color, lighting, "
        "characters and locations involved, things to keep, things to avoid). "
        "It is the primary creative document defining what shots exist and how they "
        "should look. Choose at most one such document.\n\n"
        f"[{INPUT_LABEL_CHARACTER_REFERENCE}] (collection)\n"
        "Image artifacts that depict what specific characters in the story should "
        "look like. Each entry's caption identifies the character (by name, role, "
        "or visual description). I use these as global character anchors in Layer 1 "
        "instead of generating from text — when an image references a specific "
        "character, I assign that image's path directly to the character's "
        "image_asset.uri field, and the materializer reads the bytes from disk.\n\n"
        f"[{INPUT_LABEL_LOCATION_REFERENCE}] (collection)\n"
        "Image artifacts depicting what specific locations or settings in the story "
        "should look like. Same handling as character references — I assign the "
        "path directly to the location entity's image_asset.uri field.\n\n"
        f"[{INPUT_LABEL_STYLE_REFERENCE}] (collection)\n"
        "Image artifacts conveying overall visual style, mood, palette, or "
        "aesthetic that should inform image generation. Unlike character/location "
        "references, these don't depict specific entities — they describe how "
        "things should look in general. I incorporate them as style guidance in "
        "my generation prompts."
    ),
)
