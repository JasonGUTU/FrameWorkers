"""VideoAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

import os
from typing import Any

from pydantic import BaseModel

from ..common_schema import ImageReferenceEntry
from ..descriptor import SubAgentDescriptor
from ..contracts import InputBundleV2
from .agent import VideoAgent
from .labels import (
    INPUT_LABEL_KEYFRAMES_METADATA,
    INPUT_LABEL_SCREENPLAY,
    INPUT_LABEL_SHOT_STILLS,
)
from .schema import VideoAgentInput
from .evaluator import VideoEvaluator
from .materializer import VideoMaterializer
from inference.generation.video_generators.service import FalVideoService, WavespeedVideoService

OUTPUT_ASSET_KEY = "video"


def build_input(
    _task_id: str,
    input_bundle_v2: InputBundleV2,
) -> BaseModel:
    resolved = input_bundle_v2.resolved_artifacts

    sp = resolved.get(INPUT_LABEL_SCREENPLAY, {})
    sp_payload = sp.get("payload", {}) if isinstance(sp, dict) else {}

    kf = resolved.get(INPUT_LABEL_KEYFRAMES_METADATA, {})
    kf_payload = kf.get("payload", {}) if isinstance(kf, dict) else {}

    shot_stills_raw = resolved.get(INPUT_LABEL_SHOT_STILLS, [])
    if not isinstance(shot_stills_raw, list):
        shot_stills_raw = []
    shot_stills: list[ImageReferenceEntry] = []
    for it in shot_stills_raw:
        if not isinstance(it, dict):
            continue
        path = str(it.get("path", "") or "").strip()
        if not path:
            continue
        shot_stills.append(
            ImageReferenceEntry(
                path=path,
                caption_what=str(it.get("what", "") or ""),
                caption_why=str(it.get("why", "") or ""),
                mime=str(it.get("mime", "") or ""),
                scope=str(it.get("scope", "") or ""),
            )
        )

    return VideoAgentInput(
        screenplay=sp_payload,
        keyframes_metadata=kf_payload,
        shot_stills=shot_stills,
    )


def materializer_factory(services: dict[str, Any]) -> VideoMaterializer:
    return VideoMaterializer(video_service=services["video_service"])


def _video_service_factory(_ctx: dict[str, Any] | None = None) -> FalVideoService | WavespeedVideoService:
    """Select pipeline video backend.

    - ``FW_VIDEO_BACKEND=fal`` (default): ``FalVideoService``
    - ``FW_VIDEO_BACKEND=wavespeed``: ``WavespeedVideoService``
    """
    backend = os.getenv("FW_VIDEO_BACKEND", "fal").strip().lower()
    if backend in ("wavespeed", "wave_speed", "ws"):
        return WavespeedVideoService()
    return FalVideoService()


CATALOG_ENTRY = (
    "VideoAgent\n"
    "  - Input: screenplay + per-shot keyframe images\n"
    "  - Output: video_package (shot segments, scene clips, final video)\n"
    "  - Purpose: Plan and generate video clips from keyframe images."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_id="VideoAgent",
    asset_key=OUTPUT_ASSET_KEY,
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: VideoAgent(llm_client=llm),
    evaluator_factory=VideoEvaluator,
    build_input=build_input,
    service_factories={
        "video_service": lambda ctx: _video_service_factory(ctx),
    },
    materializer_factory=materializer_factory,
    input_needs_description=(
        "I generate per-shot moving video clips by feeding a planned starting frame "
        "and a motion description into an image-to-video model, then assemble the "
        "clips into a final video.\n\n"
        "For each [label] below, find every artifact in the registry whose caption "
        "describes the same kind of thing. Use the natural-language caption only — "
        "do not match by filename or by any tag. Pay attention to the difference "
        "between visual identity references (which depict an entity in isolation) "
        "and actual planned frames of shots (which depict a specific moment of the "
        "story). I want the latter, never the former.\n\n"
        f"[{INPUT_LABEL_SCREENPLAY}] (single)\n"
        "The unified screenplay document defining the temporal structure of the "
        "story as an ordered sequence of scenes and shots, with per-shot creative "
        "direction (camera, action, mood). I rely on this to know how many shots "
        "there are and what each shot is supposed to convey. Choose at most one.\n\n"
        f"[{INPUT_LABEL_KEYFRAMES_METADATA}] (single)\n"
        "The planning document produced by the keyframe step that — for each shot "
        "in the screenplay — gives a textual description of the planned frame and "
        "a separate hint about how that frame should move when animated. I use "
        "this to fetch the prompt and motion intent for each shot. It is a JSON "
        "document, not an image. Choose at most one.\n\n"
        f"[{INPUT_LABEL_SHOT_STILLS}] (collection)\n"
        "The actual rendered starting frame images for the planned shots of the "
        "screenplay. Each one is a single still that depicts one specific shot of "
        "the story timeline (its planned visual at the beginning of that shot). "
        "I will load every one of these and pass it through an image-to-video model "
        "to produce the corresponding moving clip.\n"
        "IMPORTANT: do NOT include images that are visual identity references for a "
        "character, location, or prop in isolation, even though they are also images "
        "produced by the keyframe step. Those identity-reference images are not tied "
        "to any specific shot of the story timeline; they describe what an entity "
        "looks like in general. They are intermediate outputs of the keyframe step "
        "and are not the frames of the final video. I want only the per-shot frames. "
        "Include every per-shot frame — there should be exactly one per shot defined "
        "in the screenplay above."
    ),
)
