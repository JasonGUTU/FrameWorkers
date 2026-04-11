"""Unit tests for AudioService's speaker-id mapping and audit payload.

Covers the two behaviors that used to leak into ``AudioMaterializer``:

* ``_speaker_id_to_voice``: the speaker-identifier → concrete TTS voice
  mapping. The materializer used to hard-code the OpenAI voice roster;
  it now lives on the service so each backend can implement its own.
* ``AudioGenerationResult.resolved_payload``: the audit dict the
  materializer writes into ``audio_generation_prompt``. The
  materializer used to build this dict itself while peeking at
  ``self.audio_svc.tts_model``; the service now returns it alongside
  the bytes.
"""

from __future__ import annotations

import asyncio

from inference.generation.audio_generators.service import (
    AudioService,
    FalAudioService,
    MockAudioService,
)
from inference.generation.audio_generators.types import AudioGenerationResult


# ---------------------------------------------------------------------------
# _speaker_id_to_voice
# ---------------------------------------------------------------------------


def test_base_speaker_id_to_voice_is_deterministic_and_in_roster() -> None:
    """Same speaker_id always picks the same voice from the sorted roster."""
    svc = AudioService()
    voice_a1 = svc._speaker_id_to_voice("Narrator")
    voice_a2 = svc._speaker_id_to_voice("Narrator")
    voice_b = svc._speaker_id_to_voice("Elias")
    # Deterministic
    assert voice_a1 == voice_a2
    # Within the OpenAI voice roster
    assert voice_a1 in {"alloy", "echo", "fable", "nova", "onyx", "shimmer"}
    assert voice_b in {"alloy", "echo", "fable", "nova", "onyx", "shimmer"}


def test_base_speaker_id_to_voice_empty_returns_default() -> None:
    svc = AudioService()
    assert svc._speaker_id_to_voice("") == svc.default_voice


def test_mock_speaker_id_to_voice_returns_mock_regardless_of_input() -> None:
    """Mock backend has no real voice roster — every speaker maps to ``mock``."""
    svc = MockAudioService()
    assert svc._speaker_id_to_voice("anyone") == "mock"
    assert svc._speaker_id_to_voice("") == "mock"


def test_fal_speaker_id_to_voice_passes_identifier_through() -> None:
    """Fal's voice namespace depends on the concrete model; pass the id through."""
    svc = FalAudioService(api_key="test")
    assert svc._speaker_id_to_voice("alloy") == "alloy"
    assert svc._speaker_id_to_voice("Elias") == "Elias"
    assert svc._speaker_id_to_voice("") == svc.default_voice


# ---------------------------------------------------------------------------
# generate_speech — returns AudioGenerationResult with audit payload
# ---------------------------------------------------------------------------


def test_mock_generate_speech_returns_result_with_audit_payload() -> None:
    svc = MockAudioService()
    result = asyncio.run(
        svc.generate_speech("Hello world.", speaker_id="Narrator")
    )
    assert isinstance(result, AudioGenerationResult)
    assert result.bytes  # non-empty placeholder
    payload = result.resolved_payload
    assert payload["kind"] == "tts"
    assert payload["model"] == "mock"
    assert payload["voice"] == "mock"
    assert payload["text"] == "Hello world."


def test_mock_generate_speech_explicit_voice_overrides_speaker_id() -> None:
    """Caller can still pass ``voice=`` to bypass the speaker mapping."""
    svc = MockAudioService()
    result = asyncio.run(
        svc.generate_speech("Text", speaker_id="ignored", voice="custom_voice")
    )
    assert result.resolved_payload["voice"] == "custom_voice"


# ---------------------------------------------------------------------------
# generate_music / generate_ambience — audit payload format
# ---------------------------------------------------------------------------


def test_mock_generate_music_returns_audit_payload() -> None:
    svc = MockAudioService()
    result = asyncio.run(
        svc.generate_music(mood="calm", scene_id="sc_001", duration_sec=3.0)
    )
    assert result.bytes
    payload = result.resolved_payload
    assert payload["kind"] == "music"
    assert payload["mood"] == "calm"
    assert payload["scene_id"] == "sc_001"
    assert payload["duration_sec"] == 3.0


def test_mock_generate_ambience_returns_audit_payload() -> None:
    svc = MockAudioService()
    result = asyncio.run(
        svc.generate_ambience(description="wind through trees", scene_id="sc_002")
    )
    assert result.bytes
    payload = result.resolved_payload
    assert payload["kind"] == "ambience"
    assert payload["description"] == "wind through trees"
    assert payload["scene_id"] == "sc_002"
