"""KeyFrameAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel

from ..common_schema import ImageReferenceEntry, ResolvedArtifactEntry
from ..descriptor import SubAgentDescriptor
from .agent import KeyFrameAgent
from .labels import (
    INPUT_LABEL_CHARACTER_REFERENCE,
    INPUT_LABEL_LOCATION_REFERENCE,
    INPUT_LABEL_PROP_REFERENCE,
    INPUT_LABEL_SCREENPLAY,
    INPUT_LABEL_STYLE_REFERENCE,
)
from .schema import KeyFrameAgentInput
from .evaluator import KeyframeEvaluator
from .materializer import KeyframeMaterializer
from inference.generation import select_image_service


def build_input(
    _task_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    sp = ResolvedArtifactEntry.coerce(resolved_artifacts.get(INPUT_LABEL_SCREENPLAY))
    return KeyFrameAgentInput(
        screenplay_json_text=json.dumps(
            sp.payload or {}, ensure_ascii=False, indent=2
        ),
        character_references=ImageReferenceEntry.list_from_resolved(
            resolved_artifacts.get(INPUT_LABEL_CHARACTER_REFERENCE)
        ),
        location_references=ImageReferenceEntry.list_from_resolved(
            resolved_artifacts.get(INPUT_LABEL_LOCATION_REFERENCE)
        ),
        prop_references=ImageReferenceEntry.list_from_resolved(
            resolved_artifacts.get(INPUT_LABEL_PROP_REFERENCE)
        ),
        style_references=ImageReferenceEntry.list_from_resolved(
            resolved_artifacts.get(INPUT_LABEL_STYLE_REFERENCE)
        ),
    )


def materializer_factory(services: dict[str, Any]) -> KeyframeMaterializer:
    return KeyframeMaterializer(image_service=services["image_service"])


def build_captions(agent_id: str, output_dict: dict) -> dict:
    content = output_dict.get("content", {})
    ga = content.get("global_anchors", {})
    scenes = content.get("scenes", [])
    scene_count = len(scenes)
    shot_count = sum(
        len(sc.get("shots", [])) for sc in scenes if isinstance(sc, dict)
    )
    caps: dict = {}
    # JSON snapshot
    caps[agent_id] = {
        "caption": (
            f"Keyframe planning document: {scene_count} scene(s), {shot_count} "
            f"shot(s), with per-shot frame descriptions and motion hints. "
            f"Consumed by VideoAgent for image-to-video generation."
        ),
        "scope": "global",
    }
    # L1 global entity references
    for kind_key, kind_label in [("characters", "character"), ("locations", "location"), ("props", "prop")]:
        for anchor in ga.get(kind_key, []):
            eid = anchor.get("entity_id", "") if isinstance(anchor, dict) else ""
            if eid:
                caps[f"img_{eid}_global"] = {
                    "caption": f"Global {kind_label} reference image for {eid}. Visual identity anchor — not a video frame.",
                    "scope": "global",
                }
    # L2 + L3
    for sc in scenes:
        if not isinstance(sc, dict):
            continue
        scene_id = sc.get("scene_id", "")
        sk = sc.get("stability_keyframes", {})
        for kind_key, kind_label in [("characters", "character"), ("locations", "location"), ("props", "prop")]:
            for anchor in sk.get(kind_key, []) if isinstance(sk, dict) else []:
                eid = anchor.get("entity_id", "") if isinstance(anchor, dict) else ""
                if eid and scene_id:
                    caps[f"img_{eid}_{scene_id}"] = {
                        "caption": f"Scene-level {kind_label} reference for {eid} in scene {scene_id}. Intermediate consistency rendering — not a video frame.",
                        "scope": f"scene:{scene_id}",
                    }
        for shot in sc.get("shots", []):
            if not isinstance(shot, dict):
                continue
            shot_id = shot.get("shot_id", "")
            if not shot_id:
                continue
            for kf in shot.get("keyframes", []):
                kid = kf.get("keyframe_id", "") if isinstance(kf, dict) else ""
                if kid:
                    caps[f"img_{shot_id}_{kid}"] = {
                        "caption": f"Rendered starting frame for shot {shot_id} in scene {scene_id}. To be animated into a video clip by VideoAgent.",
                        "scope": f"shot:{shot_id}",
                    }
    return caps


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
    build_captions=build_captions,
    service_factories={
        "image_service": lambda ctx: select_image_service(),
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
        f"[{INPUT_LABEL_PROP_REFERENCE}] (collection)\n"
        "Image artifacts depicting what specific props or objects in the story "
        "should look like. Same handling as character references — I assign the "
        "path directly to the prop entity's image_asset.uri field.\n\n"
        f"[{INPUT_LABEL_STYLE_REFERENCE}] (collection)\n"
        "Image artifacts conveying overall visual style, mood, palette, or "
        "aesthetic that should inform image generation. Unlike character/location "
        "references, these don't depict specific entities — they describe how "
        "things should look in general. I incorporate them as style guidance in "
        "my generation prompts."
    ),
)
