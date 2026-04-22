"""NarrationAgent — storytelling creative head.

Takes a creative brief (brief or prose) and produces a narrator-voice
audiobook script split into illustration-aligned segments. Output drives
both IllustrationAgent (per-segment image prompt + global style anchor)
and NarratorAgent (per-line TTS text + pause hints).
"""
