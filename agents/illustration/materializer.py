"""Illustration materializer — anchor-style image generation.

Strategy: first-frame-as-style-anchor.

  Segment 1  → ``generate_image(prompt = overall_style + image_prompt)``
               This image seeds the cross-segment art style.
  Segments 2..N → ``edit_image(reference=[seg1_bytes], prompt=<custom>)``
                  in PARALLEL.  The prompt explicitly tells the model to
                  use the reference for STYLE ONLY (palette, brush strokes,
                  mood, lighting) and NOT to carry over subjects from it.

Critically, this materializer does NOT use ``ImageService``'s
``semantic_context`` path.  That path prepends an "Edit the attached
reference to match the text below; keep subject identity" instruction
which is correct for KeyFrameAgent's cross-shot same-character use case
but wrong here — for illustrated storybook segments the subject DOES
change between illustrations.  We pass raw prompts directly via the
``prompt=`` kwarg to bypass that instruction.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, TYPE_CHECKING

from ..base_agent import DEFAULT_ASSET_RETRIES
from ..descriptor import BaseMaterializer, MediaAsset
from inference.generation.image_generators.service import ImageService

if TYPE_CHECKING:
    from ..base_agent import MaterializeContext

logger = logging.getLogger(__name__)


def _compose_anchor_generate_prompt(overall_style: str, image_prompt: str) -> str:
    """Text-to-image prompt for the anchor (segment 1).

    Style anchor lives up-front so the model weights it heavily when
    seeding the cross-segment visual identity.
    """
    style = overall_style.strip()
    scene = image_prompt.strip()
    if not style:
        return scene
    return f"{style}. {scene}"


def _compose_anchored_edit_prompt(overall_style: str, image_prompt: str) -> str:
    """Image-to-image prompt for segments 2..N.

    Instructs the model to use the attached anchor image for visual STYLE
    only, not content — bypassing ``ImageService._compose_edit_prompt``'s
    default "keep subject identity" instruction.
    """
    style = overall_style.strip()
    scene = image_prompt.strip()
    return (
        "Use the attached image ONLY as a visual style reference "
        "(palette, brush stroke quality, mood, lighting, level of "
        "detail). The NEW scene content is described below; do NOT "
        "carry over subjects or objects from the reference image "
        "unless the description mentions them.\n\n"
        f"Scene: {scene}\n\n"
        f"Style anchor (preserve): {style}"
    )


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

        if not illustrations:
            raise RuntimeError("IllustrationMaterializer: empty illustrations list")

        # --- Seg 1: generate the style anchor (hard prerequisite) ---
        # Retry transient failures up to DEFAULT_ASSET_RETRIES; raise on
        # exhaustion since the anchor is required for the tail edits.
        first = illustrations[0]
        first_prompt = _compose_anchor_generate_prompt(
            overall_style, first.get("image_prompt", ""),
        )
        last_exc: Exception | None = None
        anchor_bytes: bytes | None = None
        for attempt in range(1, DEFAULT_ASSET_RETRIES + 1):
            try:
                first_result = await self.svc.generate_image(prompt=first_prompt)
                anchor_bytes = first_result.bytes
                if anchor_bytes:
                    break
                last_exc = RuntimeError("generate_image returned empty bytes")
            except Exception as exc:
                last_exc = exc
            logger.warning(
                "[attempt %d/%d] IllustrationMaterializer: anchor "
                "generation failed: %s",
                attempt, DEFAULT_ASSET_RETRIES, last_exc,
            )

        if not anchor_bytes:
            raise RuntimeError(
                f"IllustrationMaterializer: anchor generation failed after "
                f"{DEFAULT_ASSET_RETRIES} attempts: {last_exc}"
            )

        assets: list[MediaAsset] = []
        assets.append(
            MediaAsset(
                sys_id=f"illustration_{first.get('segment_id', 'seg_001')}",
                data=anchor_bytes,
                extension="png",
                uri_holder=first.setdefault("image", {}),
            )
        )

        # --- Seg 2..N: parallel edit_image with partial-resume retry ---
        # Each attempt gathers all pending entries; only the failed ones
        # are retried in subsequent attempts. Raise on exhaustion if any
        # tail entry still failed.
        async def _edit_one(entry: dict) -> bytes | Exception:
            prompt = _compose_anchored_edit_prompt(
                overall_style, entry.get("image_prompt", ""),
            )
            try:
                result = await self.svc.edit_image(
                    reference_images=anchor_bytes,
                    prompt=prompt,
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
                assets.append(
                    MediaAsset(
                        sys_id=f"illustration_{entry.get('segment_id', 'seg_xxx')}",
                        data=results[idx],
                        extension="png",
                        uri_holder=entry.setdefault("image", {}),
                    )
                )

        logger.info(
            "IllustrationMaterializer: produced %d/%d images",
            len(assets), len(illustrations),
        )
        return assets
