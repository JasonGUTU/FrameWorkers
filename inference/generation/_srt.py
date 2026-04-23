"""Tiny SRT renderer — pure Python, zero LLM.

A ``segments_to_srt`` pass consumes any
``[{start_sec|start_time, end_sec|end_time, text}, ...]`` list and
emits a valid SRT block. Both NarratorMaterializer (per-line TTS
timing) and CompositorMaterializer (per-line ASR timing from
TranscriptionAgent) use this so there is one place where SRT
serialisation happens.

Deliberately does NOT do "subtitle readability shaping" (line wrap
≤ 40 chars, cue ≤ 7 s, inter-cue gaps). The segments we receive
either come from line-level TTS (NarratorAgent — already
readable-sized) or Whisper/fal ASR (TranscriptionAgent — natural
speech boundaries, typically 3–7 s). If a long segment ever sneaks
through, the Compositor ffmpeg burn-in still renders it; we'd add a
splitter helper here if a real source of long cues appears.
"""

from __future__ import annotations

from typing import Any, Iterable


def format_srt_time(sec: float) -> str:
    """Format seconds as an SRT timestamp ``HH:MM:SS,mmm``.

    Negative values clamp to zero. Accepts float; rounds to the nearest
    millisecond.
    """
    ms_total = max(0, int(round(float(sec) * 1000)))
    hours, ms_total = divmod(ms_total, 3_600_000)
    minutes, ms_total = divmod(ms_total, 60_000)
    seconds, millis = divmod(ms_total, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"


def _coerce_seg_field(seg: dict, *keys: str, default: float = 0.0) -> float:
    """Return the first key's value coerced to float, else ``default``."""
    for k in keys:
        if k in seg and seg[k] is not None:
            try:
                return float(seg[k])
            except (TypeError, ValueError):
                continue
    return default


def segments_to_srt(segments: Iterable[dict[str, Any]]) -> str:
    """Render a list of segment dicts as an SRT text block.

    Accepts either ``start_sec``/``end_sec`` (NarratorAgent's clip
    shape) or ``start_time``/``end_time`` (TranscriptionAgent's
    transcript segment shape). Segments with empty text are skipped so
    they don't produce blank cues.
    """
    entries: list[str] = []
    cue_index = 0
    for seg in segments:
        if not isinstance(seg, dict):
            continue
        text = str(seg.get("text", "") or "").strip()
        if not text:
            continue
        start = _coerce_seg_field(seg, "start_sec", "start_time")
        end = _coerce_seg_field(seg, "end_sec", "end_time")
        if end <= start:
            continue
        cue_index += 1
        entries.append(
            f"{cue_index}\n{format_srt_time(start)} --> {format_srt_time(end)}\n{text}\n"
        )
    return "\n".join(entries)
