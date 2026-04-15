"""VideoAnalysisAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

from pydantic import BaseModel

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import SubAgentDescriptor
from .agent import VideoAnalysisAgent
from .labels import INPUT_LABEL_SOURCE_VIDEO
from .schema import VideoAnalysisAgentInput
from .evaluator import VideoAnalysisEvaluator


def build_input(
    _step_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    video = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_SOURCE_VIDEO)
    )
    return VideoAnalysisAgentInput(
        source_video_path=video.path,
    )


def build_captions(agent_id: str, output_dict: dict) -> dict:
    content = output_dict.get("content", {})
    summary = content.get("video_summary", {})
    title = summary.get("title", "Untitled")
    scene_count = len(content.get("scenes", []))
    genre = summary.get("genre", "")
    return {
        agent_id: {
            "caption": (
                f"Video analysis: '{title}' — {scene_count} scene(s), "
                f"{genre}. Structured scene-by-scene breakdown with "
                f"entities and descriptions."
            ),
            "scope": "global",
        },
    }


CATALOG_ENTRY = (
    "VideoAnalysisAgent\n"
    "  - Input: a source-video artifact + analysis-intent text (what aspects the user cares "
    "about — e.g. 'find the funniest moments', 'identify all speakers').\n"
    "  - Output: video_analysis (scene segments, per-scene visual descriptions, entities, "
    "overall content summary).\n"
    "  - Purpose: Deep structured analysis of video content via vision LLM — scene detection, "
    "visual description, entity identification, content summarization. Run me when the user "
    "wants understanding / analysis / summarization of an existing video, OR as a prep step "
    "before content-driven highlight selection (so the highlight step gets richer scene "
    "metadata). SKIP when the user only wants simple per-clip operations (style transfer, "
    "inpainting, transcription)."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_id="VideoAnalysisAgent",
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: VideoAnalysisAgent(llm_client=llm),
    evaluator_factory=VideoAnalysisEvaluator,
    build_input=build_input,
    build_captions=build_captions,
    materializer_factory=None,
    input_needs_description=(
        "I perform deep structured analysis of video content: scene "
        "detection, visual description, entity identification, and "
        "content summarization.\n\n"
        f"[{INPUT_LABEL_SOURCE_VIDEO}] (single)\n"
        "The video file to analyze. I use a vision-capable LLM to "
        "watch the video and produce a structured breakdown."
    ),
)
