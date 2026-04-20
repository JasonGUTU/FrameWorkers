"""Schema definitions for AudioMixAgent input / output interfaces.

Post-refactor shape: AudioMixAgent produces a single film-wide final
audio track by amix'ing the video's own audio (Kling's dialogue +
foley, baked into each clip) with the optional global music cue and
optional global ambience bed.

The agent's JSON output is now essentially metadata-only: all binary
material (the wav) is emitted by the materializer and registered as a
standalone artifact (sys_id ``aud_final``) in global_memory. Downstream
consumers (CompositorAgent) discover it by caption-based resolution,
not by reading an asset block from this payload.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..common_schema import Meta


class AudioMixContent(BaseModel):
    """Empty content envelope — kept for schema stability.

    The actual final-mix wav is a separate artifact registered under
    sys_id ``aud_final``; this payload carries no audio fields.
    """


class AudioMixMetrics(BaseModel):
    source_track_count: int = 0


class AudioMixAgentInput(BaseModel):
    """Input: JSON text blob of the video package, direct path to the final
    video file, and optional global music + optional global ambience JSON
    packages and file paths.

    The video side is split into two fields because the VideoAgent emits
    two scope=global artifacts (a JSON manifest and an mp4 binary) and the
    InputResolver must route each via a separate label (see
    ``agents/audio_mix/labels.py`` for the rationale):

      * ``video_json_text`` — serialized JSON payload of the VideoAgent's
        video package (scenes, shot_segments, timing). Used by this
        agent's LLM to reason about video structure.
      * ``video_file_path`` — direct on-disk path to the final assembled
        mp4 (binary artifact, no JSON payload). Used by the materializer
        to extract the Kling-baked audio track via ffmpeg.

    Music and ambience follow the same JSON-text + file-path split,
    because the music/ambience packages no longer embed a wav uri in
    their JSON (the wav is a standalone artifact). The LLM reads the
    JSON text for mix planning; the materializer reads the file path to
    load the wav bytes for amix.

      * ``music_json_text`` / ``ambience_json_text`` — JSON packages
        carrying LLM-chosen mood / description / duration target.
      * ``music_file_path`` / ``ambience_file_path`` — direct on-disk
        paths to the generated wav files.

    Any of music / ambience may be empty when the user did not request
    that track; in that case both the JSON text and the file path for
    that track will be empty.
    """

    video_json_text: str = ""
    video_file_path: str = ""
    music_json_text: str = ""
    music_file_path: str = ""
    ambience_json_text: str = ""
    ambience_file_path: str = ""


class AudioMixAgentOutput(BaseModel):
    meta: Meta = Field(default_factory=Meta)
    content: AudioMixContent = Field(default_factory=AudioMixContent)
    metrics: AudioMixMetrics = Field(default_factory=AudioMixMetrics)
