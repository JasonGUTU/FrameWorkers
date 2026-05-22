"""Per-panel shot category catalog.

Multi-label: a single storyboard panel can carry multiple categories
(e.g. ``[ACTION_FIGHT, DIALOGUE_TWO_SHOT]`` for "fight + shouting").
ShotPromptAgent loads all matching guidance docs and asks the LLM to
weave their emphases into a single coherent prompt.

Each member maps to ``sub_agents/shot_prompt/guidance/<value>.md``.

Note: current set mixes content (transformation/action/dialogue/monologue)
and framing (close_up/wide/two_shot) dimensions. Flat for prototyping;
split into two enums when programmatic framing control is needed.
"""
from __future__ import annotations

from enum import Enum


class ShotCategory(str, Enum):
    TRANSFORMATION_BODY_HORROR = "transformation_body_horror"
    ACTION_FIGHT = "action_fight"
    EMOTIONAL_CLOSE_UP = "emotional_close_up"
    ESTABLISHING_WIDE = "establishing_wide"
    DIALOGUE_TWO_SHOT = "dialogue_two_shot"
    INNER_MONOLOGUE_VO = "inner_monologue_VO"
