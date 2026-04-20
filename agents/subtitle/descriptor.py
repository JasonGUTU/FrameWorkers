"""SubtitleAgent descriptor — built from a single AgentSpec.

Using ``SubAgentDescriptor.from_spec`` means the catalog_entry (read by
the Director planner) and input_needs_description (read by InputResolver)
are rendered from one source, so they can't drift apart the way they did
previously (catalog claimed "screenplay OR transcript", needs_description
only mentioned screenplay).
"""

from __future__ import annotations

import json

from pydantic import BaseModel

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import AgentSpec, InputLabelSpec, SubAgentDescriptor
from .agent import SubtitleAgent
from .evaluator import SubtitleEvaluator
from .labels import INPUT_LABEL_SOURCE_TEXT, INPUT_LABEL_VIDEO_PACKAGE
from .schema import SubtitleAgentInput


def build_input(
    _step_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    source = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_SOURCE_TEXT)
    )
    video_pkg = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_VIDEO_PACKAGE)
    )
    return SubtitleAgentInput(
        screenplay_json_text=json.dumps(
            source.payload or {}, ensure_ascii=False, indent=2
        ),
        video_json_text=json.dumps(
            video_pkg.payload or {}, ensure_ascii=False, indent=2
        ) if video_pkg.payload else "",
    )


def build_captions(agent_id: str, output_dict: dict) -> dict:
    content = output_dict.get("content", {})
    tracks = content.get("tracks", [])
    langs = ", ".join(t.get("language", "?") for t in tracks) or "?"
    cue_count = sum(len(t.get("cues", [])) for t in tracks)
    return {
        agent_id: {
            "caption": (
                f"Subtitle track(s) ({langs}): {cue_count} cue(s) with "
                f"SRT timing. Generated from source-text dialogue/narration."
            ),
            "scope": "global",
        },
    }


SPEC = AgentSpec(
    agent_id="SubtitleAgent",
    inputs=[
        InputLabelSpec(
            name=INPUT_LABEL_SOURCE_TEXT,
            cardinality="single",
            description=(
                "Timed source text to subtitle. Accepts ANY of: a "
                "screenplay document (for newly-created films); a "
                "translated screenplay; a timestamped transcript (for "
                "existing media with no screenplay); or a pre-existing "
                "subtitle track in text form. Payload is forwarded as "
                "raw JSON text and the LLM extracts dialogue/narration "
                "lines from whatever structure it has."
            ),
        ),
        InputLabelSpec(
            name=INPUT_LABEL_VIDEO_PACKAGE,
            cardinality="single",
            optional=True,
            description=(
                "Optional assembled-video package (JSON manifest) with "
                "per-shot durations for precise timing alignment. If "
                "absent, cue timing is estimated from reading-speed "
                "heuristics against the source text."
            ),
        ),
    ],
    output_description=(
        "subtitle_tracks (SRT-formatted cues with timing, one track per "
        "language)."
    ),
    purpose_and_routing=(
        """Generate timed SRT subtitle tracks from a source text (either a screenplay's dialogue or a transcript of existing audio). Trigger: requests to add subtitle / caption tracks (any language, single or bilingual) onto a video deliverable."""
    ),
    input_preamble=(
        "I generate timed subtitle tracks (SRT format) by reading a timed "
        "source text (screenplay, translated screenplay, timestamped "
        "transcript, or existing subtitle text) and optionally aligning "
        "cue timing to a video package."
    ),
)


DESCRIPTOR = SubAgentDescriptor.from_spec(
    SPEC,
    agent_factory=lambda llm: SubtitleAgent(llm_client=llm),
    evaluator_factory=SubtitleEvaluator,
    build_input=build_input,
    build_captions=build_captions,
)
