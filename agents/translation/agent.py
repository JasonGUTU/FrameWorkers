"""TranslationAgent — translate structured text while preserving structure.

Input:  TranslationAgentInput (source_json_text + target_language)
Output: TranslationAgentOutput (translated text with detected/target language info)

Single LLM call.  The LLM receives the upstream payload as a JSON text blob,
translates all human-readable content (dialogue, narration, descriptions,
titles) into the target language, and preserves structural keys (scene_id,
shot_id, block_type, etc.) and ordering unchanged.
"""

from __future__ import annotations

from typing import Any

from ..base_agent import BaseAgent
from .schema import TranslationAgentInput, TranslationAgentOutput


TRANSLATION_OUTPUT_TEMPLATE = """{
  "content": {
    "source_language": "<detected ISO code, e.g. zh>",
    "target_language": "<target ISO code, e.g. en>",
    "translated_payload": {
      "content": {
        "<MIRROR the entire source JSON structure here, with all human-readable values translated>"
      }
    }
  }
}"""


class TranslationAgent(BaseAgent[TranslationAgentInput, TranslationAgentOutput]):

    async def generate(
        self,
        input_data: TranslationAgentInput,
        *,
        rework_notes: str = "",
    ) -> TranslationAgentOutput:
        output = await self._llm_fill_full(input_data, rework_notes)
        self.recompute_metrics(output)
        return output

    def system_prompt(self) -> str:
        return (
            "You are TranslationAgent: translate structured text from one "
            "language to another while preserving the original structure "
            "exactly.\n\n"
            "=== WHEN TO REJECT UPSTREAM INPUT ===\n"
            "Use the shared input_rejection escape hatch (see the UPSTREAM "
            "INPUT REJECTION block above) ONLY if the source text makes "
            "translation impossible. Concretely, reject when ANY of these "
            "is true after you have read source_json_text carefully:\n"
            "  * source_json_text is empty, whitespace-only, or an empty "
            "JSON object — there is literally nothing to translate.\n"
            "  * The source contains no human-readable text whatsoever "
            "(only ids, asset_ids, format codes, numeric fields, "
            "placeholders) — there are no translatable strings.\n"
            "When you reject, populate the rejection fields like this:\n"
            "  * reason: the single most specific defect (e.g. 'source "
            "payload contains only structural ids and placeholders — no "
            "human-readable text to translate').\n"
            "  * missing_labels: ['source_text'] (my only input label).\n"
            "  * offending_fields: e.g. ['content'] or whatever paths you "
            "scanned and found empty of translatable content.\n"
            "  * upstream_agent_hint: '' (the source can come from many "
            "agents — leave empty unless the payload's meta clearly "
            "identifies the producer).\n"
            "If the source is merely short (a single sentence) or in an "
            "unusual format — DO NOT reject; translate whatever text is "
            "there.\n"
            "=== END WHEN TO REJECT UPSTREAM INPUT ===\n\n"
            "=== INPUT FORMAT ===\n"
            "You will receive a raw text blob (often JSON) and a target "
            "language code. The source text may be a screenplay, transcript, "
            "story blueprint, or any structured document.\n\n"
            "=== TRANSLATION RULES ===\n"
            "1. Translate ALL human-readable text: dialogue, narration, "
            "descriptions, titles, summaries, mood keywords, location names.\n"
            "2. PRESERVE all structural keys unchanged: scene_id, shot_id, "
            "block_type, character_id, asset_id, order numbers, format "
            "strings, uri placeholders.\n"
            "3. PRESERVE the exact same JSON structure, nesting, and array "
            "ordering as the source.\n"
            "4. Character names: transliterate naturally into the target "
            "language (e.g. 小明 → Xiao Ming for English, or keep original "
            "if the target culture would recognize it).\n"
            "5. Keep technical terms, file paths, and format codes as-is.\n"
            "6. Put the translated document in the 'translated_payload' field "
            "as a NATIVE JSON OBJECT (not a string). It must mirror the source "
            "structure exactly with only human-readable values translated.\n"
            "7. CRITICAL: translated_payload MUST NOT be empty. It must "
            "contain the complete translated document as a JSON object.\n\n"
            "=== OUTPUT FORMAT ===\n"
            "JSON only; no markdown; match the user-message template exactly.\n\n"
            "Do NOT include an artifact_caption block — the system generates "
            "it automatically."
        )

    def build_user_prompt(self, input_data: TranslationAgentInput) -> str:
        return (
            f"Translate the following text into **{input_data.target_language}**.\n\n"
            "=== SOURCE TEXT ===\n"
            f"{input_data.source_json_text}\n"
            "=== END SOURCE TEXT ===\n\n"
            "Produce the translation in EXACTLY this shape:\n\n"
            f"{TRANSLATION_OUTPUT_TEMPLATE}\n\n"
            "Return JSON only."
        )

    def parse_output(self, raw: dict[str, Any]) -> TranslationAgentOutput:
        return TranslationAgentOutput.model_validate(raw)

    def recompute_metrics(self, output: TranslationAgentOutput) -> None:
        c = output.content
        output.metrics.source_language = c.source_language
        output.metrics.target_language = c.target_language
        output.metrics.has_payload = bool(c.translated_payload)
