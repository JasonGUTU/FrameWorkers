"""KeyFrameAgent — generates keyframe image prompts for each shot.

Input:  KeyFrameAgentInput (screenplay, constraints)
Output: KeyFrameAgentOutput (KeyframesPackage with stability_keyframes +
        shot keyframes, metrics)

Coupling: receives unified screenplay from ScreenplayAgent; output feeds VideoAgent.

Uses **skeleton-first mode**: the structural scaffold (IDs, order, source refs,
image_asset placeholders, keyframe_ids) is pre-built deterministically from
the screenplay (shots + consistency packs).  The LLM is asked only to fill ``prompt_summary`` fields
(the creative image-generation prompts).  This eliminates ~67% of output
tokens and makes structural errors impossible.

**Parallel LLM calls:** ``_run_skeleton_mode`` is overridden to split the
creative fill into 1 global-anchors call + N per-scene calls, all running
concurrently via ``asyncio.gather``.  This avoids the single-call timeout
that occurs when all prompt_summaries are requested in one massive response.
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

from ..base_agent import BaseAgent, ExecutionResult
from ..contracts.input_bundle_v2 import InputBundleV2
from ..common_schema import ImageAsset
from .schema import (
    KeyFrameAgentInput,
    KeyFrameAgentOutput,
    KeyframeScene,
    KeyframeSceneSource,
    KeyframesContent,
    Keyframe,
    KeyframeConstraintsApplied,
    ShotKeyframes,
    ShotKeyframeSource,
    StabilityAnchorKeyframe,
    StabilityKeyframes,
)

logger = logging.getLogger(__name__)


def _placeholder_image(fmt: str = "png") -> ImageAsset:
    """Return a default placeholder ImageAsset."""
    return ImageAsset(
        asset_id="",
        uri="placeholder",
        width=1024,
        height=576,
        format=fmt,
    )


class KeyFrameAgent(BaseAgent[KeyFrameAgentInput, KeyFrameAgentOutput]):

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._prop_name_to_id: dict[str, str] = {}
        # Unified switch first, then legacy switch for backward compatibility.
        # Default off for faster low-latency runs.
        raw = os.getenv(
            "FW_ENABLE_PROP_PIPELINE",
            os.getenv("FW_ENABLE_PROP_KEYFRAMES", "0"),
        ).strip().lower()
        self._enable_prop_keyframes = raw in {"1", "true", "yes", "on"}

    # ------------------------------------------------------------------
    # Prompts (system prompt shared by both legacy and skeleton modes)
    # ------------------------------------------------------------------

    def system_prompt(self) -> str:
        return (
            "You are KeyFrameAgent: three layers of STATIC image prompts only.\n"
            "L1 global_anchors: standalone t2i — canonical look per entity; simple bg unless "
            "the entity is a place; avoid pasting global style paragraphs (backend adds style).\n"
            "L2 stability_keyframes: short edit deltas vs global — light/environment/pose only.\n"
            "L3 per shot: prompt_summary = one frozen frame (no sound/edit/dialogue/music meta); "
            "video_motion_hint = 1–3 sentences of subtle I2V motion only, not a copy of the still.\n"
            "L1 standalone wording; L2/L3 may use edit phrasing ('Show…', 'Frame…'). English; "
            "2–6 short sentences per prompt_summary. JSON only; empty string not null; "
            "every prompt_summary non-empty."
        )

    # ------------------------------------------------------------------
    # Skeleton-first mode
    # ------------------------------------------------------------------

    def build_skeleton(
        self, input_data: KeyFrameAgentInput
    ) -> KeyFrameAgentOutput | None:
        """Pre-build the full keyframes structure from the screenplay.

        Walks the screenplay to extract all scenes, shots, characters,
        locations, and props.  Creates the complete KeyFrameAgentOutput
        with every structural field filled and all ``prompt_summary``
        fields left as empty strings for the LLM to fill.
        """
        sp = input_data.screenplay
        sp_content = sp.get("content", {})
        sp_scenes = sp_content.get("scenes", [])
        sp_asset_id = sp.get("meta", {}).get("asset_id", "")
        img_fmt = input_data.constraints.image_format

        if not sp_scenes:
            return None  # fall back to legacy mode

        # --- Collect all unique entities across scenes ---
        all_char_ids: dict[str, bool] = {}  # ordered set
        all_loc_ids: dict[str, bool] = {}
        all_props: dict[str, str] = {}  # prop_id → prop_name (ordered)

        for sp_scene in sp_scenes:
            pack = sp_scene.get("scene_consistency_pack", {})
            loc = pack.get("location_lock", {})
            if loc.get("location_id"):
                all_loc_ids[loc["location_id"]] = True
            for ch in pack.get("character_locks", []):
                if ch.get("character_id"):
                    all_char_ids[ch["character_id"]] = True
            # Fallback: character IDs only at shot level.
            for shot in sp_scene.get("shots", []):
                for cid in shot.get("characters_in_frame", []):
                    if isinstance(cid, str) and cid:
                        all_char_ids[cid] = True
            if self._enable_prop_keyframes:
                for pr in pack.get("props_lock", []):
                    pid = pr.get("prop_id", "")
                    pname = pr.get("prop_name", "")
                    if pid:
                        all_props[pid] = pname

        # Build reverse mapping (name → id) for prompt context
        self._prop_name_to_id = {v: k for k, v in all_props.items()}

        # --- Layer 1: global_anchors ---
        global_chars = [
            StabilityAnchorKeyframe(
                entity_type="character",
                entity_id=cid,
                purpose="identity_anchor",
                keyframe_id=f"kf_global_{cid}",
                image_asset=_placeholder_image(img_fmt),
            )
            for cid in all_char_ids
        ]
        global_locs = [
            StabilityAnchorKeyframe(
                entity_type="location",
                entity_id=lid,
                purpose="style_anchor",
                keyframe_id=f"kf_global_{lid}",
                image_asset=_placeholder_image(img_fmt),
            )
            for lid in all_loc_ids
        ]
        global_props = [
            StabilityAnchorKeyframe(
                entity_type="prop",
                entity_id=pid,
                display_name=pname,
                purpose="prop_anchor",
                keyframe_id=f"kf_global_{pid}",
                image_asset=_placeholder_image(img_fmt),
            )
            for pid, pname in all_props.items()
        ]

        # --- Per-scene scaffolding ---
        kf_global_counter = 1
        scenes: list[KeyframeScene] = []

        for scene_order, sp_scene in enumerate(sp_scenes, 1):
            scene_id = sp_scene.get("scene_id", f"sc_{scene_order:03d}")
            pack = sp_scene.get("scene_consistency_pack", {})

            # Layer 2: stability_keyframes for this scene
            scene_char_ids = [
                ch["character_id"]
                for ch in pack.get("character_locks", [])
                if ch.get("character_id")
            ]
            # Keep scene-level character anchors available even when character_locks
            # is empty but shot-level character assignment exists.
            for shot in sp_scene.get("shots", []):
                for cid in shot.get("characters_in_frame", []):
                    if isinstance(cid, str) and cid and cid not in scene_char_ids:
                        scene_char_ids.append(cid)
            scene_loc_id = pack.get("location_lock", {}).get("location_id", "")
            scene_props: list[tuple[str, str]] = []
            if self._enable_prop_keyframes:
                scene_props = [
                    (pr["prop_id"], pr.get("prop_name", ""))
                    for pr in pack.get("props_lock", [])
                    if pr.get("prop_id")
                ]

            stab_chars = [
                StabilityAnchorKeyframe(
                    entity_type="character",
                    entity_id=cid,
                    purpose="scene_adaptation",
                    keyframe_id=f"kf_{cid}_{scene_id}",
                    image_asset=_placeholder_image(img_fmt),
                )
                for cid in scene_char_ids
            ]
            stab_locs = [
                StabilityAnchorKeyframe(
                    entity_type="location",
                    entity_id=scene_loc_id,
                    purpose="scene_adaptation",
                    keyframe_id=f"kf_{scene_loc_id}_{scene_id}",
                    image_asset=_placeholder_image(img_fmt),
                )
            ] if scene_loc_id else []
            stab_props = [
                StabilityAnchorKeyframe(
                    entity_type="prop",
                    entity_id=pid,
                    display_name=pname,
                    purpose="scene_adaptation",
                    keyframe_id=f"kf_{pid}_{scene_id}",
                    image_asset=_placeholder_image(img_fmt),
                )
                for pid, pname in scene_props
            ]

            # Layer 3: shot keyframes
            shot_list: list[ShotKeyframes] = []
            for shot_order, sp_shot in enumerate(
                sp_scene.get("shots", []), 1
            ):
                shot_id = sp_shot.get("shot_id", "")
                # One still per shot — VideoAgent uses this PNG as the sole conditioning image.
                keyframes: list[Keyframe] = [
                    Keyframe(
                        keyframe_id=f"kf_{kf_global_counter:03d}",
                        order=1,
                        image_asset=_placeholder_image(img_fmt),
                        constraints_applied=KeyframeConstraintsApplied(
                            characters_in_frame=sp_shot.get(
                                "characters_in_frame", []
                            ),
                            props_in_frame=(
                                sp_shot.get("props_in_frame", [])
                                if self._enable_prop_keyframes
                                else []
                            ),
                        ),
                    )
                ]
                kf_global_counter += 1

                shot_list.append(
                    ShotKeyframes(
                        shot_id=shot_id,
                        order=shot_order,
                        source=ShotKeyframeSource(source_shot_id=shot_id),
                        estimated_duration_sec=sp_shot.get(
                            "estimated_duration_sec", 3.0
                        ),
                        keyframes=keyframes,
                    )
                )

            scenes.append(
                KeyframeScene(
                    scene_id=scene_id,
                    order=scene_order,
                    source=KeyframeSceneSource(
                        screenplay_asset_id=sp_asset_id,
                        screenplay_scene_id=scene_id,
                    ),
                    stability_keyframes=StabilityKeyframes(
                        characters=stab_chars,
                        locations=stab_locs,
                        props=stab_props,
                    ),
                    shots=shot_list,
                )
            )

        output = KeyFrameAgentOutput()
        output.content = KeyframesContent(
            global_anchors=StabilityKeyframes(
                characters=global_chars,
                locations=global_locs,
                props=global_props,
            ),
            scenes=scenes,
        )
        return output

    # ------------------------------------------------------------------
    # Style extraction helper
    # ------------------------------------------------------------------

    def _extract_style_section(self, sp_content: dict) -> str:
        """Build style directive text from screenplay scene style_lock."""
        style_notes: list[str] = []
        must_avoid: list[str] = []
        for sp_scene in sp_content.get("scenes", []):
            sl = sp_scene.get("scene_consistency_pack", {}).get("style_lock", {})
            style_notes.extend(sl.get("global_style_notes", []))
            must_avoid.extend(sl.get("must_avoid", []))
        style_notes = list(dict.fromkeys(style_notes))
        must_avoid = list(dict.fromkeys(must_avoid))
        if not style_notes and not must_avoid:
            return ""
        parts = []
        if style_notes:
            parts.append("Style: " + "; ".join(style_notes))
        if must_avoid:
            parts.append("Must avoid: " + "; ".join(must_avoid))
        return (
            "=== STYLE REF (do not paste verbatim; backend re-injects) ===\n"
            + "\n".join(parts) + "\n"
            "Anchor mood in concrete light/materials; at most one short phrase per summary.\n\n"
        )

    # ------------------------------------------------------------------
    # Per-chunk prompt builders (global + per-scene)
    # ------------------------------------------------------------------

    def _build_creative_prompt_global(
        self, sp_content: dict, skeleton: KeyFrameAgentOutput
    ) -> str:
        """Prompt asking the LLM to fill global_anchors prompt_summary only."""
        ga = skeleton.content.global_anchors
        ga_chars = [
            f'    {{"entity_id": "{c.entity_id}", "prompt_summary": "<FILL>"}}'
            for c in ga.characters
        ]
        ga_locs = [
            f'    {{"entity_id": "{l.entity_id}", "prompt_summary": "<FILL>"}}'
            for l in ga.locations
        ]
        ga_props = [
            f'    {{"entity_id": "{p.entity_id}", "prompt_summary": "<FILL>"}}'
            for p in ga.props
        ]
        template = (
            '{\n  "characters": [\n' + ",\n".join(ga_chars) + "\n  ],\n"
            '  "locations": [\n' + ",\n".join(ga_locs) + "\n  ],\n"
            '  "props": [\n' + ",\n".join(ga_props) + "\n  ]\n}"
        )
        # Gather a brief character/location/prop summary from screenplay packs.
        entity_context = self._gather_entity_context(sp_content)
        style = self._extract_style_section(sp_content)
        return (
            "Layer 1: standalone t2i prompt per entity — canonical physical look.\n\n"
            f"{style}"
            f"=== ENTITIES ===\n{entity_context}\n\n"
            "Replace each <FILL> with a full image prompt.\n"
            f"{template}\n\n"
            "Return JSON only."
        )

    @staticmethod
    def _join_note_list(raw: Any) -> str:
        if not isinstance(raw, list):
            return ""
        bits = [str(x).strip() for x in raw if str(x).strip()]
        return " | ".join(bits)

    @classmethod
    def _compact_scene_pack_lines(cls, pack: dict) -> str:
        """Scene pack as compact lines (same facts as JSON; no list/row caps — long prompts surface upstream)."""
        if not isinstance(pack, dict):
            return ""
        lines: list[str] = []
        loc = pack.get("location_lock") or {}
        if isinstance(loc, dict):
            lid = str(loc.get("location_id", "")).strip()
            tod = str(loc.get("time_of_day", "")).strip()
            lines.append(f"location: id={lid} time={tod}")
            env_s = cls._join_note_list(loc.get("environment_notes"))
            if env_s:
                lines.append(f"environment: {env_s}")
        for cl in pack.get("character_locks") or []:
            if not isinstance(cl, dict):
                continue
            cid = str(cl.get("character_id", "")).strip()
            if not cid:
                continue
            idn = cls._join_note_list(cl.get("identity_notes"))
            wn = cls._join_note_list(cl.get("wardrobe_notes"))
            mk = cls._join_note_list(cl.get("must_keep"))
            bits = " | ".join(b for b in (idn, wn, mk) if b)
            lines.append(f"char {cid}: {bits}" if bits else f"char {cid}")
        for pl in pack.get("props_lock") or []:
            if not isinstance(pl, dict):
                continue
            pid = str(pl.get("prop_id", "")).strip()
            pn = str(pl.get("prop_name", "")).strip()
            label = pid or pn
            if not label:
                continue
            mk = cls._join_note_list(pl.get("must_keep"))
            lines.append(f"prop {label}: {mk}" if mk else f"prop {label}")
        st = pack.get("style_lock") or {}
        if isinstance(st, dict):
            gs = cls._join_note_list(st.get("global_style_notes"))
            ma = cls._join_note_list(st.get("must_avoid"))
            if gs:
                lines.append(f"style: {gs}")
            if ma:
                lines.append(f"avoid: {ma}")
        return "\n".join(lines) if lines else "(no pack fields)"

    @staticmethod
    def _gather_entity_context(sp_content: dict) -> str:
        """Extract character/location/prop descriptions from screenplay packs."""
        chars: dict[str, list[str]] = {}
        locs: dict[str, list[str]] = {}
        props: dict[str, tuple[str, list[str]]] = {}  # prop_id → (name, notes)
        for sc in sp_content.get("scenes", []):
            pack = sc.get("scene_consistency_pack", {})
            for cl in pack.get("character_locks", []):
                cid = cl.get("character_id", "")
                notes = cl.get("identity_notes", []) + cl.get("wardrobe_notes", [])
                chars.setdefault(cid, []).extend(notes)
            ll = pack.get("location_lock", {})
            lid = ll.get("location_id", "")
            env = ll.get("environment_notes", [])
            if lid:
                locs.setdefault(lid, []).extend(env)
            for pl in pack.get("props_lock", []):
                pid = pl.get("prop_id", "")
                pn = pl.get("prop_name", "")
                mk = pl.get("must_keep", [])
                if pid:
                    existing = props.get(pid)
                    if existing:
                        existing[1].extend(mk)
                    else:
                        props[pid] = (pn, list(mk))
        parts: list[str] = []
        for cid, notes in chars.items():
            parts.append(f"Character {cid}: " + "; ".join(dict.fromkeys(notes)))
        for lid, notes in locs.items():
            parts.append(f"Location {lid}: " + "; ".join(dict.fromkeys(notes)))
        for pid, (pn, notes) in props.items():
            parts.append(f"Prop {pid} (\"{pn}\"): " + "; ".join(dict.fromkeys(notes)))
        return "\n".join(parts)

    def _build_creative_prompt_scene(
        self, sp_scene: dict, skel_scene: KeyframeScene, sp_content: dict
    ) -> str:
        """Prompt asking the LLM to fill one scene's prompt_summary fields."""
        scene_id = sp_scene.get("scene_id", "")
        pack = sp_scene.get("scene_consistency_pack", {})

        shots_summary: list[str] = []
        for sh in sp_scene.get("shots", []):
            shots_summary.append(
                f"  {sh.get('shot_id','')}: type={sh.get('shot_type','')}, "
                f"visual_goal=\"{sh.get('visual_goal','')}\", "
                f"action_focus=\"{sh.get('action_focus','')}\", "
                f"chars={sh.get('characters_in_frame',[])}, "
                f"props={sh.get('props_in_frame',[])}, "
                f"camera={sh.get('camera',{})}"
            )
        context = (
            "=== SCENE PACK (compact) ===\n"
            f"{self._compact_scene_pack_lines(pack)}\n"
            "=== SHOTS ===\n" + "\n".join(shots_summary)
        )

        stab = skel_scene.stability_keyframes
        sc_chars = [
            f'      {{"entity_id": "{c.entity_id}", "prompt_summary": "<FILL>"}}'
            for c in stab.characters
        ]
        sc_locs = [
            f'      {{"entity_id": "{l.entity_id}", "prompt_summary": "<FILL>"}}'
            for l in stab.locations
        ]
        sc_props = [
            f'      {{"entity_id": "{p.entity_id}", "prompt_summary": "<FILL>"}}'
            for p in stab.props
        ]
        shot_parts: list[str] = []
        for shot in skel_scene.shots:
            kf_entries = [
                f'          {{"keyframe_id": "{kf.keyframe_id}", '
                f'"prompt_summary": "<FILL>", "video_motion_hint": "<FILL>"}}'
                for kf in shot.keyframes
            ]
            shot_parts.append(
                f'      {{"shot_id": "{shot.shot_id}", "keyframes": [\n'
                + ",\n".join(kf_entries) + "\n      ]}}"
            )

        template = (
            '{\n  "scene_id": "' + scene_id + '",\n'
            '  "stability_keyframes": {\n'
            '    "characters": [\n' + ",\n".join(sc_chars) + "\n    ],\n"
            '    "locations": [\n' + ",\n".join(sc_locs) + "\n    ],\n"
            '    "props": [\n' + ",\n".join(sc_props) + "\n    ]\n"
            '  },\n'
            '  "shots": [\n' + ",\n".join(shot_parts) + "\n  ]\n}"
        )
        style = self._extract_style_section(sp_content)
        return (
            f"Scene {scene_id}: fill L2 stability_keyframes + L3 shot rows.\n"
            "L2: edit deltas vs global anchor; do not dump full style lists.\n"
            "L3: one keyframe per shot — prompt_summary (still) and video_motion_hint (motion); "
            "do not duplicate still text into motion.\n\n"
            f"{style}"
            f"{context}\n\n"
            "Replace each <FILL>.\n"
            f"{template}\n\n"
            "Return JSON only."
        )

    # ------------------------------------------------------------------
    # Parallel skeleton mode (override base class single-call approach)
    # ------------------------------------------------------------------

    async def _run_skeleton_mode(
        self,
        input_data: KeyFrameAgentInput,
        skeleton: KeyFrameAgentOutput,
        rework_notes: str,
    ) -> KeyFrameAgentOutput:
        """Fill creative fields via parallel LLM calls (1 global + N scenes).

        Overrides ``BaseAgent._run_skeleton_mode`` to avoid a single massive
        LLM call that would time out.
        """
        sp_content = input_data.screenplay.get("content", {})
        sp_scenes = sp_content.get("scenes", [])
        system = self.system_prompt()

        rework_suffix = ""
        if rework_notes:
            rework_suffix = (
                "\n\n--- REWORK INSTRUCTIONS (from quality review) ---\n"
                f"{rework_notes}\n"
                "--- END REWORK INSTRUCTIONS ---\n"
                "Apply the above fixes while preserving everything else."
            )

        # Build all prompts
        global_prompt = self._build_creative_prompt_global(sp_content, skeleton) + rework_suffix

        scene_prompts: list[str] = []
        for sp_scene, skel_scene in zip(sp_scenes, skeleton.content.scenes):
            scene_prompts.append(
                self._build_creative_prompt_scene(sp_scene, skel_scene, sp_content) + rework_suffix
            )

        # Fire all LLM calls in parallel
        logger.info(
            "[%s] Launching %d parallel LLM calls (1 global + %d scenes)",
            self.agent_name, 1 + len(scene_prompts), len(scene_prompts),
        )
        coros = [self.llm.chat_json(system, global_prompt)]
        for sp in scene_prompts:
            coros.append(self.llm.chat_json(system, sp))

        results = await asyncio.gather(*coros, return_exceptions=True)

        # Check for errors
        for i, r in enumerate(results):
            if isinstance(r, Exception):
                label = "global" if i == 0 else f"scene {i}"
                raise RuntimeError(
                    f"[{self.agent_name}] Parallel LLM call failed for {label}: {r}"
                ) from r

        global_creative = results[0]
        scene_creatives = results[1:]

        logger.info(
            "[%s] All %d parallel LLM calls completed, merging …",
            self.agent_name, len(results),
        )

        # Merge global anchors
        self._fill_global(skeleton, global_creative)

        # Merge per-scene
        for skel_scene, sc_creative in zip(skeleton.content.scenes, scene_creatives):
            self._fill_scene(skel_scene, sc_creative)

        return skeleton

    # ------------------------------------------------------------------
    # Fill helpers (split from the original monolithic fill_creative)
    # ------------------------------------------------------------------

    @staticmethod
    def _fill_global(
        skeleton: KeyFrameAgentOutput, creative: dict
    ) -> None:
        """Merge global_anchors prompt_summary from LLM into skeleton."""
        char_prompts = {
            c.get("entity_id", ""): c.get("prompt_summary", "")
            for c in creative.get("characters", [])
        }
        loc_prompts = {
            l.get("entity_id", ""): l.get("prompt_summary", "")
            for l in creative.get("locations", [])
        }
        prop_prompts = {
            p.get("entity_id", ""): p.get("prompt_summary", "")
            for p in creative.get("props", [])
        }
        for ch in skeleton.content.global_anchors.characters:
            ch.prompt_summary = char_prompts.get(ch.entity_id, "")
        for lo in skeleton.content.global_anchors.locations:
            lo.prompt_summary = loc_prompts.get(lo.entity_id, "")
        for pr in skeleton.content.global_anchors.props:
            pr.prompt_summary = prop_prompts.get(pr.entity_id, "")

    @staticmethod
    def _fill_scene(
        skel_scene: KeyframeScene, creative: dict
    ) -> None:
        """Merge one scene's prompt_summary from LLM into skeleton."""
        stab_data = creative.get("stability_keyframes", {})
        stab_char_map = {
            c.get("entity_id", ""): c.get("prompt_summary", "")
            for c in stab_data.get("characters", [])
        }
        stab_loc_map = {
            l.get("entity_id", ""): l.get("prompt_summary", "")
            for l in stab_data.get("locations", [])
        }
        stab_prop_map = {
            p.get("entity_id", ""): p.get("prompt_summary", "")
            for p in stab_data.get("props", [])
        }
        for ch in skel_scene.stability_keyframes.characters:
            ch.prompt_summary = stab_char_map.get(ch.entity_id, "")
        for lo in skel_scene.stability_keyframes.locations:
            lo.prompt_summary = stab_loc_map.get(lo.entity_id, "")
        for pr in skel_scene.stability_keyframes.props:
            pr.prompt_summary = stab_prop_map.get(pr.entity_id, "")

        shot_map: dict[str, dict] = {
            s.get("shot_id", ""): s
            for s in creative.get("shots", [])
        }
        for shot in skel_scene.shots:
            shot_data = shot_map.get(shot.shot_id, {})
            kf_map: dict[str, tuple[str, str]] = {}
            for k in shot_data.get("keyframes", []):
                kid = k.get("keyframe_id", "")
                kf_map[kid] = (
                    str(k.get("prompt_summary", "") or ""),
                    str(k.get("video_motion_hint", "") or "").strip(),
                )
            for kf in shot.keyframes:
                ps, vm = kf_map.get(kf.keyframe_id, ("", ""))
                kf.prompt_summary = ps
                kf.video_motion_hint = vm

    def recompute_metrics(self, output: KeyFrameAgentOutput) -> None:
        c = output.content
        self._normalize_order(c.scenes)
        for scene in c.scenes:
            self._normalize_order(scene.shots)
            for shot in scene.shots:
                self._normalize_order(shot.keyframes)
        scene_count = len(c.scenes)
        shot_count = sum(len(s.shots) for s in c.scenes)
        kf_count = sum(
            len(sh.keyframes) for s in c.scenes for sh in s.shots
        )
        output.metrics.scene_count = scene_count
        output.metrics.shot_count = shot_count
        output.metrics.keyframe_count_total = kf_count
        output.metrics.avg_keyframes_per_shot = (
            kf_count / shot_count if shot_count else 0.0
        )
        output.metrics.global_character_anchor_count = len(
            c.global_anchors.characters
        )
        output.metrics.global_location_anchor_count = len(
            c.global_anchors.locations
        )
        output.metrics.global_prop_anchor_count = len(
            c.global_anchors.props
        )
        output.metrics.stability_character_keyframe_count = sum(
            len(s.stability_keyframes.characters) for s in c.scenes
        )
        output.metrics.stability_location_keyframe_count = sum(
            len(s.stability_keyframes.locations) for s in c.scenes
        )
        output.metrics.stability_prop_keyframe_count = sum(
            len(s.stability_keyframes.props) for s in c.scenes
        )

    # Quality evaluation has been moved to KeyframeEvaluator
    # (see evaluator.py in this package).
