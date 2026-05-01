"""Tiny placeholder media payloads used by ``Mock*Service`` implementations.

These are valid-but-empty bytes for the three media kinds the framework
supports — small enough to ship inline, valid enough that downstream
ffmpeg/decoders won't choke on them in dry-run / mock pipelines.
"""

from __future__ import annotations

# 1x1 transparent PNG (smallest valid PNG).
MOCK_PNG = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
    b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
    b"\r\n\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)

# Minimal MP4 ftyp header — just enough so callers can detect "this is mp4".
MOCK_MP4_HEADER = (
    b"\x00\x00\x00\x1c"
    b"ftyp"
    b"isom"
    b"\x00\x00\x02\x00"
    b"isomiso2mp41"
)

# Empty 16-bit / 44.1kHz mono RIFF WAVE container (44-byte header, no samples).
# Kept for backward-compatibility callers that don't care about duration
# (e.g. mux-audio-with-video stubs). Most TTS / music / ambience callsites
# should use ``mock_wav_silence(duration_sec)`` instead — a 0-sample WAV
# parses to ``duration == 0`` and breaks downstream timing math (e.g.
# NarratorMaterializer would collapse every clip to ``end_sec == start_sec``).
MOCK_WAV = (
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


import io as _io
import wave as _wave

_MOCK_WAV_SAMPLE_RATE = 44100
_MOCK_WAV_CHANNELS = 1
_MOCK_WAV_SAMPLE_WIDTH = 2


def mock_wav_silence(duration_sec: float) -> bytes:
    """Build a valid silent 16-bit / 44.1 kHz mono WAV of the given duration.

    Use this from ``Mock*Service`` audio generators that need to honor a
    requested duration. Returning 0-sample audio (the bare ``MOCK_WAV``
    constant) is decoder-valid but breaks any downstream that measures
    duration from the bytes — see NarratorMaterializer._audio_duration_sec
    and the rationale at ``narrator/materializer.py:60-65`` for the
    real-world incident this prevents.
    """
    n_frames = max(0, int(round(duration_sec * _MOCK_WAV_SAMPLE_RATE)))
    buf = _io.BytesIO()
    with _wave.open(buf, "wb") as wf:
        wf.setnchannels(_MOCK_WAV_CHANNELS)
        wf.setsampwidth(_MOCK_WAV_SAMPLE_WIDTH)
        wf.setframerate(_MOCK_WAV_SAMPLE_RATE)
        wf.writeframes(
            b"\x00" * n_frames * _MOCK_WAV_CHANNELS * _MOCK_WAV_SAMPLE_WIDTH
        )
    return buf.getvalue()
