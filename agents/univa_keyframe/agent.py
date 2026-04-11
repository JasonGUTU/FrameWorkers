"""UnivaKeyFrameAgent -- character image refinement + keyframe planning.

Mirrors UniVA's Stage 2 (character image gen with LLM prompt refinement) and
Stage 3 (per-shot keyframe planning).  Skeleton-first mode:
  - Skeleton: deterministic keyframe prompts composed from storyboard fields.
  - Creative fill: one LLM call PER CHARACTER, mirroring UniVA's
    ``refine_gen_prompt(media_type="character")`` per-character loop.  This
    matches the original behaviour where each character gets a dedicated,
    full-attention pass through ``character_prompt_refine.txt`` rather than
    being batched.
  - Materializer: image_service (selected by ``select_image_service()``)
    generates character images + shot keyframes.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any

from ..base_agent import BaseAgent
from .schema import (
    UnivaKeyFrameInput,
    UnivaKeyFrameOutput,
    UnivaKeyFrameContent,
    UnivaKeyFrameMetrics,
    UnivaCharacterImage,
    UnivaShotKeyframe,
)
from ..common_schema import ImageAsset

logger = logging.getLogger(__name__)

_PROMPT_DIR = Path(__file__).with_name("prompts")


def _compose_keyframe_prompt(shot: dict) -> str:
    """Reproduce UniVA's deterministic keyframe prompt formula."""
    setting = shot.get("setting_description", "")
    plot = shot.get("plot_correspondence", "")
    static_desc = shot.get("static_shot_description", "")
    perspective = shot.get("shot_perspective_design", {})
    distance = perspective.get("distance", "")
    angle = perspective.get("angle", "")
    lens = perspective.get("lens", "")
    return f"{setting} {plot} {static_desc} {distance}, {angle}, {lens}"


class UnivaKeyFrameAgent(BaseAgent[UnivaKeyFrameInput, UnivaKeyFrameOutput]):
    """Skeleton-first agent: pre-builds keyframe structure, LLM refines each character prompt."""

    def system_prompt(self) -> str:
        refine_prompt = (_PROMPT_DIR / "character_prompt_refine.txt").read_text(
            encoding="utf-8",
        )
        return (
            f"{refine_prompt}\n\n"
            "# Output Rules (system-injected)\n"
            "- Return JSON only, no markdown, no code fences.\n"
            "- Output MUST be exactly: {\"prompt\": \"...\"}\n"
            "- The prompt string must follow the workflow above and produce a "
            "single, full-detail English image-generation description for the "
            "one character in the user message.\n"
        )

    def build_user_prompt(self, input_data: UnivaKeyFrameInput) -> str:
        # Unused in skeleton mode; kept to satisfy BaseAgent interface.
        return ""

    def build_skeleton(self, input_data: UnivaKeyFrameInput) -> UnivaKeyFrameOutput | None:
        sb = input_data.storyboard
        characters = sb.get("characters", [])
        shots = sb.get("shots", [])

        char_images = []
        for ch in characters:
            char_images.append(UnivaCharacterImage(
                char_id=ch.get("id", ""),
                char_name=ch.get("name", ""),
                original_description=ch.get("description", ""),
                refined_prompt="",  # filled per-character by _generate
                image_asset=ImageAsset(),
            ))

        shot_kfs = []
        for shot in shots:
            onstage = shot.get("onstage_characters", [])
            shot_kfs.append(UnivaShotKeyframe(
                shot_id=shot.get("id", 0),
                keyframe_prompt=_compose_keyframe_prompt(shot),
                onstage_char_ids=onstage,
                image_asset=ImageAsset(),
            ))

        return UnivaKeyFrameOutput(
            content=UnivaKeyFrameContent(
                character_images=char_images,
                shot_keyframes=shot_kfs,
            ),
            metrics=UnivaKeyFrameMetrics(
                character_image_count=len(char_images),
                shot_keyframe_count=len(shot_kfs),
            ),
        )

    def build_creative_prompt(
        self,
        input_data: UnivaKeyFrameInput,
        skeleton: UnivaKeyFrameOutput,
    ) -> str:
        # Per-character refinement happens in ``_refine_one_character`` below;
        # this method is required by BaseAgent skeleton mode but the actual
        # creative-fill is custom (one LLM call per character, not one batch).
        return ""

    def fill_creative(
        self,
        skeleton: UnivaKeyFrameOutput,
        creative: dict[str, Any],
    ) -> UnivaKeyFrameOutput:
        # Custom per-character fill done in ``_generate`` override below.
        return skeleton

    async def _refine_one_character(
        self,
        system_prompt: str,
        char_name: str,
        original_description: str,
    ) -> str:
        """One LLM call per character, mirroring UniVA's per-character refine_gen_prompt."""
        if not original_description:
            return ""
        # Mirror UniVA: feed the raw description as the user message; the
        # template in the system prompt provides the refinement workflow.
        user_input = (
            f"Character: {char_name or 'unnamed'}\n"
            f"Description: {original_description}"
        )
        try:
            data = await self.llm.chat_json(system_prompt, user_input)
            refined = ""
            if isinstance(data, dict):
                refined = str(data.get("prompt", "") or "")
            return refined or original_description
        except Exception as exc:
            logger.warning(
                "[UnivaKF] character refine failed for %s: %s",
                char_name, exc,
            )
            return original_description

    async def generate(
        self,
        input_data: UnivaKeyFrameInput,
        *,
        rework_notes: str = "",
    ) -> UnivaKeyFrameOutput:
        """Build skeleton then refine each character's prompt via a parallel
        per-character LLM call. Custom flow because UniVA's prompt
        refinement is one LLM call per character, not a single batched
        call (which is what the default ``_llm_fill_creative`` helper
        would do).
        """
        skeleton = self.build_skeleton(input_data)
        if skeleton is None:
            raise RuntimeError("UnivaKeyFrameAgent skeleton build returned None")

        # Refine each character's prompt in parallel — one LLM call per
        # character, mirroring UniVA's per-character refine_gen_prompt loop.
        sys_prompt = self.system_prompt()
        tasks = [
            self._refine_one_character(sys_prompt, ci.char_name, ci.original_description)
            for ci in skeleton.content.character_images
        ]
        refined_prompts = await asyncio.gather(*tasks, return_exceptions=True)

        for ci, result in zip(skeleton.content.character_images, refined_prompts):
            if isinstance(result, Exception):
                logger.warning(
                    "[UnivaKF] character %s refine raised: %s",
                    ci.char_id, result,
                )
                ci.refined_prompt = ci.original_description
            else:
                ci.refined_prompt = result or ci.original_description

        self.recompute_metrics(skeleton)
        return skeleton

    def recompute_metrics(self, output: UnivaKeyFrameOutput) -> None:
        c = output.content
        char_count = len(c.character_images)
        shot_count = len(c.shot_keyframes)
        output.metrics.character_image_count = char_count
        output.metrics.shot_keyframe_count = shot_count
