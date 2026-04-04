"""ScreenplayAgent — unified screenplay + shot planning.

Input:  ScreenplayAgentInput (story_blueprint, constraints, user_provided_text)
Output: ScreenplayAgentOutput (scenes → shots: narrative + visual per take)

Blueprint path: skeleton-first from story; LLM fills shots and consistency packs.
User-text path: LLM structures raw text into the same unified schema.

Coupling: output feeds KeyFrameAgent (and downstream) as the sole ``screenplay`` artifact.

Blueprint creative-fill embeds only a **field-selected** story dict in the LLM user message
(see ``_story_content_embed_for_creative_llm``): the creative model does not need the same
long bios the Story asset stores. ``build_skeleton`` still reads the **full**
``story_blueprint`` from ``resolved_inputs``. Whole-field omission only — no slicing.
"""

from __future__ import annotations

import json
from typing import Any

from ..base_agent import BaseAgent
from ..common_schema import DurationEstimate
from .schema import (
    Camera,
    CharacterLock,
    CharacterWardrobeNote,
    ContinuityRefs,
    KeyframePlan,
    LocationLock,
    PropLock,
    SceneConsistencyPack,
    SceneContinuity,
    SceneEnd,
    SceneHeading,
    ScreenplayAgentInput,
    ScreenplayAgentOutput,
    ScreenplayContent,
    ScreenplayScene,
    ScreenplaySceneSource,
    ScriptShot,
    StyleLock,
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
        "scene_consistency_pack": {
          "location_lock": {
            "location_id": "loc_001",
            "time_of_day": "DAY",
            "environment_notes": ["<FILL>"]
          },
          "character_locks": [
            { "character_id": "char_001", "identity_notes": ["<FILL>"], "wardrobe_notes": ["<FILL>"], "must_keep": ["<FILL>"] }
          ],
          "props_lock": [ { "prop_name": "<FILL>", "must_keep": [] } ],
          "style_lock": {
            "global_style_notes": ["<FILL>"],
            "must_avoid": ["<FILL>"]
          }
        },
        "shots": [
          {
            "block_type": "action",
            "character_id": "",
            "character_name": "",
            "text": "<visible action, no camera jargon>",
            "continuity_refs": { "props": [], "wardrobe_character_ids": [] },
            "estimated_duration_sec": 3.0,
            "shot_type": "medium",
            "camera": { "angle": "eye_level", "movement": "static", "framing_notes": "<FILL>" },
            "visual_goal": "<FILL>",
            "action_focus": "<FILL>",
            "characters_in_frame": [],
            "props_in_frame": [],
            "keyframe_plan": { "keyframe_count": 1, "keyframe_notes": [] }
          },
          {
            "block_type": "dialogue",
            "character_id": "char_001",
            "character_name": "<name>",
            "text": "<line>",
            "continuity_refs": { "props": [], "wardrobe_character_ids": ["char_001"] },
            "estimated_duration_sec": 3.0,
            "shot_type": "medium",
            "camera": { "angle": "eye_level", "movement": "static", "framing_notes": "" },
            "visual_goal": "<FILL>",
            "action_focus": "<FILL>",
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
        self._target_duration_sec: float = 10.0

    @staticmethod
    def _story_content_embed_for_creative_llm(content: Any) -> dict[str, Any]:
        """Story ``content`` fields embedded in the blueprint creative user message.

        The LLM only sees this dict. We omit whole keys that duplicate narrative the
        screenplay pass must still write (profiles, long location prose, arc conflict
        blocks, per-scene goal/conflict/turn). Skeleton uses the full blueprint separately.

        This is not token slicing — excluded fields are absent from the embedded object,
        not truncated. Persisted ``story_blueprint`` JSON is unchanged.
        """
        if not isinstance(content, dict):
            return {}

        out: dict[str, Any] = {}

        out["logline"] = str(content.get("logline", "") or "")

        ed = content.get("estimated_duration")
        if isinstance(ed, dict):
            out["estimated_duration"] = {
                "seconds": ed.get("seconds", 0),
                "confidence": ed.get("confidence", 0.7),
            }

        style = content.get("style")
        if isinstance(style, dict):
            genres = list(style.get("genre") or [])
            tones = list(style.get("tone_keywords") or [])
            out["style"] = {
                "genre": [str(x) for x in genres],
                "tone_keywords": [str(x) for x in tones],
            }

        out["cast"] = []
        for m in content.get("cast") or []:
            if not isinstance(m, dict):
                continue
            out["cast"].append(
                {
                    "character_id": str(m.get("character_id", "") or ""),
                    "name": str(m.get("name", "") or ""),
                    "role": str(m.get("role", "") or ""),
                }
            )

        out["locations"] = []
        for loc in content.get("locations") or []:
            if not isinstance(loc, dict):
                continue
            out["locations"].append(
                {
                    "location_id": str(loc.get("location_id", "") or ""),
                    "name": str(loc.get("name", "") or ""),
                }
            )

        out["story_arc"] = []
        for step in content.get("story_arc") or []:
            if not isinstance(step, dict):
                continue
            out["story_arc"].append(
                {
                    "step_id": str(step.get("step_id", "") or ""),
                    "order": step.get("order", 0),
                    "step_type": str(step.get("step_type", "") or ""),
                    "summary": str(step.get("summary", "") or ""),
                }
            )

        out["scene_outline"] = []
        for sc in content.get("scene_outline") or []:
            if not isinstance(sc, dict):
                continue
            chars = sc.get("characters_present")
            if not isinstance(chars, list):
                chars = []
            out["scene_outline"].append(
                {
                    "scene_id": str(sc.get("scene_id", "") or ""),
                    "order": sc.get("order", 0),
                    "linked_step_id": str(sc.get("linked_step_id", "") or ""),
                    "location_id": str(sc.get("location_id", "") or ""),
                    "time_of_day_hint": str(sc.get("time_of_day_hint", "") or "DAY"),
                    "characters_present": [str(x) for x in chars if str(x).strip()],
                }
            )

        return out

    def build_skeleton(
        self, input_data: ScreenplayAgentInput
    ) -> ScreenplayAgentOutput | None:
        if input_data.user_provided_text:
            return None

        bp = input_data.story_blueprint
        if not bp:
            return None

        self._target_duration_sec = 10.0
        ed = bp.get("estimated_duration", {}) if isinstance(bp, dict) else {}
        if isinstance(ed, dict):
            try:
                sec = float(ed.get("seconds") or 0)
                if sec > 0:
                    self._target_duration_sec = sec
            except (TypeError, ValueError):
                pass

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
                    source=ScreenplaySceneSource(screenplay_scene_id=scene_id),
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
                    scene_consistency_pack=SceneConsistencyPack(
                        location_lock=LocationLock(
                            location_id=loc_id,
                            time_of_day=so.get("time_of_day_hint", "DAY"),
                        ),
                        character_locks=[
                            CharacterLock(character_id=cid)
                            for cid in chars_present
                        ],
                    ),
                )
            )

        output = ScreenplayAgentOutput()
        output.content = ScreenplayContent(scenes=scenes)
        output.metrics.target_duration_sec = self._target_duration_sec
        return output

    def build_creative_prompt(
        self,
        input_data: ScreenplayAgentInput,
        skeleton: ScreenplayAgentOutput,
    ) -> str:
        bp = input_data.story_blueprint
        bp_embed = self._story_content_embed_for_creative_llm(bp)
        bp_json = json.dumps(bp_embed, ensure_ascii=False, indent=2)
        max_shots = input_data.constraints.max_shots_per_scene

        scene_entries: list[str] = []
        for scene in skeleton.content.scenes:
            char_entries = [
                f'            {{"character_id": "{cl.character_id}", '
                f'"identity_notes": ["<FILL>"], '
                f'"wardrobe_notes": ["<FILL>"], '
                f'"must_keep": ["<FILL>"]}}'
                for cl in scene.scene_consistency_pack.character_locks
            ]
            char_block = ",\n".join(char_entries) if char_entries else ""
            wardrobe_entries = [
                f'          {{"character_id": "{w.character_id}", '
                f'"wardrobe": "<FILL>", "must_keep": []}}'
                for w in scene.continuity.character_wardrobe_notes
            ]
            wardrobe_block = ",\n".join(wardrobe_entries) if wardrobe_entries else ""

            scene_entries.append(
                f'    {{\n'
                f'      "scene_id": "{scene.scene_id}",\n'
                f'      "interior_exterior": "<FILL: INT or EXT>",\n'
                f'      "summary": "<FILL>",\n'
                f'      "estimated_duration": {{"seconds": 0, "confidence": 0.7}},\n'
                f'      "props_present": [],\n'
                f'      "must_keep_scene_facts": [],\n'
                f'      "wardrobe": [\n{wardrobe_block}\n      ],\n'
                f'      "location_lock": {{"environment_notes": ["<FILL>"]}},\n'
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
                f'          "block_type": "action",\n'
                f'          "character_id": "",\n'
                f'          "character_name": "",\n'
                f'          "text": "<FILL>",\n'
                f'          "continuity_refs": {{"props": [], "wardrobe_character_ids": []}},\n'
                f'          "estimated_duration_sec": 3.0,\n'
                f'          "shot_type": "medium",\n'
                f'          "camera": {{"angle": "eye_level", "movement": "static", '
                f'"framing_notes": "<FILL>"}},\n'
                f'          "visual_goal": "<FILL>",\n'
                f'          "action_focus": "<FILL>",\n'
                f'          "characters_in_frame": [],\n'
                f'          "props_in_frame": [],\n'
                f'          "keyframe_plan": {{"keyframe_count": 1, "keyframe_notes": []}}\n'
                f'        }}\n'
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
            "Scene shells are fixed (ids, heading, location/character lock ids). "
            "Fill: title; per scene interior_exterior, summary, estimated_duration, wardrobe, "
            "props_present, must_keep_scene_facts, scene_end; "
            "environment_notes, character_locks, props_lock, style_lock; "
            "shots[] — one row per continuous take (script fields + camera/visual_goal/action_focus/"
            "characters_in_frame/props_in_frame/keyframe_plan). "
            "No shot_id; keyframe_plan.keyframe_count=1.\n\n"
            f"=== STORY CONTEXT (embedded subset for this LLM call) ===\n{bp_json}\n"
            "(Workspace still holds the full story blueprint. This block omits whole fields "
            "the screenplay pass re-authors: cast profile/motivation/flaw, location descriptions, "
            "arc conflict/turning_point, scene goal/conflict/turn — infer dialogue and packs "
            "from logline, arc summaries, and outline grid.)\n\n"
            f"=== OUTPUT ===\n{template}\n\n"
            f"Max shots/scene: {max_shots}. Template shows one shot example per scene — output ALL shots. "
            "Natural dialogue. Scene durations ~±20% of blueprint target.\n"
            "Return JSON only."
        )

    def fill_creative(
        self, skeleton: ScreenplayAgentOutput, creative: dict
    ) -> ScreenplayAgentOutput:
        skeleton.content.title = creative.get("title", "")
        scene_map = {s.get("scene_id", ""): s for s in creative.get("scenes", [])}
        shot_counter = 1
        prop_id_map: dict[str, str] = {}

        for scene in skeleton.content.scenes:
            sc_data = scene_map.get(scene.scene_id, {})

            ie = sc_data.get("interior_exterior", "")
            if ie:
                scene.heading.interior_exterior = ie

            scene.summary = sc_data.get("summary", "")

            est_dur = sc_data.get("estimated_duration", {})
            if isinstance(est_dur, dict):
                scene.estimated_duration = DurationEstimate(
                    seconds=est_dur.get("seconds", 0),
                    confidence=est_dur.get("confidence", 0.7),
                )

            se_data = sc_data.get("scene_end", {})
            scene.scene_end = SceneEnd(
                turn=se_data.get("turn", ""),
                emotional_shift=se_data.get("emotional_shift", ""),
            )

            scene.continuity.props_present = sc_data.get("props_present", [])
            scene.continuity.must_keep_scene_facts = sc_data.get(
                "must_keep_scene_facts", []
            )

            wardrobe_map = {
                w.get("character_id", ""): w for w in sc_data.get("wardrobe", [])
            }
            for wn in scene.continuity.character_wardrobe_notes:
                wd = wardrobe_map.get(wn.character_id, {})
                wn.wardrobe = wd.get("wardrobe", "")
                wn.must_keep = wd.get("must_keep", [])

            pack = scene.scene_consistency_pack
            ll = sc_data.get("location_lock", {})
            if ll:
                pack.location_lock.environment_notes = ll.get("environment_notes", [])

            char_map = {c.get("character_id", ""): c for c in sc_data.get("character_locks", [])}
            for cl in pack.character_locks:
                cd = char_map.get(cl.character_id, {})
                cl.identity_notes = cd.get("identity_notes", [])
                cl.wardrobe_notes = cd.get("wardrobe_notes", [])
                cl.must_keep = cd.get("must_keep", [])

            pack.props_lock = [
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

            st = sc_data.get("style_lock", {})
            pack.style_lock = StyleLock(
                global_style_notes=st.get("global_style_notes", []),
                must_avoid=st.get("must_avoid", []),
            )

            shots: list[ScriptShot] = []
            for shot_order, sh_data in enumerate(sc_data.get("shots", []), 1):
                cam_data = sh_data.get("camera", {}) if isinstance(sh_data.get("camera"), dict) else {}
                kf_data = sh_data.get("keyframe_plan", {}) if isinstance(sh_data.get("keyframe_plan"), dict) else {}
                cr = sh_data.get("continuity_refs", {})
                if not isinstance(cr, dict):
                    cr = {}
                raw_props = sh_data.get("props_in_frame", [])
                mapped_props = [prop_id_map.get(p, p) for p in raw_props]

                shots.append(
                    ScriptShot(
                        shot_id=f"sh_{shot_counter:03d}",
                        order=shot_order,
                        block_type=sh_data.get("block_type", "action"),
                        character_id=sh_data.get("character_id", ""),
                        character_name=sh_data.get("character_name", ""),
                        text=sh_data.get("text", ""),
                        continuity_refs=ContinuityRefs(
                            props=cr.get("props", []),
                            wardrobe_character_ids=cr.get("wardrobe_character_ids", []),
                        ),
                        estimated_duration_sec=float(sh_data.get("estimated_duration_sec", 3.0)),
                        shot_type=sh_data.get("shot_type", "medium"),
                        camera=Camera(
                            angle=cam_data.get("angle", "eye_level"),
                            movement=cam_data.get("movement", "static"),
                            framing_notes=cam_data.get("framing_notes", ""),
                        ),
                        visual_goal=sh_data.get("visual_goal", ""),
                        action_focus=sh_data.get("action_focus", ""),
                        characters_in_frame=sh_data.get("characters_in_frame", []),
                        props_in_frame=mapped_props,
                        keyframe_plan=KeyframePlan(
                            keyframe_count=1,
                            keyframe_notes=kf_data.get("keyframe_notes", []),
                        ),
                    )
                )
                shot_counter += 1
            scene.shots = shots

        return skeleton

    def system_prompt(self) -> str:
        return (
            "You are ScreenplayAgent: screenplay + shot planning. "
            "JSON only; no markdown; use empty string/list for unknowns, not null; "
            "match the user message template exactly."
        )

    def build_user_prompt(self, input_data: ScreenplayAgentInput) -> str:
        return self._build_structuring_prompt(input_data)

    def _build_structuring_prompt(self, input_data: ScreenplayAgentInput) -> str:
        self._target_duration_sec = 10.0
        return (
            "Structure the user's screenplay into JSON; preserve dialogue and action.\n\n"
            "--- USER TEXT ---\n"
            f"{input_data.user_provided_text}\n"
            "--- END ---\n\n"
            "Infer language/runtime from text. IDs: sc_001, char_001, loc_001. "
            "Omit shot_id (system assigns sh_001…). "
            "Each shot = one take: block_type, text, shot_type, camera, visual_goal, action_focus, "
            "keyframe_plan with keyframe_count=1.\n\n"
            f"{SCREENPLAY_OUTPUT_TEMPLATE}\n\n"
            "Return JSON only."
        )

    def parse_output(self, raw: dict[str, Any]) -> ScreenplayAgentOutput:
        return ScreenplayAgentOutput.model_validate(raw)

    def recompute_metrics(self, output: ScreenplayAgentOutput) -> None:
        c = output.content
        self._normalize_order(c.scenes)
        # Global sequential shot_id + per-scene order (trust structure, not LLM ids)
        g = 1
        for scene in c.scenes:
            for i, sh in enumerate(scene.shots, 1):
                sh.shot_id = f"sh_{g:03d}"
                sh.order = i
                g += 1
        sum_dur = sum(s.estimated_duration.seconds for s in c.scenes)
        if sum_dur > 0:
            self._target_duration_sec = float(sum_dur)
        output.metrics.target_duration_sec = self._target_duration_sec
        output.metrics.scene_count = len(c.scenes)
        shot_total = sum(len(s.shots) for s in c.scenes)
        output.metrics.shot_count_total = shot_total
        output.metrics.sum_shot_duration_sec = sum(
            sh.estimated_duration_sec for s in c.scenes for sh in s.shots
        )
        output.metrics.avg_shots_per_scene = (
            shot_total / len(c.scenes) if c.scenes else 0.0
        )
        output.metrics.dialogue_block_count = sum(
            1 for s in c.scenes for sh in s.shots if sh.block_type == "dialogue"
        )
        output.metrics.action_block_count = sum(
            1 for s in c.scenes for sh in s.shots if sh.block_type == "action"
        )
        output.metrics.sum_scene_duration_sec = sum(
            s.estimated_duration.seconds for s in c.scenes
        )
        output.metrics.estimated_total_duration_sec = (
            output.metrics.sum_scene_duration_sec
        )
