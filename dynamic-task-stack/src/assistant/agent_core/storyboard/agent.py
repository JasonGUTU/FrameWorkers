"""StoryboardAgent — translates Screenplay into a Storyboard (scene → shots).

Input:  StoryboardAgentInput (project_id, draft_id, screenplay, constraints)
Output: StoryboardAgentOutput (Storyboard with scene_consistency_pack, shots,
        metrics)

Uses **skeleton-first mode** (normal generation): pre-builds scene shells
with known structural fields (scene_id, order, source, location_lock,
character_lock shells) from the screenplay.  The LLM fills creative content:
estimated duration, consistency-pack details (environment_notes, identity_notes,
wardrobe_notes, style_lock), and the entire shots array.

Coupling: receives Screenplay from ScreenplayAgent; output feeds KeyFrameAgent.
"""

from __future__ import annotations

import json
from typing import Any

from ..base_agent import BaseAgent
from ..common_schema import DurationEstimate
from .schema import (
    Camera,
    CharacterLock,
    KeyframePlan,
    LocationLock,
    PropLock,
    SceneConsistencyPack,
    Shot,
    StoryboardAgentInput,
    StoryboardAgentOutput,
    StoryboardContent,
    StoryboardScene,
    StoryboardSceneSource,
    StyleLock,
)


