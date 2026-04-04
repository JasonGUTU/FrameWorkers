"""Video clip materializer — generates video clips via VideoService.

This materializer is a **pure generator** — it calls VideoService to
produce video bytes and returns ``list[MediaAsset]``.  It never performs
file I/O; persistence is handled exclusively by Assistant.
"""

from __future__ import annotations

import json
import logging
import math
import os
from io import BytesIO
from typing import Any

from PIL import Image

from ..descriptor import BaseMaterializer, MediaAsset
from ..contracts.input_bundle_v2 import InputBundleV2
from inference.generation.video_generators.service import VideoService

logger = logging.getLogger(__name__)


class VideoMaterializer(BaseMaterializer):
    """Generate video clips for all shots via VideoService.

    Constructor:
        video_service: ``VideoService`` instance.
    """

    def __init__(self, video_service: VideoService) -> None:
        self.video_svc = video_service
        # Unified switch first, then legacy switch for backward compatibility.
        # Default off for faster testing.
        raw = os.getenv(
            "FW_ENABLE_PROP_PIPELINE",
            os.getenv("FW_VIDEO_ENABLE_PROP_CONSISTENCY", "0"),
        ).strip().lower()
        self._enable_prop_consistency = raw in {"1", "true", "yes", "on"}

    @staticmethod
    def naming_spec_v2() -> dict[str, Any]:
        return {
            "agent_id": "VideoAgent",
            "spec_version": "1.0",
            "rules": [
                {
                    "artifact_family": "video_clip",
                    "semantic_meaning": "shot/scene/final video clips",
                    "recommended_name_pattern": "clip_{shot_or_scene_or_final}.mp4",
                    "id_source": "screenplay shot_id and scene_id",
                    "ordering_rules": "shot clips follow scene shot order",
                    "examples": ["clip_sh_001.mp4", "clip_sc_001.mp4", "clip_final.mp4"],
                    "rename_hints": {"stable_parts": "clip prefix and id token", "mutable_parts": "optional readability infix"},
                }
            ],
        }

    @staticmethod
    def _resolved_inputs(input_bundle_v2: InputBundleV2) -> dict[str, Any]:
        ctx = getattr(input_bundle_v2, "context", {})
        resolved = ctx.get("resolved_inputs") if isinstance(ctx, dict) else None
        return resolved if isinstance(resolved, dict) else {}

    @staticmethod
    def _normalize_local_path(uri: str) -> str:
        if not uri:
            return ""
        if uri.startswith("file://"):
            return uri[7:]
        return uri

    @staticmethod
    def _merge_keyframe_images_for_video_api(
        images: list[bytes],
        prompt_summaries: list[str],
    ) -> tuple[list[bytes], list[str], str]:
        """Stitch multiple PNGs into one horizontal strip (tests / tooling only).

        **Production video** uses a single Layer-3 shot PNG per ``VideoMaterializer``
        call; this helper remains for ``tests/inference`` merge smoke tests.

        Returns:
            (``[merged_png]``, ``[summary_for_constraints]``, layout_tag)
        """
        n = len(images)
        if n <= 1:
            return images, prompt_summaries, "unchanged_single_or_empty"

        panels = [Image.open(BytesIO(b)).convert("RGB") for b in images]
        h = max(p.height for p in panels)
        scaled: list[Image.Image] = []
        for p in panels:
            nw = max(1, int(round(p.width * h / p.height)))
            scaled.append(p.resize((nw, h), Image.Resampling.LANCZOS))
        total_w = sum(p.width for p in scaled)
        canvas = Image.new("RGB", (total_w, h))
        x = 0
        for p in scaled:
            canvas.paste(p, (x, 0))
            x += p.width

        # fal Kling image-to-video rejects conditioning images outside 0.4 <= w/h <= 2.5
        # (wide horizontal merges exceed the max unless letterboxed).
        tw, th = canvas.size
        ar = tw / max(th, 1)
        _KLING_AR_MIN, _KLING_AR_MAX = 0.4, 2.5
        pad_color = (16, 16, 16)
        if ar > _KLING_AR_MAX:
            new_h = max(1, int(math.ceil(tw / _KLING_AR_MAX)))
            bg = Image.new("RGB", (tw, new_h), pad_color)
            y0 = max(0, (new_h - th) // 2)
            bg.paste(canvas, (0, y0))
            canvas = bg
        elif ar < _KLING_AR_MIN:
            new_w = max(1, int(math.ceil(th * _KLING_AR_MIN)))
            bg = Image.new("RGB", (new_w, th), pad_color)
            x0 = max(0, (new_w - tw) // 2)
            bg.paste(canvas, (x0, 0))
            canvas = bg

        out = BytesIO()
        canvas.save(out, format="PNG")
        merged = out.getvalue()

        if n == 2:
            summary = (
                "Reference: single horizontal composite PNG (two equal-height panels "
                "left-to-right). Left panel = first reference; right panel = second. "
                "Use this one image as the sole visual conditioning input."
            )
            if len(prompt_summaries) >= 2:
                summary += (
                    " | Panel text notes (left then right): "
                    + prompt_summaries[0]
                    + " || "
                    + prompt_summaries[1]
                )
            elif prompt_summaries:
                summary += " | Notes: " + " | ".join(prompt_summaries)
        else:
            summary = (
                f"Reference: single horizontal composite of {n} panels "
                "(left-to-right, equalized height). Sole conditioning image."
            )
            if prompt_summaries:
                summary += " | Notes: " + " || ".join(prompt_summaries)

        return [merged], [summary], f"horizontal_merge_{n}_panels"

    def _build_shot_keyframe_inputs_index(
        self, input_bundle_v2: InputBundleV2
    ) -> dict[str, list[dict[str, str]]]:
        """Map shot_id → at most one loadable L3 keyframe row.

        Row keys: ``uri``, ``prompt_summary`` (image / constraints), optional
        ``video_motion_hint`` (I2V text prefix only; no substitute for empty).
        """
        index: dict[str, list[dict[str, str]]] = {}
        keyframes = self._resolved_inputs(input_bundle_v2).get("keyframes", {})
        content = keyframes.get("content", {}) if isinstance(keyframes, dict) else {}

        for scene in content.get("scenes", []):
            for shot in scene.get("shots", []):
                shot_id = shot.get("shot_id", "")
                if not shot_id:
                    continue
                for kf in shot.get("keyframes", []):
                    image_asset = kf.get("image_asset", {})
                    uri = self._normalize_local_path(image_asset.get("uri", ""))
                    prompt_summary = str(kf.get("prompt_summary", "")).strip()
                    video_motion_hint = str(kf.get("video_motion_hint", "") or "").strip()
                    if not uri and not prompt_summary:
                        continue
                    index[shot_id] = [
                        {
                            "uri": uri,
                            "prompt_summary": prompt_summary,
                            "video_motion_hint": video_motion_hint,
                        }
                    ]
                    break

        return index

    def _build_screenplay_shot_index(self, input_bundle_v2: InputBundleV2) -> dict[str, dict[str, Any]]:
        """Build shot_id -> screenplay shot metadata used for clip prompting."""
        index: dict[str, dict[str, Any]] = {}
        screenplay = self._resolved_inputs(input_bundle_v2).get("screenplay", {})
        content = screenplay.get("content", {}) if isinstance(screenplay, dict) else {}
        for scene in content.get("scenes", []):
            consistency_pack = (
                scene.get("scene_consistency_pack", {})
                if isinstance(scene.get("scene_consistency_pack", {}), dict)
                else {}
            )
            location_lock = (
                consistency_pack.get("location_lock", {})
                if isinstance(consistency_pack.get("location_lock", {}), dict)
                else {}
            )
            style_lock = (
                consistency_pack.get("style_lock", {})
                if isinstance(consistency_pack.get("style_lock", {}), dict)
                else {}
            )
            for shot in scene.get("shots", []):
                shot_id = shot.get("shot_id", "")
                if not shot_id:
                    continue
                camera = shot.get("camera", {}) if isinstance(shot.get("camera", {}), dict) else {}
                keyframe_plan = (
                    shot.get("keyframe_plan", {})
                    if isinstance(shot.get("keyframe_plan", {}), dict)
                    else {}
                )
                index[shot_id] = {
                    "shot_type": str(shot.get("shot_type", "")).strip(),
                    "visual_goal": str(shot.get("visual_goal", "")).strip(),
                    "action_focus": str(shot.get("action_focus", "")).strip(),
                    "characters_in_frame": [
                        str(cid).strip()
                        for cid in shot.get("characters_in_frame", [])
                        if str(cid).strip()
                    ],
                    "props_in_frame": (
                        [
                            str(pid).strip()
                            for pid in shot.get("props_in_frame", [])
                            if str(pid).strip()
                        ]
                        if self._enable_prop_consistency
                        else []
                    ),
                    "camera_angle": str(camera.get("angle", "")).strip(),
                    "camera_movement": str(camera.get("movement", "")).strip(),
                    "framing_notes": str(camera.get("framing_notes", "")).strip(),
                    "scene_id": str(scene.get("scene_id", "")).strip(),
                    "scene_location_id": str(location_lock.get("location_id", "")).strip(),
                    "scene_time_of_day": str(location_lock.get("time_of_day", "")).strip(),
                    "scene_environment_notes": [
                        str(note).strip()
                        for note in location_lock.get("environment_notes", [])
                        if str(note).strip()
                    ],
                    "scene_style_notes": [
                        str(note).strip()
                        for note in style_lock.get("global_style_notes", [])
                        if str(note).strip()
                    ],
                    "scene_must_avoid": [
                        str(note).strip()
                        for note in style_lock.get("must_avoid", [])
                        if str(note).strip()
                    ],
                    "keyframe_notes": [
                        str(note).strip()
                        for note in keyframe_plan.get("keyframe_notes", [])
                        if str(note).strip()
                    ],
                }
        return index

    @staticmethod
    def _build_structured_constraints(
        shot_id: str,
        prompt_summaries: list[str],
        storyboard_shot: dict[str, Any],
        *,
        video_motion_hints: list[str] | None = None,
    ) -> dict[str, Any]:
        """Build model-facing structured consistency constraints for one shot."""
        vmh = list(video_motion_hints) if video_motion_hints else []
        return {
            "shot_id": shot_id,
            "consistency_type": "entity_anchor_constraints",
            "keyframe_role": "shot_still_l3_only",
            "characters_in_frame": storyboard_shot.get("characters_in_frame", []),
            "scene_context": {
                "scene_id": storyboard_shot.get("scene_id", ""),
                "location_id": storyboard_shot.get("scene_location_id", ""),
                "time_of_day": storyboard_shot.get("scene_time_of_day", ""),
                "environment_notes": storyboard_shot.get("scene_environment_notes", []),
                "style_notes": storyboard_shot.get("scene_style_notes", []),
                "must_avoid": storyboard_shot.get("scene_must_avoid", []),
            },
            "visual_goal": storyboard_shot.get("visual_goal", ""),
            "action_focus": storyboard_shot.get("action_focus", ""),
            "camera": {
                "angle": storyboard_shot.get("camera_angle", ""),
                "movement": storyboard_shot.get("camera_movement", ""),
                "framing_notes": storyboard_shot.get("framing_notes", ""),
            },
            "storyboard_keyframe_notes": storyboard_shot.get("keyframe_notes", []),
            "keyframe_prompt_summaries": prompt_summaries,
            "keyframe_video_motion_hints": vmh,
        }

    @staticmethod
    def _build_clip_prompt(
        shot_id: str,
        prompt_summaries: list[str],
        storyboard_shot: dict[str, Any],
        *,
        anchor_image_count: int,
        omit_scene_tone_blocks: bool = False,
    ) -> str:
        """Compose a concise, task-first shot prompt for video generation.

        When ``omit_scene_tone_blocks`` is True (used with a non-empty
        ``video_motion_hint`` prefix), environment/style/must_avoid lines are
        omitted — they duplicate the L3 still + motion prefix for I2V.
        """
        parts: list[str] = [f"Shot {shot_id}"]
        if omit_scene_tone_blocks:
            parts.append(
                "Ref: one L3 still for look; motion from text prefix + below."
            )
        else:
            parts.append(
                "Visual reference: a single Layer-3 shot still (composition, cast, props); "
                "use it for look consistency only — motion/timing follow this text prompt."
            )
        shot_type = storyboard_shot.get("shot_type", "")
        if shot_type:
            parts.append(f"Type: {shot_type}")
        visual_goal = storyboard_shot.get("visual_goal", "")
        if visual_goal:
            parts.append(f"Visual goal: {visual_goal}")
        action_focus = storyboard_shot.get("action_focus", "")
        if action_focus:
            parts.append(f"Action focus: {action_focus}")
        characters_in_frame = storyboard_shot.get("characters_in_frame", [])
        if characters_in_frame:
            parts.append("Characters in frame: " + ", ".join(characters_in_frame))
        scene_location_id = storyboard_shot.get("scene_location_id", "")
        scene_time_of_day = storyboard_shot.get("scene_time_of_day", "")
        if scene_location_id or scene_time_of_day:
            scene_context_bits: list[str] = []
            if scene_location_id:
                scene_context_bits.append(f"location_id={scene_location_id}")
            if scene_time_of_day:
                scene_context_bits.append(f"time_of_day={scene_time_of_day}")
            parts.append("Scene context: " + ", ".join(scene_context_bits))
        scene_environment_notes = storyboard_shot.get("scene_environment_notes", [])
        if not omit_scene_tone_blocks and scene_environment_notes:
            parts.append("Scene environment notes: " + " || ".join(scene_environment_notes))
        scene_style_notes = storyboard_shot.get("scene_style_notes", [])
        if not omit_scene_tone_blocks and scene_style_notes:
            parts.append("Scene style notes: " + " || ".join(scene_style_notes))
        scene_must_avoid = storyboard_shot.get("scene_must_avoid", [])
        if not omit_scene_tone_blocks and scene_must_avoid:
            parts.append("Scene must avoid: " + " || ".join(scene_must_avoid))
        camera_angle = storyboard_shot.get("camera_angle", "")
        camera_movement = storyboard_shot.get("camera_movement", "")
        if camera_angle or camera_movement:
            parts.append(
                "Camera: "
                + ", ".join(
                    [x for x in [f"angle={camera_angle}" if camera_angle else "", f"movement={camera_movement}" if camera_movement else ""] if x]
                )
            )
        framing_notes = storyboard_shot.get("framing_notes", "")
        if framing_notes:
            parts.append(f"Framing notes: {framing_notes}")
        parts.append(f"Anchor images: {anchor_image_count}")
        if action_focus and not omit_scene_tone_blocks:
            parts.append("Task focus: in this scene, complete this shot action: " + action_focus)
        return " | ".join(parts)

    @staticmethod
    def _load_keyframe_images_with_prompts(
        keyframe_inputs: list[dict[str, str]],
    ) -> tuple[list[bytes], list[str], list[str]]:
        """Load L3 PNGs plus parallel ``prompt_summary`` / ``video_motion_hint`` lists."""
        images: list[bytes] = []
        prompt_summaries: list[str] = []
        video_motion_hints: list[str] = []
        for item in keyframe_inputs:
            uri = item.get("uri", "")
            if not uri or not os.path.isfile(uri):
                continue
            try:
                with open(uri, "rb") as fh:
                    images.append(fh.read())
                ps = str(item.get("prompt_summary", "") or "")
                vmh = str(item.get("video_motion_hint", "") or "").strip()
                if ps.strip():
                    prompt_summaries.append(ps)
                else:
                    prompt_summaries.append("")
                video_motion_hints.append(vmh)
            except Exception:
                continue
        return images, prompt_summaries, video_motion_hints

    async def materialize(
        self,
        task_id: str,
        asset_dict: dict[str, Any],
        input_bundle_v2: InputBundleV2,
    ) -> list[MediaAsset]:
        """Generate actual video clips for all shots.

        System-generates sequential asset_ids (IDs already include type prefix):
          Shot clip  -- ``clip_{shot_id}``      e.g. ``clip_sh_001``
          Scene clip -- ``clip_{scene_id}``     e.g. ``clip_sc_001``
          Final      -- ``clip_final``

        Returns:
            List of ``MediaAsset`` objects for Assistant to persist.
        """
        pending: list[MediaAsset] = []
        content = asset_dict.get("content", {})
        scene_bytes_list: list[bytes] = []
        shot_keyframe_inputs = self._build_shot_keyframe_inputs_index(input_bundle_v2)
        screenplay_shot_index = self._build_screenplay_shot_index(input_bundle_v2)

        for scene in content.get("scenes", []):
            scene_id = scene.get("scene_id", "")
            clip_bytes_list: list[bytes] = []

            for seg in scene.get("shot_segments", []):
                shot_id = seg.get("shot_id", "")
                video_asset = seg.get("video_asset", {})
                sys_vid_id = f"clip_{shot_id}"
                video_asset["asset_id"] = sys_vid_id
                (
                    keyframe_images,
                    prompt_summaries,
                    video_motion_hints,
                ) = self._load_keyframe_images_with_prompts(
                    shot_keyframe_inputs.get(shot_id, [])
                )
                if not keyframe_images:
                    logger.error(
                        "Video clip skipped for %s: missing on-disk L3 shot keyframe",
                        shot_id,
                    )
                    continue

                vmh0 = str(video_motion_hints[0]).strip() if video_motion_hints else ""
                motion_active = bool(vmh0)
                clip_prompt = self._build_clip_prompt(
                    shot_id=shot_id,
                    prompt_summaries=prompt_summaries,
                    storyboard_shot=screenplay_shot_index.get(shot_id, {}),
                    anchor_image_count=len(keyframe_images),
                    omit_scene_tone_blocks=motion_active,
                )
                if motion_active:
                    clip_prompt = vmh0 + " | " + clip_prompt

                structured_constraints = self._build_structured_constraints(
                    shot_id=shot_id,
                    prompt_summaries=prompt_summaries,
                    storyboard_shot=screenplay_shot_index.get(shot_id, {}),
                    video_motion_hints=video_motion_hints,
                )

                seg["video_generation_prompt"] = clip_prompt
                seg["video_generation_constraints_json"] = (
                    json.dumps(structured_constraints, ensure_ascii=False)
                    if structured_constraints
                    else ""
                )

                try:
                    clip_bytes = await self.video_svc.generate_clip(
                        shot_id=shot_id,
                        keyframe_images=keyframe_images,
                        prompt=clip_prompt,
                        duration_sec=seg.get("estimated_duration_sec", 3.0),
                        consistency_constraints=structured_constraints,
                    )
                    ext = video_asset.get("format", "mp4")
                    pending.append(MediaAsset(
                        sys_id=sys_vid_id, data=clip_bytes,
                        extension=ext, uri_holder=video_asset,
                    ))
                    clip_bytes_list.append(clip_bytes)
                except Exception as exc:
                    logger.error("Video clip generation failed for %s: %s", shot_id, exc)

            scene_clip = scene.get("scene_clip_asset", {})
            sys_scene_clip_id = f"clip_{scene_id}"
            scene_clip["asset_id"] = sys_scene_clip_id
            if clip_bytes_list:
                try:
                    scene_bytes = await self.video_svc.assemble_scene(
                        scene_id=scene_id,
                        clip_bytes_list=clip_bytes_list,
                        transitions=scene.get("transition_plan", []),
                    )
                    pending.append(MediaAsset(
                        sys_id=sys_scene_clip_id, data=scene_bytes,
                        extension="mp4", uri_holder=scene_clip,
                    ))
                    scene_bytes_list.append(scene_bytes)
                except Exception as exc:
                    logger.error("Scene assembly failed for %s: %s", scene_id, exc)

        final = content.get("final_video_asset", {})
        final["asset_id"] = "clip_final"
        if scene_bytes_list:
            try:
                final_bytes = await self.video_svc.assemble_final(
                    scene_bytes_list=scene_bytes_list
                )
                pending.append(MediaAsset(
                    sys_id="clip_final", data=final_bytes,
                    extension="mp4", uri_holder=final,
                ))
            except Exception as exc:
                logger.error("Final video assembly failed: %s", exc)

        logger.info("All video clips materialized for %s", task_id)
        return pending
