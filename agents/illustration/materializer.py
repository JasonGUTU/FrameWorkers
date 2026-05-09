"""Illustration materializer — character-anchored multi-ref image generation.

Strategy: two-stage anchor + multi-reference edit.

  Stage 1 (Character anchors)
    For each entry in ``content.character_anchors``, t2i a portrait
    still using the identity-reference scaffold (KeyFrame-style: neutral
    studio backdrop, isolated subject) so the result is a clean i2i
    reference for downstream edits. Anchor bytes are kept in memory
    only — not registered as workspace artifacts.

  Stage 2 (Per-segment illustrations)
    Segment 1 → ``generate_image(prompt = overall_style + image_prompt)``.
        This image seeds the cross-segment art style (palette, brush
        stroke, mood, lighting) and IS the first page of the picture
        book.
    Segments 2..N → ``edit_image(reference_images=[seg1, *char_anchors],
                                  ref_kind="picture_book", ref_manifest=...)``
        in PARALLEL. Each segment attaches:
          - Reference 1 = segment 1 (STYLE anchor — palette / brush /
            mood / lighting; subjects in seg 1 are NOT carried over)
          - References 2..K = the portrait anchors of each character_id
            in this segment's ``characters_in_segment`` (CHARACTER
            anchors — face / hair / costume preserved)
        The MULTI-SUBJECT scaffold in ``ImageService`` already encodes
        the per-kind preservation rules; this materializer only wires
        up the bytes + manifest.

This trades a small amount of extra t2i calls (one per recurring
character) for picture-book–quality cross-segment character
consistency. Without anchors, the image model re-invents every
recurring character's face / hair / costume per segment, which
breaks the central illusion that the story is about ONE specific
protagonist.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, TYPE_CHECKING

from ..base_agent import DEFAULT_ASSET_RETRIES
from ..descriptor import BaseMaterializer, MediaAsset
from inference.generation.image_generators.service import ImageService
from inference.generation.image_generators.types import ImageSemanticContext

if TYPE_CHECKING:
    from ..base_agent import MaterializeContext

logger = logging.getLogger(__name__)


def _compose_anchor_generate_prompt(overall_style: str, image_prompt: str) -> str:
    """Text-to-image prompt for segment 1 (the style-anchor illustration).

    Style anchor lives up-front so the model weights it heavily when
    seeding the cross-segment visual identity.
    """
    style = overall_style.strip()
    scene = image_prompt.strip()
    if not style:
        return scene
    return f"{style}. {scene}"


class IllustrationMaterializer(BaseMaterializer):

    def __init__(self, image_service: ImageService) -> None:
        self.svc = image_service

    async def materialize(
        self,
        ctx: "MaterializeContext",
        asset_dict: dict[str, Any],
    ) -> list[MediaAsset]:
        content = asset_dict.get("content", {}) or {}
        overall_style = str(content.get("overall_style", "") or "").strip()
        illustrations = content.get("illustrations", []) or []
        anchors_raw = content.get("character_anchors", []) or []

        if not illustrations:
            raise RuntimeError("IllustrationMaterializer: empty illustrations list")

        # ── Stage 1: t2i character anchors ───────────────────────────────
        # Identity-reference scaffold: neutral studio backdrop + portrait
        # framing, applied via ImageSemanticContext(is_identity_reference=True,
        # ref_kind="character"). Same path KeyFrame uses for character L1.
        # Anchor bytes are dict-stored for stage 2 i2i AND persisted to the
        # workspace under sys_id ``illustration_anchor_<char_id>`` for
        # debug / audit. No downstream agent declares this label in its
        # inputs, so it won't be surfaced into any consumer's
        # resolved_artifacts — purely a debug trail.
        anchor_bytes_by_char: dict[str, bytes] = {}
        assets: list[MediaAsset] = []
        for entry in anchors_raw:
            if not isinstance(entry, dict):
                continue
            char_id = str(entry.get("character_id", "") or "").strip()
            appearance = str(entry.get("appearance_prompt", "") or "").strip()
            if not char_id or not appearance:
                logger.warning(
                    "IllustrationMaterializer: skipping anchor entry "
                    "(character_id=%r, appearance_prompt empty=%s)",
                    char_id, not appearance,
                )
                continue

            anchor_ctx = ImageSemanticContext(
                prompt_summary=appearance,
                is_identity_reference=True,
                # picture-book ref_kind makes anchor t2i use painterly
                # scaffold + lets overall_style pass through, so anchors
                # match the segments' folk-illustration aesthetic instead
                # of the cinematic photoreal default.
                ref_kind="character_picturebook",
                style_notes=[overall_style] if overall_style else [],
            )
            last_exc: Exception | None = None
            anchor_bytes: bytes | None = None
            for attempt in range(1, DEFAULT_ASSET_RETRIES + 1):
                try:
                    result = await self.svc.generate_image(
                        semantic_context=anchor_ctx,
                    )
                    anchor_bytes = result.bytes
                    if anchor_bytes:
                        break
                    last_exc = RuntimeError("generate_image returned empty bytes")
                except Exception as exc:
                    last_exc = exc
                logger.warning(
                    "[attempt %d/%d] IllustrationMaterializer: anchor "
                    "generation failed for %s: %s",
                    attempt, DEFAULT_ASSET_RETRIES, char_id, last_exc,
                )

            if not anchor_bytes:
                # A missing anchor degrades but does not break the run:
                # downstream segments that reference this char will fall
                # back to seg-1-as-only-reference (style only). Log loudly.
                logger.error(
                    "IllustrationMaterializer: failed to generate anchor "
                    "for %s after %d attempts; segments referencing %s "
                    "will lack character identity consistency: %s",
                    char_id, DEFAULT_ASSET_RETRIES, char_id, last_exc,
                )
                continue
            anchor_bytes_by_char[char_id] = anchor_bytes
            # Audit-only persistence; sys_id distinct from page assets
            # so caption resolution against `illustration_<seg_id>` is
            # unaffected.
            assets.append(
                MediaAsset(
                    sys_id=f"illustration_anchor_{char_id}",
                    data=anchor_bytes,
                    extension="png",
                    uri_holder={},
                )
            )

        logger.info(
            "IllustrationMaterializer: %d/%d character anchors generated",
            len(anchor_bytes_by_char), len(anchors_raw),
        )

        # ── Stage 2 / Seg 1: t2i style anchor (also a delivered page) ──
        first = illustrations[0]
        first_prompt = _compose_anchor_generate_prompt(
            overall_style, first.get("image_prompt", ""),
        )
        last_exc = None
        seg1_bytes: bytes | None = None
        for attempt in range(1, DEFAULT_ASSET_RETRIES + 1):
            try:
                first_result = await self.svc.generate_image(prompt=first_prompt)
                seg1_bytes = first_result.bytes
                if seg1_bytes:
                    break
                last_exc = RuntimeError("generate_image returned empty bytes")
            except Exception as exc:
                last_exc = exc
            logger.warning(
                "[attempt %d/%d] IllustrationMaterializer: seg-1 style "
                "anchor generation failed: %s",
                attempt, DEFAULT_ASSET_RETRIES, last_exc,
            )

        if not seg1_bytes:
            raise RuntimeError(
                f"IllustrationMaterializer: seg-1 style anchor failed after "
                f"{DEFAULT_ASSET_RETRIES} attempts: {last_exc}"
            )

        # Local uri_holder dicts — Pattern B. ArtifactWriter still needs
        # a dict per asset to stamp uri into for ArtifactRef bookkeeping,
        # but it is NOT shared with the persisted entry: the entry JSON
        # carries no uri / image block, downstream finds the PNG by
        # caption-based resolution against sys_id ``illustration_<seg_id>``.
        anchor_uri_holder: dict[str, Any] = {}
        assets.append(
            MediaAsset(
                sys_id=f"illustration_{first.get('segment_id', 'seg_001')}",
                data=seg1_bytes,
                extension="png",
                uri_holder=anchor_uri_holder,
            )
        )

        # ── Stage 2 / Seg 2..N: parallel multi-ref edit ─────────────────
        # Each tail segment attaches:
        #   Reference 1: seg-1 (STYLE anchor)
        #   References 2..K: character anchors for chars in this segment
        # The service-layer multi-subject scaffold (`_EDIT_PREFIX_MULTI_SUBJECT`)
        # tells the model to preserve STYLE refs for palette/brush/mood
        # only and CHARACTER refs for face/hair/costume identity.
        async def _edit_one(entry: dict) -> bytes | Exception:
            seg_id = str(entry.get("segment_id", "") or "")
            scene = str(entry.get("image_prompt", "") or "")
            chars_in_seg = [
                str(c).strip()
                for c in entry.get("characters_in_segment", []) or []
                if isinstance(c, str) and str(c).strip()
            ]

            refs: list[bytes] = [seg1_bytes]
            ref_manifest: list[str] = [
                "Reference 1: STYLE anchor (the picture-book art-style — "
                "preserve palette, brush stroke, mood, lighting only)"
            ]
            ref_n = 2
            for char_id in chars_in_seg:
                anchor = anchor_bytes_by_char.get(char_id)
                if anchor is None:
                    logger.warning(
                        "IllustrationMaterializer: segment %s lists "
                        "character %s but no anchor available; "
                        "skipping that ref",
                        seg_id, char_id,
                    )
                    continue
                refs.append(anchor)
                ref_manifest.append(
                    f"Reference {ref_n}: CHARACTER anchor for {char_id} "
                    f"(preserve face, hair, body type, wardrobe)"
                )
                ref_n += 1

            edit_ctx = ImageSemanticContext(
                prompt_summary=scene,
                style_notes=[overall_style] if overall_style else [],
            )
            try:
                result = await self.svc.edit_image(
                    reference_images=refs,
                    semantic_context=edit_ctx,
                    ref_kind="picture_book",
                    ref_manifest=ref_manifest,
                )
                if result.bytes:
                    return result.bytes
                return RuntimeError("edit_image returned empty bytes")
            except Exception as exc:
                return exc

        tail = illustrations[1:]
        if tail:
            results: dict[int, bytes] = {}
            last_excs: dict[int, Exception] = {}
            for attempt in range(1, DEFAULT_ASSET_RETRIES + 1):
                pending_idxs = [i for i in range(len(tail)) if i not in results]
                if not pending_idxs:
                    break
                pending_entries = [tail[i] for i in pending_idxs]
                partial = await asyncio.gather(
                    *(_edit_one(e) for e in pending_entries),
                    return_exceptions=True,
                )
                for idx, outcome in zip(pending_idxs, partial):
                    if isinstance(outcome, bytes) and outcome:
                        results[idx] = outcome
                    elif isinstance(outcome, Exception):
                        last_excs[idx] = outcome
                    else:
                        last_excs[idx] = RuntimeError(f"unexpected outcome: {outcome!r}")
                logger.info(
                    "[attempt %d/%d] IllustrationMaterializer: %d/%d tail "
                    "edits successful",
                    attempt, DEFAULT_ASSET_RETRIES, len(results), len(tail),
                )

            if len(results) < len(tail):
                failed_idxs = [i for i in range(len(tail)) if i not in results]
                failed_seg_ids = [
                    tail[i].get("segment_id", f"#{i+1}") for i in failed_idxs
                ]
                first_exc = last_excs.get(failed_idxs[0])
                raise RuntimeError(
                    f"IllustrationMaterializer: edit_image failed for "
                    f"{len(failed_idxs)}/{len(tail)} tail segments after "
                    f"{DEFAULT_ASSET_RETRIES} attempts: {failed_seg_ids}; "
                    f"first error: {first_exc}"
                )

            for idx, entry in enumerate(tail):
                # Per-entry local uri_holder — see anchor for rationale.
                tail_uri_holder: dict[str, Any] = {}
                assets.append(
                    MediaAsset(
                        sys_id=f"illustration_{entry.get('segment_id', 'seg_xxx')}",
                        data=results[idx],
                        extension="png",
                        uri_holder=tail_uri_holder,
                    )
                )

        logger.info(
            "IllustrationMaterializer: produced %d/%d page images "
            "(%d in-memory character anchors used)",
            len(assets), len(illustrations), len(anchor_bytes_by_char),
        )
        return assets
