"""Consumer-declared input label names for CompositorAgent.

Same rationale as ``agents/audio_mix/labels.py``: video and audio each
ship as TWO coexisting scope=global artifacts (JSON manifest + binary
file) with similar captions, so we declare one label per artifact kind
so the caption-driven InputResolver can route each independently.

  * ``video_package`` — assembled-video JSON manifest (LLM consumes for
    structural planning).
  * ``video_file`` — final assembled mp4 on disk (materializer's ffmpeg
    input).
  * ``audio_package`` — final-audio-mix JSON asset descriptor (LLM reads
    to know which tracks are present).
  * ``audio_file`` — final mixed wav on disk (materializer muxes this
    onto the video via ffmpeg).
"""

INPUT_LABEL_VIDEO_PACKAGE = "video_package"
INPUT_LABEL_VIDEO_FILE = "video_file"
INPUT_LABEL_AUDIO_PACKAGE = "audio_package"
INPUT_LABEL_AUDIO_FILE = "audio_file"
INPUT_LABEL_SUBTITLE_TRACKS = "subtitle_tracks"
INPUT_LABEL_SCREENPLAY = "screenplay"

# Illustrated-storytelling mode: an ordered image sequence replaces the
# assembled video, and a per-segment timing manifest tells the compositor
# how long each image stays on screen. Both are routed in ONLY in
# slideshow flows; they are mutually exclusive with ``video_package`` /
# ``video_file`` (an artifact-kind invariant the LLM prompt enforces).
INPUT_LABEL_ILLUSTRATION_SEQUENCE = "illustration_sequence"
INPUT_LABEL_SEGMENT_TIMING = "segment_timing"
