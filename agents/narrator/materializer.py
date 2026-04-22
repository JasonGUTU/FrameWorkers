"""Narrator materializer — TTS each line, concat with pauses, emit SRT + timing.

Produces three registered artifacts per run:

  * ``aud_narrator_full``        — concatenated narrator wav
  * ``narrator_srt``             — subtitle track JSON wrapping a per-line
                                   timed SRT (same shape SubtitleAgent
                                   emits, so Compositor consumes it via
                                   the ``subtitle_tracks`` label without
                                   special-casing)
  * ``narrator_segment_timing``  — per-segment start/end/duration JSON,
                                   consumed by the slideshow compositor
                                   via the ``segment_timing`` label to
                                   align each illustration to its
                                   narrated duration

Also stamps ``clips`` / ``segment_timings`` / ``srt_text`` /
``total_duration_sec`` back onto ``asset_dict`` so the persisted
snapshot carries the full timing view for debug / replay tools.
"""

from __future__ import annotations

import io
import json
import logging
import wave
from typing import Any, TYPE_CHECKING

from ..descriptor import BaseMaterializer, MediaAsset
from inference.generation.audio_generators.service import AudioService

if TYPE_CHECKING:
    from ..base_agent import MaterializeContext

logger = logging.getLogger(__name__)


# Stable sys_ids for the three standalone artifacts.
NARRATOR_AUDIO_SYS_ID = "aud_narrator_full"
NARRATOR_SRT_SYS_ID = "narrator_srt"
NARRATOR_SEGMENT_TIMING_SYS_ID = "narrator_segment_timing"

# Silence wav (stereo 44.1kHz PCM16) parameters — match AudioService._ffmpeg_run's
# output format so concat inputs line up. Keep fixed so pause silence and TTS
# outputs both pass through ffmpeg without resample drift.
_SILENCE_SAMPLE_RATE = 44100
_SILENCE_CHANNELS = 2
_SILENCE_SAMPLE_WIDTH = 2  # 16-bit


def _wav_duration_sec(wav_bytes: bytes) -> float:
    """Parse wav header to get duration. Returns 0 on malformed input."""
    try:
        with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            return frames / float(rate) if rate > 0 else 0.0
    except Exception:
        # Mock TTS / malformed wav — conservatively report 0; the L3 asset
        # check will flag this downstream.
        return 0.0


def _silence_wav_bytes(duration_sec: float) -> bytes:
    """Generate a silent wav blob of the given duration."""
    n_frames = max(0, int(round(duration_sec * _SILENCE_SAMPLE_RATE)))
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(_SILENCE_CHANNELS)
        wf.setsampwidth(_SILENCE_SAMPLE_WIDTH)
        wf.setframerate(_SILENCE_SAMPLE_RATE)
        wf.writeframes(b"\x00" * n_frames * _SILENCE_CHANNELS * _SILENCE_SAMPLE_WIDTH)
    return buf.getvalue()


