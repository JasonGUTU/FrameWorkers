"""Keyframe image materializer — global + scene + shot anchor chain.

  Layer 1 — Global anchors: text -> ``generate_image()`` (characters, locations, props*).
            **Pre-check**: if the agent's LLM output already wrote a real
            file path into an entity's ``image_asset.uri`` field (because a
            user-uploaded reference was selected for that entity), we skip
            t2i for that entity and read the file bytes directly.
  Layer 2 — Scene anchors: default global ref + prompt -> ``edit_image()``; or ``t2i`` mode.
  Layer 3 — One still per shot: edit from scene **location** L2 (or text-only fallback) so the
            PNG matches the shot ``prompt_summary``; VideoAgent consumes **only** this URI.

*Props are included when KeyFrameAgent emitted prop anchors (``FW_ENABLE_PROP_PIPELINE``).

Responsibility boundary
-----------------------
The materializer owns three things:

1. **Layer orchestration** — L1→L2→L3 chaining, retries, backfill,
   reference-image pre-fill, edit vs t2i mode decisions.
2. **Semantic extraction** — pulling ``prompt_summary`` from each
   anchor dict, extracting ``style_lock`` lists from the screenplay,
   and filtering ``must_avoid`` rules down to what applies to still
   images (dropping film/audio-level directives).
3. **Packaging** — handing each per-image request to ``ImageService``
   as a language-neutral ``ImageSemanticContext``.

It does **not** own any model-specific prompt templating — no "Edit the
attached reference..." instruction prefix, no ``Visual style:`` /
``Do NOT use:`` formatting. All of that lives in ``ImageService``.
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
from typing import Any

from typing import TYPE_CHECKING

from ..descriptor import BaseMaterializer, MediaAsset
from inference.generation.image_generators.service import ImageService
from inference.generation.image_generators.types import ImageSemanticContext

if TYPE_CHECKING:
    from ..base_agent import MaterializeContext
    from .schema import KeyFrameAgentInput

logger = logging.getLogger(__name__)


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

    # ------------------------------------------------------------------
    # Main entry point (called by Assistant)
    # ------------------------------------------------------------------

    async def materialize(
        self,
        ctx: "MaterializeContext",
        asset_dict: dict[str, Any],
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
        # Stash ctx so the per-image _generate / _edit helpers can call
        # ctx.report_failure() without getting it threaded through every
        # callsite. Reset on each materialize() call.
        self._ctx: "MaterializeContext" = ctx

        # The materializer reads its input data from ctx.typed_input only.
        # No second resolved_artifacts channel — every required field
        # must already be expressed on KeyFrameAgentInput.
        typed_input = ctx.typed_input  # type: KeyFrameAgentInput
        task_id = ctx.task_id

        content = asset_dict.get("content", {})
        scenes = content.get("scenes", [])

        style_notes, must_avoid = self._extract_style_lock_lists(typed_input)
        must_avoid = _filter_still_image_must_avoid(must_avoid)

        def _make_ctx(prompt_summary: str) -> ImageSemanticContext:
            """Per-call helper: build a semantic context for one image.

            ``style_notes`` / ``must_avoid`` are shared across all images
            in this materialize() run; the service decides which subset
            to render depending on whether it's a generate vs edit call.
            """
            return ImageSemanticContext(
                prompt_summary=prompt_summary,
                style_notes=style_notes,
                must_avoid=must_avoid,
            )

        l2_mode = self._l2_mode()
        logger.info("Keyframe L2 scene-anchor mode: %s", l2_mode)

        MAX_LAYER_RETRIES = 10

        global_anchors = content.get("global_anchors", {})
        global_image_bytes: dict[str, bytes] = {}

        # ══════════════════════════════════════════════════════════════
        # Layer 1 pre-check: pick up LLM-assigned reference image paths
        # ══════════════════════════════════════════════════════════════
        # The KeyFrameAgent LLM may have written a real file path into an
        # entity's image_asset.uri (because [character_reference] /
        # [location_reference] / [style_reference] entries were resolved
        # for that entity).  When we see one, skip t2i and read the bytes
        # directly — no fuzzy matching, no entity inference, the LLM
        # already decided.
        for entity_list_name in ("characters", "locations", "props"):
            for kf in global_anchors.get(entity_list_name, []) or []:
                if not isinstance(kf, dict):
                    continue
                eid = str(kf.get("entity_id", "") or "").strip()
                img_asset = kf.get("image_asset", {})
                if not isinstance(img_asset, dict):
                    continue
                uri = str(img_asset.get("uri", "") or "").strip()
                if not eid or not uri:
                    continue
                if uri in {"placeholder", ""} or uri.startswith("error:"):
                    continue
                if not os.path.isfile(uri):
                    continue
                try:
                    with open(uri, "rb") as fh:
                        ref_bytes = fh.read()
                except OSError as exc:
                    logger.warning(
                        "[L1-prefill] Failed to read reference image %s for %s: %s",
                        uri, eid, exc,
                    )
                    continue
                global_image_bytes[eid] = ref_bytes
                ext = img_asset.get("format", "png")
                self._pending.append(MediaAsset(
                    sys_id=f"img_{eid}_global",
                    data=ref_bytes,
                    extension=ext,
                    uri_holder=img_asset,
                ))
                logger.info(
                    "[L1-prefill] Used LLM-assigned reference image for %s: %s",
                    eid, uri,
                )

        # ══════════════════════════════════════════════════════════════
        # Layer 1: Global Anchors — text -> Gemini generate, retry
        # ══════════════════════════════════════════════════════════════

        l1_tasks: list[tuple[str, dict, ImageSemanticContext, str]] = []

        for entity_list in ("characters", "locations", "props"):
            for kf in global_anchors.get(entity_list, []):
                eid = kf.get("entity_id", "unknown")
                prompt_summary = kf.get("prompt_summary", "")
                if prompt_summary:
                    l1_tasks.append(
                        (eid, kf, _make_ctx(prompt_summary), f"img_{eid}_global")
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
                self._generate(kf, sctx, sys_id, layer_tag="L1")
                for _, kf, sctx, sys_id in pending
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
        backfill_tasks: list[tuple[str, dict, ImageSemanticContext, str]] = []
        for scene in scenes:
            stab = scene.get("stability_keyframes", {})
            for entity_list in ("characters", "locations", "props"):
                for kf in stab.get(entity_list, []):
                    eid = kf.get("entity_id", "unknown")
                    prompt_summary = kf.get("prompt_summary", "")
                    if prompt_summary and eid not in global_image_bytes:
                        backfill_tasks.append(
                            (eid, kf, _make_ctx(prompt_summary), f"img_{eid}_global")
                        )
        seen_backfill: set[str] = set()
        unique_backfill: list[tuple[str, dict, ImageSemanticContext, str]] = []
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
                    self._generate(kf, sctx, sys_id, layer_tag="L1.5")
                    for _, kf, sctx, sys_id in pending_bf
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
        l2_tasks: list[tuple[str, int, str, dict, str, ImageSemanticContext]] = []

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
                    l2_tasks.append((sys_id, si, eid, kf, eid, _make_ctx(raw_summary)))

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
                    self._generate(kf, sctx, sys_id, layer_tag="L2-t2i")
                    for sys_id, _, _, kf, _, sctx in pending
                ]
            else:
                coros = [
                    self._edit(
                        kf,
                        global_image_bytes[ref_key],
                        sctx,
                        sys_id,
                        layer_tag="L2",
                    )
                    for sys_id, _, _, kf, ref_key, sctx in pending
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
        l3_tasks: list[
            tuple[str, dict[str, Any], ImageSemanticContext, bytes | None, bool]
        ] = []
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
                sctx = _make_ctx(raw_summary)
                use_edit = ref_loc is not None
                l3_tasks.append((sys_id, kf0, sctx, ref_loc, use_edit))

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
            for sys_id, kf_dict, sctx, ref_b, use_edit in pending_l3:
                if use_edit and ref_b is not None:
                    coros_l3.append(
                        self._edit(
                            kf_dict,
                            ref_b,
                            sctx,
                            sys_id,
                            layer_tag="L3",
                        )
                    )
                else:
                    coros_l3.append(
                        self._generate(
                            kf_dict,
                            sctx,
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
        typed_input: "KeyFrameAgentInput",
    ) -> tuple[list[str], list[str]]:
        """Return deduped ``global_style_notes`` and raw ``must_avoid`` from screenplay."""
        sp_payload = getattr(typed_input, "screenplay", {}) or {}
        if not isinstance(sp_payload, dict):
            return [], []
        sb_content = sp_payload.get("content", {}) if isinstance(sp_payload, dict) else {}

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

    # ------------------------------------------------------------------
    # Layer helpers (generation only)
    # ------------------------------------------------------------------

    async def _generate(
        self,
        kf_dict: dict[str, Any],
        semantic_ctx: ImageSemanticContext,
        sys_id: str,
        *,
        layer_tag: str = "L1",
    ) -> bytes | None:
        """Generate image from text only, return bytes.

        The service composes the actual text prompt from ``semantic_ctx``
        and stores it on ``kf_dict`` as ``image_generation_prompt`` for
        downstream audit.
        """
        img_asset = kf_dict.get("image_asset", {})
        img_asset["asset_id"] = sys_id
        if not semantic_ctx.prompt_summary:
            return None
        try:
            result = await self.image_svc.generate_image(semantic_context=semantic_ctx)
            kf_dict["image_generation_prompt"] = result.resolved_prompt
            ext = img_asset.get("format", "png")
            self._pending.append(MediaAsset(
                sys_id=sys_id, data=result.bytes, extension=ext,
                uri_holder=img_asset,
            ))
            logger.info("[%s] Image generated: %s", layer_tag, sys_id)
            return result.bytes
        except Exception as exc:
            logger.error("[%s] Image generation failed for %s: %s", layer_tag, sys_id, exc)
            mctx = getattr(self, "_ctx", None)
            if mctx is not None and mctx.report_failure is not None:
                mctx.report_failure(
                    kind=f"keyframe_image_gen_{layer_tag.lower()}",
                    sys_id=sys_id,
                    error=f"{type(exc).__name__}: {exc}",
                )
            return None

    async def _edit(
        self,
        kf_dict: dict[str, Any],
        reference: bytes | list[bytes],
        semantic_ctx: ImageSemanticContext,
        sys_id: str,
        *,
        layer_tag: str = "L2",
    ) -> bytes | None:
        """Edit reference image(s) with a semantic context, return bytes.

        Same audit semantics as ``_generate``: ``image_generation_prompt``
        on ``kf_dict`` reflects what the service actually sent.
        """
        img_asset = kf_dict.get("image_asset", {})
        img_asset["asset_id"] = sys_id
        if not semantic_ctx.prompt_summary:
            return None
        try:
            result = await self.image_svc.edit_image(
                reference, semantic_context=semantic_ctx
            )
            kf_dict["image_generation_prompt"] = result.resolved_prompt
            ext = img_asset.get("format", "png")
            self._pending.append(MediaAsset(
                sys_id=sys_id, data=result.bytes, extension=ext,
                uri_holder=img_asset,
            ))
            logger.info("[%s] Edit generated: %s", layer_tag, sys_id)
            return result.bytes
        except Exception as exc:
            logger.error("[%s] Edit failed for %s: %s", layer_tag, sys_id, exc)
            mctx = getattr(self, "_ctx", None)
            if mctx is not None and mctx.report_failure is not None:
                mctx.report_failure(
                    kind=f"keyframe_image_edit_{layer_tag.lower()}",
                    sys_id=sys_id,
                    error=f"{type(exc).__name__}: {exc}",
                )
            return None
