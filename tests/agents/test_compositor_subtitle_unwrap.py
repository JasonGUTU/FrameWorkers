"""Unit tests for CompositorMaterializer subtitle-shape unwrapping.

Guards the bilingual wiring + the multi-producer subtitle contract.
Every shape that ends up under the ``subtitle_tracks`` collection label
must reduce to a list of burn-ready SRT blobs:

  * TranslationAgent output — nested under ``content.translated_payload``;
    a naive read would return zero tracks and silently collapse a
    ``[CN, EN]`` bilingual flow to monolingual.
  * NarratorAgent / legacy SubtitleAgent — ``content.tracks[].srt_text``.
  * TranscriptionAgent — ``content.segments[]`` with start_time/end_time/
    text; the extractor renders these to SRT via the shared helper
    (no LLM), which is why SubtitleAgent is no longer a separate step.
  * Raw ``content.srt_text`` string — plain-text SRT producers.
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

from agents.compositor.materializer import _extract_srt_texts


def test_tracks_shape_extracted():
    """NarratorAgent / SubtitleAgent shape: content.tracks[*].srt_text."""
    sub = {
        "meta": {},
        "content": {
            "tracks": [
                {"language": "zh", "srt_text": "1\n00:00:01,000 --> 00:00:02,000\n你好\n\n"},
            ],
        },
        "metrics": {},
    }
    srts = _extract_srt_texts(sub)
    assert len(srts) == 1
    assert srts[0].startswith("1\n00:00:01,000")


def test_multi_track_all_extracted():
    """Each non-empty track.srt_text produces its own SRT blob."""
    sub = {
        "content": {
            "tracks": [
                {"language": "zh", "srt_text": "1\n00:00:01,000 --> 00:00:02,000\n你好\n\n"},
                {"language": "en", "srt_text": "1\n00:00:01,000 --> 00:00:02,000\nHello\n\n"},
            ],
        },
    }
    srts = _extract_srt_texts(sub)
    assert len(srts) == 2


def test_translation_wrapper_peeled():
    """TranslationAgent output: tracks live under
    ``content.translated_payload.content.tracks`` — wrapper must be
    peeled before reading."""
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
    srts = _extract_srt_texts(trans)
    assert len(srts) == 1
    assert "Hello" in srts[0]


def test_transcription_segments_rendered_to_srt():
    """TranscriptionAgent output: segments[{start_time, end_time, text}]
    gets rendered to SRT directly — this is the post-SubtitleAgent
    replacement path."""
    transcript = {
        "content": {
            "language": "en",
            "segments": [
                {"segment_id": "seg_001", "start_time": 0.0, "end_time": 2.5, "text": "Hello world."},
                {"segment_id": "seg_002", "start_time": 2.7, "end_time": 5.0, "text": "Goodbye."},
            ],
            "full_text": "Hello world. Goodbye.",
        },
    }
    srts = _extract_srt_texts(transcript)
    assert len(srts) == 1
    body = srts[0]
    assert "00:00:00,000 --> 00:00:02,500" in body
    assert "Hello world." in body
    assert "00:00:02,700 --> 00:00:05,000" in body
    assert "Goodbye." in body
    # Cue numbering is 1-indexed per SRT spec.
    assert body.startswith("1\n")


def test_translated_transcription_unwrapped_and_rendered():
    """A translated transcript (TranslationAgent wrapping a
    TranscriptionAgent payload) should both peel the wrapper AND render
    the segments to SRT — combined path both fixes in one shot."""
    trans = {
        "content": {
            "source_language": "en",
            "target_language": "zh",
            "translated_payload": {
                "content": {
                    "language": "zh",
                    "segments": [
                        {"start_time": 0.0, "end_time": 2.0, "text": "你好"},
                    ],
                },
            },
        },
    }
    srts = _extract_srt_texts(trans)
    assert len(srts) == 1
    assert "你好" in srts[0]
    assert "00:00:00,000 --> 00:00:02,000" in srts[0]


def test_raw_srt_text_passthrough():
    """Plain producers emitting ``content.srt_text`` string get passed through."""
    raw = {
        "content": {
            "srt_text": "1\n00:00:00,500 --> 00:00:02,000\nDirect SRT\n\n",
        },
    }
    srts = _extract_srt_texts(raw)
    assert len(srts) == 1
    assert "Direct SRT" in srts[0]


def test_empty_and_malformed_shapes_return_empty():
    assert _extract_srt_texts(None) == []
    assert _extract_srt_texts({}) == []
    assert _extract_srt_texts({"content": {}}) == []
    assert _extract_srt_texts({"content": {"translated_payload": {}}}) == []
    assert _extract_srt_texts({"content": {"segments": []}}) == []
    assert _extract_srt_texts({"content": {"segments": [{"text": "", "start_time": 0, "end_time": 1}]}}) == []
    # Non-dict content — defensive.
    assert _extract_srt_texts({"content": "not a dict"}) == []
