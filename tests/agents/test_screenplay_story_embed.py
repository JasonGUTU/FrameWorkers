"""ScreenplayAgent: story dict embedded in blueprint creative LLM prompt (field omission only)."""

from __future__ import annotations

import sys
from pathlib import Path

for parent in Path(__file__).resolve().parents:
    if (parent / "agents" / "__init__.py").exists():
        if str(parent) not in sys.path:
            sys.path.insert(0, str(parent))
        break

from agents.screenplay.agent import ScreenplayAgent


def test_embed_drops_whole_long_fields_not_slices():
    content = {
        "logline": "A test.",
        "estimated_duration": {"seconds": 12.0, "confidence": 0.8},
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
    }
    c = ScreenplayAgent._story_content_embed_for_creative_llm(content)
    assert c["cast"][0].keys() == {"character_id", "name", "role"}
    assert c["locations"][0].keys() == {"location_id", "name"}
    assert c["story_arc"][0].keys() == {"step_id", "order", "step_type", "summary"}
    assert c["scene_outline"][0].keys() == {
        "scene_id",
        "order",
        "linked_step_id",
        "location_id",
        "time_of_day_hint",
        "characters_present",
    }


def test_embed_non_dict_returns_empty():
    assert ScreenplayAgent._story_content_embed_for_creative_llm(None) == {}
    assert ScreenplayAgent._story_content_embed_for_creative_llm([]) == {}
