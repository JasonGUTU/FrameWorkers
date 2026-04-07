"""UnivaKeyFrameMaterializer — character T2I + shot keyframe T2I/I2I.

Mirrors UniVA's storyvideo_gen Stages 2+3:
  Phase 1: text_to_image per character (from refined_prompt)
  Phase 2: image_to_image per shot (with character refs) or text_to_image (no chars)
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from typing import TYPE_CHECKING

from ..descriptor import BaseMaterializer, MediaAsset
from inference.generation.image_generators.service import ImageService

if TYPE_CHECKING:
    from ..base_agent import MaterializeContext

logger = logging.getLogger(__name__)

MAX_RETRIES = 3


class UnivaKeyFrameMaterializer(BaseMaterializer):

    def __init__(self, image_service: ImageService) -> None:
        self.image_svc = image_service

    async def materialize(
        self,
        ctx: "MaterializeContext",
        asset_dict: dict[str, Any],
    ) -> list[MediaAsset]:
        # UnivaKeyFrameMaterializer's data needs are entirely in asset_dict
        # (the LLM's output) — it doesn't need anything from typed_input
        # other than the implicit storyboard already encoded in asset_dict.
        media_assets: list[MediaAsset] = []
        content = asset_dict.get("content", {})
        character_images = content.get("character_images", [])
        shot_keyframes = content.get("shot_keyframes", [])

        # ==================================================================
        # Phase 1: Generate character reference images (T2I, parallel)
        # ==================================================================
        char_bytes_map: dict[str, bytes] = {}

        async def _gen_character(ci: dict) -> tuple[str, bytes | None]:
            cid = ci.get("char_id", "")
            prompt = ci.get("refined_prompt", "") or ci.get("original_description", "")
            if not prompt:
                logger.warning("Character %s has no prompt, skipping", cid)
                return cid, None
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    img = await self.image_svc.generate_image(prompt)
                    logger.info("[UnivaKF] Character %s generated (%d bytes)", cid, len(img))
                    return cid, img
                except Exception as e:
                    logger.warning("[UnivaKF] Character %s attempt %d failed: %s", cid, attempt, e)
            return cid, None

        char_tasks = [_gen_character(ci) for ci in character_images]
        char_results = await asyncio.gather(*char_tasks, return_exceptions=True)

        for i, result in enumerate(char_results):
            if isinstance(result, Exception):
                logger.error("[UnivaKF] Character generation exception: %s", result)
                continue
            cid, img_bytes = result
            if img_bytes:
                char_bytes_map[cid] = img_bytes
                # uri_holder points into asset_dict so the URI is written back
                img_asset = character_images[i].get("image_asset", {})
                media_assets.append(MediaAsset(
                    sys_id=f"img_{cid}_character",
                    data=img_bytes,
                    extension=img_asset.get("format", "png"),
                    uri_holder=img_asset,
                ))

        logger.info(
            "[UnivaKF] Phase 1 done: %d/%d character images",
            len(char_bytes_map), len(character_images),
        )

        # ==================================================================
        # Phase 2: Generate per-shot keyframes (T2I or I2I, parallel)
        # ==================================================================
        async def _gen_keyframe(kf: dict) -> tuple[int, bytes | None]:
            shot_id = kf.get("shot_id", 0)
            prompt = kf.get("keyframe_prompt", "")
            onstage = kf.get("onstage_char_ids", [])
            if not prompt:
                logger.warning("Shot %s has no keyframe prompt, skipping", shot_id)
                return shot_id, None

            # Collect character reference images for this shot
            ref_images = [
                char_bytes_map[cid]
                for cid in onstage
                if cid in char_bytes_map
            ]

            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    if ref_images:
                        # I2I with character references (mirrors UniVA's image_to_image_generate)
                        img = await self.image_svc.edit_image(ref_images, prompt)
                    else:
                        # T2I for empty-stage shots (mirrors UniVA's text_to_image_generate)
                        img = await self.image_svc.generate_image(prompt)
                    logger.info("[UnivaKF] Shot %s keyframe generated (%d bytes)", shot_id, len(img))
                    return shot_id, img
                except Exception as e:
                    logger.warning("[UnivaKF] Shot %s attempt %d failed: %s", shot_id, attempt, e)
            return shot_id, None

        kf_tasks = [_gen_keyframe(kf) for kf in shot_keyframes]
        kf_results = await asyncio.gather(*kf_tasks, return_exceptions=True)

        for i, result in enumerate(kf_results):
            if isinstance(result, Exception):
                logger.error("[UnivaKF] Keyframe generation exception: %s", result)
                continue
            shot_id, img_bytes = result
            if img_bytes:
                img_asset = shot_keyframes[i].get("image_asset", {})
                media_assets.append(MediaAsset(
                    sys_id=f"img_shot_{shot_id}_keyframe",
                    data=img_bytes,
                    extension=img_asset.get("format", "png"),
                    uri_holder=img_asset,
                ))

        logger.info(
            "[UnivaKF] Phase 2 done: %d/%d shot keyframes",
            sum(1 for r in kf_results if not isinstance(r, Exception) and r[1]),
            len(shot_keyframes),
        )

        return media_assets
