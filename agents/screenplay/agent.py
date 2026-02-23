"""ScreenplayAgent — produces a structured Screenplay.

Input:  ScreenplayAgentInput (project_id, draft_id, story_blueprint, constraints)
Output: ScreenplayAgentOutput (Screenplay with scenes → blocks, metrics)

Two modes:
- **Blueprint path** (skeleton-first): pre-builds scene shells from the
  story blueprint, LLM fills creative content.
- **User-text path** (legacy): user provides raw screenplay text, LLM
  structures it into the required JSON schema (like StoryAgent).

Coupling: receives Story Blueprint from StoryAgent (or raw text from user);
output feeds StoryboardAgent.
"""

from __future__ import annotations

import json
from typing import Any

from ..base_agent import BaseAgent
from ..common_schema import DurationEstimate
from .schema import (
    Block,
    CharacterWardrobeNote,
    ContinuityRefs,
    SceneContinuity,
    SceneEnd,
    SceneHeading,
    ScreenplayAgentInput,
    ScreenplayAgentOutput,
    ScreenplayContent,
    ScreenplayScene,
)

SCREENPLAY_OUTPUT_TEMPLATE = """{
  "content": {
    "title": "<screenplay title>",
    "scenes": [
      {
        "scene_id": "sc_001",
        "order": 1,
        "linked_story_step_id": "arc_001",
        "heading": {
          "location_id": "loc_001",
          "location_name": "<location name>",
          "interior_exterior": "INT|EXT",
          "time_of_day": "DAY|NIGHT"
        },
        "summary": "<what happens in this scene>",
        "estimated_duration": { "seconds": 20, "confidence": 0.7 },
        "continuity": {
          "props_present": [],
          "character_wardrobe_notes": [
            { "character_id": "char_001", "wardrobe": "<description>", "must_keep": ["<item>"] }
          ],
          "must_keep_scene_facts": ["<fact>"]
        },
        "blocks": [
          {
            "block_id": "b_001",
            "block_type": "action",
            "character_id": "",
            "character_name": "",
            "text": "<action description>",
            "continuity_refs": { "props": [], "wardrobe_character_ids": [] }
          },
          {
            "block_id": "b_002",
            "block_type": "dialogue",
            "character_id": "char_001",
            "character_name": "<name>",
            "text": "<dialogue line>",
            "continuity_refs": { "props": [], "wardrobe_character_ids": ["char_001"] }
          }
        ],
        "scene_end": { "turn": "<narrative turn>", "emotional_shift": "<shift>" }
      }
    ]
  }
}"""


