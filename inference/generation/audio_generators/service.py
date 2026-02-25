"""Reusable audio backend services for agents."""

from __future__ import annotations

import logging
import os
from typing import Any

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

_TTS_VOICES = {"alloy", "echo", "fable", "onyx", "nova", "shimmer"}
_DEFAULT_VOICE = "alloy"

_MOCK_WAV = (
    b"RIFF"
    b"\x24\x00\x00\x00"
    b"WAVE"
    b"fmt "
    b"\x10\x00\x00\x00"
    b"\x01\x00"
    b"\x01\x00"
    b"\x44\xac\x00\x00"
    b"\x88\x58\x01\x00"
    b"\x02\x00"
    b"\x10\x00"
    b"data"
    b"\x00\x00\x00\x00"
)


class AudioService:
    """Audio generation service backed by OpenAI TTS + pluggable music/SFX."""

    def __init__(
        self,
        client: AsyncOpenAI | None = None,
        tts_model: str = "tts-1",
        default_voice: str = _DEFAULT_VOICE,
    ) -> None:
        self._client = client
        self.tts_model = tts_model
        self.default_voice = default_voice

    @property
    def client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        return self._client

    async def generate_speech(
        self,
        text: str,
        *,
        voice: str | None = None,
        model: str | None = None,
        response_format: str = "wav",
    ) -> bytes:
        actual_voice = voice or self.default_voice
        if actual_voice not in _TTS_VOICES:
            logger.warning(
                "Unknown TTS voice '%s' — falling back to %s",
                actual_voice,
                _DEFAULT_VOICE,
            )
            actual_voice = _DEFAULT_VOICE

        logger.info(
            "Generating TTS (voice=%s, fmt=%s): %.80s...",
            actual_voice,
            response_format,
            text,
        )
        response = await self.client.audio.speech.create(
            model=model or self.tts_model,
            voice=actual_voice,
            input=text,
            response_format=response_format,
        )
        audio_bytes = response.content
        logger.info(
            "TTS generated (%d bytes, %s) for: %.60s...",
            len(audio_bytes),
            response_format,
            text,
        )
        return audio_bytes

    async def generate_music(
        self,
        *,
        mood: str,
        duration_sec: float,
        scene_id: str = "",
        **kwargs: Any,
    ) -> bytes:
        logger.info(
            "[MockMusic] Placeholder music for scene %s (mood=%s, %.1fs)",
            scene_id,
            mood,
            duration_sec,
        )
        return _MOCK_WAV

    async def generate_ambience(
        self,
        *,
        description: str,
        duration_sec: float,
        scene_id: str = "",
        **kwargs: Any,
    ) -> bytes:
        logger.info(
            "[MockAmbience] Placeholder ambience for scene %s (%.1fs): %.80s...",
            scene_id,
            duration_sec,
            description,
        )
        return _MOCK_WAV

    async def mix_scene_audio(
        self,
        *,
        narration_bytes_list: list[bytes],
        music_bytes: bytes | None = None,
        ambience_bytes: bytes | None = None,
        scene_id: str = "",
        duration_sec: float = 0.0,
    ) -> bytes:
        logger.info(
            "[Mix] Concatenating audio segments for scene %s (%.1fs)",
            scene_id,
            duration_sec,
        )
        parts: list[bytes] = []
        parts.extend(narration_bytes_list)
        if music_bytes:
            parts.append(music_bytes)
        if ambience_bytes:
            parts.append(ambience_bytes)
        if not parts:
            return _MOCK_WAV
        return b"".join(parts)

    async def assemble_final(
        self,
        *,
        scene_mix_bytes_list: list[bytes],
    ) -> bytes:
        logger.info("[FinalAssembly] Concatenating %d scene mixes", len(scene_mix_bytes_list))
        if not scene_mix_bytes_list:
            return _MOCK_WAV
        return b"".join(scene_mix_bytes_list)


class MockAudioService(AudioService):
    """Mock backend that returns placeholder WAV bytes for every call."""

    def __init__(self, **kwargs: Any) -> None:
        self.tts_model = "mock"
        self.default_voice = "mock"
        self._client = None  # type: ignore[assignment]

    async def generate_speech(
        self,
        text: str,
        *,
        voice: str | None = None,
        model: str | None = None,
        response_format: str = "wav",
    ) -> bytes:
        logger.info("[MockAudioService] Placeholder TTS for: %.80s...", text)
        return _MOCK_WAV
