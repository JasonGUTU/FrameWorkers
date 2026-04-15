"""ScreenplayAgent — univa-style full-screenplay generation from a JSON text blob.

Input:  ScreenplayAgentInput (``story_json_text`` — the upstream story
        blueprint payload serialized as raw JSON text, shape-agnostic)
Output: ScreenplayAgentOutput (scenes → shots: narrative + visual per take)

Generation model: ONE LLM call via ``_llm_fill_full``. The LLM receives the
upstream story payload as an indented JSON text blob and produces the
complete ``ScreenplayAgentOutput`` JSON in a single pass — no skeleton-
first split, no pre-computed scene shells, no field-selected story embed.
See CLAUDE.md §7 (Postel's Law at the agent layer) for the rationale.

Output contract: all content-level invariants (sh_NNN global-sequential
shot_id, sc_NNN scene_id, per-scene shot order starting at 1,
``keyframe_count == 1``, prop_NNN prop_id, character/location id reuse
from the blueprint) are owned by the LLM via the template + system
prompt, and enforced by ScreenplayEvaluator. Rework surfaces any drift
instead of a silent Python-side patch-up. ``recompute_metrics`` does
NOT rewrite any LLM-authored field — it only derives summary counts
(scene_count, shot_count_total, avg_shots_per_scene,
dialogue_block_count, action_block_count), which are never LLM-authored
because the user-message template hides the ``metrics`` field entirely.
"""

from __future__ import annotations

from typing import Any

from ..base_agent import BaseAgent
from .schema import ScreenplayAgentInput, ScreenplayAgentOutput


SCREENPLAY_OUTPUT_TEMPLATE = """{
  "content": {
    "title": "<screenplay title>",
    "scenes": [
      {
        "scene_id": "sc_001",
        "order": 1,
        "linked_story_step_id": "<arc step id from story blueprint, or empty string>",
        "heading": {
          "location_id": "loc_001",
          "location_name": "<location name from story blueprint>",
          "interior_exterior": "INT|EXT",
          "time_of_day": "DAY|NIGHT|CUSTOM"
        },
        "summary": "<one or two sentences: what happens in this scene>",
        "continuity": {
          "props_present": ["<prop name>"],
          "character_wardrobe_notes": [
            { "character_id": "char_001", "wardrobe": "<description>", "must_keep": ["<item>"] }
          ],
          "must_keep_scene_facts": ["<fact>"]
        },
        "scene_consistency_pack": {
          "location_lock": {
            "location_id": "loc_001",
            "time_of_day": "DAY",
            "environment_notes": ["<note>"]
          },
          "character_locks": [
            { "character_id": "char_001", "identity_notes": ["<note>"], "wardrobe_notes": ["<note>"], "must_keep": ["<note>"] }
          ],
          "props_lock": [ { "prop_id": "prop_001", "prop_name": "<name>", "must_keep": ["<note>"] } ],
          "style_lock": {
            "global_style_notes": ["<note>"],
            "must_avoid": ["<note>"]
          }
        },
        "shots": [
          {
            "shot_id": "sh_001",
            "order": 1,
            "block_type": "action",
            "character_id": "",
            "character_name": "",
            "text": "<visible action line>",
            "continuity_refs": { "props": [], "wardrobe_character_ids": [] },
            "shot_type": "medium",
            "camera": { "angle": "eye_level", "movement": "static", "framing_notes": "<note>" },
            "visual_goal": "<what this shot conveys>",
            "action_focus": "<what the shot foregrounds>",
            "characters_in_frame": [],
            "props_in_frame": [],
            "keyframe_plan": { "keyframe_count": 1, "keyframe_notes": [] }
          },
          {
            "shot_id": "sh_002",
            "order": 2,
            "block_type": "dialogue",
            "character_id": "char_001",
            "character_name": "<name>",
            "text": "<spoken line>",
            "continuity_refs": { "props": [], "wardrobe_character_ids": ["char_001"] },
            "shot_type": "medium",
            "camera": { "angle": "eye_level", "movement": "static", "framing_notes": "" },
            "visual_goal": "<note>",
            "action_focus": "<note>",
            "characters_in_frame": ["char_001"],
            "props_in_frame": [],
            "keyframe_plan": { "keyframe_count": 1, "keyframe_notes": [] }
          }
        ],
        "scene_end": { "turn": "<narrative turn>", "emotional_shift": "<shift>" },
        "estimated_duration_seconds": 12.4
      }
    ]
  }
}"""


