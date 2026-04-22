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
            logger.warning("IllustrationMaterializer: empty illustrations list")
            return []

        # --- Seg 1: generate the style anchor ---
        first = illustrations[0]
        first_prompt = _compose_anchor_generate_prompt(
            overall_style, first.get("image_prompt", ""),
        )
        try:
            first_result = await self.svc.generate_image(prompt=first_prompt)
            anchor_bytes = first_result.bytes
        except Exception as exc:
            logger.error(
                "IllustrationMaterializer: anchor generation failed: %s", exc,
            )
            return []

        assets: list[MediaAsset] = []
        assets.append(
            MediaAsset(
                sys_id=f"illustration_{first.get('segment_id', 'seg_001')}",
                data=anchor_bytes,
                extension="png",
                uri_holder=first.setdefault("image", {}),
            )
        )

        # --- Seg 2..N: parallel edit_image using the anchor for style ---
        async def _edit_one(entry: dict) -> tuple[dict, bytes | None]:
            prompt = _compose_anchored_edit_prompt(
                overall_style, entry.get("image_prompt", ""),
            )
            try:
                result = await self.svc.edit_image(
                    reference_images=anchor_bytes,
                    prompt=prompt,
                )
                return entry, result.bytes
            except Exception as exc:
                logger.error(
                    "IllustrationMaterializer: edit for %s failed: %s",
                    entry.get("segment_id"), exc,
                )
                return entry, None

        tail = illustrations[1:]
        if tail:
            results = await asyncio.gather(*(_edit_one(e) for e in tail))
            for entry, img_bytes in results:
                if img_bytes is None:
                    continue
                assets.append(
                    MediaAsset(
                        sys_id=f"illustration_{entry.get('segment_id', 'seg_xxx')}",
                        data=img_bytes,
                        extension="png",
                        uri_holder=entry.setdefault("image", {}),
                    )
                )

        logger.info(
            "IllustrationMaterializer: produced %d/%d images",
            len(assets), len(illustrations),
        )
        return assets
