"""HighlightAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

import json

from pydantic import BaseModel

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import SubAgentDescriptor
from .agent import HighlightAgent
from .labels import INPUT_LABEL_SOURCE_VIDEO, INPUT_LABEL_VIDEO_ANALYSIS
from .schema import HighlightAgentInput
from .evaluator import HighlightEvaluator
from .materializer import HighlightMaterializer

from inference.generation import select_video_service


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

    # Extract criteria from the video entry caption/payload
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
    content = output_dict.get("content", {})
    clips = content.get("clips", [])
    criteria = content.get("criteria", "")
    total_dur = sum(
        max(0, c.get("end_time", 0) - c.get("start_time", 0))
        for c in clips
    )
    return {
        agent_id: {
            "caption": (
                f"Highlight reel: {len(clips)} clip(s), {total_dur:.1f}s total. "
                f"Criteria: {criteria}."
            ),
            "scope": "global",
        },
    }


def materializer_factory(services: dict) -> HighlightMaterializer:
    return HighlightMaterializer(video_service=services["video_service"])


CATALOG_ENTRY = (
    "HighlightAgent\n"
    "  - Input: a source-video artifact + selection criteria text (e.g. '剪出精彩片段', "
    "'best moments') + OPTIONAL video-analysis artifact for scene-aware selection.\n"
    "  - Output: highlight_reel (selected clips compiled into a single reel).\n"
    "  - Purpose: Select the best / most relevant segments from a video and compile them "
    "into a highlight reel. Need both an ingested source video AND user selection criteria "
    "before I can run. If the user wants content-driven selection (e.g. 'extract key "
    "discussions' from a meeting), prefer running deep video analysis FIRST so I get "
    "richer scene metadata; for simple 'best parts of a vlog' I can run without it."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_id="HighlightAgent",
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: HighlightAgent(llm_client=llm),
    evaluator_factory=HighlightEvaluator,
    build_input=build_input,
    build_captions=build_captions,
    service_factories={
        "video_service": lambda ctx: select_video_service(),
    },
    materializer_factory=materializer_factory,
    input_needs_description=(
        "I select the best highlight segments from a video and compile "
        "them into a highlight reel.\n\n"
        f"[{INPUT_LABEL_SOURCE_VIDEO}] (single)\n"
        "The source video to extract highlights from. Payload may "
        "contain 'criteria' describing what kind of highlights to "
        "select.\n\n"
        f"[{INPUT_LABEL_VIDEO_ANALYSIS}] (single)\n"
        "Optional VideoAnalysisAgent output providing structured scene "
        "analysis for informed clip selection."
    ),
)
