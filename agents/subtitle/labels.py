"""Consumer-declared input label names for SubtitleAgent.

Note: this agent's source-text input accepts screenplay, translated
screenplay, timestamped transcript, OR existing subtitle text. The label
is named ``source_text`` (not ``screenplay``) so the name itself doesn't
bias InputResolver toward screenplay-only matching.
"""

INPUT_LABEL_SOURCE_TEXT = "source_text"
INPUT_LABEL_VIDEO_PACKAGE = "video_package"
