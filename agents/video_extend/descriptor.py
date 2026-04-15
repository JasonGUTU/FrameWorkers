"""VideoExtendAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

from pydantic import BaseModel

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import SubAgentDescriptor
from .agent import VideoExtendAgent
from .labels import INPUT_LABEL_SOURCE_VIDEO
from .schema import VideoExtendAgentInput
from .evaluator import VideoExtendEvaluator
from .materializer import VideoExtendMaterializer

from inference.generation import select_video_service


def build_input(
    _step_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    video = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_SOURCE_VIDEO)
    )

    continuation = ""
    if video.payload and isinstance(video.payload.get("continuation"), str):
        continuation = video.payload["continuation"]
    elif video.caption:
        continuation = video.caption

    return VideoExtendAgentInput(
        source_video_path=video.path,
        continuation_description=continuation,
    )


def build_captions(agent_id: str, output_dict: dict) -> dict:
    content = output_dict.get("content", {})
    spec = content.get("extension_spec", {})
    dur = spec.get("target_duration_seconds", 0)
    desc = spec.get("continuation_prompt", "")
    return {
        agent_id: {
            "caption": (
                f"Video extension (+{dur}s): {desc}. "
                f"Continuation clip generated from source video."
            ),
            "scope": "global",
        },
    }


def materializer_factory(services: dict) -> VideoExtendMaterializer:
    return VideoExtendMaterializer(video_service=services["video_service"])


CATALOG_ENTRY = (
    "VideoExtendAgent\n"
    "  - Input: a source-video artifact + a continuation-description text (e.g. '延长到 15 秒', "
    "'add 5 more seconds where the character walks away').\n"
    "  - Output: extended_video (a continuation clip seamlessly appended to the source).\n"
    "  - Purpose: Extend / continue a video by generating new frames that seamlessly follow "
    "the source video's last frame. Need both an ingested source video AND a user "
    "continuation description before I can run. The output is itself a finished video — no "
    "further composition needed unless the user wants subtitles, audio, or another edit "
    "chained on top."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_id="VideoExtendAgent",
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: VideoExtendAgent(llm_client=llm),
    evaluator_factory=VideoExtendEvaluator,
    build_input=build_input,
    build_captions=build_captions,
    service_factories={
        "video_service": lambda ctx: select_video_service(),
    },
    materializer_factory=materializer_factory,
    input_needs_description=(
        "I extend/continue a video clip by generating new frames that "
        "seamlessly follow the source video's ending.\n\n"
        f"[{INPUT_LABEL_SOURCE_VIDEO}] (single)\n"
        "The source video to extend. The last frame is used as the "
        "starting point for continuation. The caption or payload should "
        "describe what should happen next."
    ),
)