def _format_srt_time(sec: float) -> str:
    """Format seconds as SRT timestamp: HH:MM:SS,mmm."""
    ms_total = int(round(sec * 1000))
    hours, ms_total = divmod(ms_total, 3_600_000)
    minutes, ms_total = divmod(ms_total, 60_000)
    seconds, millis = divmod(ms_total, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"


def _build_srt_text(
    clips: list[dict[str, Any]], id_to_text: dict[str, str],
) -> str:
    """Render line-level clips as an SRT block. Index starts at 1."""
    entries: list[str] = []
    for i, clip in enumerate(clips, start=1):
        line_id = str(clip.get("line_id", "") or "")
        text = (id_to_text.get(line_id, "") or "").strip()
        if not text:
            continue
        start = float(clip.get("start_sec", 0.0) or 0.0)
        end = float(clip.get("end_sec", 0.0) or 0.0)
        entries.append(
            f"{i}\n{_format_srt_time(start)} --> {_format_srt_time(end)}\n{text}\n"
        )
    return "\n".join(entries)


class NarratorMaterializer(BaseMaterializer):

    def __init__(self, audio_service: AudioService) -> None:
        self.svc = audio_service

    async def materialize(
        self,
        ctx: "MaterializeContext",
        asset_dict: dict[str, Any],
    ) -> list[MediaAsset]:
        content = asset_dict.get("content", {}) or {}
        lines = content.get("lines", []) or []
        language = str(content.get("language", "") or "").strip()
        if not lines:
            logger.warning("NarratorMaterializer: empty lines worklist")
            return []

        # --- 1. TTS each line; measure duration; insert pause silence ---
        concat_blobs: list[bytes] = []
        clips: list[dict[str, Any]] = []
        id_to_text: dict[str, str] = {}
        cursor = 0.0

        speaker_used = ""
        for i, line in enumerate(lines):
            if not isinstance(line, dict):
                continue
            line_id = str(line.get("line_id", "") or "")
            segment_id = str(line.get("segment_id", "") or "")
            text = str(line.get("text", "") or "").strip()
            pause_ms = int(line.get("pause_after_ms", 0) or 0)

            if not text:
                logger.warning("NarratorMaterializer: line[%d] %s has empty text", i, line_id)
                continue

            id_to_text[line_id] = text

            try:
                result = await self.svc.generate_speech(text=text)
            except Exception as exc:
                logger.error(
                    "NarratorMaterializer: TTS failed for %s (%s): %s",
                    line_id, segment_id, exc,
                )
                continue

            wav_bytes = result.bytes or b""
            concat_blobs.append(wav_bytes)
            dur = _wav_duration_sec(wav_bytes)
            if not speaker_used:
                speaker_used = (result.resolved_payload or {}).get("voice", "") if result.resolved_payload else ""

            start = cursor
            end = cursor + dur
            clips.append({
                "line_id": line_id,
                "segment_id": segment_id,
                "start_sec": round(start, 3),
                "end_sec": round(end, 3),
                "duration_sec": round(dur, 3),
            })
            cursor = end

            if pause_ms > 0:
                silence = _silence_wav_bytes(pause_ms / 1000.0)
                concat_blobs.append(silence)
                cursor += pause_ms / 1000.0

        if not concat_blobs:
            logger.error("NarratorMaterializer: no TTS blobs produced")
            return []

        # --- 2. Concatenate all TTS + silence blobs into one wav ---
        if len(concat_blobs) == 1:
            full_audio = concat_blobs[0]
        else:
            full_audio = AudioService._ffmpeg_concat(concat_blobs) or b"".join(concat_blobs)

        total_duration = round(cursor, 3)

        # --- 3. Aggregate per-segment timing from per-line clips ---
        segment_timings: list[dict[str, Any]] = []
        seg_order: list[str] = []
        seg_to_clips: dict[str, list[dict[str, Any]]] = {}
        for clip in clips:
            sid = clip.get("segment_id", "")
            if sid and sid not in seg_to_clips:
                seg_order.append(sid)
            seg_to_clips.setdefault(sid, []).append(clip)

        for sid in seg_order:
            members = seg_to_clips[sid]
            if not members:
                continue
            start = min(c["start_sec"] for c in members)
            end = max(c["end_sec"] for c in members)
            # Include the trailing pause of the last member line so the
            # illustration stays until the next segment's first line kicks in.
            last = max(members, key=lambda c: c["end_sec"])
            last_pause_ms = 0
            for raw_line in lines:
                if isinstance(raw_line, dict) and raw_line.get("line_id") == last["line_id"]:
                    last_pause_ms = int(raw_line.get("pause_after_ms", 0) or 0)
                    break
            end_with_tail = end + last_pause_ms / 1000.0
            segment_timings.append({
                "segment_id": sid,
                "start_sec": round(start, 3),
                "end_sec": round(end_with_tail, 3),
                "duration_sec": round(end_with_tail - start, 3),
                "line_ids": [c["line_id"] for c in members],
            })

        # --- 4. Build SRT from per-line clips ---
        srt_text = _build_srt_text(clips, id_to_text)

        # --- 5. Stamp back onto asset_dict so persisted JSON carries the view ---
        content["clips"] = [
            {k: v for k, v in c.items() if k != "segment_id"}  # schema.clips doesn't carry segment_id
            for c in clips
        ]
        content["segment_timings"] = segment_timings
        content["srt_text"] = srt_text
        content["total_duration_sec"] = total_duration
        content["speaker"] = speaker_used or content.get("speaker", "")
        metrics = asset_dict.setdefault("metrics", {})
        metrics["total_duration_sec"] = total_duration

        # --- 6. Emit three registered artifacts ---
        audio_uri_holder: dict[str, Any] = {}
        srt_uri_holder: dict[str, Any] = {}
        timing_uri_holder: dict[str, Any] = {}

        # SubtitleAgent-compatible wrapper so the compositor picks up the
        # SRT via the ``subtitle_tracks`` label with no special-casing.
        srt_envelope = {
            "content": {
                "tracks": [
                    {"language": language or "und", "srt_text": srt_text},
                ],
            },
        }
        timing_envelope = {
            "content": {
                "total_duration_sec": total_duration,
                "segment_timings": segment_timings,
            },
        }

        return [
            MediaAsset(
                sys_id=NARRATOR_AUDIO_SYS_ID,
                data=full_audio,
                extension="wav",
                uri_holder=audio_uri_holder,
            ),
            MediaAsset(
                sys_id=NARRATOR_SRT_SYS_ID,
                data=json.dumps(srt_envelope, ensure_ascii=False, indent=2).encode("utf-8"),
                extension="json",
                uri_holder=srt_uri_holder,
            ),
            MediaAsset(
                sys_id=NARRATOR_SEGMENT_TIMING_SYS_ID,
                data=json.dumps(timing_envelope, ensure_ascii=False, indent=2).encode("utf-8"),
                extension="json",
                uri_holder=timing_uri_holder,
            ),
        ]
