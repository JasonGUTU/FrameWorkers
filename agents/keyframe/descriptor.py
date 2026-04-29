"""KeyFrameAgent descriptor — built from a single AgentSpec."""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel

from inference.generation import select_image_service

from ..common_schema import ImageReferenceEntry, ResolvedArtifactEntry
from ..descriptor import AgentSpec, InputLabelSpec, SubAgentDescriptor
from .agent import KeyFrameAgent
from .evaluator import KeyframeEvaluator
from .labels import (
    INPUT_LABEL_CHARACTER_REFERENCE,
    INPUT_LABEL_LOCATION_REFERENCE,
    INPUT_LABEL_PROP_REFERENCE,
    INPUT_LABEL_SCREENPLAY,
    INPUT_LABEL_STYLE_REFERENCE,
)
from .materializer import KeyframeMaterializer
from .schema import KeyFrameAgentInput


def build_input(
    _step_id: str,
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
    caps[agent_id] = {
        "caption": (
            f"Keyframe planning document: {scene_count} scene(s), {shot_count} "
            f"shot(s), with per-shot frame descriptions and motion hints. "
            f"Consumed by a downstream image-to-video generation step."
        ),
        "scope": "global",
    }
    for kind_key, kind_label in [
        ("characters", "character"),
        ("locations", "location"),
        ("props", "prop"),
    ]:
        for anchor in ga.get(kind_key, []):
            eid = anchor.get("entity_id", "") if isinstance(anchor, dict) else ""
            if eid:
                caps[f"img_{eid}_global"] = {
                    "caption": (
                        f"Global {kind_label} reference image for {eid}. "
                        f"Visual identity anchor — not a video frame."
                    ),
                    "scope": "global",
                }
    for sc in scenes:
        if not isinstance(sc, dict):
            continue
        scene_id = sc.get("scene_id", "")
        sk = sc.get("stability_keyframes", {})
        for kind_key, kind_label in [
            ("characters", "character"),
            ("locations", "location"),
            ("props", "prop"),
        ]:
            for anchor in sk.get(kind_key, []) if isinstance(sk, dict) else []:
                eid = anchor.get("entity_id", "") if isinstance(anchor, dict) else ""
                if eid and scene_id:
                    caps[f"img_{eid}_{scene_id}"] = {
                        "caption": (
                            f"Scene-level {kind_label} reference for {eid} "
                            f"in scene {scene_id}. Intermediate consistency "
                            f"rendering — not a video frame."
                        ),
                        "scope": f"scene:{scene_id}",
                    }
        for shot in sc.get("shots", []):
            if not isinstance(shot, dict):
                continue
            shot_id = shot.get("shot_id", "")
            if not shot_id:
                continue
            # Invariant: keyframe_count == 1 per shot (evaluator enforces).
            # The sys_id suffix is a stable constant so ArtifactRef keys
            # survive re-runs; the keyframe itself no longer carries a
            # keyframe_id field in the schema.
            kfs = shot.get("keyframes", []) or []
            if kfs:
                kid = "kf_001"
                caps[f"img_{shot_id}_{kid}"] = {
                    "caption": (
                        f"Rendered starting frame for shot {shot_id} "
                        f"in scene {scene_id}. To be animated into a "
                        f"video clip by an image-to-video generation step."
                    ),
                    "scope": f"shot:{shot_id}",
                }
    return caps


SPEC = AgentSpec(
    agent_id="KeyFrameAgent",
    inputs=[
        InputLabelSpec(
            name=INPUT_LABEL_SCREENPLAY,
            cardinality="single",
            description=(
                "The full unified screenplay document for the story: "
                "scenes broken into ordered shots with camera direction, "
                "action description, and per-scene consistency information "
                "(visual style, color, lighting, characters and locations "
                "involved, things to keep, things to avoid). It is the "
                "primary creative document defining what shots exist and "
                "how they should look. Choose at most one such document."
            ),
        ),
        InputLabelSpec(
            name=INPUT_LABEL_CHARACTER_REFERENCE,
            cardinality="collection",
            optional=True,
            description=(
                "Image artifacts that depict what specific characters in "
                "the story should look like. Each entry's caption "
                "identifies the character (by name, role, or visual "
                "description). When present, I use these as global "
                "character anchors in Layer 1 instead of generating from "
                "text — I record the resolved image path on the matching "
                "character entity so the materializer reads the bytes from "
                "disk instead of running text-to-image. When absent, I "
                "generate the character anchor from text alone."
            ),
        ),
        InputLabelSpec(
            name=INPUT_LABEL_LOCATION_REFERENCE,
            cardinality="collection",
            optional=True,
            description=(
                "Image artifacts depicting what specific locations or "
                "settings in the story should look like. Same handling as "
                "character references — when present, the resolved path is "
                "recorded on the matching location entity; when absent, "
                "the location is generated from text."
            ),
        ),
        InputLabelSpec(
            name=INPUT_LABEL_PROP_REFERENCE,
            cardinality="collection",
            optional=True,
            description=(
                "Image artifacts depicting what specific props or objects "
                "in the story should look like. Same handling as character "
                "references — when present, the resolved path is recorded "
                "on the matching prop entity; when absent, the prop is "
                "generated from text."
            ),
        ),
        InputLabelSpec(
            name=INPUT_LABEL_STYLE_REFERENCE,
            cardinality="collection",
            optional=True,
            description=(
                "Image artifacts conveying overall visual style, mood, "
                "palette, or aesthetic that should inform image "
                "generation. Unlike character/location references, these "
                "don't depict specific entities — they describe how "
                "things should look in general. When present, I "
                "incorporate them as style guidance in my generation "
                "prompts; when absent, the style is inferred from the "
                "screenplay's per-scene mood / tone metadata."
            ),
        ),
    ],
    output_description=(
        "keyframes_package (L1 global stability anchors + L2 per-scene "
        "stability + L3 one still per shot); each L3 row has "
        "prompt_summary (image API) + video_motion_hint (I2V text only)."
    ),
    purpose_and_trigger=(
        """Generate per-shot keyframe still images for every shot in a screenplay — uses character / location / style reference images when available to keep visual identity consistent across shots. Trigger: include whenever the plan produces a multi-shot film and needs per-shot starting frames before video synthesis. Requires an upstream screenplay; reference images are optional."""
    ),
    input_preamble=(
        "I plan and render the visual reference images for a video: "
        "identity sheets for each character/location/prop, scene-level "
        "adaptations, and one starting frame per planned shot. I work "
        "primarily from a written screenplay.\n\n"
        "For each [label] below, find every artifact in the registry "
        "whose caption describes the same kind of thing. Use the "
        "natural-language caption only — do not match by filename or by "
        "any tag. Sources are irrelevant: an image may have come from a "
        "user upload or from another agent's run; both are treated "
        "identically once their captions semantically match."
    ),
)


DESCRIPTOR = SubAgentDescriptor.from_spec(
    SPEC,
    agent_factory=lambda llm: KeyFrameAgent(llm_client=llm),
    evaluator_factory=KeyframeEvaluator,
    build_input=build_input,
    build_captions=build_captions,
    service_factories={"image_service": lambda ctx: select_image_service()},
    materializer_factory=materializer_factory,
)
