"""AudioAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from ..descriptor import SubAgentDescriptor
from .agent import AudioAgent
from .labels import INPUT_LABEL_FINAL_VIDEO, INPUT_LABEL_SCREENPLAY
from .schema import AudioAgentInput
from .evaluator import AudioEvaluator
from .materializer import AudioMaterializer
from inference.generation import select_audio_service


def build_input(
    _task_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    sp = resolved_artifacts.get(INPUT_LABEL_SCREENPLAY, {})
    sp_payload = sp.get("payload", {}) if isinstance(sp, dict) else {}

    fv = resolved_artifacts.get(INPUT_LABEL_FINAL_VIDEO, {})
    fv_payload = fv.get("payload", {}) if isinstance(fv, dict) else {}

    return AudioAgentInput(
        screenplay=sp_payload,
        final_video=fv_payload,
    )


def materializer_factory(services: dict[str, Any]) -> AudioMaterializer:
    return AudioMaterializer(audio_service=services["audio_service"])


def build_captions(agent_id: str, output_dict: dict) -> dict:
    content = output_dict.get("content", {})
    scenes = content.get("scenes", [])
    scene_count = len(scenes)
    narr_count = sum(
        len(sc.get("narration_segments", []))
        for sc in scenes if isinstance(sc, dict)
    )
    caps: dict = {}
    caps[agent_id] = {
        "caption": (
            f"Audio package: {scene_count} scene(s), {narr_count} "
            f"narration segment(s), music + ambience per scene. "
            f"Final audio for video muxing."
        ),
        "scope": "global",
    }
    for sc in scenes:
        if not isinstance(sc, dict):
            continue
        scene_id = sc.get("scene_id", "")
        if not scene_id:
            continue
        for seg in sc.get("narration_segments", []):
            aid = seg.get("audio_asset", {}).get("asset_id", "") if isinstance(seg, dict) else ""
            speaker = seg.get("speaker", "narrator") if isinstance(seg, dict) else "narrator"
            if aid:
                caps[aid] = {
                    "caption": f"Narration segment by {speaker} for scene {scene_id}. One voice line of the scene's dialogue.",
                    "scope": f"scene:{scene_id}",
                }
        mc = sc.get("music_cue", {})
        mc_aid = mc.get("audio_asset", {}).get("asset_id", "") if isinstance(mc, dict) else ""
        if mc_aid:
            caps[mc_aid] = {
                "caption": f"Music cue for scene {scene_id}. Instrumental underscore, no voice.",
                "scope": f"scene:{scene_id}",
            }
        ab = sc.get("ambience_bed", {})
        ab_aid = ab.get("audio_asset", {}).get("asset_id", "") if isinstance(ab, dict) else ""
        if ab_aid:
            caps[ab_aid] = {
                "caption": f"Ambience bed for scene {scene_id}. Background atmosphere only.",
                "scope": f"scene:{scene_id}",
            }
        mx = sc.get("mix", {})
        mx_aid = mx.get("audio_asset", {}).get("asset_id", "") if isinstance(mx, dict) else ""
        if mx_aid:
            caps[mx_aid] = {
                "caption": f"Scene mix for scene {scene_id} — narration, music, and ambience combined.",
                "scope": f"scene:{scene_id}",
            }
    fa = content.get("final_audio_asset", {})
    if isinstance(fa, dict) and fa.get("asset_id"):
        caps[fa["asset_id"]] = {
            "caption": "Complete audio track for the whole story. All scene mixes joined in order.",
            "scope": "global",
        }
    fd = content.get("final_delivery_asset", {})
    if isinstance(fd, dict) and fd.get("asset_id"):
        caps[fd["asset_id"]] = {
            "caption": "Final deliverable: video muxed with complete audio. End product of the pipeline.",
            "scope": "global",
        }
    return caps


CATALOG_ENTRY = (
    "AudioAgent\n"
    "  - Input: screenplay + video package\n"
    "  - Output: audio_package (narration, music, ambience, scene mix, final audio)\n"
    "  - Purpose: Plan audio aligned with video timing."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_id="AudioAgent",
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: AudioAgent(llm_client=llm),
    evaluator_factory=AudioEvaluator,
    build_input=build_input,
    build_captions=build_captions,
    service_factories={
        "audio_service": lambda ctx: select_audio_service(),
    },
    materializer_factory=materializer_factory,
    input_needs_description=(
        "I plan and produce the audio side of the video: per-scene narration, music, "
        "ambience, and the final mixed audio aligned to the video timeline.\n\n"
        "For each [label] below, find every artifact in the registry whose caption "
        "describes the same kind of thing. Use the natural-language caption only — "
        "do not match by filename or by any tag.\n\n"
        f"[{INPUT_LABEL_SCREENPLAY}] (single)\n"
        "The unified screenplay document for the story: scenes broken into shots "
        "with dialogue lines, emotional beats, and creative direction. I read "
        "this to know what to say (narration) and what mood to score (music). "
        "Choose at most one.\n\n"
        f"[{INPUT_LABEL_FINAL_VIDEO}] (single)\n"
        "The single complete finished video file for the whole story (one continuous "
        "video, not per-shot or per-scene fragments). It is the visual side of the "
        "deliverable, against which I will mux the final audio. This is a JSON "
        "manifest describing the assembled video, not the raw video file itself. "
        "Choose at most one — and only the document describing the complete final "
        "video, not intermediate per-shot or per-scene assemblies."
    ),
)
