"""VideoAnalysisAgent descriptor — built from a single AgentSpec."""

from __future__ import annotations

from pydantic import BaseModel

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import AgentSpec, InputLabelSpec, SubAgentDescriptor
from .agent import VideoAnalysisAgent
from .evaluator import VideoAnalysisEvaluator
from .labels import INPUT_LABEL_SOURCE_VIDEO
from .schema import VideoAnalysisAgentInput


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
    # Caption role: signal "video analysis document" for downstream
    # consumers (Story reference, Music mood derivation). Content
    # (title / genre free text) lives in the JSON payload, NOT caption.
    # See MEMORY:feedback_caption_role_not_content.
    content = output_dict.get("content", {})
    scene_count = len(content.get("scenes", []))
    return {
        agent_id: {
            "caption": (
                f"Video analysis document: {scene_count} scene(s). "
                f"Structured scene-by-scene breakdown with entities and "
                f"descriptions."
            ),
            "scope": "global",
        },
    }


SPEC = AgentSpec(
    agent_id="VideoAnalysisAgent",
    inputs=[
        InputLabelSpec(
            name=INPUT_LABEL_SOURCE_VIDEO,
            cardinality="single",
            description=(
                "The video FILE on disk to analyze — a binary mp4 "
                "artifact (mime=video/mp4) whose actual bytes a vision-"
                "capable LLM watches to produce a structured breakdown "
                "(scene boundaries, visual descriptions, entities, "
                "summary). This label targets the mp4 binary "
                "specifically, NOT any JSON/manifest video_package "
                "artifact that may coexist."
            ),
        ),
    ],
    output_description=(
        "video_analysis (scene segments, per-scene visual descriptions, "
        "entities, overall content summary)."
    ),
    purpose_and_routing=(
        """Deep structured analysis of an existing video — scene boundaries, mood, entities, climax candidates — producing a structured JSON for downstream consumers. Trigger: requests to analyse an existing video's narrative beats / mood curve / pacing / climax detection."""
    ),
    input_preamble=(
        "I perform deep structured analysis of video content: scene "
        "detection, visual description, entity identification, and "
        "content summarization."
    ),
)


DESCRIPTOR = SubAgentDescriptor.from_spec(
    SPEC,
    agent_factory=lambda llm: VideoAnalysisAgent(llm_client=llm),
    evaluator_factory=VideoAnalysisEvaluator,
    build_input=build_input,
    build_captions=build_captions,
)
