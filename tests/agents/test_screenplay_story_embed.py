"""ScreenplayAgent — univa-style JSON-text pass-through.

After the archetype flip, ``build_input`` no longer unpacks specific
fields of the upstream story payload. It dumps the whole payload
(whatever shape it has) into ``ScreenplayAgentInput.story_json_text``
as an indented JSON text blob, and the agent's LLM reads the shape
directly. These tests pin that pass-through invariant so any future
regression that re-introduces field-selection on the upstream story
trips immediately.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

for parent in Path(__file__).resolve().parents:
    if (parent / "agents" / "__init__.py").exists():
        if str(parent) not in sys.path:
            sys.path.insert(0, str(parent))
        break

from agents.common_schema import ResolvedArtifactEntry
from agents.screenplay.descriptor import build_input
from agents.screenplay.labels import INPUT_LABEL_STORY
from agents.screenplay.schema import ScreenplayAgentInput


def _canonical_story_payload() -> dict:
    return {
        "meta": {"asset_type": "story_blueprint", "language": "en"},
        "content": {
            "logline": "A test.",
            "style": {"genre": ["drama"], "tone_keywords": ["t1", "t2"]},
            "cast": [
                {
                    "character_id": "char_001",
                    "name": "Hero",
                    "role": "protagonist",
                    "profile": "LONG PROFILE TEXT",
                    "motivation": "LONG",
                    "flaw": "LONG",
                }
            ],
            "locations": [
                {
                    "location_id": "loc_001",
                    "name": "Cafe",
                    "description": "VERY LONG LOCATION DESCRIPTION",
                }
            ],
            "story_arc": [
                {
                    "step_id": "arc_001",
                    "order": 1,
                    "step_type": "setup",
                    "summary": "Hook",
                    "conflict": "LONG CONFLICT",
                    "turning_point": "LONG TP",
                }
            ],
            "scene_outline": [
                {
                    "scene_id": "sc_001",
                    "order": 1,
                    "linked_step_id": "arc_001",
                    "location_id": "loc_001",
                    "time_of_day_hint": "DAY",
                    "characters_present": ["char_001"],
                    "goal": "LONG GOAL",
                    "conflict": "LONG",
                    "turn": "LONG",
                }
            ],
        },
        "metrics": {"character_count": 1, "location_count": 1, "scene_count": 1},
    }


def test_build_input_roundtrip_preserves_every_field():
    """The entire upstream payload survives verbatim through build_input.

    The old field-selected embed (dropped in the univa-style flip)
    shrank cast entries to ``{character_id, name, role}`` and dropped
    profile / motivation / flaw / description / conflict / turning_point.
    The new pass-through must preserve ALL of them — if a future change
    re-adds field selection, ``round_tripped == original`` will fail.
    """
    payload = _canonical_story_payload()
    entry = ResolvedArtifactEntry(
        caption="story_blueprint",
        scope="global",
        path="/tmp/story.json",
        mime="application/json",
        payload=payload,
    )
    typed = build_input("task_test", {INPUT_LABEL_STORY: entry})

    assert isinstance(typed, ScreenplayAgentInput)
    assert typed.story_json_text  # non-empty
    round_tripped = json.loads(typed.story_json_text)
    assert round_tripped == payload


def test_build_input_handles_non_canonical_shape():
    """An upstream with different field names still passes through verbatim.

    This is the whole point of the univa flip: ScreenplayAgent's
    build_input must NOT know or care that a canonical ``StoryBlueprint``
    uses ``content.scene_outline`` — any well-formed JSON object with
    any field names should make it through untouched so the LLM can
    reason about the shape itself.
    """
    weird_payload = {
        "blueprint": {
            "chars": [{"id": "h1", "title": "Hero"}],
            "world": "somewhere",
            "beats": ["open", "mid", "end"],
        },
        "notes": "free-form annotation",
    }
    entry = ResolvedArtifactEntry(
        caption="story_blueprint",
        scope="global",
        path="/tmp/story.json",
        mime="application/json",
        payload=weird_payload,
    )
    typed = build_input("task_test", {INPUT_LABEL_STORY: entry})

    assert isinstance(typed, ScreenplayAgentInput)
    assert json.loads(typed.story_json_text) == weird_payload


def test_build_input_missing_payload_yields_empty_object_text():
    """Entry present but payload is None — emit '{}' (not a crash)."""
    entry = ResolvedArtifactEntry()  # all fields blank, payload is None
    typed = build_input("task_test", {INPUT_LABEL_STORY: entry})
    assert isinstance(typed, ScreenplayAgentInput)
    assert json.loads(typed.story_json_text) == {}


def test_build_input_missing_label_yields_empty_object_text():
    """Label absent from resolved_artifacts entirely — same behavior."""
    typed = build_input("task_test", {})
    assert isinstance(typed, ScreenplayAgentInput)
    assert json.loads(typed.story_json_text) == {}


def test_build_input_unicode_preserved():
    """Non-ASCII content is preserved verbatim (ensure_ascii=False)."""
    payload = {"content": {"logline": "一个关于时间的故事", "cast": ["李四"]}}
    entry = ResolvedArtifactEntry(
        caption="story_blueprint",
        scope="global",
        path="/tmp/story.json",
        mime="application/json",
        payload=payload,
    )
    typed = build_input("task_test", {INPUT_LABEL_STORY: entry})
    assert json.loads(typed.story_json_text) == payload
    # Verify it's actually stored as UTF-8 characters, not \uXXXX escapes
    assert "一个关于时间的故事" in typed.story_json_text
