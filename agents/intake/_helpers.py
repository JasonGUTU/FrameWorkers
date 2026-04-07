"""Shared helpers for the four intake sub-agents.

The intake agents have a common lifecycle:

  1. Receive a raw upload artifact (placeholder caption).
  2. Read the original user_intent text from the placeholder caption's
     ``why`` field (or from the artifact's ``payload``).
  3. Run a modality-specific understanding step (text LLM / vision LLM /
     etc.) to produce an objective description of the content.
  4. Synthesize a caption from (objective description + user intent).
  5. Emit the new caption-rich artifact (caption + reference back to the
     original raw bytes path, no re-persistence).

This module provides the helpers used by step 4 (caption synthesis) and
some utility functions used by step 2 (parsing placeholder captions).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


# ---------------------------------------------------------------------------
# Conventions for placeholder captions
# ---------------------------------------------------------------------------

PLACEHOLDER_SCOPE = "raw_pending"
"""``ArtifactRef.scope`` value used by ``workspace.persist_raw_upload`` to
mark a freshly-uploaded artifact that has not yet been semantically
analyzed by an intake agent.

Intake agents pick up these artifacts via a ``[raw_<kind>_upload]`` label,
analyze them, and emit a new artifact with a more meaningful scope
(typically ``"global"`` / ``"user_provided"`` / etc.).
"""


def make_placeholder_caption(*, mime: str, user_intent: str) -> dict[str, str]:
    """Build the placeholder caption for a freshly-uploaded raw artifact.

    Used by ``workspace.persist_raw_upload()`` (and by tests). The
    ``what`` field is generic and ``what``-shaped enough to be matched by
    intake agents' label descriptions; the ``why`` field carries the
    user's free-text intent verbatim so the intake LLM can read it.
    """
    return {
        "what": f"raw user upload, mime={mime or 'unknown'}, awaiting semantic analysis",
        "why": (user_intent or "").strip(),
        "scope": PLACEHOLDER_SCOPE,
    }


def is_placeholder_entry(entry: Any) -> bool:
    """Heuristic: does this resolved-artifact entry look like a raw_pending
    placeholder created by ``persist_raw_upload``?

    Used by intake agents inside ``build_input`` to filter out anything
    that has already been processed.
    """
    if not isinstance(entry, dict):
        return False
    if str(entry.get("scope") or "").strip() == PLACEHOLDER_SCOPE:
        return True
    what = str(entry.get("what") or "").lower()
    return "raw user upload" in what and "awaiting semantic analysis" in what


# ---------------------------------------------------------------------------
# Caption synthesis (step 4 of the intake lifecycle)
# ---------------------------------------------------------------------------

@dataclass
class IntakeCaption:
    """Final caption produced by an intake agent."""

    what: str
    why: str
    scope: str = "global"


def synthesize_caption(
    *,
    objective_description: str,
    user_intent: str,
    role_hint: str,
) -> IntakeCaption:
    """Combine the LLM's objective description with the user's stated intent
    into a final caption.

    The two layers stay distinct in the output:
      * ``what`` carries the objective description (what the artifact
        physically is).
      * ``why`` carries the user's verbatim intent (what they said it was
        for).

    Importantly, neither layer encodes provenance or pipeline-role
    predictions. The downstream consumer's LLM is responsible for
    deciding whether the artifact applies to its label.

    ``role_hint`` is a short, modality-agnostic prefix added to the
    ``what`` field (e.g. ``"image of"``, ``"video clip showing"``,
    ``"audio sample of"``, ``"text describing"``) to help downstream
    semantic matching without making per-pipeline assumptions.
    """
    what = (objective_description or "").strip()
    if role_hint:
        what = f"{role_hint} {what}".strip()
    why = (user_intent or "").strip()
    if not why:
        why = "(no user intent provided)"
    return IntakeCaption(what=what, why=why, scope="global")
