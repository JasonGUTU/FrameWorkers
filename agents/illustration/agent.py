"""IllustrationAgent — no-LLM per-segment illustration generator.

``generate()`` mirrors the upstream NarrationAgent segments into this
agent's own output shell (segment_id + image_prompt) so the materializer
has a deterministic worklist; no LLM call happens in this phase because
NarrationAgent already owns all creative decisions (per-segment prompt +
cross-segment art-style anchor).

The actual image generation — first-frame-as-style-anchor strategy,
parallel edit_image for segments 2..N — lives entirely in
``IllustrationMaterializer``.
"""

from __future__ import annotations

import json
import logging

from ..base_agent import BaseAgent
from .schema import (
    IllustrationAgentInput,
    IllustrationAgentOutput,
    IllustrationContent,
    IllustrationEntry,
    IllustrationMetrics,
)

logger = logging.getLogger(__name__)


class IllustrationAgent(BaseAgent[IllustrationAgentInput, IllustrationAgentOutput]):

    async def generate(
        self,
        input_data: IllustrationAgentInput,
        *,
        rework_notes: str = "",
    ) -> IllustrationAgentOutput:
        """Parse NarrationAgent output, mirror segments into output shell."""
        output = IllustrationAgentOutput()

        try:
            narr = json.loads(input_data.narration_script_json_text or "{}")
        except Exception as exc:
            logger.warning(
                "[IllustrationAgent] failed to parse narration_script_json_text: %s",
                exc,
            )
            narr = {}

        content = narr.get("content", narr) if isinstance(narr, dict) else {}
        overall_style = str(content.get("overall_style", "") or "").strip()
        segments = content.get("segments", []) if isinstance(content, dict) else []

        output.content = IllustrationContent(
            overall_style=overall_style,
            illustrations=[
                IllustrationEntry(
                    segment_id=str(seg.get("segment_id", "") or ""),
                    image_prompt=str(seg.get("image_prompt", "") or ""),
                )
                for seg in segments
                if isinstance(seg, dict)
            ],
        )
        output.metrics = IllustrationMetrics(
            illustration_count=len(output.content.illustrations),
        )
        return output
