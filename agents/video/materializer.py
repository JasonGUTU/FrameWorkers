"""Video clip materializer — generates video clips via VideoService.

This materializer is a **pure generator** — it calls VideoService to
produce video bytes and returns ``list[MediaAsset]``.  It never performs
file I/O; persistence is handled exclusively by Assistant.
"""

from __future__ import annotations

import logging
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

        for scene in content.get("scenes", []):
            scene_id = scene.get("scene_id", "")
            clip_bytes_list: list[bytes] = []

            for seg in scene.get("shot_segments", []):
                shot_id = seg.get("shot_id", "")
                video_asset = seg.get("video_asset", {})
                sys_vid_id = f"clip_{shot_id}"
                video_asset["asset_id"] = sys_vid_id

                try:
                    clip_bytes = await self.video_svc.generate_clip(
                        shot_id=shot_id,
                        keyframe_images=[],
                        prompt=f"Shot {shot_id}",
                        duration_sec=seg.get("estimated_duration_sec", 3.0),
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
