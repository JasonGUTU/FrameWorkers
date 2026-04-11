"""ScreenplayAgent — univa-style full-screenplay generation from a JSON text blob.

Input:  ScreenplayAgentInput (``story_json_text`` — the upstream story
        blueprint payload serialized as raw JSON text, shape-agnostic)
Output: ScreenplayAgentOutput (scenes → shots: narrative + visual per take)

Generation model: ONE LLM call via ``_llm_fill_full``. The LLM receives the
upstream story payload as an indented JSON text blob and produces the
complete ``ScreenplayAgentOutput`` JSON in a single pass. There is no
skeleton-first split, no deterministic pre-computation of scene shells
from ``scene_outline``, and no field-selected "story embed" — the LLM
is the sole consumer of the story shape.

Why this shape: the old skeleton-first path hard-coded 18 specific
field paths (``content.cast[].character_id``, ``content.locations[].name``,
``content.scene_outline[].time_of_day_hint``, …) as string ``dict.get``
calls scattered across ``_story_content_embed_for_creative_llm`` and
``build_skeleton``. Any upstream StoryAgent variant that deviated from
those exact field names silently degraded to empty output (zero scenes,
empty creative embed) without tripping any validator. Univa-style
pass-through eliminates that hidden coupling: the LLM reads whatever
shape arrives and reasons about it directly. The contract between
StoryAgent and ScreenplayAgent is now "a JSON object describing a
story" — not "a specific 18-field schema matching ``StoryBlueprintContent``".

Coupling: output still feeds KeyFrameAgent (and downstream) as the sole
``screenplay`` artifact — the ``ScreenplayAgentOutput`` schema is
unchanged, so every downstream consumer sees the same contract it
always did. Only the upstream → ScreenplayAgent edge became
shape-agnostic.

Post-processing in ``recompute_metrics``: deliberately minimal. The
philosophy is "LLM produces correct output from the template + system
prompt; evaluator catches drift; we do NOT silently patch up LLM
mistakes in post-processing". Rewrites that remain:

  * ``shot_id`` global re-assignment as ``sh_NNN`` — kept because
    ``ScreenplayEvaluator`` only checks uniqueness, not the naming
    format, and downstream agents assume ``sh_NNN``. Candidate for
    future removal once the evaluator learns to check format.
  * ``keyframe_count`` forcing to 1 — kept as a belt-and-suspenders
    alongside the evaluator's existing ``keyframe_count != 1`` check.
  * ``order`` normalisation via ``_normalize_order``.

Explicitly NOT post-processed (trusted to the LLM + evaluator):

  * ``props_lock[].prop_id`` — the template shows ``"prop_id": "prop_001"``
    and the system prompt spells out the ``prop_NNN`` convention, so
    the LLM is expected to write these directly. Earlier revisions of
    this file auto-assigned prop_ids from prop_name first-occurrence
    and remapped ``shots.props_in_frame`` from name → id; both were
    defensive rewrites that contradicted the "trust producer's own
    output" principle from CLAUDE.md §7 and have been removed.
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
        "scene_end": { "turn": "<narrative turn>", "emotional_shift": "<shift>" }
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
            "Every shot's keyframe_plan.keyframe_count MUST be 1.\n"
            "Dialogue shots (block_type=='dialogue'): character_id and text must "
            "BOTH be non-empty. Action shots (block_type=='action'): leave "
            "character_id and character_name empty.\n"
            "scene_consistency_pack: fill EVERY lock (location_lock, "
            "character_locks, props_lock, style_lock) with concrete notes drawn "
            "from the blueprint's descriptive text. An empty list means 'nothing "
            "to lock', not a lazy placeholder.\n\n"
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
            "  * scene_id: sc_001, sc_002, … in order\n"
            "  * heading.location_id / character_locks[].character_id: reuse ids\n"
            "    from the blueprint when present; otherwise invent and reuse\n"
            "    consistently\n"
            "  * scene_consistency_pack: fill every lock with concrete notes\n"
            "    drawn from the blueprint's descriptive fields\n"
            "  * shots: each a distinct visual beat, keyframe_plan.keyframe_count=1\n"
            "  * scene_end.turn / emotional_shift: derived from the blueprint's\n"
            "    beat / arc descriptions\n\n"
            "Return JSON only."
        )

    def parse_output(self, raw: dict[str, Any]) -> ScreenplayAgentOutput:
        return ScreenplayAgentOutput.model_validate(raw)

    def recompute_metrics(self, output: ScreenplayAgentOutput) -> None:
        """Canonicalize structural fields and recompute derived counts.

        Deliberately minimal — see the module docstring. Only rewrites
        ``shot_id`` / ``order`` / ``keyframe_count`` remain; ``prop_id``
        and ``props_in_frame`` are trusted to the LLM so that evaluator
        rework (or a human read of the output) surfaces LLM drift
        instead of silently masking it.
        """
        c = output.content
        self._normalize_order(c.scenes)

        # Global sequential shot_id + per-scene order. ``shot_id`` stays
        # force-assigned because ``ScreenplayEvaluator`` only checks
        # uniqueness, not ``sh_NNN`` format, and downstream agents
        # assume that format. ``keyframe_count`` is clamped as a
        # belt-and-suspenders alongside the evaluator's existing
        # ``keyframe_count != 1`` check.
        g = 1
        for scene in c.scenes:
            for i, sh in enumerate(scene.shots, 1):
                sh.shot_id = f"sh_{g:03d}"
                sh.order = i
                sh.keyframe_plan.keyframe_count = 1
                g += 1

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
