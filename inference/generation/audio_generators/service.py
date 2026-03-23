"""Reusable audio backend services for agents."""

from __future__ import annotations

import asyncio
import logging
import os
import subprocess
import tempfile
from typing import Any

import httpx
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

    async def mux_audio_with_video(
        self,
        *,
        video_bytes: bytes,
        audio_bytes: bytes,
    ) -> bytes:
        """Mux final narration/music track into final video bytes.

        Uses ffmpeg when available. Falls back to original video bytes if muxing
        fails so pipeline can continue while still returning a playable file.
        """
        if not video_bytes or not audio_bytes:
            return video_bytes

        temp_dir = tempfile.mkdtemp(prefix="fw_mux_")
        video_path = os.path.join(temp_dir, "video.mp4")
        audio_path = os.path.join(temp_dir, "audio.wav")
        out_path = os.path.join(temp_dir, "muxed.mp4")
        try:
            with open(video_path, "wb") as fh:
                fh.write(video_bytes)
            with open(audio_path, "wb") as fh:
                fh.write(audio_bytes)

            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                video_path,
                "-i",
                audio_path,
                "-filter_complex",
                "[1:a]apad[aout]",
                "-map",
                "0:v:0",
                "-map",
                "[aout]",
                "-c:v",
                "copy",
                "-c:a",
                "aac",
                "-shortest",
                "-movflags",
                "+faststart",
                "-fflags",
                "+genpts",
                "-max_interleave_delta",
                "0",
                out_path,
            ]
            proc = subprocess.run(
                cmd,
                capture_output=True,
                check=False,
                text=True,
                timeout=60,
            )
            if proc.returncode != 0 or not os.path.exists(out_path):
                logger.warning(
                    "ffmpeg mux failed (code=%s), keeping original video: %s",
                    proc.returncode,
                    (proc.stderr or "").strip()[:300],
                )
                return video_bytes
            with open(out_path, "rb") as fh:
                return fh.read()
        except FileNotFoundError:
            logger.warning("ffmpeg not found, skipping mux and keeping original video")
            return video_bytes
        except Exception as exc:
            logger.warning("Mux error, keeping original video: %s", exc)
            return video_bytes
        finally:
            for p in (video_path, audio_path, out_path):
                if os.path.exists(p):
                    try:
                        os.remove(p)
                    except OSError:
                        pass
            try:
                os.rmdir(temp_dir)
            except OSError:
                pass


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

    async def mux_audio_with_video(
        self,
        *,
        video_bytes: bytes,
        audio_bytes: bytes,
    ) -> bytes:
        logger.info("[MockAudioService] Placeholder mux for final delivery")
        return video_bytes


class FalAudioService(AudioService):
    """Audio generation service backed by fal.ai."""

    def __init__(
        self,
        api_key: str | None = None,
        tts_model: str | None = None,
        timeout: float = 180.0,
    ) -> None:
        self._api_key = api_key or os.getenv("FAL_API_KEY", "")
        self.tts_model = tts_model or os.getenv(
            "FAL_TTS_MODEL",
            "fal-ai/minimax/speech-02-turbo",
        )
        self.default_voice = "default"
        self.timeout = timeout
        self._http: httpx.AsyncClient | None = None
        self._client = None

    @property
    def http(self) -> httpx.AsyncClient:
        if self._http is None or self._http.is_closed:
            self._http = httpx.AsyncClient(timeout=self.timeout)
        return self._http

    async def generate_speech(
        self,
        text: str,
        *,
        voice: str | None = None,
        model: str | None = None,
        response_format: str = "wav",
    ) -> bytes:
        model_id = model or self.tts_model
        arguments: dict[str, Any] = {"text": text}
        if voice:
            arguments["voice"] = voice
        if response_format:
            arguments["format"] = response_format

        logger.info("[fal.ai] Generating speech with model=%s", model_id)
        result = await self._submit(model_id=model_id, arguments=arguments)
        audio_url = self._extract_audio_url(result)
        audio_bytes = await self._download_binary(audio_url)
        logger.info("[fal.ai] TTS generated (%d bytes)", len(audio_bytes))
        return audio_bytes

    async def _submit(self, *, model_id: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if not self._api_key:
            raise RuntimeError("FAL_API_KEY is required for FalAudioService")
        try:
            import fal_client
        except ImportError as exc:
            raise RuntimeError("fal-client is required. Install with `pip install fal-client`.") from exc

        previous = os.getenv("FAL_KEY")
        os.environ["FAL_KEY"] = self._api_key
        try:
            result = await asyncio.to_thread(
                fal_client.subscribe,
                model_id,
                arguments=arguments,
                with_logs=False,
            )
            if not isinstance(result, dict):
                raise RuntimeError(f"Unexpected fal.ai response type: {type(result).__name__}")
            return result
        finally:
            if previous is None:
                os.environ.pop("FAL_KEY", None)
            else:
                os.environ["FAL_KEY"] = previous

    async def _download_binary(self, url: str) -> bytes:
        resp = await self.http.get(url)
        resp.raise_for_status()
        return resp.content

    @staticmethod
    def _extract_audio_url(result: dict[str, Any]) -> str:
        audio_obj = result.get("audio")
        if isinstance(audio_obj, dict):
            url = audio_obj.get("url")
            if isinstance(url, str) and url:
                return url

        audios = result.get("audios")
        if isinstance(audios, list) and audios:
            first = audios[0]
            if isinstance(first, dict):
                url = first.get("url")
                if isinstance(url, str) and url:
                    return url

        audio_file = result.get("audio_file")
        if isinstance(audio_file, dict):
            url = audio_file.get("url")
            if isinstance(url, str) and url:
                return url

        direct_url = result.get("audio_url") or result.get("url")
        if isinstance(direct_url, str) and direct_url:
            return direct_url

        raise RuntimeError(f"No audio URL found in fal.ai response keys={list(result.keys())}")
