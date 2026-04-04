"""Keyframe image materializer — global + scene + shot anchor chain.

  Layer 1 — Global anchors: text -> ``generate_image()`` (characters, locations, props*)
  Layer 2 — Scene anchors: default global ref + prompt -> ``edit_image()``; or ``t2i`` mode.
  Layer 3 — One still per shot: edit from scene **location** L2 (or text-only fallback) so the
            PNG matches the shot ``prompt_summary``; VideoAgent consumes **only** this URI.

*Props are included when KeyFrameAgent emitted prop anchors (``FW_ENABLE_PROP_KEYFRAMES``).

Text descriptions (prompt_summary) are always included.  **L2/L3 edit** paths
use the same suffix: filtered ``must_avoid`` only (no ``Visual style:`` block),
because the reference image already carries global look.  **L1** and **L3 t2i**
(fallback when no location L2 ref) still get the full ``Visual style`` + ``must_avoid``
suffix.  Screenplay ``style_lock`` lines are deduped across scenes by normalized
text (whitespace + casefold) to reduce repeated suffix bulk without slicing strings.

This materializer calls ImageService to produce image bytes and returns
``list[MediaAsset]`` for Assistant persistence. It does not perform local
filesystem persistence by itself.
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
from typing import Any

from ..contracts.input_bundle_v2 import InputBundleV2
from ..descriptor import BaseMaterializer, MediaAsset
from inference.generation.image_generators.service import ImageService

logger = logging.getLogger(__name__)

# Prepended to L2/L3 **edit** prompts (reference image already encodes global style).
_L2_EDIT_INSTRUCTION_PREFIX = (
    "Edit the attached reference to match the text below; keep subject identity "
    "recognizable; apply lighting, framing, pose, and environment as described.\n\n"
)


def _keep_must_avoid_for_still_image(line: str) -> bool:
    """Drop style_lock must_avoid lines that target film/audio editing, not a single frame."""
    s = line.strip()
    if not s:
        return False
    low = s.lower()
    if re.search(
        r"\b(loud|noise|noises|audio|sound|sounds)\b",
        low,
    ):
        return False
    if re.search(
        r"(choppy|jarring|abrupt).{0,80}\bcuts?\b|\bcuts?.{0,80}(choppy|jarring|obscure)",
        low,
    ):
        return False
    if re.search(r"\b(montage|transitions?|pacing)\b", low):
        return False
    if re.search(r"\b(subtitle|subtitles|caption|captions)\b", low):
        return False
    return True


def _filter_still_image_must_avoid(items: list[str]) -> list[str]:
    out: list[str] = []
    for raw in items:
        if isinstance(raw, str) and _keep_must_avoid_for_still_image(raw):
            out.append(raw.strip())
    return list(dict.fromkeys(out))


class KeyframeMaterializer(BaseMaterializer):
    @staticmethod
    def _resolved_inputs(input_bundle_v2: InputBundleV2 | None) -> dict[str, Any]:
        if not input_bundle_v2:
            return {}
        ctx = getattr(input_bundle_v2, "context", {})
        resolved = ctx.get("resolved_inputs") if isinstance(ctx, dict) else None
        return resolved if isinstance(resolved, dict) else {}

    """L1/L2/L3 keyframe image materializer.

    Constructor:
        image_service: ``ImageService`` instance for Gemini image gen/edit.
    """

    def __init__(self, image_service: ImageService) -> None:
        self.image_svc = image_service

    @staticmethod
    def _l2_mode() -> str:
        """``edit`` (default): image+prompt edit. ``t2i``: scene anchors from text only (no global ref)."""
        v = os.getenv("FW_KEYFRAME_L2_MODE", "edit").strip().lower()
        if v in {"t2i", "generate", "text2image", "txt2img"}:
            return "t2i"
        return "edit"

    @staticmethod
    def naming_spec_v2() -> dict[str, Any]:
        return {
            "agent_id": "KeyFrameAgent",
            "spec_version": "1.0",
            "rules": [
                {
                    "artifact_family": "keyframe_image",
                    "semantic_meaning": "generated keyframe images for global/scene/shot anchors",
                    "recommended_name_pattern": "img_{entity_or_shot_id}_{scope_or_seq}.png",
                    "id_source": "screenplay/keyframe IDs",
                    "ordering_rules": "for shot keyframes, preserve screenplay shot order",
                    "examples": ["img_char_001_global.png", "img_loc_001_sc_001.png"],
                    "rename_hints": {"stable_parts": "img prefix and id tokens", "mutable_parts": "suffix formatting"},
                }
            ],
        }

    # ------------------------------------------------------------------
    # Main entry point (called by Assistant)
    # ------------------------------------------------------------------

    async def materialize(
        self,
        task_id: str,
        asset_dict: dict[str, Any],
        input_bundle_v2: InputBundleV2,
    ) -> list[MediaAsset]:
        """Generate L1 global, L2 scene, and L3 per-shot stills.

        Parallel ``asyncio.gather`` within each retry round. L2 depends on L1;
        L3 depends on L2 location anchors for the default **edit-from-scene-loc**
        path (falls back to text-only generation if no location ref).

        Optional ``reference_images`` in resolved inputs inject L0 global anchors.

        Naming:
          L1: ``img_{entity_id}_global``
          L2: ``img_{entity_id}_{scene_id}``
          L3: ``img_{shot_id}_{keyframe_id}`` (one row per shot; first keyframe only)

        Returns:
            ``MediaAsset`` list for Assistant persistence.
        """
        self._pending: list[MediaAsset] = []

        content = asset_dict.get("content", {})
        scenes = content.get("scenes", [])

        style_notes, must_avoid = self._extract_style_lock_lists(input_bundle_v2)
        must_avoid = _filter_still_image_must_avoid(must_avoid)
        l1_style_suffix = self._compose_style_suffix(style_notes, must_avoid, include_visual_style=True)
        l2_edit_suffix = self._compose_style_suffix(style_notes, must_avoid, include_visual_style=False)
        l2_t2i_suffix = l1_style_suffix

        l2_mode = self._l2_mode()
        logger.info("Keyframe L2 scene-anchor mode: %s", l2_mode)

        MAX_LAYER_RETRIES = 10

        # ══════════════════════════════════════════════════════════════
        # Layer 0: Inject user-provided reference images as global anchors
        # ══════════════════════════════════════════════════════════════
        global_anchors = content.get("global_anchors", {})
        global_image_bytes: dict[str, bytes] = {}

        ref_images: list[dict[str, Any]] = (
            self._resolved_inputs(input_bundle_v2).get("reference_images", [])
            if input_bundle_v2
            else []
        )
        if ref_images:
            self._inject_reference_images(
                ref_images, global_anchors, global_image_bytes,
                input_bundle_v2=input_bundle_v2,
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
                        (eid, kf, prompt + l1_style_suffix, f"img_{eid}_global")
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
                self._generate(kf, prompt, sys_id, layer_tag="L1")
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
                            (eid, kf, prompt + l1_style_suffix, f"img_{eid}_global")
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
                    self._generate(kf, prompt, sys_id, layer_tag="L1.5")
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
        # Layer 2: Scene anchors — edit (default) or text-only (FW_KEYFRAME_L2_MODE=t2i)
        # ══════════════════════════════════════════════════════════════
        l2_tasks: list[tuple[str, int, str, dict, str, str]] = []

        for si, scene in enumerate(scenes):
            scene_id = scene.get("scene_id", "")
            stab = scene.get("stability_keyframes", {})

            for entity_list in ("characters", "locations", "props"):
                for kf in stab.get(entity_list, []):
                    eid = kf.get("entity_id", "unknown")
                    sys_id = f"img_{eid}_{scene_id}"
                    raw_summary = kf.get("prompt_summary", "")
                    if not raw_summary:
                        continue
                    if l2_mode == "edit":
                        if eid not in global_image_bytes:
                            logger.warning(
                                "[L2] Global anchor still missing for %s; skipping %s",
                                eid, sys_id,
                            )
                            continue
                        composed = (
                            _L2_EDIT_INSTRUCTION_PREFIX
                            + raw_summary
                            + l2_edit_suffix
                        )
                    else:
                        composed = raw_summary + l2_t2i_suffix
                    l2_tasks.append((sys_id, si, eid, kf, eid, composed))

        completed_l2: set[str] = set()
        l2_bytes_by_sys_id: dict[str, bytes] = {}

        for attempt in range(1, MAX_LAYER_RETRIES + 1):
            pending = [t for t in l2_tasks if t[0] not in completed_l2]
            if not pending:
                break
            logger.info(
                "=== Layer 2: Generating %d scene anchors across %d scenes "
                "(attempt %d/%d, mode=%s) ===",
                len(pending), len(scenes), attempt, MAX_LAYER_RETRIES, l2_mode,
            )
            if l2_mode == "t2i":
                coros = [
                    self._generate(kf, prompt, sys_id, layer_tag="L2-t2i")
                    for sys_id, _, _, kf, _, prompt in pending
                ]
            else:
                coros = [
                    self._edit(
                        kf,
                        global_image_bytes[ref_key],
                        prompt,
                        sys_id,
                        layer_tag="L2",
                    )
                    for sys_id, _, _, kf, ref_key, prompt in pending
                ]
            results = await asyncio.gather(*coros, return_exceptions=True)
            for task, result in zip(pending, results):
                sys_id, _, _ = task[0], task[1], task[2]
                if isinstance(result, Exception):
                    logger.error("[L2] Error for %s: %s", sys_id, result)
                elif isinstance(result, bytes):
                    completed_l2.add(sys_id)
                    l2_bytes_by_sys_id[sys_id] = result
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
        # Layer 3: one still per shot (edit from scene location L2, else t2i)
        # ══════════════════════════════════════════════════════════════
        l3_tasks: list[tuple[str, dict[str, Any], str, bytes | None, bool]] = []
        for scene in scenes:
            scene_id = str(scene.get("scene_id", "") or "").strip()
            stab = scene.get("stability_keyframes", {}) or {}
            loc_id = ""
            for lk in stab.get("locations") or []:
                if not isinstance(lk, dict):
                    continue
                loc_id = str(lk.get("entity_id", "") or "").strip()
                if loc_id:
                    break
            loc_sys = f"img_{loc_id}_{scene_id}" if loc_id and scene_id else ""
            ref_loc = l2_bytes_by_sys_id.get(loc_sys) if loc_sys else None
            if ref_loc is None and loc_id:
                ref_loc = global_image_bytes.get(loc_id)

            for shot in scene.get("shots") or []:
                if not isinstance(shot, dict):
                    continue
                shot_id = str(shot.get("shot_id", "") or "").strip()
                kfs = shot.get("keyframes") or []
                if not kfs:
                    continue
                kf0 = kfs[0]
                if not isinstance(kf0, dict):
                    continue
                kid = str(kf0.get("keyframe_id", "") or "kf_001").strip() or "kf_001"
                sys_id = f"img_{shot_id}_{kid}"
                raw_summary = str(kf0.get("prompt_summary", "") or "").strip()
                if not raw_summary:
                    logger.warning("[L3] skip shot %s: empty prompt_summary", shot_id)
                    continue
                if ref_loc is not None:
                    composed = (
                        _L2_EDIT_INSTRUCTION_PREFIX + raw_summary + l2_edit_suffix
                    )
                    l3_tasks.append((sys_id, kf0, composed, ref_loc, True))
                else:
                    l3_tasks.append(
                        (
                            sys_id,
                            kf0,
                            raw_summary + l1_style_suffix,
                            None,
                            False,
                        )
                    )

        completed_l3: set[str] = set()
        for attempt in range(1, MAX_LAYER_RETRIES + 1):
            pending_l3 = [t for t in l3_tasks if t[0] not in completed_l3]
            if not pending_l3:
                break
            logger.info(
                "=== Layer 3: %d shot stills (attempt %d/%d) ===",
                len(pending_l3),
                attempt,
                MAX_LAYER_RETRIES,
            )
            coros_l3: list[Any] = []
            for sys_id, kf_dict, prompt, ref_b, use_edit in pending_l3:
                if use_edit and ref_b is not None:
                    coros_l3.append(
                        self._edit(
                            kf_dict,
                            ref_b,
                            prompt,
                            sys_id,
                            layer_tag="L3",
                        )
                    )
                else:
                    coros_l3.append(
                        self._generate(
                            kf_dict,
                            prompt,
                            sys_id,
                            layer_tag="L3-t2i",
                        )
                    )
            results_l3 = await asyncio.gather(*coros_l3, return_exceptions=True)
            for task_t, result in zip(pending_l3, results_l3):
                sid = task_t[0]
                if isinstance(result, Exception):
                    logger.error("[L3] Error for %s: %s", sid, result)
                elif isinstance(result, bytes):
                    completed_l3.add(sid)
                else:
                    logger.warning("[L3] No image for %s (attempt %d)", sid, attempt)

        failed_l3 = [t[0] for t in l3_tasks if t[0] not in completed_l3]
        if failed_l3:
            raise RuntimeError(
                f"Layer 3: failed shot keyframe images after "
                f"{MAX_LAYER_RETRIES} attempts: {failed_l3}"
            )
        logger.info(
            "Layer 3 complete: %d/%d shot stills generated",
            len(completed_l3),
            len(l3_tasks),
        )

        logger.info(
            "Keyframe materialize complete for %s (L1=%d, L2=%d, L3=%d)",
            task_id,
            len(l1_tasks),
            len(l2_tasks),
            len(l3_tasks),
        )

        return self._pending

    # ------------------------------------------------------------------
    # Style consistency helper
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_style_lock_lists(
        input_bundle_v2: InputBundleV2 | None,
    ) -> tuple[list[str], list[str]]:
        """Return deduped ``global_style_notes`` and raw ``must_avoid`` from screenplay."""
        if not input_bundle_v2:
            return [], []
        sb = KeyframeMaterializer._resolved_inputs(input_bundle_v2).get("screenplay", {})
        sb_content = sb.get("content", {}) if isinstance(sb, dict) else {}

        style_notes: list[str] = []
        must_avoid: list[str] = []
        for scene in sb_content.get("scenes", []):
            if not isinstance(scene, dict):
                continue
            sl = scene.get("scene_consistency_pack", {}).get("style_lock", {})
            if not isinstance(sl, dict):
                continue
            for x in sl.get("global_style_notes", []) or []:
                if isinstance(x, str) and x.strip():
                    style_notes.append(x.strip())
            for x in sl.get("must_avoid", []) or []:
                if isinstance(x, str) and x.strip():
                    must_avoid.append(x.strip())

        return (
            KeyframeMaterializer._dedupe_preserve_order_normalized(style_notes),
            KeyframeMaterializer._dedupe_preserve_order_normalized(must_avoid),
        )

    @staticmethod
    def _dedupe_preserve_order_normalized(strings: list[str]) -> list[str]:
        """Drop exact duplicates after whitespace-normalization and casefold.

        Merges repeated ``style_lock`` lines across many scenes when producers
        paste the same prose with different spacing/casing — no substring slicing.
        """
        seen: set[str] = set()
        out: list[str] = []
        for raw in strings:
            if not isinstance(raw, str):
                continue
            s = raw.strip()
            if not s:
                continue
            key = " ".join(s.split()).casefold()
            if key in seen:
                continue
            seen.add(key)
            out.append(s)
        return out

    @staticmethod
    def _compose_style_suffix(
        style_notes: list[str],
        must_avoid: list[str],
        *,
        include_visual_style: bool,
    ) -> str:
        """Build trailing prompt chunk. L2 edit omits ``Visual style:`` to avoid duplicating summaries."""
        parts: list[str] = []
        if include_visual_style and style_notes:
            parts.append("Visual style: " + "; ".join(style_notes) + ".")
        if must_avoid:
            parts.append("Do NOT use: " + "; ".join(must_avoid) + ".")
        if not parts:
            return ""
        return "\n" + " ".join(parts)

    # ------------------------------------------------------------------
    # Layer helpers (generation only)
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
        kf_dict["image_generation_prompt"] = prompt
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
        layer_tag: str = "L2",
    ) -> bytes | None:
        """Edit reference image(s) with prompt (Gemini), return bytes."""
        img_asset = kf_dict.get("image_asset", {})
        img_asset["asset_id"] = sys_id
        if not prompt:
            return None
        kf_dict["image_generation_prompt"] = prompt
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

    def _inject_reference_images(
        self,
        ref_images: list[dict[str, Any]],
        global_anchors: dict[str, Any],
        global_image_bytes: dict[str, bytes],
        *,
        input_bundle_v2: InputBundleV2 | None = None,
    ) -> None:
        """Match user-provided reference images to global anchor entities."""
        blueprint_text: dict[str, str] = {}
        blueprint = KeyframeMaterializer._resolved_inputs(input_bundle_v2).get("story_blueprint", {})
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
        for entity_list in ("characters", "locations"):
            for kf in global_anchors.get(entity_list, []):
                eid = kf.get("entity_id", "")
                if eid:
                    entity_lookup[eid] = (kf, entity_list)

        _TYPE_TO_CATEGORY = {
            "character": "characters",
            "location": "locations",
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
            kf_dict["image_generation_prompt"] = (
                "[user_reference_image] Injected from resolved_inputs.reference_images; "
                "no text-to-image API call."
            )

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

