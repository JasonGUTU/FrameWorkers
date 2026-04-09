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
