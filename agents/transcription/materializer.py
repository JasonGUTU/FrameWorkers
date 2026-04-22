"""Transcription materializer — STT seeding via the pre_generate hook.

TranscriptionAgent is a tool-type agent: its LLM's job is polishing
already-transcribed segments, not inventing them. The actual STT work
must happen BEFORE the LLM runs, otherwise L1 rejects the empty
placeholder the LLM produces and the retry loop never reaches a
materializer that overrides it.

This materializer therefore does its work in ``pre_generate``, which
BaseAgent.run() invokes exactly once before entering the retry loop.
It calls the STT service and serializes the raw segments into
``input_data.raw_segments_json_text``; the agent's user_prompt renders
that JSON inline so the LLM sees real ASR output. ``materialize()`` is
a no-op (transcripts are pure-text artifacts — no binary asset).
"""

from __future__ import annotations

import json
import logging
from typing import Any, TYPE_CHECKING

from ..descriptor import BaseMaterializer, MediaAsset
from inference.generation.transcription_service import TranscriptionBackend

if TYPE_CHECKING:
    from ..base_agent import MaterializeContext
    from .schema import TranscriptionAgentInput

logger = logging.getLogger(__name__)


class TranscriptionMaterializer(BaseMaterializer):
    """Transcribe audio/video via an external STT service."""

    def __init__(self, transcription_service: TranscriptionBackend) -> None:
        self.stt_svc = transcription_service

    async def pre_generate(
        self,
        ctx: "MaterializeContext",
        input_data: "TranscriptionAgentInput",
    ) -> None:
        """Call STT once and seed ``input_data.raw_segments_json_text``.

        Runs before the LLM loop (BaseAgent.run() invokes this exactly
        once per run), so every LLM retry sees the same real ASR output
        without re-paying the STT call.
        """
        result = await self.stt_svc.transcribe(input_data.source_media_path)

        raw_segments = [
            {
                "segment_id": f"seg_{i + 1:03d}",
                "start_time": seg.start,
                "end_time": seg.end,
                "text": seg.text,
            }
            for i, seg in enumerate(result.segments)
        ]
        payload = {
            "language": result.language,
            "segments": raw_segments,
            "full_text": result.full_text,
        }
        input_data.raw_segments_json_text = json.dumps(
            payload, ensure_ascii=False, indent=2
        )
        logger.info(
            "TranscriptionMaterializer.pre_generate: %d segments, "
            "language=%s for task %s",
            len(raw_segments), result.language, ctx.step_id,
        )

    async def materialize(
        self,
        ctx: "MaterializeContext",
        asset_dict: dict[str, Any],
    ) -> list[MediaAsset]:
        """No binary output — transcripts persist as JSON via the
        standard agent pipeline. STT itself already ran in
        ``pre_generate``."""
        return []
