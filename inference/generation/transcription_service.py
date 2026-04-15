"""Transcription service — speech-to-text.

Backends:
- ``TranscriptionService``: OpenAI Whisper API (requires OPENAI_API_KEY)
- ``FalTranscriptionService``: fal.ai Whisper (requires FAL_API_KEY)
- ``MockTranscriptionService``: placeholder segments (no API call)
"""

from __future__ import annotations

import base64
import logging
import os
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class TranscriptSegment:
    start: float = 0.0
    end: float = 0.0
    text: str = ""


@dataclass
class TranscriptionResult:
    language: str = ""
    segments: list[TranscriptSegment] = field(default_factory=list)
    full_text: str = ""


class TranscriptionService:
    """Speech-to-text service backed by OpenAI Whisper API."""

    def __init__(
        self,
        client: "AsyncOpenAI | None" = None,
        model: str = "whisper-1",
    ) -> None:
        self._client = client
        self.model = model

    @property
    def client(self):
        if self._client is None:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        return self._client

    async def transcribe(self, media_path: str) -> TranscriptionResult:
        if not media_path or not os.path.isfile(media_path):
            logger.warning("TranscriptionService: file not found: %s", media_path)
            return TranscriptionResult()

        logger.info("Transcribing %s with model %s", media_path, self.model)

        with open(media_path, "rb") as audio_file:
            response = await self.client.audio.transcriptions.create(
                model=self.model,
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["segment"],
            )

        segments = []
        for seg in getattr(response, "segments", []) or []:
            segments.append(TranscriptSegment(
                start=seg.get("start", 0.0) if isinstance(seg, dict) else getattr(seg, "start", 0.0),
                end=seg.get("end", 0.0) if isinstance(seg, dict) else getattr(seg, "end", 0.0),
                text=(seg.get("text", "") if isinstance(seg, dict) else getattr(seg, "text", "")).strip(),
            ))

        full_text = getattr(response, "text", "") or ""
        language = getattr(response, "language", "") or ""

        return TranscriptionResult(language=language, segments=segments, full_text=full_text)


class FalTranscriptionService:
    """Speech-to-text service backed by fal.ai Whisper.

    Environment variables:
      FAL_API_KEY              — required
      FAL_WHISPER_MODEL        — model id (default: fal-ai/whisper)
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        self._api_key = api_key or os.getenv("FAL_API_KEY", "")
        self._model = (model or os.getenv("FAL_WHISPER_MODEL", "")).strip()
        if not self._model:
            raise RuntimeError("No whisper model configured. Set FAL_WHISPER_MODEL in .env")

    async def transcribe(self, media_path: str) -> TranscriptionResult:
        if not media_path or not os.path.isfile(media_path):
            logger.warning("FalTranscriptionService: file not found: %s", media_path)
            return TranscriptionResult()

        import asyncio
        from .fal_helpers import fal_subscribe

        logger.info("[fal.ai] Transcribing %s with model %s", media_path, self._model)

        # fal.ai Whisper requires a hosted URL, not a data URL.
        # Use fal_client.upload to get a temporary hosted URL.
        # fal_client reads FAL_KEY from env for upload auth.
        previous_key = os.getenv("FAL_KEY")
        if self._api_key:
            os.environ["FAL_KEY"] = self._api_key
        try:
            import fal_client
            audio_url = await asyncio.to_thread(fal_client.upload_file, media_path)
        finally:
            if previous_key is None:
                os.environ.pop("FAL_KEY", None)
            else:
                os.environ["FAL_KEY"] = previous_key
        logger.info("[fal.ai] Uploaded audio to: %s", audio_url)

        arguments: dict[str, Any] = {
            "audio_url": audio_url,
            "task": "transcribe",
            "chunk_level": "segment",
        }

        result = await fal_subscribe(self._api_key, self._model, arguments)

        # Parse fal.ai Whisper response
        chunks = result.get("chunks") or result.get("segments") or []
        full_text = result.get("text", "")
        language = result.get("language", "") or result.get("inferred_language", "") or ""

        segments = []
        for chunk in chunks:
            if isinstance(chunk, dict):
                start = chunk.get("start", chunk.get("timestamp", [0, 0])[0] if isinstance(chunk.get("timestamp"), list) else 0.0)
                end = chunk.get("end", chunk.get("timestamp", [0, 0])[1] if isinstance(chunk.get("timestamp"), list) else 0.0)
                text = chunk.get("text", "").strip()
                if text:
                    segments.append(TranscriptSegment(start=float(start), end=float(end), text=text))

        if not full_text and segments:
            full_text = " ".join(s.text for s in segments)

        logger.info("[fal.ai] Transcription complete: %d segments, language=%s", len(segments), language)
        return TranscriptionResult(language=language, segments=segments, full_text=full_text)


class MockTranscriptionService:
    """Mock transcription that returns placeholder segments."""

    async def transcribe(self, media_path: str) -> TranscriptionResult:
        logger.info("[MockTranscription] Placeholder transcription for %s", media_path)
        return TranscriptionResult(
            language="en",
            segments=[
                TranscriptSegment(start=0.0, end=3.0, text="This is a placeholder transcription."),
                TranscriptSegment(start=3.5, end=6.0, text="The real service uses OpenAI Whisper."),
            ],
            full_text="This is a placeholder transcription. The real service uses OpenAI Whisper.",
        )
