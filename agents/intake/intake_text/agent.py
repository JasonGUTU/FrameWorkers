"""IntakeTextAgent — wraps raw user text into a caption-rich workspace artifact.

Pure pass-through: reads the raw text from disk verbatim, emits an
IntakeTextOutput whose payload carries the text as-is. No LLM involved.

The agent's real job is structural — caption normalization + scope-flip
(raw_pending → global) happen at the framework level via the descriptor
+ global_memory. IntakeTextContent simply carries the text downstream
content agents read through ``entry.payload``.
"""

from __future__ import annotations

import logging

from ...base_agent import BaseAgent
from .schema import (
    IntakeTextContent,
    IntakeTextInput,
    IntakeTextMetrics,
    IntakeTextOutput,
)

logger = logging.getLogger(__name__)


class IntakeTextAgent(BaseAgent[IntakeTextInput, IntakeTextOutput]):

    async def generate(
        self,
        input_data: IntakeTextInput,
        *,
        rework_notes: str = "",
    ) -> IntakeTextOutput:
        """Read the raw text from disk verbatim — no LLM call, any length."""
        text = self._read_text_file(input_data.raw_text_path).strip()
        output = IntakeTextOutput()
        output.content = IntakeTextContent(text=text)
        output.metrics = IntakeTextMetrics(char_count=len(text))
        return output

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
