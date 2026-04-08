"""IntakeVideoAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

from pydantic import BaseModel

from ...descriptor import SubAgentDescriptor
from ...contracts import InputBundleV2
from .agent import IntakeVideoAgent
from .labels import INPUT_LABEL_RAW_VIDEO_UPLOAD
from .schema import IntakeVideoInput
from .evaluator import IntakeVideoEvaluator


def build_input(
    _task_id: str,
    input_bundle_v2: InputBundleV2,
) -> BaseModel:
    resolved = input_bundle_v2.resolved_artifacts
    entry = resolved.get(INPUT_LABEL_RAW_VIDEO_UPLOAD, {})
    if isinstance(entry, list):
        entry = entry[0] if entry else {}
    raw_video_path = ""
    user_intent = ""
    if isinstance(entry, dict):
        raw_video_path = str(entry.get("path", "") or "")
        user_intent = str(entry.get("why", "") or "")
    return IntakeVideoInput(raw_video_path=raw_video_path, user_intent=user_intent)


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
    materializer_factory=None,
    input_needs_description=(
        "I convert raw user-uploaded video into a caption-rich workspace "
        "artifact.\n\n"
        f"[{INPUT_LABEL_RAW_VIDEO_UPLOAD}] (single)\n"
        "A raw user-uploaded video that has not yet been semantically "
        "analyzed. The placeholder caption marks it as 'raw user upload, "
        "mime=video/*, awaiting semantic analysis'. Pick the single most "
        "recent such pending video upload."
    ),
)
