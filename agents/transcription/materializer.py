"""Transcription materializer — calls transcription service for STT.

Calls an external speech-to-text service (OpenAI Whisper) to transcribe
audio/video files.  The raw segments are written into the asset_dict
so the LLM can post-process them (cleanup, speaker attribution).

The materializer produces no MediaAsset output — the transcript is a
pure-text artifact stored as JSON by the standard pipeline.
"""

from __future__ import annotations

import json
import logging
from typing import Any, TYPE_CHECKING

from ..descriptor import BaseMaterializer, MediaAsset
from inference.generation.transcription_service import TranscriptionService

if TYPE_CHECKING:
    from ..base_agent import MaterializeContext
    from .schema import TranscriptionAgentInput

logger = logging.getLogger(__name__)


class TranscriptionMaterializer(BaseMaterializer):
    """Transcribe audio/video via an external STT service."""

    def __init__(self, transcription_service: TranscriptionService) -> None:
        self.stt_svc = transcription_service

    async def materialize(
        self,
        ctx: "MaterializeContext",
        asset_dict: dict[str, Any],
    ) -> list[MediaAsset]:
        """Run STT on the source media file.

        Writes raw transcription segments back into asset_dict so the
        agent's LLM phase (or recompute_metrics) can consume them.
        Returns empty list — no binary media assets produced.
        """
        typed_input: TranscriptionAgentInput = ctx.typed_input

        result = await self.stt_svc.transcribe(typed_input.source_media_path)

        # Write results back into asset_dict for the LLM / post-processing
        content = asset_dict.setdefault("content", {})
        content["language"] = result.language
        content["full_text"] = result.full_text
        content["segments"] = [
            {
                "segment_id": f"seg_{i + 1:03d}",
                "start_time": seg.start,
                "end_time": seg.end,
                "speaker": "",
                "text": seg.text,
                "confidence": 0.0,
            }
            for i, seg in enumerate(result.segments)
        ]

        logger.info(
            "TranscriptionMaterializer: %d segments, language=%s for task %s",
            len(result.segments), result.language, ctx.step_id,
        )
        return []
