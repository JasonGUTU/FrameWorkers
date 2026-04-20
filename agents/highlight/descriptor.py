"""HighlightAgent descriptor — built from a single AgentSpec."""

from __future__ import annotations

import json

from pydantic import BaseModel

from inference.generation import select_video_service

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import AgentSpec, InputLabelSpec, SubAgentDescriptor
from .agent import HighlightAgent
from .evaluator import HighlightEvaluator
from .labels import INPUT_LABEL_SOURCE_VIDEO, INPUT_LABEL_VIDEO_ANALYSIS
from .materializer import HighlightMaterializer
from .schema import HighlightAgentInput


def build_input(
    _step_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    video = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_SOURCE_VIDEO)
    )
    analysis = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_VIDEO_ANALYSIS)
    )

    criteria = ""
    if video.payload and isinstance(video.payload.get("criteria"), str):
        criteria = video.payload["criteria"]

    return HighlightAgentInput(
        source_video_path=video.path,
        analysis_json_text=json.dumps(
            analysis.payload or {}, ensure_ascii=False, indent=2
        ) if analysis.payload else "",
        criteria=criteria,
    )


def build_captions(agent_id: str, output_dict: dict) -> dict:
    # Caption role: signal "highlight reel manifest" + metrics
    # (count/duration). Content (criteria free text) lives in the JSON
    # payload, NOT in caption.
    # See MEMORY:feedback_caption_role_not_content.
    content = output_dict.get("content", {})
    clips = content.get("clips", [])
    total_dur = sum(
        max(0, c.get("end_time", 0) - c.get("start_time", 0))
        for c in clips
    )
    return {
        agent_id: {
            "caption": (
                f"Highlight reel manifest: {len(clips)} clip(s), "
                f"{total_dur:.1f}s total, compiled from a source video. "
                f"Structured manifest — see payload for selection criteria."
            ),
            "scope": "global",
        },
        "highlight_reel": {
            "caption": (
                "Highlight reel video binary (mp4) — compiled highlight "
                "clips concatenated into a single mp4 ready for playback "
                "or re-ingestion by downstream video agents."
            ),
            "scope": "global",
        },
    }


def materializer_factory(services: dict) -> HighlightMaterializer:
    return HighlightMaterializer(video_service=services["video_service"])


SPEC = AgentSpec(
    agent_id="HighlightAgent",
    inputs=[
        InputLabelSpec(
            name=INPUT_LABEL_SOURCE_VIDEO,
            cardinality="single",
            description=(
                "The source video FILE on disk — a binary mp4 artifact "
                "(mime=video/mp4) whose actual bytes the materializer "
                "needs to feed ffmpeg for clip extraction. This label "
                "targets the mp4 binary specifically, NOT any "
                "JSON/manifest video_package artifact that may coexist "
                "in the workspace."
            ),
        ),
        InputLabelSpec(
            name=INPUT_LABEL_VIDEO_ANALYSIS,
            cardinality="single",
            optional=True,
            description=(
                "Optional VideoAnalysisAgent output providing structured "
                "scene analysis for informed clip selection. Required "
                "for narrative / content-driven selection criteria; can "
                "be skipped for purely visual / kinetic criteria."
            ),
        ),
    ],
    output_description=(
        "highlight_reel (selected clips compiled into a single reel)."
    ),
    purpose_and_routing=(
        """Extract highlight / best-moment clips from an existing video and compile them into a reel. The highlight reel IS the deliverable by default. Trigger: requests to extract specific themed moments / climax / highlight scenes / best clips into a reel."""
    ),
    input_preamble=(
        "I select the best highlight segments from a video and compile "
        "them into a highlight reel."
    ),
)


DESCRIPTOR = SubAgentDescriptor.from_spec(
    SPEC,
    agent_factory=lambda llm: HighlightAgent(llm_client=llm),
    evaluator_factory=HighlightEvaluator,
    build_input=build_input,
    build_captions=build_captions,
    service_factories={"video_service": lambda ctx: select_video_service()},
    materializer_factory=materializer_factory,
)