class StoryboardAgent(BaseAgent[StoryboardAgentInput, StoryboardAgentOutput]):

    # ------------------------------------------------------------------
    # Skeleton-first mode
    # ------------------------------------------------------------------

    def build_skeleton(
        self, input_data: StoryboardAgentInput
    ) -> StoryboardAgentOutput | None:
        """Pre-build scene shells from the screenplay.

        Fills: scene_id, order, source, location_lock (location_id,
        time_of_day), character_lock shells.  Leaves creative content
        (estimated duration, consistency-pack details, shots[]) for
        the LLM.
        """
        sp = input_data.screenplay
        if not sp:
            return None

        sp_content = sp.get("content", {})
        sp_asset_id = sp.get("meta", {}).get("asset_id", "")
        sp_scenes = sp_content.get("scenes", [])

        if not sp_scenes:
            return None

        scenes: list[StoryboardScene] = []
        for scene_order, sp_scene in enumerate(sp_scenes, 1):
            scene_id = sp_scene.get("scene_id", "")
            heading = sp_scene.get("heading", {})

            # Extract unique characters from this scene's blocks
            char_ids: dict[str, bool] = {}
            for block in sp_scene.get("blocks", []):
                cid = block.get("character_id", "")
                if cid:
                    char_ids[cid] = True

            scenes.append(
                StoryboardScene(
                    scene_id=scene_id,
                    order=scene_order,
                    source=StoryboardSceneSource(
                        screenplay_asset_id=sp_asset_id,
                        screenplay_scene_id=scene_id,
                    ),
                    scene_consistency_pack=SceneConsistencyPack(
                        location_lock=LocationLock(
                            location_id=heading.get("location_id", ""),
                            time_of_day=heading.get("time_of_day", "DAY"),
                        ),
                        character_locks=[
                            CharacterLock(character_id=cid)
                            for cid in char_ids
                        ],
                    ),
                )
            )

        output = StoryboardAgentOutput()
        output.content = StoryboardContent(scenes=scenes)
        return output

    def build_creative_prompt(
        self,
        input_data: StoryboardAgentInput,
        skeleton: StoryboardAgentOutput,
    ) -> str:
        """Build prompt asking LLM to fill creative content per scene."""
        sp = input_data.screenplay
        sp_json = json.dumps(sp, ensure_ascii=False, indent=2)

        # Build template showing what needs to be filled per scene
        scene_entries: list[str] = []
        for scene in skeleton.content.scenes:
            char_entries = [
                f'            {{"character_id": "{cl.character_id}", '
                f'"identity_notes": ["<FILL>"], '
                f'"wardrobe_notes": ["<FILL>"], '
                f'"must_keep": ["<FILL>"]}}'
                for cl in scene.scene_consistency_pack.character_locks
            ]
            char_block = (
                ",\n".join(char_entries) if char_entries else ""
            )
            scene_entries.append(
                f'    {{\n'
                f'      "scene_id": "{scene.scene_id}",\n'
                f'      "estimated_duration": '
                f'{{"seconds": 0, "confidence": 0.7}},\n'
                f'      "location_lock": {{\n'
                f'        "environment_notes": ["<FILL>"]\n'
                f'      }},\n'
                f'      "character_locks": [\n{char_block}\n      ],\n'
                f'      "props_lock": [\n'
                f'        {{"prop_name": "<FILL>", "must_keep": []}}\n'
                f'      ],\n'
                f'      "style_lock": {{\n'
                f'        "global_style_notes": ["<FILL>"],\n'
                f'        "must_avoid": ["<FILL>"]\n'
                f'      }},\n'
                f'      "shots": [\n'
                f'        {{\n'
                f'          "linked_blocks": ["<block_ids>"],\n'
                f'          "estimated_duration_sec": 3.0,\n'
                f'          "shot_type": "medium",\n'
                f'          "camera": {{"angle": "eye_level", '
                f'"movement": "static", "framing_notes": "<FILL>"}},\n'
                f'          "visual_goal": "<FILL>",\n'
                f'          "action_focus": "<FILL>",\n'
                f'          "characters_in_frame": [],\n'
                f'          "props_in_frame": [],\n'
                f'          "keyframe_plan": {{'
                f'"keyframe_count": 1, "keyframe_notes": []}}\n'
                f'        }}\n'
                f'      ]\n'
                f'    }}'
            )

        template = (
            '{\n  "scenes": [\n'
            + ",\n".join(scene_entries)
            + "\n  ]\n}"
        )

        return (
            "The system has pre-built scene shells with known structural "
            "fields (scene_id, order, source, location_lock.location_id, "
            "location_lock.time_of_day, character_lock shells).\n\n"
            "Your job is to fill ALL creative content:\n"
            "- Per scene: estimated_duration, environment_notes, "
            "character lock details, props_lock, style_lock, shots[]\n"
            "- shots[]: Generate ALL shots for each scene.\n"
            "  Each shot needs: linked_blocks, estimated_duration_sec, "
            "shot_type, camera, visual_goal, action_focus, "
            "characters_in_frame, props_in_frame, keyframe_plan.\n"
            "  Do NOT include shot_ids — they will be auto-assigned.\n\n"
            f"=== SCREENPLAY ===\n{sp_json}\n\n"
            "=== OUTPUT FORMAT ===\n"
            f"{template}\n\n"
            "CRITICAL:\n"
            "- The shots array shows only ONE example per scene. You MUST "
            "generate ALL shots needed (typically 3-8 per scene).\n"
            "- Each shot should cover one or more screenplay blocks.\n"
            "- All linked_blocks must reference existing block IDs from "
            "the screenplay.\n"
            f"- Max shots per scene: "
            f"{input_data.constraints.max_shots_per_scene}\n"
            f"- Language: {input_data.constraints.language}\n\n"
            "Return JSON only."
        )

    def fill_creative(
        self, skeleton: StoryboardAgentOutput, creative: dict
    ) -> StoryboardAgentOutput:
        """Merge LLM creative output into the pre-built scene shells."""
        scene_map = {
            s.get("scene_id", ""): s
            for s in creative.get("scenes", [])
        }

        shot_counter = 1
        prop_id_map: dict[str, str] = {}  # prop_name → prop_NNN (global)

        for scene in skeleton.content.scenes:
            sc_data = scene_map.get(scene.scene_id, {})

            # estimated_duration
            est_dur = sc_data.get("estimated_duration", {})
            if isinstance(est_dur, dict):
                scene.estimated_duration = DurationEstimate(
                    seconds=est_dur.get("seconds", 0),
                    confidence=est_dur.get("confidence", 0.7),
                )

            # location_lock — environment_notes only (ID/time pre-filled)
            loc_data = sc_data.get("location_lock", {})
            scene.scene_consistency_pack.location_lock.environment_notes = (
                loc_data.get("environment_notes", [])
            )

            # character_locks — fill creative fields by matching character_id
            char_map = {
                c.get("character_id", ""): c
                for c in sc_data.get("character_locks", [])
            }
            for cl in scene.scene_consistency_pack.character_locks:
                cd = char_map.get(cl.character_id, {})
                cl.identity_notes = cd.get("identity_notes", [])
                cl.wardrobe_notes = cd.get("wardrobe_notes", [])
                cl.must_keep = cd.get("must_keep", [])

            # props_lock — auto-assign prop_id (like shot_id)
            scene.scene_consistency_pack.props_lock = [
                PropLock(
                    prop_id=prop_id_map.setdefault(
                        p.get("prop_name", ""),
                        f"prop_{len(prop_id_map) + 1:03d}",
                    ),
                    prop_name=p.get("prop_name", ""),
                    must_keep=p.get("must_keep", []),
                )
                for p in sc_data.get("props_lock", [])
            ]

            # style_lock — entirely from LLM
            style_data = sc_data.get("style_lock", {})
            scene.scene_consistency_pack.style_lock = StyleLock(
                global_style_notes=style_data.get(
                    "global_style_notes", []
                ),
                must_avoid=style_data.get("must_avoid", []),
            )

            # shots — auto-assign shot_ids
            shots: list[Shot] = []
            for shot_order, sh_data in enumerate(
                sc_data.get("shots", []), 1
            ):
                cam_data = sh_data.get("camera", {})
                kf_data = sh_data.get("keyframe_plan", {})

                raw_props = sh_data.get("props_in_frame", [])
                mapped_props = [
                    prop_id_map.get(p, p) for p in raw_props
                ]

                shots.append(
                    Shot(
                        shot_id=f"sh_{shot_counter:03d}",
                        order=shot_order,
                        linked_blocks=sh_data.get("linked_blocks", []),
                        estimated_duration_sec=sh_data.get(
                            "estimated_duration_sec", 3.0
                        ),
                        shot_type=sh_data.get("shot_type", "medium"),
                        camera=Camera(
                            angle=cam_data.get("angle", "eye_level"),
                            movement=cam_data.get("movement", "static"),
                            framing_notes=cam_data.get(
                                "framing_notes", ""
                            ),
                        ),
                        visual_goal=sh_data.get("visual_goal", ""),
                        action_focus=sh_data.get("action_focus", ""),
                        characters_in_frame=sh_data.get(
                            "characters_in_frame", []
                        ),
                        props_in_frame=mapped_props,
                        keyframe_plan=KeyframePlan(
                            keyframe_count=kf_data.get(
                                "keyframe_count", 1
                            ),
                            keyframe_notes=kf_data.get(
                                "keyframe_notes", []
                            ),
                        ),
                    )
                )
                shot_counter += 1
            scene.shots = shots

        return skeleton

    # ------------------------------------------------------------------
    # Prompts — skeleton mode only (no legacy path for StoryboardAgent)
    # ------------------------------------------------------------------

    def system_prompt(self) -> str:
        return (
            "You are StoryboardAgent — a professional storyboard artist.\n"
            "Output Rules:\n"
            "- Return JSON only, no markdown, no code fences.\n"
            "- If something is unknown, use empty string or empty list, not null.\n"
            "- Follow the output format in the user message exactly."
        )

    def recompute_metrics(self, output: StoryboardAgentOutput) -> None:
        c = output.content
        self._normalize_order(c.scenes)
        for scene in c.scenes:
            self._normalize_order(scene.shots)
        scene_count = len(c.scenes)
        shot_count = sum(len(s.shots) for s in c.scenes)
        sum_dur = sum(
            sh.estimated_duration_sec for s in c.scenes for sh in s.shots
        )
        output.metrics.scene_count = scene_count
        output.metrics.shot_count_total = shot_count
        output.metrics.avg_shots_per_scene = (
            shot_count / scene_count if scene_count else 0.0
        )
        output.metrics.sum_shot_duration_sec = sum_dur

    # Quality evaluation has been moved to StoryboardEvaluator
    # (see evaluator.py in this package).
