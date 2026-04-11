"""IntakeVideoAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

from pydantic import BaseModel

from ...common_schema import ResolvedArtifactEntry
from ...descriptor import SubAgentDescriptor
from .agent import IntakeVideoAgent
from .labels import INPUT_LABEL_RAW_VIDEO_UPLOAD
from .schema import IntakeVideoInput
from .evaluator import IntakeVideoEvaluator


def build_input(
    _task_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    raw = resolved_artifacts.get(INPUT_LABEL_RAW_VIDEO_UPLOAD)
    if isinstance(raw, list):
        raw = raw[0] if raw else None
    entry = ResolvedArtifactEntry.coerce(raw)
    return IntakeVideoInput(raw_video_path=entry.path)


def build_captions(agent_id: str, output_dict: dict) -> dict:
    return {
        agent_id: {
            "caption": "User-uploaded video reference. Available for downstream agents.",
            "scope": "global",
        },
    }


CATALOG_ENTRY = (
    "IntakeVideoAgent\n"
    "  - Input: raw_video_upload (placeholder caption pointing at a raw video file)\n"
    "  - Output: a caption-rich video artifact for downstream content agents.\n"
    "  - Purpose: Run a video-understanding LLM over a freshly-uploaded user video."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_id="IntakeVideoAgent",
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: IntakeVideoAgent(llm_client=llm),
    evaluator_factory=IntakeVideoEvaluator,
    build_input=build_input,
    build_captions=build_captions,
    materializer_factory=None,
    input_needs_description=(
        "I convert raw user-uploaded video into a caption-rich workspace "
        "artifact.\n\n"
        f"[{INPUT_LABEL_RAW_VIDEO_UPLOAD}] (single)\n"
        "A raw user-uploaded video whose caption starts with "
        "'Raw user upload (mime=video/' and has scope 'raw_pending'. "
        "Pick the single most recent such pending video upload."
    ),
)
