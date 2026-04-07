"""Input bundle v2 contract — single source of input for sub-agents.

The bundle has two slots:

  * ``task_id`` — current task identifier.

  * ``context['resolved_artifacts']`` — pre-indexed dict produced by
    ``InputResolver``.  Keyed by **consumer-declared label names**.
    JSON entries: single dict ``{"payload": ..., "path": ..., "scope": ...,
    "mime": ..., "what": ..., "why": ...}``.
    Media entries: list of dicts (same shape, ``payload`` typically absent).

Sub-agents have **only one input mechanism**: the InputResolver-selected
``resolved_artifacts``.  There is no ``hints`` slot, no direct hint reads,
no special user-text channel.  Any user-supplied raw input is persisted
into the workspace as an artifact (via an Intake agent) before any
content-generating sub-agent runs, so it always arrives through the
caption-driven InputResolver path like everything else.

Producers and consumers communicate purely through natural-language
captions interpreted by the InputResolver LLM.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class InputBundleV2:
    """Generic artifact bundle passed to sub-agent descriptor/builders."""

    task_id: str
    context: dict[str, Any] = field(default_factory=dict)

    @property
    def resolved_artifacts(self) -> dict[str, Any]:
        """Pre-indexed dict of artifacts placed by InputResolver.

        Keyed by **consumer-declared label name** (from the consuming agent's
        ``input_needs_description`` ``[label]`` headers).

        Each value is either a single artifact entry (for ``(single)`` labels)
        or a list of artifact entries (for ``(collection)`` labels).
        Each entry has keys: ``what, why, scope, path, mime`` and optionally
        ``payload`` (the loaded JSON for JSON artifacts).
        """
        val = self.context.get("resolved_artifacts")
        return val if isinstance(val, dict) else {}