class ScreenplayAgent(BaseAgent[ScreenplayAgentInput, ScreenplayAgentOutput]):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    async def generate(
        self,
        input_data: ScreenplayAgentInput,
        *,
        rework_notes: str = "",
    ) -> ScreenplayAgentOutput:
        """Single full-output LLM call from the story JSON text blob."""
        output = await self._llm_fill_full(input_data, rework_notes)
        self.recompute_metrics(output)
        return output

    def system_prompt(self) -> str:
        return (
            "You are ScreenplayAgent: turn a high-level story blueprint into a "
            "unified screenplay (scenes broken into shots, with narrative + "
            "visual direction and consistency packs).\n\n"
            "=== INPUT FORMAT ===\n"
            "You will receive the upstream story blueprint as a RAW JSON TEXT BLOB "
            "inside the user message. Do NOT assume specific field names in "
            "advance. READ the JSON, understand whatever shape it happens to have, "
            "and extract the elements you need. Typical fields you may encounter "
            "include logline/premise, cast/characters, locations/settings, "
            "story_arc/beats, scene_outline/scenes, style/tone — but the exact "
            "names and nesting may vary. Reason from the text, not from assumed "
            "keys.\n\n"
            "=== OUTPUT FORMAT ===\n"
            "JSON only; no markdown; match the user-message template exactly. Use "
            "empty string or empty list for unknowns, never null. Your output will "
            "be validated against a strict Pydantic schema, so fields with enum "
            "values (block_type, shot_type, camera.angle, camera.movement, "
            "interior_exterior, time_of_day) must use valid values shown in the "
            "template.\n\n"
            "=== ID CONVENTIONS ===\n"
            "If the story blueprint provides character/location ids (char_001, "
            "loc_001 style, or anything else), REUSE those exact ids everywhere "
            "you reference the same entity: scene_consistency_pack.character_locks"
            "[].character_id, scene_consistency_pack.location_lock.location_id, "
            "shots[].character_id, continuity.character_wardrobe_notes[]."
            "character_id, etc. If the blueprint has no ids, invent stable ones "
            "(char_001, loc_001, prop_001, …) and reuse them consistently across "
            "every scene.\n\n"
            "For props, assign prop_id values of the form prop_001, prop_002, … "
            "in scene_consistency_pack.props_lock[].prop_id. In shots."
            "props_in_frame[], reference props by their prop_id (not by name).\n\n"
            "linked_story_step_id: if the blueprint exposes arc/beat ids (arc_001 "
            "style), point each scene's linked_story_step_id at the single most "
            "central beat that scene dramatizes (usually its climax or inciting "
            "moment, NOT its setup). If no arc ids are exposed, use an empty "
            "string.\n\n"
            "=== STRUCTURAL REQUIREMENTS ===\n"
            "scene_id: sc_001, sc_002, sc_003, … in the order the scenes appear. "
            "scene.order: 1, 2, 3, … matching the scene's position (first scene "
            "has order=1, second scene has order=2, and so on).\n"
            "shot_id: sh_001, sh_002, sh_003, … with 3-digit zero-padding. "
            "shot_ids are GLOBALLY SEQUENTIAL across the entire screenplay — the "
            "first shot of the first scene is sh_001, the next shot is sh_002 "
            "whether it is in the same scene or the next scene, and numbering "
            "NEVER restarts at the scene boundary. If the screenplay has 3 scenes "
            "with 4 / 3 / 5 shots, the shot_ids run sh_001 … sh_012 straight "
            "through. No gaps, no duplicates.\n"
            "shot.order: 1, 2, 3, … RESTARTING at 1 inside each scene (so the "
            "first shot of every scene has order=1).\n"
            "Every shot's keyframe_plan.keyframe_count MUST be 1.\n"
            "Dialogue shots (block_type=='dialogue'): character_id and text must "
            "BOTH be non-empty. Action shots (block_type=='action'): leave "
            "character_id and character_name empty.\n"
            "scene_consistency_pack: fill EVERY lock (location_lock, "
            "character_locks, props_lock, style_lock) with concrete notes drawn "
            "from the blueprint's descriptive text. An empty list means 'nothing "
            "to lock', not a lazy placeholder.\n\n"
            "=== SCENE DURATION ESTIMATE (shared source of truth) ===\n"
            "For every scene, compute estimated_duration_seconds as a "
            "decimal number of seconds using this exact formula:\n"
            "  dialogue_words = total word count across all shots whose "
            "block_type is 'dialogue', 'narration', or 'monologue' in the "
            "scene (count words in the shot.text string, whitespace-split).\n"
            "  action_shots   = count of shots in the scene whose "
            "block_type == 'action'.\n"
            "  estimated_duration_seconds = (dialogue_words / 2.5) + "
            "(action_shots * 3.0).\n"
            "  * 2.5 words/sec approximates 150 wpm TTS rate; the 3s-per-"
            "action-shot term reserves visual-pacing time for shots with "
            "no spoken line.\n"
            "  * Result must be strictly > 0 for any scene that has at "
            "least one shot (every non-empty scene contributes time). "
            "Round to one decimal place.\n"
            "  * This number is the SINGLE SOURCE OF TRUTH for scene "
            "duration — NarrationAgent / MusicAgent / AmbienceAgent all "
            "read it verbatim downstream instead of re-deriving it, so "
            "they stay in sync. Do NOT fold real-world pacing tweaks "
            "into this field; keep it a pure mechanical estimate.\n\n"
            "Do NOT include an artifact_caption block — the system generates it "
            "automatically."
        )

    def build_user_prompt(self, input_data: ScreenplayAgentInput) -> str:
        return (
            "Read the upstream story blueprint below and produce a complete "
            "screenplay that dramatizes it.\n\n"
            "=== STORY BLUEPRINT (raw JSON — read the shape before writing) ===\n"
            f"{input_data.story_json_text}\n"
            "=== END STORY BLUEPRINT ===\n\n"
            "Extract from the blueprint:\n"
            "  - who the characters are (their ids, names, roles — preserve any\n"
            "    ids the blueprint provides)\n"
            "  - where the scenes take place (location ids + names, interior vs\n"
            "    exterior, time of day)\n"
            "  - what story beats to cover (from whatever arc / outline / scenes /\n"
            "    beats field the blueprint exposes)\n"
            "  - what tone / genre / style to honor (from any style / tone / mood\n"
            "    fields)\n\n"
            "Then produce the full screenplay JSON in EXACTLY this shape:\n\n"
            f"{SCREENPLAY_OUTPUT_TEMPLATE}\n\n"
            "Per-scene requirements:\n"
            "  * scene_id: sc_001, sc_002, … in order; scene.order = 1, 2, 3, …\n"
            "  * heading.location_id / character_locks[].character_id: reuse ids\n"
            "    from the blueprint when present; otherwise invent and reuse\n"
            "    consistently\n"
            "  * scene_consistency_pack: fill every lock with concrete notes\n"
            "    drawn from the blueprint's descriptive fields\n"
            "  * shots: each a distinct visual beat, keyframe_plan.keyframe_count=1\n"
            "  * shot_id: sh_001, sh_002, sh_003, … GLOBALLY sequential across\n"
            "    the whole screenplay, 3-digit zero-padded, never restarting at\n"
            "    scene boundaries. shot.order: 1, 2, 3, … restarting per scene.\n"
            "  * scene_end.turn / emotional_shift: derived from the blueprint's\n"
            "    beat / arc descriptions\n\n"
            "Return JSON only."
        )

    def parse_output(self, raw: dict[str, Any]) -> ScreenplayAgentOutput:
        return ScreenplayAgentOutput.model_validate(raw)

    def recompute_metrics(self, output: ScreenplayAgentOutput) -> None:
        """Derive summary metrics from content — pure derived data, zero rewrites.

        All LLM-authored fields (shot_id, scene/shot order, keyframe_count,
        prop_id, …) are left untouched; ScreenplayEvaluator enforces their
        invariants via structural checks + rework. The ``metrics`` field is
        hidden from the user-message template, so it is never LLM-authored
        in the first place — populating it here is derivation, not a
        silent patch-up of LLM output.
        """
        c = output.content
        output.metrics.scene_count = len(c.scenes)
        shot_total = sum(len(s.shots) for s in c.scenes)
        output.metrics.shot_count_total = shot_total
        output.metrics.avg_shots_per_scene = (
            shot_total / len(c.scenes) if c.scenes else 0.0
        )
        output.metrics.dialogue_block_count = sum(
            1 for s in c.scenes for sh in s.shots if sh.block_type == "dialogue"
        )
        output.metrics.action_block_count = sum(
            1 for s in c.scenes for sh in s.shots if sh.block_type == "action"
        )
