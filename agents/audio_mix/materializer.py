"""AudioMix materializer — amix the video's own audio with optional global underlays.

Post-refactor architecture:
  * The video's audio track (Kling's baked-in dialogue + foley) is the
    base layer — extracted with ffmpeg from the final video mp4.
  * Optional global MusicAgent output (single film-wide wav registered
    under sys_id ``aud_music_film``) overlays on top.
  * Optional global AmbienceAgent output (single film-wide wav
    registered under sys_id ``aud_amb_film``) overlays on top.
  * ffmpeg amix with duration=longest produces the final wav,
    registered under sys_id ``aud_final``.

Scene-level mixing is gone: dialogue + foley are already time-locked to
the visuals by Kling itself, and the music / ambience beds are
continuous underlays that don't need per-scene alignment.

The music / ambience wavs are located via direct file-path fields on
``typed_input`` (routed from InputResolver's ``music_file`` /
``ambience_file`` labels). The upstream JSON packages no longer carry
an ``audio_asset`` block — the wav is a standalone artifact in
global_memory.
"""

from __future__ import annotations

import logging
import os
import subprocess
import tempfile
from typing import Any, TYPE_CHECKING

from ..descriptor import BaseMaterializer, MediaAsset
from inference.generation.audio_generators.service import AudioService

if TYPE_CHECKING:
    from ..base_agent import MaterializeContext
    from .schema import AudioMixAgentInput

logger = logging.getLogger(__name__)


# Stable sys_id for the final film-wide audio mix. AudioMixAgent emits
# exactly one wav per run, so a constant sys_id suffices.
FINAL_AUDIO_SYS_ID = "aud_final"


class AudioMixMaterializer(BaseMaterializer):

    def __init__(self, audio_service: AudioService) -> None:
        self.svc = audio_service

    @staticmethod
    def _normalize_local_path(uri: str) -> str:
        if not uri:
            return ""
        if uri.startswith("file://"):
            return uri[7:]
        return uri

    @classmethod
    def _load_bytes(cls, uri: str) -> bytes | None:
        if not uri or uri == "placeholder":
            return None
        path = cls._normalize_local_path(uri)
        if not os.path.isfile(path):
            logger.warning("[AudioMix] upstream track not on disk: %s", path)
            return None
        try:
            with open(path, "rb") as fh:
                return fh.read()
        except Exception as exc:
            logger.warning("[AudioMix] failed reading %s: %s", path, exc)
            return None

    @staticmethod
    def _extract_audio_from_video(video_path: str) -> bytes | None:
        """Extract the baked-in audio track from a video mp4 as PCM WAV bytes.

        Kling's ``generate_audio`` writes dialogue + foley into a single
        AAC stream inside the mp4; we demux and re-encode to PCM so the
        downstream amix filter receives a uniformly-formatted input.
        Returns None when the video has no audio track or ffmpeg fails.
        """
        if not video_path or not os.path.isfile(video_path):
            return None
        with tempfile.TemporaryDirectory(prefix="fw_audio_mix_") as tmp_dir:
            out_path = os.path.join(tmp_dir, "track.wav")
            proc = subprocess.run(
                [
                    "ffmpeg", "-y", "-i", video_path,
                    "-vn", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2",
                    out_path,
                ],
                capture_output=True, check=False, text=True, timeout=120,
            )
            if proc.returncode != 0 or not os.path.isfile(out_path):
                tail = (proc.stderr or "").strip()[-300:]
                logger.warning(
                    "[AudioMix] ffmpeg audio-extract failed (code=%s): %s",
                    proc.returncode, tail,
                )
                return None
            with open(out_path, "rb") as fh:
                return fh.read()

    async def materialize(
        self,
        ctx: "MaterializeContext",
        asset_dict: dict[str, Any],
    ) -> list[MediaAsset]:
        typed_input = ctx.typed_input  # type: AudioMixAgentInput

        video_path = self._normalize_local_path(typed_input.video_file_path)
        video_audio = self._extract_audio_from_video(video_path) if video_path else None

        music_bytes = self._load_bytes(typed_input.music_file_path)
        amb_bytes = self._load_bytes(typed_input.ambience_file_path)

        inputs: list[bytes] = []
        if video_audio:
            inputs.append(video_audio)
        if music_bytes:
            inputs.append(music_bytes)
        if amb_bytes:
            inputs.append(amb_bytes)

        pending: list[MediaAsset] = []

        if not inputs:
            logger.warning(
                "[AudioMix] no source tracks found (video_path=%r "
                "music_file=%r ambience_file=%r); emitting no final "
                "audio asset",
                video_path,
                typed_input.music_file_path,
                typed_input.ambience_file_path,
            )
            if ctx.report_failure is not None:
                ctx.report_failure(
                    kind="audio_mix_no_sources",
                    sys_id=FINAL_AUDIO_SYS_ID,
                    error="No source audio tracks available to mix.",
                )
            return pending

        if len(inputs) == 1:
            # Single real track — pass through, no mix needed.
            mixed = inputs[0]
        else:
            joined = AudioService._ffmpeg_amix(inputs)
            if joined:
                mixed = joined
            else:
                logger.warning(
                    "[AudioMix] ffmpeg amix failed for %d inputs — "
                    "falling back to the longest source.", len(inputs),
                )
                mixed = max(inputs, key=len)

        # Local uri_holder — we no longer mutate asset_dict; the final
        # wav is a standalone artifact and the persisted JSON envelope
        # stays empty (content: {}).
        uri_holder: dict[str, Any] = {}
        pending.append(MediaAsset(
            sys_id=FINAL_AUDIO_SYS_ID, data=mixed,
            extension="wav", uri_holder=uri_holder,
        ))
        return pending
