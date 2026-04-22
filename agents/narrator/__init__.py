"""NarratorAgent — TTS renderer for illustrated-storytelling narration.

Consumes a NarrationAgent script (segments of narrator lines with
per-line pauses) and produces the concatenated narrator audio, the
per-line timed SRT, and a per-segment timing manifest the slideshow
compositor uses to align each illustration to its narrated duration.

No LLM phase — all creative decisions (text to speak, when to pause)
were made by NarrationAgent; this agent is pure TTS execution +
timing bookkeeping + SRT assembly.
"""
