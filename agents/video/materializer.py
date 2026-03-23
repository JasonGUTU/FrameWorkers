"""Video clip materializer — generates video clips via VideoService.

This materializer is a **pure generator** — it calls VideoService to
produce video bytes and returns ``list[MediaAsset]``.  It never performs
file I/O; persistence is handled exclusively by Assistant.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from ..descriptor import BaseMaterializer, MediaAsset
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
    def _normalize_local_path(uri: str) -> str:
        if not uri:
            return ""
        if uri.startswith("file://"):
            return uri[7:]
        return uri

    def _build_shot_keyframe_inputs_index(
        self, assets: dict[str, Any]
    ) -> dict[str, list[dict[str, str]]]:
        """Build shot_id -> ordered keyframe inputs (uri + prompt summary)."""
        index: dict[str, list[dict[str, str]]] = {}
        keyframes = (assets or {}).get("keyframes", {})
        content = keyframes.get("content", {}) if isinstance(keyframes, dict) else {}
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
                inputs: list[dict[str, str]] = []
                for kf in shot.get("keyframes", []):
                    image_asset = kf.get("image_asset", {})
                    uri = self._normalize_local_path(image_asset.get("uri", ""))
                    prompt_summary = str(kf.get("prompt_summary", "")).strip()
                    if uri or prompt_summary:
                        inputs.append(
                            {
                                "uri": uri,
                                "prompt_summary": prompt_summary,
                            }
                        )
                if inputs:
                    index[shot_id] = inputs
        return index

    def _build_storyboard_shot_index(self, assets: dict[str, Any]) -> dict[str, dict[str, Any]]:
        """Build shot_id -> storyboard shot metadata used for clip prompting."""
        index: dict[str, dict[str, Any]] = {}
        storyboard = (assets or {}).get("storyboard", {})
        content = storyboard.get("content", {}) if isinstance(storyboard, dict) else {}
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
    ) -> dict[str, Any]:
        """Build model-facing structured consistency constraints for one shot."""
        return {
            "shot_id": shot_id,
            "consistency_type": "entity_anchor_constraints",
            "keyframe_role": "stability_and_consistency_only",
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
        }

    @staticmethod
    def _build_clip_prompt(
        shot_id: str,
        prompt_summaries: list[str],
        storyboard_shot: dict[str, Any],
    ) -> str:
        """Compose a concise, task-first shot prompt for video generation."""
        parts: list[str] = [f"Shot {shot_id}"]
        parts.append(
            "Keyframe policy: keyframe anchors are for stability/consistency only "
            "(identity, props state, scene look), not additional story actions."
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
        if scene_environment_notes:
            parts.append("Scene environment notes: " + " || ".join(scene_environment_notes))
        scene_style_notes = storyboard_shot.get("scene_style_notes", [])
        if scene_style_notes:
            parts.append("Scene style notes: " + " || ".join(scene_style_notes))
        scene_must_avoid = storyboard_shot.get("scene_must_avoid", [])
        if scene_must_avoid:
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
        keyframe_count = max(len(prompt_summaries), len(storyboard_shot.get("keyframe_notes", [])))
        parts.append(f"Anchor images: {keyframe_count}")
        if action_focus:
            parts.append("Task focus: in this scene, complete this shot action: " + action_focus)
        return " | ".join(parts)

    @staticmethod
    def _load_keyframe_images_with_prompts(
        keyframe_inputs: list[dict[str, str]],
    ) -> tuple[list[bytes], list[str]]:
        images: list[bytes] = []
        prompt_summaries: list[str] = []
        for item in keyframe_inputs:
            uri = item.get("uri", "")
            if not uri or not os.path.isfile(uri):
                continue
            try:
                with open(uri, "rb") as fh:
                    images.append(fh.read())
                prompt_summary = item.get("prompt_summary", "")
                if prompt_summary:
                    prompt_summaries.append(prompt_summary)
            except Exception:
                # Skip bad inputs and let backend fall back gracefully.
                continue
        return images, prompt_summaries

    async def materialize(
        self,
        project_id: str,
        asset_dict: dict[str, Any],
        assets: dict[str, Any],
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
        shot_keyframe_inputs = self._build_shot_keyframe_inputs_index(assets)
        storyboard_shot_index = self._build_storyboard_shot_index(assets)

        for scene in content.get("scenes", []):
            scene_id = scene.get("scene_id", "")
            clip_bytes_list: list[bytes] = []

            for seg in scene.get("shot_segments", []):
                shot_id = seg.get("shot_id", "")
                video_asset = seg.get("video_asset", {})
                sys_vid_id = f"clip_{shot_id}"
                video_asset["asset_id"] = sys_vid_id
                keyframe_images, prompt_summaries = self._load_keyframe_images_with_prompts(
                    shot_keyframe_inputs.get(shot_id, [])
                )
                clip_prompt = self._build_clip_prompt(
                    shot_id=shot_id,
                    prompt_summaries=prompt_summaries,
                    storyboard_shot=storyboard_shot_index.get(shot_id, {}),
                )
                structured_constraints = self._build_structured_constraints(
                    shot_id=shot_id,
                    prompt_summaries=prompt_summaries,
                    storyboard_shot=storyboard_shot_index.get(shot_id, {}),
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

        logger.info("All video clips materialized for %s", project_id)
        return pending
