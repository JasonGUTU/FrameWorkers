"""Audio generation service — wraps OpenAI TTS and audio backends.

Called by Assistant as a post-processing step **after** AudioAgent's
JSON plan passes the quality gate.  Flow:

    AudioAgent (LLM plan)
        → Evaluator (quality gate)
        → AudioService.generate_speech() / generate_music() / …   ← this module
        → AssetManager.save_binary()
        → update ``audio_asset.uri`` in the asset dict

Three types of audio content:
  1. **Narration / Dialogue** — OpenAI TTS (``tts-1`` / ``tts-1-hd``).
  2. **Music cues**           — mock (empty WAV); plug in Suno / MusicGen later.
  3. **Ambience beds**        — mock (empty WAV); plug in ElevenLabs SFX later.
"""

from __future__ import annotations

import logging
from typing import Any

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

# Valid OpenAI TTS voices.
_TTS_VOICES = {"alloy", "echo", "fable", "onyx", "nova", "shimmer"}
_DEFAULT_VOICE = "alloy"

# Minimal valid WAV header (44 bytes, 0 data) — used as mock placeholder.
_MOCK_WAV = (
    b"RIFF"
    b"\x24\x00\x00\x00"  # file size - 8  (36 = 0x24 for empty data)
    b"WAVE"
    b"fmt "
    b"\x10\x00\x00\x00"  # chunk size = 16
    b"\x01\x00"  # PCM
    b"\x01\x00"  # mono
    b"\x44\xac\x00\x00"  # 44100 Hz
    b"\x88\x58\x01\x00"  # byte rate
    b"\x02\x00"  # block align
    b"\x10\x00"  # bits per sample
    b"data"
    b"\x00\x00\x00\x00"  # data size = 0
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
        """Lazy-init the OpenAI client."""
        if self._client is None:
            import os

            self._client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        return self._client

    # ------------------------------------------------------------------
    # Narration / Dialogue (OpenAI TTS)
    # ------------------------------------------------------------------

    async def generate_speech(
        self,
        text: str,
        *,
        voice: str | None = None,
        model: str | None = None,
        response_format: str = "wav",
    ) -> bytes:
        """Generate speech audio from text using OpenAI TTS.

        Args:
            text:            The dialogue / narration text to speak.
            voice:           One of alloy, echo, fable, onyx, nova, shimmer.
            model:           ``tts-1`` (fast) or ``tts-1-hd`` (quality).
            response_format: ``wav``, ``mp3``, ``opus``, ``aac``, ``flac``.

        Returns:
            Raw audio bytes in the requested format.
        """
        actual_voice = voice or self.default_voice
        if actual_voice not in _TTS_VOICES:
            logger.warning(
                "Unknown TTS voice '%s' — falling back to %s",
                actual_voice,
                _DEFAULT_VOICE,
            )
            actual_voice = _DEFAULT_VOICE

        logger.info(
            "Generating TTS (voice=%s, fmt=%s): %.80s…",
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
            "TTS generated (%d bytes, %s) for: %.60s…",
            len(audio_bytes),
            response_format,
            text,
        )
        return audio_bytes

    # ------------------------------------------------------------------
    # Music (mock — empty WAV placeholder)
    # ------------------------------------------------------------------

    async def generate_music(
        self,
        *,
        mood: str,
        duration_sec: float,
        scene_id: str = "",
        **kwargs: Any,
    ) -> bytes:
        """Generate a music-cue audio track for a scene.

        Returns an empty WAV placeholder.
        Replace with Suno / MusicGen when available.
        """
        logger.info(
            "[MockMusic] Placeholder music for scene %s (mood=%s, %.1fs)",
            scene_id,
            mood,
            duration_sec,
        )
        return _MOCK_WAV

    # ------------------------------------------------------------------
    # Ambience / SFX (mock — empty WAV placeholder)
    # ------------------------------------------------------------------

    async def generate_ambience(
        self,
        *,
        description: str,
        duration_sec: float,
        scene_id: str = "",
        **kwargs: Any,
    ) -> bytes:
        """Generate an ambient-sound audio track for a scene.

        Returns an empty WAV placeholder.
        Replace with ElevenLabs SFX / Freesound when available.
        """
        logger.info(
            "[MockAmbience] Placeholder ambience for scene %s (%.1fs): %.80s…",
            scene_id,
            duration_sec,
            description,
        )
        return _MOCK_WAV

    # ------------------------------------------------------------------
    # Mix (concatenation — simple fallback; override for real mixing)
    # ------------------------------------------------------------------

    async def mix_scene_audio(
        self,
        *,
        narration_bytes_list: list[bytes],
        music_bytes: bytes | None = None,
        ambience_bytes: bytes | None = None,
        scene_id: str = "",
        duration_sec: float = 0.0,
    ) -> bytes:
        """Mix narration, music, and ambience into a scene audio track.

        Current implementation: returns the concatenation of all raw byte
        segments (not real audio mixing — works as a placeholder because
        all segments share the same WAV format from TTS).
        Override for real audio mixing (pydub / ffmpeg).
        """
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
        # Simple concatenation; all TTS outputs share the same WAV format.
        return b"".join(parts)

    async def assemble_final(
        self,
        *,
        scene_mix_bytes_list: list[bytes],
    ) -> bytes:
        """Assemble scene mixes into the final audio track.

        Current implementation: concatenates all scene mix bytes.
        Override for real audio assembly (ffmpeg concat).
        """
        logger.info("[FinalAssembly] Concatenating %d scene mixes", len(scene_mix_bytes_list))
        if not scene_mix_bytes_list:
            return _MOCK_WAV
        return b"".join(scene_mix_bytes_list)


# =====================================================================
#  Mock service — returns WAV placeholders for all audio types
# =====================================================================


class MockAudioService(AudioService):
    """Mock backend that returns placeholder WAV bytes for every call.

    Use with ``--debug`` to skip real OpenAI TTS API calls during testing.
    """

    def __init__(self, **kwargs: Any) -> None:
        # Skip parent __init__ so we don't need a real OpenAI client.
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
        logger.info("[MockAudioService] Placeholder TTS for: %.80s…", text)
        return _MOCK_WAV
