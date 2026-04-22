"""Unit tests for CompositorMaterializer subtitle-shape unwrapping.

Guards the bilingual wiring: a TranslationAgent output nests the
translated subtitle tracks under ``content.translated_payload`` so the
consumer sees the original document shape just translated. Without
unwrapping, the materializer reads ``content.tracks`` on the
translation envelope (which has none) and silently drops the translated
language track — collapsing a ``[CN, EN]`` plan into a monolingual
burn-in.
"""

from __future__ import annotations

import sys
from pathlib import Path


def _resolve_project_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "agents" / "__init__.py").exists():
            return parent
    raise RuntimeError("Cannot locate project root")


_root = _resolve_project_root()
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from agents.compositor.materializer import _extract_subtitle_tracks


def test_subtitle_agent_output_tracks_extracted():
    """SubtitleAgent output: ``content.tracks`` at the top of its own
    content block."""
    sub = {
        "meta": {},
        "content": {
            "tracks": [
                {"language": "zh", "srt_text": "1\n00:00:01,000 --> 00:00:02,000\n你好\n\n"},
            ],
        },
        "metrics": {},
    }
    tracks = _extract_subtitle_tracks(sub)
    assert len(tracks) == 1
    assert tracks[0]["srt_text"].startswith("1\n00:00:01,000")


def test_translation_agent_output_tracks_extracted():
    """TranslationAgent output: tracks live under
    ``content.translated_payload.content.tracks`` — the wrapper must be
    peeled."""
    trans = {
        "meta": {},
        "content": {
            "source_language": "zh",
            "target_language": "en",
            "translated_payload": {
                "meta": {},
                "content": {
                    "tracks": [
                        {"language": "en", "srt_text": "1\n00:00:01,000 --> 00:00:02,000\nHello\n\n"},
                    ],
                },
                "metrics": {},
            },
        },
        "metrics": {},
    }
    tracks = _extract_subtitle_tracks(trans)
    assert len(tracks) == 1
    assert "Hello" in tracks[0]["srt_text"]


def test_empty_and_malformed_shapes_return_empty():
    assert _extract_subtitle_tracks(None) == []
    assert _extract_subtitle_tracks({}) == []
    assert _extract_subtitle_tracks({"content": {}}) == []
    assert _extract_subtitle_tracks({"content": {"translated_payload": {}}}) == []
    # Non-dict content — defensive.
    assert _extract_subtitle_tracks({"content": "not a dict"}) == []
