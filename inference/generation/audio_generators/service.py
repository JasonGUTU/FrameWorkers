"""Reusable audio backend services for agents."""

from __future__ import annotations

import logging
import os
import subprocess
import tempfile
from typing import Any

import httpx
from openai import AsyncOpenAI

from .._mock_data import MOCK_WAV
from ..fal_helpers import (
    LazyHttpxClientMixin,
    extract_fal_media_url,
    fal_subscribe,
    http_download_bytes,
)
from .types import AudioGenerationResult

logger = logging.getLogger(__name__)

# Fixed voice roster for the OpenAI-backed TTS path. Listed as a sorted
# tuple so ``_speaker_id_to_voice`` produces a stable deterministic
# mapping across runs (sets aren't order-preserving for hashing).
_TTS_VOICES: tuple[str, ...] = ("alloy", "echo", "fable", "nova", "onyx", "shimmer")
_DEFAULT_VOICE = "alloy"


def _is_mock_wav(data: bytes | None) -> bool:
    """True if ``data`` is the silent ``MOCK_WAV`` placeholder (or so short
    it can't possibly carry real audio).

    Callers drop placeholder inputs before handing the rest to ffmpeg so
    the mix is built only from real audio and placeholders never end up
    corrupting the output stream.
    """
    if not data:
        return True
    if data == MOCK_WAV:
        return True
    # Anything shorter than 200 bytes can't possibly contain real audio
    # samples — a usable WAV body needs at least a few hundred bytes.
    return len(data) < 200


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

    def _speaker_id_to_voice(self, speaker_id: str) -> str:
        """Deterministic mapping from an abstract speaker identifier to a
        concrete TTS voice name.

        The same ``speaker_id`` always picks the same voice within a
        pipeline run, so a narrator or character doesn't swap voices
        between scenes. Uses a stable hash over the sorted voice roster
        so the mapping is reproducible. Different TTS backends override
        this to use their own voice namespace (fal models, etc.).
        """
        if not speaker_id:
            return self.default_voice
        return _TTS_VOICES[hash(speaker_id) % len(_TTS_VOICES)]

    async def generate_speech(
        self,
        text: str,
        *,
        speaker_id: str = "",
        voice: str | None = None,
        model: str | None = None,
        response_format: str = "wav",
    ) -> AudioGenerationResult:
        # Explicit ``voice=`` still wins; otherwise derive from speaker_id.
        if voice is None:
            voice = self._speaker_id_to_voice(speaker_id)
        actual_voice = voice or self.default_voice
        if actual_voice not in _TTS_VOICES:
            logger.warning(
                "Unknown TTS voice '%s' — falling back to %s",
                actual_voice,
                _DEFAULT_VOICE,
            )
            actual_voice = _DEFAULT_VOICE

        actual_model = model or self.tts_model
        logger.info(
            "Generating TTS (voice=%s, fmt=%s): %.80s...",
            actual_voice,
            response_format,
            text,
        )
        response = await self.client.audio.speech.create(
            model=actual_model,
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
        return AudioGenerationResult(
            bytes=audio_bytes,
            resolved_payload={
                "kind": "tts",
                "model": actual_model,
                "voice": actual_voice,
                "text": text,
            },
        )

    async def generate_music(
        self,
        *,
        mood: str,
        duration_sec: float = 0.0,
        scene_id: str = "",
        **kwargs: Any,
    ) -> AudioGenerationResult:
        logger.info(
            "[MockMusic] Placeholder music for scene %s (mood=%s)",
            scene_id,
            mood,
        )
        return AudioGenerationResult(
            bytes=MOCK_WAV,
            resolved_payload={
                "kind": "music",
                "mood": mood,
                "scene_id": scene_id,
                "duration_sec": duration_sec,
            },
        )

    async def generate_ambience(
        self,
        *,
        description: str,
        duration_sec: float = 0.0,
        scene_id: str = "",
        **kwargs: Any,
    ) -> AudioGenerationResult:
        logger.info(
            "[MockAmbience] Placeholder ambience for scene %s: %.80s...",
            scene_id,
            description,
        )
        return AudioGenerationResult(
            bytes=MOCK_WAV,
            resolved_payload={
                "kind": "ambience",
                "description": description,
                "scene_id": scene_id,
                "duration_sec": duration_sec,
            },
        )

    # ------------------------------------------------------------------
    # ffmpeg helpers
    # ------------------------------------------------------------------

    # Upstream TTS / music / ambience services return mixed formats (fal
    # F5-TTS ships 32 kHz mono MP3 inside a ``.wav`` filename; stable-audio
    # ships 44.1 kHz stereo PCM; OpenAI TTS ships 24 kHz). ffmpeg's ``amix``
    # and ``concat`` refuse to operate on sources with differing sample
    # rates or channel layouts, so we normalise every input through
    # ``aresample`` + ``aformat`` before the operation.
    _NORM_FILTER = "aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo"

    @staticmethod
    def _ffmpeg_amix(inputs: list[bytes]) -> bytes | None:
        n = len(inputs)
        norm = "".join(f"[{i}:a]{AudioService._NORM_FILTER}[a{i}];" for i in range(n))
        mix = "".join(f"[a{i}]" for i in range(n)) + f"amix=inputs={n}:duration=longest:dropout_transition=0[out]"
        return AudioService._ffmpeg_run(inputs, filter_complex=norm + mix)

    @staticmethod
    def _ffmpeg_concat(inputs: list[bytes]) -> bytes | None:
        n = len(inputs)
        norm = "".join(f"[{i}:a]{AudioService._NORM_FILTER}[a{i}];" for i in range(n))
        cat = "".join(f"[a{i}]" for i in range(n)) + f"concat=n={n}:v=0:a=1[out]"
        return AudioService._ffmpeg_run(inputs, filter_complex=norm + cat)

    @staticmethod
    def _ffmpeg_run(inputs: list[bytes], *, filter_complex: str) -> bytes | None:
        """Shared ffmpeg runner: write inputs → run filter → read output → cleanup.

        Inputs are written with a ``.wav`` suffix but the container format is
        auto-detected by ffmpeg, so MP3-inside-.wav blobs (fal F5-TTS ships
        these) decode correctly.
        """
        temp_dir = tempfile.mkdtemp(prefix="fw_audio_")
        in_paths = [os.path.join(temp_dir, f"in_{i}.wav") for i in range(len(inputs))]
        out_path = os.path.join(temp_dir, "out.wav")
        try:
            for path, blob in zip(in_paths, inputs):
                with open(path, "wb") as fh:
                    fh.write(blob)
            cmd: list[str] = ["ffmpeg", "-y"]
            for p in in_paths:
                cmd += ["-i", p]
            cmd += [
                "-filter_complex", filter_complex,
                "-map", "[out]",
                "-c:a", "pcm_s16le",
                "-ar", "44100",
                "-ac", "2",
                out_path,
            ]
            proc = subprocess.run(
                cmd,
                capture_output=True,
                check=False,
                text=True,
                timeout=120,
            )
            if proc.returncode != 0 or not os.path.exists(out_path):
                logger.warning(
                    "ffmpeg audio op failed (code=%s): %s",
                    proc.returncode,
                    (proc.stderr or "").strip()[:300],
                )
                return None
            with open(out_path, "rb") as fh:
                return fh.read()
        except FileNotFoundError:
            logger.warning("ffmpeg not found, audio op cannot proceed")
            return None
        except Exception as exc:
            logger.warning("ffmpeg audio op error: %s", exc)
            return None
        finally:
            for p in in_paths + [out_path]:
                if os.path.exists(p):
                    try:
                        os.remove(p)
                    except OSError:
                        pass
            try:
                os.rmdir(temp_dir)
            except OSError:
                pass

    async def mux_audio_with_video(
        self,
        *,
        video_bytes: bytes,
        audio_bytes: bytes,
    ) -> bytes:
        """Mux a final audio track into final video bytes.

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

    def _speaker_id_to_voice(self, speaker_id: str) -> str:
        # Mock has no voice roster — every speaker maps to ``"mock"`` so
        # the audit record is still meaningful (caller sees the speaker
        # was recognized) without touching the OpenAI voice table.
        return "mock"

    async def generate_speech(
        self,
        text: str,
        *,
        speaker_id: str = "",
        voice: str | None = None,
        model: str | None = None,
        response_format: str = "wav",
    ) -> AudioGenerationResult:
        logger.info("[MockAudioService] Placeholder TTS for: %.80s...", text)
        return AudioGenerationResult(
            bytes=MOCK_WAV,
            resolved_payload={
                "kind": "tts",
                "model": self.tts_model,
                "voice": voice or self._speaker_id_to_voice(speaker_id),
                "text": text,
            },
        )

    async def mux_audio_with_video(
        self,
        *,
        video_bytes: bytes,
        audio_bytes: bytes,
    ) -> bytes:
        logger.info("[MockAudioService] Placeholder mux for final delivery")
        return video_bytes


class FalAudioService(AudioService, LazyHttpxClientMixin):
    """Audio generation service backed by fal.ai."""

    def __init__(
        self,
        api_key: str | None = None,
        tts_model: str | None = None,
        timeout: float = 180.0,
    ) -> None:
        self._api_key = api_key or os.getenv("FAL_API_KEY", "")
        self.tts_model = tts_model or os.getenv("FAL_TTS_MODEL", "")
        if not self.tts_model:
            raise RuntimeError("No TTS model configured. Set FAL_TTS_MODEL in .env")
        self.default_voice = "default"
        self.timeout = timeout
        self._http: httpx.AsyncClient | None = None
        self._client = None

    def _speaker_id_to_voice(self, speaker_id: str) -> str:
        # fal TTS models accept provider-specific voice strings. Until a
        # concrete fal voice roster is wired in, we pass the speaker_id
        # through verbatim so the caller can opt into a specific voice,
        # and fall back to ``self.default_voice`` when no speaker_id is set.
        return speaker_id or self.default_voice

    async def generate_speech(
        self,
        text: str,
        *,
        speaker_id: str = "",
        voice: str | None = None,
        model: str | None = None,
        response_format: str = "wav",
    ) -> AudioGenerationResult:
        model_id = model or self.tts_model
        actual_voice = voice if voice is not None else self._speaker_id_to_voice(speaker_id)
        arguments: dict[str, Any] = {"text": text}
        if actual_voice:
            arguments["voice"] = actual_voice
        if response_format:
            arguments["format"] = response_format

        logger.info("[fal.ai] Generating speech with model=%s", model_id)
        result = await fal_subscribe(self._api_key, model_id, arguments)
        audio_url = extract_fal_media_url(result, media_type="audio")
        audio_bytes = await http_download_bytes(self.http, audio_url)
        logger.info("[fal.ai] TTS generated (%d bytes)", len(audio_bytes))
        return AudioGenerationResult(
            bytes=audio_bytes,
            resolved_payload={
                "kind": "tts",
                "model": model_id,
                "voice": actual_voice,
                "text": text,
            },
        )

    async def generate_music(
        self,
        *,
        mood: str,
        duration_sec: float = 0.0,
        scene_id: str = "",
        **kwargs: Any,
    ) -> AudioGenerationResult:
        """Generate background music via fal.ai audio generation model."""
        model_id = os.getenv("FAL_MUSIC_MODEL", "").strip()
        if not model_id:
            raise RuntimeError("No music model configured. Set FAL_MUSIC_MODEL in .env")
        prompt = f"Background music: {mood}. Instrumental, no vocals."
        arguments: dict[str, Any] = {"prompt": prompt}
        if duration_sec > 0:
            # fal-ai/stable-audio requires an integer seconds_total
            arguments["seconds_total"] = int(min(duration_sec, 30.0))

        logger.info("[fal.ai] Generating music: model=%s, mood=%s", model_id, mood)
        result = await fal_subscribe(self._api_key, model_id, arguments)
        audio_url = extract_fal_media_url(result, media_type="audio")
        audio_bytes = await http_download_bytes(self.http, audio_url)
        logger.info("[fal.ai] Music generated (%d bytes)", len(audio_bytes))
        return AudioGenerationResult(
            bytes=audio_bytes,
            resolved_payload={
                "kind": "music",
                "model": model_id,
                "mood": mood,
                "scene_id": scene_id,
                "duration_sec": duration_sec,
            },
        )

    async def generate_ambience(
        self,
        *,
        description: str,
        duration_sec: float = 0.0,
        scene_id: str = "",
        **kwargs: Any,
    ) -> AudioGenerationResult:
        """Generate ambient sound via fal.ai audio generation model."""
        model_id = os.getenv("FAL_AMBIENCE_MODEL", "").strip()
        if not model_id:
            raise RuntimeError("No ambience model configured. Set FAL_AMBIENCE_MODEL in .env")
        prompt = f"Ambient environmental sound: {description}. No music, no speech."
        arguments: dict[str, Any] = {"prompt": prompt}
        if duration_sec > 0:
            # fal-ai/stable-audio requires an integer seconds_total
            arguments["seconds_total"] = int(min(duration_sec, 30.0))

        logger.info("[fal.ai] Generating ambience: model=%s, desc=%s", model_id, description[:60])
        result = await fal_subscribe(self._api_key, model_id, arguments)
        audio_url = extract_fal_media_url(result, media_type="audio")
        audio_bytes = await http_download_bytes(self.http, audio_url)
        logger.info("[fal.ai] Ambience generated (%d bytes)", len(audio_bytes))
        return AudioGenerationResult(
            bytes=audio_bytes,
            resolved_payload={
                "kind": "ambience",
                "model": model_id,
                "description": description,
                "scene_id": scene_id,
                "duration_sec": duration_sec,
            },
        )
