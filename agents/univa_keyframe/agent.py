"""UnivaKeyFrameAgent — character image refinement + keyframe planning.

Input:  UnivaKeyFrameInput (storyboard_json_text)
Output: UnivaKeyFrameOutput (character_images + shot_keyframes)

Generation model: TWO-PHASE LLM.
  Phase 1: ONE ``_llm_fill_full`` call reads the storyboard JSON text
           and produces the full output structure (characters with
           original_description, shots with composed keyframe_prompt).
  Phase 2: N parallel per-character LLM calls refine each character's
           image-generation prompt via ``character_prompt_refine.txt``.

Zero Python-side string-key access on the upstream storyboard — the
Phase 1 LLM is the sole consumer of the storyboard shape. See CLAUDE.md
§7 (Postel's Law at the agent layer).
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
)

logger = logging.getLogger(__name__)

_PROMPT_DIR = Path(__file__).with_name("prompts")


UNIVA_KF_OUTPUT_TEMPLATE = """{
  "content": {
    "character_images": [
      {
        "char_id": "<from storyboard character id>",
        "char_name": "<from storyboard character name>",
        "original_description": "<VERBATIM from storyboard character description>",
        "refined_prompt": "",
        "image_asset": {"asset_id": "", "uri": "placeholder", "width": 1024, "height": 576, "format": "png"}
      }
    ],
    "shot_keyframes": [
      {
        "shot_id": 0,
        "keyframe_prompt": "<composed from the shot's setting_description + plot_correspondence + static_shot_description + shot_perspective_design fields, concatenated into one image prompt>",
        "onstage_char_ids": ["<from shot onstage_characters list>"],
        "image_asset": {"asset_id": "", "uri": "placeholder", "width": 1024, "height": 576, "format": "png"}
      }
    ]
  }
}"""


class UnivaKeyFrameAgent(BaseAgent[UnivaKeyFrameInput, UnivaKeyFrameOutput]):

    def system_prompt(self) -> str:
        return (
            "You are UnivaKeyFrameAgent: read a storyboard and produce "
            "character image descriptions + per-shot keyframe prompts.\n\n"
            "=== INPUT FORMAT ===\n"
            "You will receive the upstream storyboard as a RAW JSON TEXT "
            "BLOB. Do NOT assume specific field names. READ the JSON and "
            "find characters (with id, name, description) and shots (with "
            "setting, plot, visual description, camera/perspective "
            "design). Reason from the text.\n\n"
            "=== YOUR JOB ===\n"
            "1. For each CHARACTER in the storyboard, copy its id, name, "
            "and description VERBATIM into character_images. Leave "
            "refined_prompt empty (a separate LLM pass will fill it).\n"
            "2. For each SHOT, compose a keyframe_prompt by concatenating "
            "the shot's visual description fields (setting, plot, static "
            "description, camera distance/angle/lens) into one "
            "continuous image-generation prompt. Copy onstage_characters "
            "into onstage_char_ids.\n"
            "3. All image_asset fields: leave as placeholder.\n\n"
            "=== OUTPUT FORMAT ===\n"
            "JSON only; no markdown; match the template exactly.\n\n"
            "Do NOT include an artifact_caption block — the system "
            "generates it automatically."
        )

    def build_user_prompt(self, input_data: UnivaKeyFrameInput) -> str:
        return (
            "=== STORYBOARD (raw JSON — read before writing) ===\n"
            f"{input_data.storyboard_json_text}\n"
            "=== END STORYBOARD ===\n\n"
            "Produce the full keyframe plan in this shape:\n\n"
            f"{UNIVA_KF_OUTPUT_TEMPLATE}\n\n"
            "Return JSON only."
        )

    def parse_output(self, raw: dict[str, Any]) -> UnivaKeyFrameOutput:
        return UnivaKeyFrameOutput.model_validate(raw)

    async def _refine_one_character(
        self,
        refine_system: str,
        char_name: str,
        original_description: str,
    ) -> str:
        """One LLM call per character, mirroring UniVA's per-character refine_gen_prompt."""
        if not original_description:
            return ""
        user_input = (
            f"Character: {char_name or 'unnamed'}\n"
            f"Description: {original_description}"
        )
        try:
            data = await self.llm.chat_json(refine_system, user_input)
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
        """Phase 1: extract characters + shots via _llm_fill_full.
        Phase 2: refine each character's prompt via parallel per-character LLM calls.
        """
        # Phase 1: main extraction
        output = await self._llm_fill_full(input_data, rework_notes)

        # Phase 2: per-character prompt refinement (parallel)
        refine_prompt = (_PROMPT_DIR / "character_prompt_refine.txt").read_text(
            encoding="utf-8",
        )
        refine_system = (
            f"{refine_prompt}\n\n"
            "# Output Rules (system-injected)\n"
            "- Return JSON only, no markdown, no code fences.\n"
            "- Output MUST be exactly: {\"prompt\": \"...\"}\n"
        )
        tasks = [
            self._refine_one_character(
                refine_system, ci.char_name, ci.original_description
            )
            for ci in output.content.character_images
        ]
        if tasks:
            refined_prompts = await asyncio.gather(*tasks, return_exceptions=True)
            for ci, result in zip(output.content.character_images, refined_prompts):
                if isinstance(result, Exception):
                    logger.warning("[UnivaKF] refine raised for %s: %s", ci.char_id, result)
                    ci.refined_prompt = ci.original_description
                else:
                    ci.refined_prompt = result or ci.original_description

        self.recompute_metrics(output)
        return output

    def recompute_metrics(self, output: UnivaKeyFrameOutput) -> None:
        c = output.content
        output.metrics.character_image_count = len(c.character_images)
        output.metrics.shot_keyframe_count = len(c.shot_keyframes)