class ScreenplayAgent(BaseAgent[ScreenplayAgentInput, ScreenplayAgentOutput]):

    # ------------------------------------------------------------------
    # Skeleton-first mode (blueprint path only)
    # ------------------------------------------------------------------

    def build_skeleton(
        self, input_data: ScreenplayAgentInput
    ) -> ScreenplayAgentOutput | None:
        """Pre-build scene shells from the story blueprint.

        Only used for the blueprint path (normal pipeline from StoryAgent).
        When ``user_provided_text`` is set, returns ``None`` to use legacy
        mode — the LLM structures the raw text directly.
        """
        if input_data.user_provided_text:
            return None  # user text → legacy mode

        bp = input_data.story_blueprint
        if not bp:
            return None

        # bp is already the content portion (assistant extracts it)
        locations = {
            loc.get("location_id", ""): loc
            for loc in bp.get("locations", [])
        }
        scene_outline = bp.get("scene_outline", [])

        if not scene_outline:
            return None

        scenes: list[ScreenplayScene] = []
        for so in scene_outline:
            scene_id = so.get("scene_id", "")
            loc_id = so.get("location_id", "")
            loc = locations.get(loc_id, {})
            chars_present = so.get("characters_present", [])

            scenes.append(
                ScreenplayScene(
                    scene_id=scene_id,
                    order=so.get("order", 0),
                    linked_story_step_id=so.get("linked_step_id", ""),
                    heading=SceneHeading(
                        location_id=loc_id,
                        location_name=loc.get("name", ""),
                        time_of_day=so.get("time_of_day_hint", "DAY"),
                    ),
                    continuity=SceneContinuity(
                        character_wardrobe_notes=[
                            CharacterWardrobeNote(character_id=cid)
                            for cid in chars_present
                        ],
                    ),
                )
            )

        output = ScreenplayAgentOutput()
        output.content = ScreenplayContent(scenes=scenes)
        return output

    def build_creative_prompt(
        self,
        input_data: ScreenplayAgentInput,
        skeleton: ScreenplayAgentOutput,
    ) -> str:
        """Build prompt asking LLM to fill creative content per scene."""
        bp = input_data.story_blueprint
        bp_json = json.dumps(bp, ensure_ascii=False, indent=2)

        # Build template showing what needs to be filled per scene
        scene_entries: list[str] = []
        for scene in skeleton.content.scenes:
            wardrobe_entries = [
                f'          {{"character_id": "{w.character_id}", '
                f'"wardrobe": "<FILL>", "must_keep": []}}'
                for w in scene.continuity.character_wardrobe_notes
            ]
            wardrobe_block = (
                ",\n".join(wardrobe_entries) if wardrobe_entries else ""
            )
            scene_entries.append(
                f'    {{\n'
                f'      "scene_id": "{scene.scene_id}",\n'
                f'      "interior_exterior": "<FILL: INT or EXT>",\n'
                f'      "summary": "<FILL>",\n'
                f'      "estimated_duration": {{"seconds": 0, "confidence": 0.7}},\n'
                f'      "props_present": [],\n'
                f'      "must_keep_scene_facts": [],\n'
                f'      "wardrobe": [\n{wardrobe_block}\n      ],\n'
                f'      "blocks": [\n'
                f'        {{"block_type": "action", "character_id": "", '
                f'"character_name": "", "text": "<FILL>", '
                f'"props": [], "wardrobe_character_ids": []}}\n'
                f'      ],\n'
                f'      "scene_end": {{"turn": "<FILL>", "emotional_shift": "<FILL>"}}\n'
                f'    }}'
            )

        template = (
            '{\n'
            '  "title": "<FILL>",\n'
            '  "scenes": [\n'
            + ",\n".join(scene_entries)
            + "\n  ]\n}"
        )

        return (
            "The system has pre-built scene shells with known structural "
            "fields (scene_id, order, linked_story_step_id, heading).\n\n"
            "Your job is to fill ALL creative content:\n"
            "- title: screenplay title\n"
            "- Per scene: interior_exterior (INT/EXT), summary, "
            "estimated_duration, blocks[], scene_end, props_present, "
            "must_keep_scene_facts, wardrobe descriptions\n"
            "- blocks[]: Generate ALL dialogue/action/narration blocks.\n"
            "  Each block needs: block_type, character_id, character_name, "
            "text. Do NOT include block_ids — they will be auto-assigned.\n\n"
            f"=== STORY BLUEPRINT ===\n{bp_json}\n\n"
            "=== OUTPUT FORMAT ===\n"
            f"{template}\n\n"
            "CRITICAL:\n"
            "- The blocks array shows only ONE example per scene. You MUST "
            "generate ALL blocks (typically 3-10 per scene).\n"
            "- Dialogue style: natural, filmable, concise.\n"
            "- Keep character voice consistent with profiles/motivation/flaw.\n"
            f"- Language: {input_data.constraints.language}\n\n"
            "Return JSON only."
        )

    def fill_creative(
        self, skeleton: ScreenplayAgentOutput, creative: dict
    ) -> ScreenplayAgentOutput:
        """Merge LLM creative output into the pre-built scene shells."""
        skeleton.content.title = creative.get("title", "")

        scene_map = {
            s.get("scene_id", ""): s
            for s in creative.get("scenes", [])
        }

        block_counter = 1

        for scene in skeleton.content.scenes:
            sc_data = scene_map.get(scene.scene_id, {})

            # heading.interior_exterior
            ie = sc_data.get("interior_exterior", "")
            if ie:
                scene.heading.interior_exterior = ie

            # summary
            scene.summary = sc_data.get("summary", "")

            # estimated_duration
            est_dur = sc_data.get("estimated_duration", {})
            if isinstance(est_dur, dict):
                scene.estimated_duration = DurationEstimate(
                    seconds=est_dur.get("seconds", 0),
                    confidence=est_dur.get("confidence", 0.7),
                )

            # blocks — auto-assign block_ids
            blocks: list[Block] = []
            for b_data in sc_data.get("blocks", []):
                blocks.append(
                    Block(
                        block_id=f"b_{block_counter:03d}",
                        block_type=b_data.get("block_type", "action"),
                        character_id=b_data.get("character_id", ""),
                        character_name=b_data.get("character_name", ""),
                        text=b_data.get("text", ""),
                        continuity_refs=ContinuityRefs(
                            props=b_data.get("props", []),
                            wardrobe_character_ids=b_data.get(
                                "wardrobe_character_ids", []
                            ),
                        ),
                    )
                )
                block_counter += 1
            scene.blocks = blocks

            # scene_end
            se_data = sc_data.get("scene_end", {})
            scene.scene_end = SceneEnd(
                turn=se_data.get("turn", ""),
                emotional_shift=se_data.get("emotional_shift", ""),
            )

            # continuity
            scene.continuity.props_present = sc_data.get(
                "props_present", []
            )
            scene.continuity.must_keep_scene_facts = sc_data.get(
                "must_keep_scene_facts", []
            )

            # wardrobe notes
            wardrobe_map = {
                w.get("character_id", ""): w
                for w in sc_data.get("wardrobe", [])
            }
            for wn in scene.continuity.character_wardrobe_notes:
                wd = wardrobe_map.get(wn.character_id, {})
                wn.wardrobe = wd.get("wardrobe", "")
                wn.must_keep = wd.get("must_keep", [])

        return skeleton

    # ------------------------------------------------------------------
    # Prompts — shared by skeleton mode and user-text (legacy) mode
    # ------------------------------------------------------------------

    def system_prompt(self) -> str:
        return (
            "You are ScreenplayAgent — a professional screenwriter.\n"
            "Output Rules:\n"
            "- Return JSON only, no markdown, no code fences.\n"
            "- If something is unknown, use empty string or empty list, not null.\n"
            "- Follow the output format in the user message exactly."
        )

    def build_user_prompt(self, input_data: ScreenplayAgentInput) -> str:
        """Legacy-mode prompt — only used for user-text structuring path."""
        return self._build_structuring_prompt(input_data)

    def _build_structuring_prompt(self, input_data: ScreenplayAgentInput) -> str:
        """Structure raw user-provided screenplay text into JSON.

        Preserves dialogue and action descriptions verbatim.
        """
        return (
            "You are receiving raw screenplay text provided directly by the "
            "user. Your job is to **structure** this text into the required "
            "JSON schema — do NOT rewrite or embellish the creative content. "
            "Preserve the user's dialogue, action descriptions, scene "
            "structure, and character names as faithfully as possible.\n\n"
            "--- BEGIN USER TEXT ---\n"
            f"{input_data.user_provided_text}\n"
            "--- END USER TEXT ---\n\n"
            f"Constraints:\n"
            f"- Language: {input_data.constraints.language}\n"
            f"- Assign scene_ids starting from sc_001.\n"
            f"- Assign character_ids starting from char_001.\n"
            f"- Assign location_ids starting from loc_001.\n"
            f"- Assign block_ids starting from b_001 globally.\n"
            f"- Estimate per-scene duration (seconds, confidence).\n\n"
            f"You MUST output JSON matching EXACTLY this structure "
            f"(fill in real content):\n"
            f"{SCREENPLAY_OUTPUT_TEMPLATE}\n\n"
            "Self-check:\n"
            "- Each block has a unique block_id (b_001, b_002, ...)\n"
            "- dialogue blocks include character_id + character_name + text\n"
            "- action blocks describe visible action (no camera terms)\n\n"
            "Return JSON only."
        )

    def recompute_metrics(self, output: ScreenplayAgentOutput) -> None:
        c = output.content
        self._normalize_order(c.scenes)
        output.metrics.scene_count = len(c.scenes)
        output.metrics.dialogue_block_count = sum(
            1 for s in c.scenes for b in s.blocks if b.block_type == "dialogue"
        )
        output.metrics.action_block_count = sum(
            1 for s in c.scenes for b in s.blocks if b.block_type == "action"
        )
        output.metrics.sum_scene_duration_sec = sum(
            s.estimated_duration.seconds for s in c.scenes
        )
        output.metrics.estimated_total_duration_sec = (
            output.metrics.sum_scene_duration_sec
        )

    # Quality evaluation has been moved to ScreenplayEvaluator
    # (see evaluator.py in this package).
