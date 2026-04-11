"""IntakeImageAgent — runs a vision LLM on a raw user image upload.

Output: caption-rich workspace artifact pointing at the same image bytes,
ready for downstream content agents to discover via their image labels.

Implementation note
-------------------
The vision LLM call cannot go through ``LLMClient.chat_json`` (text-only
JSON helper). This agent implements ``generate`` directly, inlines the
OpenAI-style multimodal message construction (text + base64 data-URI
image), and dispatches through ``LLMClient.acall``, which forwards the
content array to the underlying provider.
"""

from __future__ import annotations

import base64
import json
import logging
from pathlib import Path
from typing import Any, Dict

from ...base_agent import BaseAgent
from ...common_schema import ImageAsset
from .schema import IntakeImageContent, IntakeImageInput, IntakeImageOutput

logger = logging.getLogger(__name__)


class IntakeImageAgent(BaseAgent[IntakeImageInput, IntakeImageOutput]):

    def system_prompt(self) -> str:
        return (
            "You are IntakeImageAgent. Look at a user-uploaded image and "
            "produce a single short objective description (one sentence, "
            "STRICTLY <= 150 chars) of what is visible: subject, key "
            "visible attributes, lighting/mood. Be terse — drop adverbs "
            "and filler. Do NOT speculate about meaning or intent — "
            "describe only the surface visual content.\n\n"
            "Return strict JSON of the shape "
            "{\"visual_description\": \"...\"}."
        )

    def build_user_prompt(self, input_data: IntakeImageInput) -> str:
        """Text portion of the multimodal user message.

        The image is attached separately as a multimodal content item;
        only the text portion is constructed here.
        """
        return (
            "Describe the attached image in ONE short sentence "
            "(STRICTLY <= 150 characters): subject, key visible attributes, "
            "lighting/mood. Drop adverbs and filler. Do not speculate "
            "about purpose.\n\n"
            "Return strict JSON: {\"visual_description\": \"...\"}"
        )

    async def generate(
        self,
        input_data: IntakeImageInput,
        *,
        rework_notes: str = "",
    ) -> IntakeImageOutput:
        """Build a multimodal message, run the vision LLM, emit the artifact.

        Steps:
          1. Build the structural skeleton (image_asset.uri pre-set).
          2. Build a multimodal message containing the system prompt, the
             user-text portion, and the image bytes (read from
             ``raw_image_path`` and base64-encoded inline as a data URI).
          3. Dispatch via ``LLMClient.acall`` (passes the OpenAI-style
             multimodal content array to litellm/openai-sdk underneath).
          4. Parse the assistant text as JSON and pull
             ``visual_description``; fall back to the raw text if JSON
             parsing fails (some vision models do not honor JSON mode).
          5. Return the output with visual_description populated.
        """
        skeleton = self._build_skeleton(input_data)
        image_path = (input_data.raw_image_path or "").strip()

        if not image_path:
            skeleton.content.visual_description = ""
            return skeleton

        user_text = self.build_user_prompt(input_data)
        if rework_notes:
            user_text += (
                "\n\n--- REWORK INSTRUCTIONS (from quality review) ---\n"
                f"{rework_notes}\n"
                "--- END REWORK INSTRUCTIONS ---"
            )

        image_path_obj = Path(image_path)
        if not image_path_obj.is_file():
            logger.warning(
                "[%s] image file missing at %s",
                self.agent_name, image_path,
            )
            skeleton.content.visual_description = ""
            return skeleton

        img_bytes = image_path_obj.read_bytes()
        suffix = image_path_obj.suffix.lower().lstrip(".")
        mime_subtype = {
            "png": "png", "jpg": "jpeg", "jpeg": "jpeg",
            "gif": "gif", "webp": "webp", "bmp": "bmp", "tiff": "tiff",
        }.get(suffix, "png")
        data_uri = (
            f"data:image/{mime_subtype};base64,"
            + base64.b64encode(img_bytes).decode("utf-8")
        )
        multimodal_msg = {
            "role": "user",
            "content": [
                {"type": "text", "text": user_text},
                {"type": "image_url", "image_url": {"url": data_uri}},
            ],
        }

        messages = [
            {"role": "system", "content": self.system_prompt()},
            multimodal_msg,
        ]

        visual = ""
        try:
            response = await self.llm.acall(
                messages,
                response_format={"type": "json_object"},
            )
            visual = self._parse_visual_description(response)
        except Exception as exc:
            logger.warning(
                "[%s] vision LLM call failed: %s — emitting fallback caption",
                self.agent_name, exc,
            )

        skeleton.content.visual_description = visual
        return skeleton

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    @staticmethod
    def _build_skeleton(input_data: IntakeImageInput) -> IntakeImageOutput:
        skeleton = IntakeImageOutput()
        skeleton.content = IntakeImageContent(
            visual_description="",
            image_asset=ImageAsset(
                uri=(input_data.raw_image_path or ""),
                asset_id="",
            ),
        )
        return skeleton

    @staticmethod
    def _parse_visual_description(response: Dict[str, Any]) -> str:
        """Extract ``visual_description`` from a vision LLM response.

        Tries strict JSON parsing first; if the model returned plain text
        (some providers ignore ``response_format`` for vision endpoints),
        falls back to using the trimmed raw text as the description.
        """
        text = IntakeImageAgent._extract_assistant_text(response)
        if not text:
            return ""
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return text.strip()
        if isinstance(parsed, dict):
            return str(parsed.get("visual_description") or "").strip()
        return ""

    @staticmethod
    def _extract_assistant_text(response: Dict[str, Any]) -> str:
        choices = response.get("choices") or []
        if not choices:
            return ""
        message = choices[0].get("message") or {}
        content = message.get("content", "")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    parts.append(item.get("text", ""))
            return "".join(parts)
        return ""
