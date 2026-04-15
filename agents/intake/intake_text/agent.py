"""IntakeTextAgent — wraps raw user text into a caption-rich workspace artifact.

Dual-mode: short text is captured statically (no LLM call); long text is
summarized by an LLM. Both produce the same shape of caption-rich
artifact, so downstream agents see no difference.

Implementation note
-------------------
This agent implements ``generate`` directly (rather than composing the
BaseAgent helpers) because the short / long branches do not fit a single
skeleton-or-LLM pattern. Short text returns a fully-formed output and
skips the LLM entirely; long text issues one ``chat_json`` call to
produce a one-sentence summary, then synthesizes the final caption.
"""

from __future__ import annotations

import logging
from typing import Any

from ...base_agent import BaseAgent
from .schema import (
    IntakeTextContent,
    IntakeTextInput,
    IntakeTextMetrics,
    IntakeTextOutput,
)

logger = logging.getLogger(__name__)

# Threshold (in characters) below which we skip the LLM call entirely.
# Short user prompts ("a film about a cat") never need a summary —
# the verbatim text IS the brief.
SHORT_TEXT_THRESHOLD = 800


class IntakeTextAgent(BaseAgent[IntakeTextInput, IntakeTextOutput]):

    SHORT_TEXT_THRESHOLD = SHORT_TEXT_THRESHOLD

    def system_prompt(self) -> str:
        return (
            "You are IntakeTextAgent. Read a long natural-language text "
            "submission from a user and produce a brief one-sentence "
            "summary (<= 200 chars) describing what kind of text it is "
            "and the essential subject matter. Do not interpret or "
            "rewrite — describe only the surface content.\n\n"
            "Return strict JSON of the shape {\"summary\": \"...\"}."
        )

    def build_user_prompt(self, input_data: IntakeTextInput) -> str:
        """Build the long-text summarization prompt.

        Only used in the long-text branch of ``generate``. Reads the file
        contents from disk so that the LLM sees the verbatim user text.
        """
        text = self._read_text_file(input_data.raw_text_path)
        return (
            "User-uploaded text follows. Produce a one-sentence summary "
            "describing what this text is and what it covers.\n\n"
            "=== USER TEXT ===\n"
            f"{text}\n"
            "=== END ===\n\n"
            "Return strict JSON: {\"summary\": \"...\"}"
        )

    async def generate(
        self,
        input_data: IntakeTextInput,
        *,
        rework_notes: str = "",
    ) -> IntakeTextOutput:
        """Read the raw text from disk and emit a caption-rich artifact.

        Two paths:
          * Short text (<= ``SHORT_TEXT_THRESHOLD`` chars): no LLM call,
            the verbatim text IS the brief and the caption is synthesized
            statically.
          * Long text: one ``chat_json`` call asks the LLM for a one-
            sentence surface description; the result populates the
            artifact's ``what`` field.
        """
        text = self._read_text_file(input_data.raw_text_path).strip()

        output = IntakeTextOutput()
        output.content = IntakeTextContent(text=text, summary="")
        output.metrics = IntakeTextMetrics(char_count=len(text))

        if not text:
            return output

        if len(text) <= self.SHORT_TEXT_THRESHOLD:
            return output

        # Long text — call the LLM for a one-sentence summary.
        system = self.system_prompt()
        user = self.build_user_prompt(input_data)
        if rework_notes:
            user += (
                "\n\n--- REWORK INSTRUCTIONS (from quality review) ---\n"
                f"{rework_notes}\n"
                "--- END REWORK INSTRUCTIONS ---"
            )

        summary = ""
        try:
            creative_json = await self.llm.chat_json(system, user)
            if isinstance(creative_json, dict):
                summary = str(
                    creative_json.get("summary")
                    or creative_json.get("text")
                    or ""
                ).strip()
        except Exception as exc:
            logger.warning(
                "[%s] LLM summary failed: %s — falling back to static caption",
                self.agent_name, exc,
            )

        output.content.summary = summary
        return output

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    @staticmethod
    def _read_text_file(path: str) -> str:
        if not path:
            return ""
        try:
            with open(path, "r", encoding="utf-8") as fh:
                return fh.read()
        except Exception as exc:
            logger.warning(
                "[IntakeTextAgent] failed to read raw text file %s: %s",
                path, exc,
            )
            return ""
