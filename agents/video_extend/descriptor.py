"""VideoExtendAgent descriptor — built from a single AgentSpec."""

from __future__ import annotations

import json

from pydantic import BaseModel

from inference.generation import select_video_service

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import AgentSpec, InputLabelSpec, SubAgentDescriptor
from .agent import VideoExtendAgent
from .evaluator import VideoExtendEvaluator
from .labels import (
    INPUT_LABEL_CONTINUATION_INSTRUCTION,
    INPUT_LABEL_SOURCE_VIDEO,
)
from .materializer import VideoExtendMaterializer
from .schema import VideoExtendAgentInput


def build_input(
    _step_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    video = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_SOURCE_VIDEO)
    )
    instruction = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_CONTINUATION_INSTRUCTION)
    )

    if instruction.payload:
        continuation = json.dumps(
            instruction.payload, ensure_ascii=False, indent=2
        )
    else:
        continuation = instruction.caption

    return VideoExtendAgentInput(
        source_video_path=video.path,
        continuation_description=continuation,
    )


def build_captions(agent_id: str, output_dict: dict) -> dict:
    # Caption role: signal "video extension output" + target duration
    # (metric). Content (continuation_prompt free text) lives in the
    # JSON payload, NOT in caption.
    # See MEMORY:feedback_caption_role_not_content.
    content = output_dict.get("content", {})
    spec = content.get("extension_spec", {})
    dur = spec.get("target_duration_seconds", 0)
    return {
        agent_id: {
            "caption": (
                f"Extended video (+{dur}s): continuation clip generated "
                f"from a source video. Structured manifest — see payload "
                f"for the extension specification."
            ),
            "scope": "global",
        },
        "video_extend_output": {
            "caption": (
                "Extended video binary (mp4) — continuation clip generated "
                "from the source video, ready for re-ingestion by "
                "downstream video agents (analysis / style transfer / "
                "inpainting / compositing)."
            ),
            "scope": "global",
        },
    }


def materializer_factory(services: dict) -> VideoExtendMaterializer:
    return VideoExtendMaterializer(video_service=services["video_service"])


SPEC = AgentSpec(
    agent_id="VideoExtendAgent",
    inputs=[
        InputLabelSpec(
            name=INPUT_LABEL_SOURCE_VIDEO,
            cardinality="single",
            description=(
                "The source video clip FILE on disk — a binary mp4 "
                "artifact (mime=video/mp4) whose actual bytes the "
                "materializer needs to extract the last frame from via "
                "ffmpeg (the last frame becomes the starting keyframe "
                "for the continuation). This label targets the mp4 "
                "binary specifically, NOT any JSON/manifest "
                "video_package artifact that may coexist."
            ),
        ),
        InputLabelSpec(
            name=INPUT_LABEL_CONTINUATION_INSTRUCTION,
            cardinality="single",
            description=(
                "The user's natural-language instruction describing how "
                "the video should be extended — what happens next, "
                "target duration, plot beat, physical movement, or scene "
                "transition. Typically the ``[creative_brief]`` artifact "
                "registered from the user's chat / text upload (caption "
                "usually starts with 'User-submitted creative brief'). "
                "Pick the single most recent such instruction."
            ),
        ),
    ],
    output_description=(
        "extended_video (a continuation clip seamlessly appended to the "
        "source)."
    ),
    purpose_and_trigger=(
        """Extend the duration of an existing video clip by appending a continuation generated from its last frame (slow-mo, atmospheric inserts, close-ups, sound-effect overlays). The extended clip IS the deliverable by default. Trigger: requests to lengthen / add cinematic devices to an existing clip — visual continuation grounded in the source's last frame. This agent does NOT generate new screenplay or scene content; it only extrapolates visually from the source clip's tail."""
    ),
    input_preamble=(
        "I extend / continue a video clip by generating new frames that "
        "seamlessly follow the source video's ending."
    ),
)


DESCRIPTOR = SubAgentDescriptor.from_spec(
    SPEC,
    agent_factory=lambda llm: VideoExtendAgent(llm_client=llm),
    evaluator_factory=VideoExtendEvaluator,
    build_input=build_input,
    build_captions=build_captions,
    service_factories={"video_service": lambda ctx: select_video_service()},
    materializer_factory=materializer_factory,
)
