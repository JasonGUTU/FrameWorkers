"""IntakeVideoAgent descriptor — built from a single AgentSpec."""

from __future__ import annotations

from pydantic import BaseModel

from ...common_schema import ResolvedArtifactEntry
from ...descriptor import AgentSpec, InputLabelSpec, SubAgentDescriptor
from .agent import IntakeVideoAgent
from .evaluator import IntakeVideoEvaluator
from .labels import INPUT_LABEL_RAW_VIDEO_UPLOAD
from .schema import IntakeVideoInput


def build_input(
    _step_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    raw = resolved_artifacts.get(INPUT_LABEL_RAW_VIDEO_UPLOAD)
    if isinstance(raw, list):
        raw = raw[0] if raw else None
    entry = ResolvedArtifactEntry.coerce(raw)
    return IntakeVideoInput(raw_video_path=entry.path)


def build_captions(agent_id: str, _output_dict: dict) -> dict:
    # Pure role/载体 caption — content (visual_summary, video_asset) lives
    # only in the JSON snapshot payload; consumers read it via entry.payload.
    # See MEMORY:feedback_caption_role_not_content.
    return {
        agent_id: {
            "caption": (
                "Structured metadata document (JSON) for a user-uploaded "
                "video. Payload carries the visual summary and video-asset "
                "metadata."
            ),
            "scope": "global",
        },
    }


SPEC = AgentSpec(
    agent_id="IntakeVideoAgent",
    inputs=[
        InputLabelSpec(
            name=INPUT_LABEL_RAW_VIDEO_UPLOAD,
            cardinality="single",
            description=(
                "A raw user-uploaded video whose caption starts with "
                "'Raw user upload (mime=video/' and has scope "
                "'raw_pending'. Pick the single most recent such pending "
                "video upload."
            ),
        ),
    ],
    output_description=(
        "a caption-rich video artifact discoverable by downstream "
        "video-consuming agents (VideoAnalysisAgent, StyleTransferAgent, "
        "VideoExtendAgent, HighlightAgent, TranscriptionAgent, "
        "SubtitleAgent for existing video)."
    ),
    purpose_and_routing=(
        """Intake a raw user-uploaded video and register it as a caption-rich workspace artifact. Trigger: user uploaded a video file."""
    ),
    input_preamble=(
        "I convert raw user-uploaded video into a caption-rich workspace "
        "artifact."
    ),
    promotes_consumed_inputs_to_global=True,
)


DESCRIPTOR = SubAgentDescriptor.from_spec(
    SPEC,
    agent_factory=lambda llm: IntakeVideoAgent(llm_client=llm),
    evaluator_factory=IntakeVideoEvaluator,
    build_input=build_input,
    build_captions=build_captions,
)
