"""VideoAgent descriptor — built from a single AgentSpec."""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel

from inference.generation import select_video_service

from ..common_schema import ImageReferenceEntry, ResolvedArtifactEntry
from ..descriptor import AgentSpec, InputLabelSpec, SubAgentDescriptor
from .agent import VideoAgent
from .evaluator import VideoEvaluator
from .labels import (
    INPUT_LABEL_KEYFRAMES_METADATA,
    INPUT_LABEL_SCREENPLAY,
    INPUT_LABEL_SHOT_STILLS,
)
from .materializer import VideoMaterializer
from .schema import VideoAgentInput


def build_input(
    _step_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    sp = ResolvedArtifactEntry.coerce(resolved_artifacts.get(INPUT_LABEL_SCREENPLAY))
    kf = ResolvedArtifactEntry.coerce(resolved_artifacts.get(INPUT_LABEL_KEYFRAMES_METADATA))
    return VideoAgentInput(
        screenplay_json_text=json.dumps(
            sp.payload or {}, ensure_ascii=False, indent=2
        ),
        keyframes_metadata_json_text=json.dumps(
            kf.payload or {}, ensure_ascii=False, indent=2
        ),
        shot_stills=ImageReferenceEntry.list_from_resolved(
            resolved_artifacts.get(INPUT_LABEL_SHOT_STILLS)
        ),
    )


def materializer_factory(services: dict[str, Any]) -> VideoMaterializer:
    return VideoMaterializer(video_service=services["video_service"])


def build_captions(agent_id: str, output_dict: dict) -> dict:
    content = output_dict.get("content", {})
    scenes = content.get("scenes", [])
    shot_count = sum(
        len(sc.get("shot_segments", [])) for sc in scenes if isinstance(sc, dict)
    )
    caps: dict = {}
    caps[agent_id] = {
        "caption": (
            f"[JSON MANIFEST] Video-assembly planning metadata: "
            f"{len(scenes)} scene(s), {shot_count} shot clip(s) with "
            f"timing. Read by a downstream audio-mix step's LLM for "
            f"mix planning."
        ),
        "scope": "global",
    }
    for sc in scenes:
        if not isinstance(sc, dict):
            continue
        scene_id = sc.get("scene_id", "")
        for seg in sc.get("shot_segments", []):
            shot_id = seg.get("shot_id", "") if isinstance(seg, dict) else ""
            if shot_id:
                caps[f"clip_{shot_id}"] = {
                    "caption": (
                        f"[BINARY MP4 FILE · mime=video/mp4 · sys_id "
                        f"clip_{shot_id}] Video clip bytes for shot "
                        f"{shot_id}. One segment of the final video."
                    ),
                    "scope": f"shot:{shot_id}",
                }
        if scene_id:
            caps[f"clip_{scene_id}"] = {
                "caption": (
                    f"[BINARY MP4 FILE · mime=video/mp4 · sys_id "
                    f"clip_{scene_id}] Scene-cut bytes for scene "
                    f"{scene_id} — all shots concatenated. Intermediate "
                    f"assembly, not final."
                ),
                "scope": f"scene:{scene_id}",
            }
    caps["clip_final"] = {
        "caption": (
            f"[BINARY MP4 FILE · mime=video/mp4 · sys_id clip_final] "
            f"Complete assembled video bytes ({shot_count} shots). "
            f"Final visual deliverable — consumed by a downstream "
            f"audio-mix step's materializer via ffmpeg for audio "
            f"extraction + muxing."
        ),
        "scope": "global",
    }
    return caps


SPEC = AgentSpec(
    agent_id="VideoAgent",
    inputs=[
        InputLabelSpec(
            name=INPUT_LABEL_SCREENPLAY,
            cardinality="single",
            description=(
                "The unified screenplay document defining the temporal "
                "structure of the story as an ordered sequence of scenes "
                "and shots, with per-shot creative direction (camera, "
                "action, mood). I rely on this to know how many shots "
                "there are and what each shot is supposed to convey. "
                "Choose at most one."
            ),
        ),
        InputLabelSpec(
            name=INPUT_LABEL_KEYFRAMES_METADATA,
            cardinality="single",
            description=(
                "The planning document produced by the keyframe step "
                "that — for each shot in the screenplay — gives a textual "
                "description of the planned frame and a separate hint "
                "about how that frame should move when animated. I use "
                "this to fetch the prompt and motion intent for each "
                "shot. It is a JSON document, not an image. Choose at "
                "most one."
            ),
        ),
        InputLabelSpec(
            name=INPUT_LABEL_SHOT_STILLS,
            cardinality="collection",
            description=(
                "The actual rendered starting frame images for the "
                "planned shots of the screenplay. Each one is a single "
                "still that depicts one specific shot of the story "
                "timeline (its planned visual at the beginning of that "
                "shot). I will load every one of these and pass it "
                "through an image-to-video model to produce the "
                "corresponding moving clip.\n"
                "IMPORTANT: do NOT include images that are visual "
                "identity references for a character, location, or prop "
                "in isolation, even though they are also images produced "
                "by the keyframe step. Those identity-reference images "
                "are not tied to any specific shot of the story timeline; "
                "they describe what an entity looks like in general. They "
                "are intermediate outputs of the keyframe step and are "
                "not the frames of the final video. I want only the "
                "per-shot frames. Include every per-shot frame — there "
                "should be exactly one per shot defined in the screenplay "
                "above."
            ),
        ),
    ],
    output_description=(
        "video_package (per-shot clips, per-scene assembled clips, "
        "final assembled video — clips carry baked-in character "
        "dialogue + on-screen foley in their audio track, generated "
        "together with the visual frames; the output does not include "
        "music or ambience layers)."
    ),
    purpose_and_trigger=(
        """Generate per-shot video clips from keyframe images via image-to-video synthesis and assemble them into the full film. The image-to-video model bakes character dialogue + on-screen foley directly into each clip's audio track at generation time — the output mp4 already carries baked dialogue+foley audio. The output does not include music or ambience layers. Trigger: include whenever the plan produces a multi-shot assembled film from a screenplay and per-shot keyframes; requires both upstream."""
    ),
    input_preamble=(
        "I generate per-shot moving video clips by feeding a planned "
        "starting frame and a motion description into an image-to-video "
        "model, then assemble the clips into a final video.\n\n"
        "For each [label] below, find every artifact in the registry "
        "whose caption describes the same kind of thing. Use the "
        "natural-language caption only — do not match by filename or by "
        "any tag. Pay attention to the difference between visual "
        "identity references (which depict an entity in isolation) and "
        "actual planned frames of shots (which depict a specific moment "
        "of the story). I want the latter, never the former."
    ),
)


DESCRIPTOR = SubAgentDescriptor.from_spec(
    SPEC,
    agent_factory=lambda llm: VideoAgent(llm_client=llm),
    evaluator_factory=VideoEvaluator,
    build_input=build_input,
    build_captions=build_captions,
    service_factories={"video_service": lambda ctx: select_video_service()},
    materializer_factory=materializer_factory,
)
