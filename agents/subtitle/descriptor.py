"""SubtitleAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

import json

from pydantic import BaseModel

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import SubAgentDescriptor
from .agent import SubtitleAgent
from .labels import INPUT_LABEL_SCREENPLAY, INPUT_LABEL_VIDEO_PACKAGE
from .schema import SubtitleAgentInput
from .evaluator import SubtitleEvaluator


def build_input(
    _step_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    screenplay = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_SCREENPLAY)
    )
    video_pkg = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_VIDEO_PACKAGE)
    )
    return SubtitleAgentInput(
        screenplay_json_text=json.dumps(
            screenplay.payload or {}, ensure_ascii=False, indent=2
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
                f"SRT timing. Generated from screenplay dialogue/narration."
            ),
            "scope": "global",
        },
    }


CATALOG_ENTRY = (
    "SubtitleAgent\n"
    "  - Input: a source-text artifact with timing information — either a screenplay (for "
    "newly-created films) or a timestamped transcript (for existing videos). Optional "
    "video artifact for precise timing alignment.\n"
    "  - Output: subtitle_tracks (SRT-formatted cues with timing).\n"
    "  - Purpose: Generate timed subtitle tracks (SRT). I produce subtitles in the SOURCE "
    "language of the supplied text. For multilingual subtitles, run me on the source text "
    "FIRST to produce source-language SRT, THEN run translation on my output (or run me a "
    "second time on a translated text artifact). The subtitle file itself can be the "
    "deliverable for post-edit tasks (no compositor needed) or be passed to compositor "
    "for burn-in into a final video."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_id="SubtitleAgent",
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: SubtitleAgent(llm_client=llm),
    evaluator_factory=SubtitleEvaluator,
    build_input=build_input,
    build_captions=build_captions,
    materializer_factory=None,
    input_needs_description=(
        "I generate timed subtitle tracks (SRT format) from screenplay "
        "dialogue and narration lines, optionally aligned to video timing.\n\n"
        f"[{INPUT_LABEL_SCREENPLAY}] (single)\n"
        "The screenplay or translated screenplay containing dialogue and "
        "narration text to subtitle. Its payload is forwarded as raw JSON "
        "text.\n\n"
        f"[{INPUT_LABEL_VIDEO_PACKAGE}] (single)\n"
        "Optional video package with shot durations for timing alignment. "
        "If absent, timing is estimated from reading speed heuristics."
    ),
)
