"""NarratorAgent — no-LLM TTS renderer.

``generate()`` parses the upstream NarrationAgent script and mirrors
its (segment_id, line_id, text, pause_after_ms) tuples into this agent's
output ``content.lines`` worklist. All creative decisions are already
encoded upstream.

The real work — TTS per line, ffmpeg concat with pauses, per-segment
timing aggregation, SRT assembly — happens in NarratorMaterializer.
"""

from __future__ import annotations

import json
import logging

from ..base_agent import BaseAgent
from .schema import (
    NarratorAgentInput,
    NarratorAgentOutput,
    NarratorContent,
    NarratorLineSnapshot,
    NarratorMetrics,
)

logger = logging.getLogger(__name__)


class NarratorAgent(BaseAgent[NarratorAgentInput, NarratorAgentOutput]):

    async def generate(
        self,
        input_data: NarratorAgentInput,
        *,
        rework_notes: str = "",
    ) -> NarratorAgentOutput:
        """Parse NarrationAgent output, mirror lines into output.content.lines."""
        output = NarratorAgentOutput()

        try:
            narr = json.loads(input_data.narration_script_json_text or "{}")
        except Exception as exc:
            logger.warning(
                "[NarratorAgent] failed to parse narration_script_json_text: %s",
                exc,
            )
            narr = {}

        content = narr.get("content", narr) if isinstance(narr, dict) else {}
        language = str(content.get("language", "") or "").strip()
        segments = content.get("segments", []) if isinstance(content, dict) else []

        worklist: list[NarratorLineSnapshot] = []
        segment_ids: set[str] = set()
        for seg in segments:
            if not isinstance(seg, dict):
                continue
            seg_id = str(seg.get("segment_id", "") or "")
            segment_ids.add(seg_id)
            for line in seg.get("lines", []) or []:
                if not isinstance(line, dict):
                    continue
                worklist.append(
                    NarratorLineSnapshot(
                        line_id=str(line.get("line_id", "") or ""),
                        segment_id=seg_id,
                        text=str(line.get("text", "") or ""),
                        pause_after_ms=int(line.get("pause_after_ms", 0) or 0),
                    )
                )

        output.content = NarratorContent(language=language, lines=worklist)
        output.metrics = NarratorMetrics(
            line_count=len(worklist),
            segment_count=len(segment_ids),
            total_duration_sec=0.0,  # filled by materializer
        )
        return output
