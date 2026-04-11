"""ScreenplayAgent descriptor — self-describing manifest for the registry."""

from __future__ import annotations

import json

from pydantic import BaseModel

from ..common_schema import ResolvedArtifactEntry
from ..descriptor import SubAgentDescriptor
from .agent import ScreenplayAgent
from .schema import ScreenplayAgentInput
from .evaluator import ScreenplayEvaluator

from .labels import INPUT_LABEL_STORY


def build_input(
    _task_id: str,
    resolved_artifacts: dict,
) -> BaseModel:
    """Construct typed input from the resolved artifact dict.

    Univa-style pass-through: dump the entire upstream story payload as
    a raw indented JSON text blob into ``story_json_text``. No ``.content``
    unwrap, no field enumeration — the whole upstream JSON object (whatever
    shape it happens to have) is forwarded verbatim for the LLM to read.

    Single input: the upstream story_blueprint, selected by InputResolver
    via the ``[story]`` label. ScreenplayAgent has no concept of free-text
    user directives — any such directive flows in through the upstream
    re-run pattern (Director re-runs StoryAgent with the new brief, the
    updated story_blueprint reaches ScreenplayAgent through this same
    ``[story]`` label).
    """
    story = ResolvedArtifactEntry.coerce(resolved_artifacts.get(INPUT_LABEL_STORY))
    story_payload = story.payload or {}
    story_json_text = json.dumps(story_payload, ensure_ascii=False, indent=2)
    return ScreenplayAgentInput(story_json_text=story_json_text)


def build_captions(agent_id: str, output_dict: dict) -> dict:
    content = output_dict.get("content", {})
    scenes = content.get("scenes", [])
    scene_count = len(scenes)
    shot_count = sum(len(s.get("shots", [])) for s in scenes if isinstance(s, dict))
    return {
        agent_id: {
            "caption": (
                f"Screenplay: {scene_count} scene(s), {shot_count} shot(s). "
                f"Input for keyframe planning and audio scoring."
            ),
            "scope": "global",
        },
    }


CATALOG_ENTRY = (
    "ScreenplayAgent\n"
    "  - Input: story_blueprint (cast, locations, scene_outline)\n"
    "  - Output: screenplay (scenes -> shots: script + visual plan + consistency packs)\n"
    "  - Purpose: Unified screenplay; feeds downstream visual and audio agents."
)

DESCRIPTOR = SubAgentDescriptor(
    agent_id="ScreenplayAgent",
    catalog_entry=CATALOG_ENTRY,
    agent_factory=lambda llm: ScreenplayAgent(llm_client=llm),
    evaluator_factory=ScreenplayEvaluator,
    build_input=build_input,
    build_captions=build_captions,
    materializer_factory=None,
    input_needs_description=(
        "I take a high-level story plan and turn it into a full unified screenplay "
        "(scenes broken into shots, with visual direction, dialogue, and consistency "
        "packs).\n\n"
        f"[{INPUT_LABEL_STORY}] (single)\n"
        "The high-level narrative plan for the whole video — written before any "
        "scene breakdown exists. It defines the logline, the cast of characters, "
        "the locations, the overall story arc, and a coarse scene-level outline. "
        "It does NOT yet contain a per-shot breakdown, dialogue, or camera "
        "direction; that is exactly what I will produce. Choose at most one such "
        "document for this story."
    ),
)
