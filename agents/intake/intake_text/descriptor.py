"""IntakeTextAgent descriptor — built from a single AgentSpec."""

from __future__ import annotations

from pydantic import BaseModel

from ...common_schema import ResolvedArtifactEntry
from ...descriptor import AgentSpec, InputLabelSpec, SubAgentDescriptor
from .agent import IntakeTextAgent
from .evaluator import IntakeTextEvaluator
from .labels import INPUT_LABEL_RAW_TEXT_UPLOAD
from .schema import IntakeTextInput


def build_input(
    _step_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    raw = resolved_artifacts.get(INPUT_LABEL_RAW_TEXT_UPLOAD)
    if isinstance(raw, list):
        raw = raw[0] if raw else None
    entry = ResolvedArtifactEntry.coerce(raw)
    return IntakeTextInput(raw_text_path=entry.path)


def build_captions(agent_id: str, _output_dict: dict) -> dict:
    # Pure role/载体 caption — content (the user's raw text + optional
    # LLM summary) lives only in the JSON snapshot payload; consumers
    # read it via entry.payload, not caption.
    # See MEMORY:feedback_caption_role_not_content.
    return {
        agent_id: {
            "caption": (
                "Structured metadata document (JSON) for a user-submitted "
                "text brief. Payload carries the raw text plus an optional "
                "LLM summary for long uploads. Pipeline entry point — "
                "consumed by story and screenplay agents."
            ),
            "scope": "global",
        },
    }


SPEC = AgentSpec(
    agent_id="IntakeTextAgent",
    inputs=[
        InputLabelSpec(
            name=INPUT_LABEL_RAW_TEXT_UPLOAD,
            cardinality="single",
            description=(
                "A raw user-uploaded text artifact whose caption starts "
                "with 'Raw user upload (mime=text/plain)' and has scope "
                "'raw_pending'. Pick the single most recent such pending "
                "text upload."
            ),
        ),
    ],
    output_description=(
        "a caption-rich text artifact suitable for downstream agents to "
        "find via their semantic-typed labels (e.g. [creative_brief])."
    ),
    purpose_and_routing=(
        """Pipeline root — run FIRST on any user request containing text. Produces a caption-rich text artifact (creative brief) from the raw user upload. Trigger: any user message with text content (essentially every user turn)."""
    ),
    input_preamble=(
        "I convert raw user-uploaded text into a caption-rich workspace "
        "artifact. I am invoked once per upload, before any content agent "
        "runs."
    ),
    # Text intake does NOT promote: IntakeTextAgent's JSON snapshot is
    # self-contained (payload carries {text, summary}), so downstream agents
    # consume the snapshot's payload, never the raw .txt. Promoting would
    # surface a payload=None .txt that competes with the JSON for
    # content-semantic labels like [creative_brief] and causes resolver
    # ambiguity. Contrast with image/video intake, whose JSON only carries a
    # URI pointer to the binary — there promote IS required so downstream
    # multimodal/ffmpeg consumers can discover the raw bytes.
    promotes_consumed_inputs_to_global=False,
)


DESCRIPTOR = SubAgentDescriptor.from_spec(
    SPEC,
    agent_factory=lambda llm: IntakeTextAgent(llm_client=llm),
    evaluator_factory=IntakeTextEvaluator,
    build_input=build_input,
    build_captions=build_captions,
)
