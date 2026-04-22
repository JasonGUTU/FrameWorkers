"""NarrationAgent descriptor — built from a single AgentSpec."""

from __future__ import annotations

import json

from pydantic import BaseModel

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import AgentSpec, InputLabelSpec, SubAgentDescriptor
from .agent import NarrationAgent
from .evaluator import NarrationEvaluator
from .labels import INPUT_LABEL_CREATIVE_BRIEF
from .schema import NarrationAgentInput


def build_input(
    _step_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    """Pass-through: raw brief payload as JSON text for the LLM to read."""
    brief = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_CREATIVE_BRIEF)
    )
    return NarrationAgentInput(
        creative_brief_json_text=json.dumps(
            brief.payload or {}, ensure_ascii=False, indent=2
        ),
    )


def build_captions(agent_id: str, output_dict: dict) -> dict:
    # Caption role: tell downstream IllustrationAgent + NarratorAgent
    # there's an illustrated-storytelling script available. Counts are
    # neutral; art-style text is in payload, not caption.
    # See MEMORY:feedback_caption_role_not_content.
    content = output_dict.get("content", {})
    seg_count = len(content.get("segments", []))
    line_count = sum(len(s.get("lines", [])) for s in content.get("segments", []))
    return {
        agent_id: {
            "caption": (
                f"Illustrated-storytelling narration script: "
                f"{seg_count} segment(s), {line_count} narrator line(s). "
                f"Carries per-segment image_prompt + per-line TTS text + "
                f"cross-segment art-style anchor. Consumed by an "
                f"illustration image step and a narrator TTS step."
            ),
            "scope": "global",
        },
    }


SPEC = AgentSpec(
    agent_id="NarrationAgent",
    inputs=[
        InputLabelSpec(
            name=INPUT_LABEL_CREATIVE_BRIEF,
            cardinality="single",
            description=(
                "A natural-language brief or prose describing the story to "
                "tell. May be a short prompt ('a story about a lonely "
                "lighthouse keeper') or a long already-written prose / "
                "outline. The caption describes it as a creative brief / "
                "project intent description. Pick the single most recent / "
                "most authoritative such brief."
            ),
        ),
    ],
    output_description=(
        "narration_script (language + overall_style + segments with "
        "per-segment image_prompt and per-line TTS text)."
    ),
    purpose_and_routing=(
        """Creative head for illustrated-storytelling / audiobook-with-pictures videos. Produces a narrator script split into illustration-aligned segments — one picture's worth of story per segment. Trigger: user wants to 'read a story as an illustrated audiobook', 'make an illustrated story-time video', 'narrate this story with matching pictures', or similar. Do NOT use for cinematic / multi-shot video flows (those go through Screenplay → KeyFrame → Video instead)."""
    ),
    input_preamble=(
        "I am the creative head for illustrated-storytelling videos. "
        "I take a creative brief or long prose and produce a narrator-voice "
        "script split into illustration-aligned segments."
    ),
)


DESCRIPTOR = SubAgentDescriptor.from_spec(
    SPEC,
    agent_factory=lambda llm: NarrationAgent(llm_client=llm),
    evaluator_factory=NarrationEvaluator,
    build_input=build_input,
    build_captions=build_captions,
)
