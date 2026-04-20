"""Consumer-declared input label names for CompositorAgent.

Same rationale as ``agents/audio_mix/labels.py``: video and audio each
ship as TWO coexisting scope=global artifacts (JSON manifest + binary
file) with similar captions, so we declare one label per artifact kind
so the caption-driven InputResolver can route each independently.

  * ``video_package`` — VideoAgent JSON manifest (LLM consumes for
    structural planning).
  * ``video_file`` — final assembled mp4 on disk (materializer's ffmpeg
    input).
  * ``audio_package`` — AudioMixAgent JSON asset descriptor (LLM reads
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
