"""Keyframe image materializer — three-layer consistency chain.

All layers use OpenRouter + Gemini 2.5 Flash Image:
  Layer 1 — Global anchors:  text -> generate_image()
  Layer 2 — Scene anchors:   global anchor img + prompt -> edit_image()
  Layer 3 — Shot keyframes:  scene anchor img(s) + prompt -> edit_image()

Each layer references ONLY the layer above it.
Text descriptions (prompt_summary) are always included.
No fallback needed — Gemini natively supports image editing.

This materializer is a **pure generator** — it calls ImageService to
produce image bytes and returns ``list[MediaAsset]``.  It never performs
file I/O; persistence is handled exclusively by Assistant.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from ..descriptor import BaseMaterializer, MediaAsset
from inference.generation.image_generators.service import ImageService

logger = logging.getLogger(__name__)


class KeyframeMaterializer(BaseMaterializer):
    """Three-layer keyframe image materializer.

    Constructor:
        image_service: ``ImageService`` instance for Gemini image gen/edit.
    """

    def __init__(self, image_service: ImageService) -> None:
        self.image_svc = image_service

    # ------------------------------------------------------------------
    # Main entry point (called by Assistant)
    # ------------------------------------------------------------------

    async def materialize(
        self,
        project_id: str,
        asset_dict: dict[str, Any],
        assets: dict[str, Any],
    ) -> list[MediaAsset]:
        """Generate keyframe images with three-layer consistency chain.

        Within each layer, all images are generated **in parallel** via
        ``asyncio.gather``.  Layers are executed sequentially because each
        layer depends on the previous layer's output.

        When ``assets`` contains ``"reference_images"`` (a list of dicts
        with ``label``, ``entity_type``, and ``image_bytes``), those
        user-provided images are injected as pre-existing global anchors
        **before** Layer 1 generation.  Entities matched to a reference
        image skip generation entirely.

        Naming conventions (all system-generated, IDs already include type prefix):
          Layer 1 (global):  ``img_{char_id}_global``, ``img_{loc_id}_global``, ...
          Layer 2 (scene):   ``img_{char_id}_{scene_id}``, ``img_{loc_id}_{scene_id}``, ...
          Layer 3 (shot):    ``img_{shot_id}_kf_{NN}``

        Examples with actual IDs:
          ``img_char_001_global``, ``img_loc_001_sc_001``, ``img_sh_001_kf_01``

        Returns:
            List of ``MediaAsset`` objects for Assistant to persist.
        """
        self._pending: list[MediaAsset] = []

        content = asset_dict.get("content", {})
        scenes = content.get("scenes", [])

        style_suffix = self._build_style_suffix(assets)

        MAX_LAYER_RETRIES = 10

        # ══════════════════════════════════════════════════════════════
        # Layer 0: Inject user-provided reference images as global anchors
        # ══════════════════════════════════════════════════════════════
        global_anchors = content.get("global_anchors", {})
        global_image_bytes: dict[str, bytes] = {}

        ref_images: list[dict[str, Any]] = (
            (assets or {}).get("reference_images", [])
        )
        if ref_images:
            self._inject_reference_images(
                ref_images, global_anchors, global_image_bytes,
                assets=assets,
            )

        # ══════════════════════════════════════════════════════════════
        # Layer 1: Global Anchors — text -> Gemini generate, retry
        # ══════════════════════════════════════════════════════════════

        l1_tasks: list[tuple[str, dict, str, str]] = []

        for entity_list in ("characters", "locations", "props"):
            for kf in global_anchors.get(entity_list, []):
                eid = kf.get("entity_id", "unknown")
                prompt = kf.get("prompt_summary", "")
                if prompt:
                    l1_tasks.append(
                        (eid, kf, prompt + style_suffix, f"img_{eid}_global")
                    )

        for attempt in range(1, MAX_LAYER_RETRIES + 1):
            pending = [t for t in l1_tasks if t[0] not in global_image_bytes]
            if not pending:
                break
            logger.info(
                "=== Layer 1: Generating %d global anchors (attempt %d/%d) ===",
                len(pending), attempt, MAX_LAYER_RETRIES,
            )
            coros = [
                self._generate(kf, prompt, sys_id)
                for _, kf, prompt, sys_id in pending
            ]
            results = await asyncio.gather(*coros, return_exceptions=True)
            for (key, _, _, _), result in zip(pending, results):
                if isinstance(result, Exception):
                    logger.error("[L1] Error for %s: %s", key, result)
                elif isinstance(result, bytes):
                    global_image_bytes[key] = result
                else:
                    logger.warning("[L1] No image for %s (attempt %d)", key, attempt)

        failed_l1 = [t[0] for t in l1_tasks if t[0] not in global_image_bytes]
        if failed_l1:
            raise RuntimeError(
                f"Layer 1: failed to generate global anchors after "
                f"{MAX_LAYER_RETRIES} attempts: {failed_l1}"
            )
        logger.info(
            "Layer 1 complete: %d/%d global anchors generated",
            len(global_image_bytes), len(l1_tasks),
        )

        # ── Layer 1.5: Backfill — auto-generate missing global anchors ──
        backfill_tasks: list[tuple[str, dict, str, str]] = []
        for scene in scenes:
            stab = scene.get("stability_keyframes", {})
            for entity_list in ("characters", "locations", "props"):
                for kf in stab.get(entity_list, []):
                    eid = kf.get("entity_id", "unknown")
                    prompt = kf.get("prompt_summary", "")
                    if prompt and eid not in global_image_bytes:
                        backfill_tasks.append(
                            (eid, kf, prompt + style_suffix, f"img_{eid}_global")
                        )
        seen_backfill: set[str] = set()
        unique_backfill: list[tuple[str, dict, str, str]] = []
        for task in backfill_tasks:
            if task[0] not in seen_backfill:
                seen_backfill.add(task[0])
                unique_backfill.append(task)

        if unique_backfill:
            logger.warning(
                "[Layer 1.5] %d scene-level entities missing from global_anchors — "
                "backfilling via text-to-image: %s",
                len(unique_backfill),
                [t[0] for t in unique_backfill],
            )
            for attempt in range(1, MAX_LAYER_RETRIES + 1):
                pending_bf = [
                    t for t in unique_backfill if t[0] not in global_image_bytes
                ]
                if not pending_bf:
                    break
                logger.info(
                    "=== Layer 1.5: Backfilling %d global anchors (attempt %d/%d) ===",
                    len(pending_bf), attempt, MAX_LAYER_RETRIES,
                )
                coros = [
                    self._generate(kf, prompt, sys_id)
                    for _, kf, prompt, sys_id in pending_bf
                ]
                results = await asyncio.gather(*coros, return_exceptions=True)
                for (key, _, _, _), result in zip(pending_bf, results):
                    if isinstance(result, Exception):
                        logger.error("[L1.5] Error for %s: %s", key, result)
                    elif isinstance(result, bytes):
                        global_image_bytes[key] = result
                    else:
                        logger.warning(
                            "[L1.5] No image for %s (attempt %d)", key, attempt
                        )

            failed_bf = [
                t[0] for t in unique_backfill if t[0] not in global_image_bytes
            ]
            if failed_bf:
                raise RuntimeError(
                    f"Layer 1.5: failed to backfill global anchors after "
                    f"{MAX_LAYER_RETRIES} attempts: {failed_bf}"
                )
            logger.info(
                "Layer 1.5 complete: %d backfilled global anchors",
                len(unique_backfill),
            )

        # ══════════════════════════════════════════════════════════════
        # Layer 2: Scene Anchors — global anchor + prompt -> Gemini edit
        # ══════════════════════════════════════════════════════════════
        l2_tasks: list[tuple[str, int, str, dict, str, str]] = []
        scene_stabs: list[dict] = []

        for si, scene in enumerate(scenes):
            scene_id = scene.get("scene_id", "")
            stab = scene.get("stability_keyframes", {})
            scene_stabs.append(stab)

            for entity_list in ("characters", "locations", "props"):
                for kf in stab.get(entity_list, []):
                    eid = kf.get("entity_id", "unknown")
                    sys_id = f"img_{eid}_{scene_id}"
                    prompt = kf.get("prompt_summary", "")
                    if not prompt:
                        continue
                    if eid not in global_image_bytes:
                        logger.warning(
                            "[L2] Global anchor still missing for %s; skipping %s",
                            eid, sys_id,
                        )
                        continue
                    l2_tasks.append((sys_id, si, eid, kf, eid, prompt + style_suffix))

        scene_image_bytes_list: list[dict[str, bytes]] = [{} for _ in scenes]
        completed_l2: set[str] = set()

        for attempt in range(1, MAX_LAYER_RETRIES + 1):
            pending = [t for t in l2_tasks if t[0] not in completed_l2]
            if not pending:
                break
            logger.info(
                "=== Layer 2: Generating %d scene anchors across %d scenes "
                "(attempt %d/%d) ===",
                len(pending), len(scenes), attempt, MAX_LAYER_RETRIES,
            )
            coros = [
                self._edit(
                    kf, global_image_bytes[ref_key], prompt, sys_id,
                    layer_tag="L2",
                )
                for sys_id, _, _, kf, ref_key, prompt in pending
            ]
            results = await asyncio.gather(*coros, return_exceptions=True)
            for task, result in zip(pending, results):
                sys_id, si, entity_key = task[0], task[1], task[2]
                if isinstance(result, Exception):
                    logger.error("[L2] Error for %s: %s", sys_id, result)
                elif isinstance(result, bytes):
                    scene_image_bytes_list[si][entity_key] = result
                    completed_l2.add(sys_id)
                else:
                    logger.warning("[L2] No image for %s (attempt %d)", sys_id, attempt)

        failed_l2 = [t[0] for t in l2_tasks if t[0] not in completed_l2]
        if failed_l2:
            raise RuntimeError(
                f"Layer 2: failed to generate scene anchors after "
                f"{MAX_LAYER_RETRIES} attempts: {failed_l2}"
            )
        logger.info(
            "Layer 2 complete: %d/%d scene anchors generated",
            len(completed_l2), len(l2_tasks),
        )

        # ══════════════════════════════════════════════════════════════
        # Layer 3: Shot Keyframes — scene anchor(s) + shot prompt ->
        #          Gemini edit
        # ══════════════════════════════════════════════════════════════
        l3_tasks: list[tuple[str, dict, list[bytes], str]] = []

        for si, scene in enumerate(scenes):
            scene_imgs = scene_image_bytes_list[si]
            stab = scene_stabs[si] if si < len(scene_stabs) else {}

            for shot in scene.get("shots", []):
                shot_id = shot.get("shot_id", "unknown")
                shot_ref_images = self._collect_shot_references(shot, scene_imgs, stab)
                kf_counter = 0
                for kf in shot.get("keyframes", []):
                    kf_counter += 1
                    sys_id = f"img_{shot_id}_kf_{kf_counter:02d}"
                    prompt = kf.get("prompt_summary", "")
                    if not prompt:
                        continue
                    if not shot_ref_images:
                        raise RuntimeError(
                            f"[L3] No Layer 2 scene anchor references for "
                            f"{shot_id}; cannot generate keyframe {sys_id}"
                        )
                    l3_tasks.append((sys_id, kf, shot_ref_images, prompt + style_suffix))

        completed_l3: set[str] = set()

        for attempt in range(1, MAX_LAYER_RETRIES + 1):
            pending = [t for t in l3_tasks if t[0] not in completed_l3]
            if not pending:
                break
            logger.info(
                "=== Layer 3: Generating %d shot keyframes (attempt %d/%d) ===",
                len(pending), attempt, MAX_LAYER_RETRIES,
            )
            coros = [
                self._edit(
                    kf, ref_imgs, prompt, sys_id,
                    layer_tag="L3",
                )
                for sys_id, kf, ref_imgs, prompt in pending
            ]
            results = await asyncio.gather(*coros, return_exceptions=True)
            for (sys_id, _, _, _), result in zip(pending, results):
                if isinstance(result, Exception):
                    logger.error("[L3] Error for %s: %s", sys_id, result)
                elif isinstance(result, bytes):
                    completed_l3.add(sys_id)
                else:
                    logger.warning("[L3] No image for %s (attempt %d)", sys_id, attempt)

        failed_l3 = [t[0] for t in l3_tasks if t[0] not in completed_l3]
        if failed_l3:
            raise RuntimeError(
                f"Layer 3: failed to generate shot keyframes after "
                f"{MAX_LAYER_RETRIES} attempts: {failed_l3}"
            )
        logger.info(
            "All three layers materialized for %s (L1=%d, L2=%d, L3=%d)",
            project_id,
            len(l1_tasks),
            len(l2_tasks),
            len(l3_tasks),
        )

        return self._pending

    # ------------------------------------------------------------------
    # Style consistency helper
    # ------------------------------------------------------------------

    @staticmethod
    def _build_style_suffix(assets: dict[str, Any] | None) -> str:
        """Extract style_lock from storyboard and build a prompt suffix."""
        if not assets:
            return ""
        sb = assets.get("storyboard", {})
        sb_content = sb.get("content", {})

        style_notes: list[str] = []
        must_avoid: list[str] = []
        for scene in sb_content.get("scenes", []):
            sl = scene.get("scene_consistency_pack", {}).get("style_lock", {})
            style_notes.extend(sl.get("global_style_notes", []))
            must_avoid.extend(sl.get("must_avoid", []))

        style_notes = list(dict.fromkeys(style_notes))
        must_avoid = list(dict.fromkeys(must_avoid))

        if not style_notes and not must_avoid:
            return ""

        parts: list[str] = []
        if style_notes:
            parts.append("Visual style: " + "; ".join(style_notes) + ".")
        if must_avoid:
            parts.append("Do NOT use: " + "; ".join(must_avoid) + ".")
        return "\n" + " ".join(parts)

    # ------------------------------------------------------------------
    # Layer helpers (pure generators — no file I/O)
    # ------------------------------------------------------------------

    async def _generate(
        self,
        kf_dict: dict[str, Any],
        prompt: str,
        sys_id: str,
        *,
        layer_tag: str = "L1",
    ) -> bytes | None:
        """Generate image from text only (Gemini), return bytes."""
        img_asset = kf_dict.get("image_asset", {})
        img_asset["asset_id"] = sys_id
        if not prompt:
            return None
        try:
            img_bytes = await self.image_svc.generate_image(prompt)
            ext = img_asset.get("format", "png")
            self._pending.append(MediaAsset(
                sys_id=sys_id, data=img_bytes, extension=ext,
                uri_holder=img_asset,
            ))
            logger.info("[%s] Image generated: %s", layer_tag, sys_id)
            return img_bytes
        except Exception as exc:
            logger.error("[%s] Image generation failed for %s: %s", layer_tag, sys_id, exc)
            return None

    async def _edit(
        self,
        kf_dict: dict[str, Any],
        reference: bytes | list[bytes],
        prompt: str,
        sys_id: str,
        *,
        layer_tag: str = "L2/3",
    ) -> bytes | None:
        """Edit reference image(s) with prompt (Gemini), return bytes."""
        img_asset = kf_dict.get("image_asset", {})
        img_asset["asset_id"] = sys_id
        if not prompt:
            return None
        try:
            img_bytes = await self.image_svc.edit_image(reference, prompt)
            ext = img_asset.get("format", "png")
            self._pending.append(MediaAsset(
                sys_id=sys_id, data=img_bytes, extension=ext,
                uri_holder=img_asset,
            ))
            logger.info("[%s] Edit generated: %s", layer_tag, sys_id)
            return img_bytes
        except Exception as exc:
            logger.error("[%s] Edit failed for %s: %s", layer_tag, sys_id, exc)
            return None

    @staticmethod
    def _collect_shot_references(
        shot: dict[str, Any],
        scene_images: dict[str, bytes],
        stab: dict[str, Any],
    ) -> list[bytes]:
        """Collect scene-anchor images relevant to a shot for Layer 3 edit."""
        refs: list[bytes] = []
        seen: set[str] = set()

        all_char_ids: list[str] = []
        all_prop_ids: list[str] = []
        for kf in shot.get("keyframes", []):
            constraints = kf.get("constraints_applied", {})
            all_char_ids.extend(constraints.get("characters_in_frame", []))
            all_prop_ids.extend(constraints.get("props_in_frame", []))

        for char_id in all_char_ids:
            if char_id in scene_images and char_id not in seen:
                refs.append(scene_images[char_id])
                seen.add(char_id)

        for loc_kf in stab.get("locations", []):
            loc_id = loc_kf.get("entity_id", "")
            if loc_id in scene_images and loc_id not in seen:
                refs.append(scene_images[loc_id])
                seen.add(loc_id)
                break

        for prop_id in all_prop_ids:
            if prop_id in scene_images and prop_id not in seen:
                refs.append(scene_images[prop_id])
                seen.add(prop_id)

        return refs

    def _inject_reference_images(
        self,
        ref_images: list[dict[str, Any]],
        global_anchors: dict[str, Any],
        global_image_bytes: dict[str, bytes],
        *,
        assets: dict[str, Any] | None = None,
    ) -> None:
        """Match user-provided reference images to global anchor entities."""
        blueprint_text: dict[str, str] = {}
        blueprint = (assets or {}).get("story_blueprint", {})
        bp_content = blueprint.get("content", {}) if isinstance(blueprint, dict) else {}

        for char in bp_content.get("cast", []):
            cid = char.get("character_id", "")
            if cid:
                blueprint_text[cid] = " ".join([
                    char.get("name", ""),
                    char.get("role", ""),
                    char.get("profile", ""),
                    char.get("motivation", ""),
                    char.get("flaw", ""),
                ]).lower()

        for loc in bp_content.get("locations", []):
            lid = loc.get("location_id", "")
            if lid:
                blueprint_text[lid] = " ".join([
                    loc.get("name", ""),
                    loc.get("description", ""),
                ]).lower()

        entity_lookup: dict[str, tuple[dict[str, Any], str]] = {}
        for entity_list in ("characters", "locations", "props"):
            for kf in global_anchors.get(entity_list, []):
                eid = kf.get("entity_id", "")
                if eid:
                    entity_lookup[eid] = (kf, entity_list)

        _TYPE_TO_CATEGORY = {
            "character": "characters",
            "location": "locations",
            "prop": "props",
        }

        matched_count = 0
        already_matched_eids: set[str] = set()

        for ref in ref_images:
            raw_label = ref.get("label", "")
            img_bytes: bytes = ref.get("image_bytes", b"")
            entity_type: str = ref.get("entity_type", "")
            if not raw_label or not img_bytes:
                continue

            label = raw_label.replace("_", " ").strip().lower()
            target_category = _TYPE_TO_CATEGORY.get(entity_type, "")

            matched_eid: str | None = None
            for eid, (kf, cat) in entity_lookup.items():
                if eid in already_matched_eids:
                    continue
                if target_category and cat != target_category:
                    continue

                searchable = " ".join([
                    eid.lower(),
                    kf.get("prompt_summary", "").lower(),
                    kf.get("name", "").lower(),
                    kf.get("description", "").lower(),
                    blueprint_text.get(eid, ""),
                ])
                if label in searchable:
                    matched_eid = eid
                    logger.info(
                        "[L0-Ref] Keyword matched label '%s' -> %s",
                        label, eid,
                    )
                    break

            if matched_eid is None and target_category:
                candidates = [
                    eid for eid, (_, cat) in entity_lookup.items()
                    if cat == target_category and eid not in already_matched_eids
                ]
                if len(candidates) == 1:
                    matched_eid = candidates[0]
                    logger.info(
                        "[L0-Ref] Singleton fallback: label '%s' -> %s "
                        "(only %s in %s)",
                        label, matched_eid, matched_eid, target_category,
                    )

            if matched_eid is None:
                logger.warning(
                    "[L0-Ref] No global anchor match for reference image "
                    "label '%s' (entity_type=%s) -- will be ignored",
                    raw_label, entity_type,
                )
                continue

            if matched_eid in global_image_bytes:
                logger.info(
                    "[L0-Ref] Entity %s already has an image, skipping "
                    "reference '%s'",
                    matched_eid, raw_label,
                )
                continue

            sys_id = f"img_{matched_eid}_global"
            kf_dict = entity_lookup[matched_eid][0]
            img_asset = kf_dict.get("image_asset", {})
            img_asset["asset_id"] = sys_id

            ext = img_asset.get("format", "png")
            self._pending.append(MediaAsset(
                sys_id=sys_id, data=img_bytes, extension=ext,
                uri_holder=img_asset,
            ))
            global_image_bytes[matched_eid] = img_bytes
            already_matched_eids.add(matched_eid)
            matched_count += 1
            logger.info(
                "[L0-Ref] Injected reference image '%s' -> entity %s",
                raw_label, matched_eid,
            )

        logger.info(
            "[L0-Ref] Reference image injection complete: %d/%d matched",
            matched_count, len(ref_images),
        )
