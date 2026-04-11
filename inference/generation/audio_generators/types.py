"""Shared types for audio generation services.

``AudioGenerationResult`` is what ``generate_speech`` / ``generate_music``
/ ``generate_ambience`` return: the raw audio bytes plus an audit dict
describing what the service actually sent to its backend (kind, model,
voice, text preview, etc.). The caller writes the audit dict into its
own schema for inspection/replay.

Unlike the image and video services, audio doesn't need a separate
``*SemanticContext`` type yet — the current calls are simple enough
(a line of narration text, a mood string, an ambience description)
that the caller passes them as plain parameters. When / if a more
complex audio agent is added that wants to describe "what this cue
is for" in richer semantic terms, a ``AudioSemanticContext`` can be
introduced alongside this file.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AudioGenerationResult:
    """Return value of ``AudioService.generate_{speech,music,ambience}``.

    ``bytes`` is the generated audio payload (WAV / MP3 / whatever the
    backend produced).

    ``resolved_payload`` is a JSON-friendly dict describing what the
    service actually dispatched. Callers persist it into their output
    schema's ``audio_generation_prompt`` slot (or similar) so that an
    auditor looking at the generated pipeline artifacts can see the
    exact request that produced each clip. May be empty for mock
    backends that have nothing meaningful to report.
    """

    bytes: bytes
    resolved_payload: dict[str, Any] = field(default_factory=dict)
