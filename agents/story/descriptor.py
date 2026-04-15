"""StoryAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

import json

from pydantic import BaseModel

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import SubAgentDescriptor
from .agent import StoryAgent
from .labels import INPUT_LABEL_CREATIVE_BRIEF
from .schema import StoryAgentInput
from .evaluator import StoryEvaluator


def build_input(
    _step_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    """Construct typed input from the resolved artifact dict.

    Univa-style pass-through: dump the entire upstream IntakeTextAgent
    payload as a raw indented JSON text blob into
    ``creative_brief_json_text``. No ``.content.text`` unwrap, no
    field enumeration — the whole upstream JSON object (whatever shape
    it happens to have) is forwarded verbatim for the LLM to read.
    """
    brief = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_CREATIVE_BRIEF)
    )
    return StoryAgentInput(
        creative_brief_json_text=json.dumps(
            brief.payload or {}, ensure_ascii=False, indent=2
        ),
    )


def build_captions(agent_id: str, output_dict: dict) -> dict:
    content = output_dict.get("content", {})
    scene_count = len(content.get("scene_outline", []))
    char_count = len(content.get("cast", []))
    style = content.get("style", {})
    genres = ", ".join(style.get("genre", [])) or "unspecified genre"
    return {
        agent_id: {
            "caption": (
                f"Story blueprint: {scene_count} scene(s), {char_count} "
                f"character(s), {genres}. Structured input for screenplay "
                f"generation."
            ),
            "scope": "global",
        },
    }


CATALOG_ENTRY = (
    "StoryAgent\n"
    "  - Input: a creative brief artifact (raw or enriched with reference-image visuals).\n"
    "  - Output: story_blueprint (logline, cast, locations, story_arc, scene_outline).\n"
    "  - Purpose: Produce a structured story blueprint — the first creative step for any "
    "task that requires generating a NEW film from a brief. Run me ONLY when the user wants "
    "to create new video content from scratch (a brief / idea). SKIP me for post-edit tasks "
    "on existing videos (style transfer, inpainting, highlights, transcription, subtitle-only)."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_id="StoryAgent",
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: StoryAgent(llm_client=llm),
    evaluator_factory=StoryEvaluator,
    build_input=build_input,
    build_captions=build_captions,
    materializer_factory=None,
    input_needs_description=(
        "I am the pipeline entry point for story planning. I take a "
        "natural-language creative brief and turn it into a structured "
        "story blueprint.\n\n"
        f"[{INPUT_LABEL_CREATIVE_BRIEF}] (single)\n"
        "A natural-language brief describing what kind of story / video to "
        "produce. This may be a short prompt ('a film about a cat "
        "chasing a butterfly') or a longer detailed outline / draft story "
        "text. The caption describes it as a creative brief / project "
        "intent description. Pick the single most recent / most "
        "authoritative such brief."
    ),
)
