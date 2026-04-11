"""StoryAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

from pydantic import BaseModel

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import SubAgentDescriptor
from .agent import StoryAgent
from .labels import INPUT_LABEL_CREATIVE_BRIEF
from .schema import StoryAgentInput
from .evaluator import StoryEvaluator


def build_input(
    _task_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    """Construct typed input from the resolved artifact dict.

    The creative brief is selected by InputResolver via the
    ``[creative_brief]`` label and MUST arrive as the JSON output of
    IntakeTextAgent — a caption-rich artifact whose
    ``payload.content.text`` carries the verbatim user brief. Each
    branch below raises with a specific diagnostic so an orchestration
    bug (missing/stale/wrong-type upstream artifact) surfaces
    immediately instead of producing plausible-looking garbage from a
    caption fragment.
    """
    brief = ResolvedArtifactEntry.coerce(
        resolved_artifacts.get(INPUT_LABEL_CREATIVE_BRIEF)
    )
    if not brief.payload:
        raise ValueError(
            "StoryAgent.build_input: "
            f"[{INPUT_LABEL_CREATIVE_BRIEF}] entry missing or has no JSON "
            f"payload (path={brief.path!r}, mime={brief.mime!r}). Make sure "
            "IntakeTextAgent has run on the user's brief upload before "
            "StoryAgent — InputResolver may have picked a stale raw_pending "
            "upload or a non-text artifact."
        )
    content = brief.payload.get("content")
    if not isinstance(content, dict):
        raise ValueError(
            "StoryAgent.build_input: "
            f"[{INPUT_LABEL_CREATIVE_BRIEF}] payload has no 'content' dict "
            f"(path={brief.path!r})."
        )
    creative_brief = str(content.get("text") or "").strip()
    if not creative_brief:
        raise ValueError(
            "StoryAgent.build_input: "
            f"[{INPUT_LABEL_CREATIVE_BRIEF}] content.text is empty "
            f"(path={brief.path!r}). InputResolver picked an artifact that "
            "doesn't carry actual brief text."
        )
    return StoryAgentInput(creative_brief=creative_brief)


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
    "  - Input: creative_brief (a natural-language description of what to produce)\n"
    "  - Output: story_blueprint (logline, cast, locations, story_arc, scene_outline)\n"
    "  - Purpose: Produce a structured story blueprint. Autonomously decides "
    "whether the input is a short prompt to expand or a detailed outline to structure."
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
