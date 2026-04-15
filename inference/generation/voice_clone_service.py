"""Voice clone service — clone voice from reference audio and synthesize.

- ``MockVoiceCloneService``: returns placeholder WAV bytes (no credits).
- ``FalVoiceCloneService``: calls fal.ai TTS with voice cloning support.

The ``select_voice_clone_service()`` helper in ``__init__.py`` picks the
backend based on ``FW_USE_REAL_MEDIA_GEN``.
"""

from __future__ import annotations

import base64
import logging
import os
from dataclasses import dataclass
from typing import Any

import httpx

from ._mock_data import MOCK_WAV
from .fal_helpers import (
    LazyHttpxClientMixin,
    extract_fal_media_url,
    fal_subscribe,
    http_download_bytes,
)

logger = logging.getLogger(__name__)


@dataclass
class VoiceProfile:
    voice_id: str = ""
    description: str = ""


class VoiceCloneService:
    """Abstract voice cloning + synthesis service."""

    async def clone(self, audio_path: str) -> VoiceProfile:
        raise NotImplementedError

    async def synthesize(self, voice_id: str, text: str) -> bytes:
        raise NotImplementedError

    async def concat(self, segments: list[bytes]) -> bytes:
        if not segments:
            return MOCK_WAV
        if len(segments) == 1:
            return segments[0]
        return b"".join(segments)


class MockVoiceCloneService(VoiceCloneService):
    """Mock voice clone service that returns placeholder audio."""

    async def clone(self, audio_path: str) -> VoiceProfile:
        logger.info("[MockVoiceClone] Placeholder clone from %s", audio_path)
        return VoiceProfile(voice_id="mock_voice_001", description="Mock cloned voice")

    async def synthesize(self, voice_id: str, text: str) -> bytes:
        logger.info("[MockVoiceClone] Placeholder synthesize: %.60s", text)
        return MOCK_WAV

    async def concat(self, segments: list[bytes]) -> bytes:
        logger.info("[MockVoiceClone] Placeholder concat %d segments", len(segments))
        return MOCK_WAV


class FalVoiceCloneService(VoiceCloneService, LazyHttpxClientMixin):
    """Voice cloning service backed by fal.ai.

    Uses a two-step flow:
    1. ``clone()``: uploads reference audio to fal and gets a voice_id
       (or uses the audio directly as a reference for each synthesis call).
    2. ``synthesize()``: calls a TTS model with the cloned voice reference.
    3. ``concat()``: joins segments via ffmpeg (falls back to byte-join).

    Environment variables:
      FAL_API_KEY           — required for all calls
      FAL_VOICE_CLONE_MODEL — model for voice cloning + synthesis
                              (default: fal-ai/f5-tts)
    """

    def __init__(
        self,
        api_key: str | None = None,
        timeout: float = 180.0,
    ) -> None:
        self._api_key = api_key or os.getenv("FAL_API_KEY", "")
        self.timeout = timeout
        self._http: httpx.AsyncClient | None = None
        self._model = os.getenv("FAL_VOICE_CLONE_MODEL", "").strip()
        if not self._model:
            raise RuntimeError("No voice clone model configured. Set FAL_VOICE_CLONE_MODEL in .env")
        # Stores the reference audio data URL after clone() for use in synthesize()
        self._ref_audio_data_url: str = ""

    async def clone(self, audio_path: str) -> VoiceProfile:
        """Extract voice characteristics by storing the reference audio.

        For fal.ai voice clone models (F5-TTS, etc.), the reference audio
        is passed alongside each synthesis call rather than registered
        upfront. This method stores the audio as a data URL.
        """
        if not audio_path or not os.path.isfile(audio_path):
            logger.warning("[fal.ai] Voice clone: reference audio not found: %s", audio_path)
            return VoiceProfile(voice_id="", description="missing reference")

        with open(audio_path, "rb") as fh:
            audio_bytes = fh.read()

        # Detect mime type
        mime = "audio/wav"
        if audio_path.endswith(".mp3"):
            mime = "audio/mpeg"
        elif audio_path.endswith(".flac"):
            mime = "audio/flac"

        b64 = base64.b64encode(audio_bytes).decode()
        self._ref_audio_data_url = f"data:{mime};base64,{b64}"

        voice_id = f"clone_{os.path.basename(audio_path)}"
        logger.info("[fal.ai] Voice cloned from %s (%d bytes), id=%s", audio_path, len(audio_bytes), voice_id)
        return VoiceProfile(
            voice_id=voice_id,
            description=f"Cloned from {os.path.basename(audio_path)}",
        )

    async def synthesize(self, voice_id: str, text: str) -> bytes:
        """Synthesize speech in the cloned voice using fal.ai.

        Passes the stored reference audio alongside the text to the
        voice clone TTS model.
        """
        if not self._ref_audio_data_url:
            logger.warning("[fal.ai] No reference audio stored, returning placeholder")
            return MOCK_WAV

        logger.info("[fal.ai] Voice synthesis: model=%s, text=%.60s", self._model, text)

        arguments: dict[str, Any] = {
            "gen_text": text,
            "ref_audio_url": self._ref_audio_data_url,
            "ref_text": "",  # empty = auto-detect reference text
            "model_type": "F5-TTS",
        }

        result = await fal_subscribe(self._api_key, self._model, arguments)
        audio_url = extract_fal_media_url(result, media_type="audio")
        audio_bytes = await http_download_bytes(self.http, audio_url)
        logger.info("[fal.ai] Voice synthesis complete: %d bytes", len(audio_bytes))
        return audio_bytes

    async def concat(self, segments: list[bytes]) -> bytes:
        """Concatenate audio segments via ffmpeg."""
        from .audio_generators.service import AudioService
        if not segments:
            return MOCK_WAV
        if len(segments) == 1:
            return segments[0]

        joined = AudioService._ffmpeg_concat(segments)
        if joined:
            return joined
        # Fallback: return longest segment
        logger.warning("[fal.ai] Audio concat via ffmpeg failed, returning longest segment")
        return max(segments, key=len)
