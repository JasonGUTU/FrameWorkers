"""IllustrationAgent — per-segment illustration generator for storytelling videos.

Consumes a NarrationAgent script (segments with image_prompt +
overall_style) and produces ONE illustration per segment. Uses an
"anchor" strategy: the first segment's image is generated text-to-image
(seeds the cross-segment art style), and segments 2..N use image-to-image
editing with the anchor as a style reference — runs in parallel.

No LLM phase — all creative decisions (per-segment prompt, style) were
made by NarrationAgent; this agent is pure image-gen execution.
"""
