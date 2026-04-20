"""Common schema types shared across all agents."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Upstream-input rejection (consumer-side "loose in" with teeth)
# ---------------------------------------------------------------------------

class InputRejection(BaseModel):
    """A consumer sub-agent's structured report that upstream input is too
    incomplete / malformed for it to do its job.

    Consumers (via their main generation LLM call) emit this instead of a
    normal output when they cannot proceed. The pipeline short-circuits
    (no retry — same input would yield the same rejection) and surfaces
    this to the director so the replanner can steer toward fixing the
    producer (``replan-tail`` inserting a better upstream step), not
    retrying the consumer.

    Fields:
        reason:               Short natural-language explanation of what is
                              insufficient about the upstream payload.
        missing_labels:       Which of the consumer's declared input labels
                              had no usable content (e.g. ``["story"]``).
                              Empty list means "all labels resolved but
                              their content is unusable".
        offending_fields:     Concrete field paths the consumer expected to
                              read but could not (e.g.
                              ``["content.scene_outline"]``). Free-form.
        upstream_agent_hint:  Which producer agent_id the consumer thinks
                              should be re-run or replaced (e.g.
                              ``"StoryAgent"``). Empty string if unknown.
    """

    reason: str = ""
    missing_labels: list[str] = Field(default_factory=list)
    offending_fields: list[str] = Field(default_factory=list)
    upstream_agent_hint: str = ""


class UpstreamInputRejected(Exception):
    """Raised from ``BaseAgent.generate()`` (or helpers) when the consuming
    LLM declares upstream input insufficient.

    Carries a structured :class:`InputRejection`. ``BaseAgent.run()``
    catches this, short-circuits the retry loop, and surfaces the
    rejection through ``ExecutionResult.eval_result``.
    """

    def __init__(self, rejection: InputRejection) -> None:
        self.rejection = rejection
        super().__init__(
            f"upstream input rejected: {rejection.reason or '(no reason)'}"
        )

# ---------------------------------------------------------------------------
# Shared atomic types
# ---------------------------------------------------------------------------

class QualityScore(BaseModel):
    """A single quality dimension with numeric score and free-text notes."""

    score: float = Field(0.0, ge=0.0, le=1.0, description="Quality score 0–1")
    notes: list[str] = Field(default_factory=list)


class ImageAsset(BaseModel):
    """Pointer to a generated image file."""

    asset_id: str = ""
    uri: str = ""
    width: int = 1024
    height: int = 576
    format: str = "png"  # png | jpg | webp


class Meta(BaseModel):
    """Standard asset metadata header shared by all agent outputs.

    Orchestration uses Task Stack step_id elsewhere. Do not add project_id
    to LLM JSON; it is not part of this schema.
    """

    draft_id: str = ""
    asset_id: str = ""
    asset_type: str = ""
    schema_version: str = "0.3"
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    created_by_agent: str = ""
    language: str = "en"


# ---------------------------------------------------------------------------
# Resolver I/O: the single typed shape every InputResolver entry takes
# ---------------------------------------------------------------------------

class ResolvedArtifactEntry(BaseModel):
    """A single artifact entry as produced by ``InputResolver._build_entry``
    and consumed by every descriptor's ``build_input``.

    This is the canonical shape for the cross-agent data channel: each
    resolved label maps to either one of these (for ``(single)`` labels)
    or a list of these (for ``(collection)`` labels). Every field except
    ``payload`` is always populated by the resolver; ``payload`` is only
    loaded for JSON artifacts (``mime == "application/json"`` or
    ``.json`` path). Producers and consumers therefore communicate
    through the same four descriptive fields (``caption / scope / path /
    mime``) plus an optional structured JSON body.

    Use ``ResolvedArtifactEntry.coerce(value)`` in descriptors rather
    than constructing by hand — it accepts a raw dict (legacy tests/
    scripts still pass these), a real ``ResolvedArtifactEntry`` (current
    InputResolver output), or ``None`` (missing label), and always
    returns a well-formed entry so downstream code can read fields
    without defensive ``isinstance`` checks.
    """

    caption: str = ""
    scope: str = ""
    path: str = ""
    mime: str = ""
    payload: dict | None = None

    @classmethod
    def coerce(cls, value: Any) -> "ResolvedArtifactEntry":
        """Normalise any value into a ``ResolvedArtifactEntry``.

        Accepts:
          * an existing ``ResolvedArtifactEntry`` — returned unchanged
          * a raw ``dict`` — fields copied by name, missing fields
            default to empty strings, payload only kept if dict-typed
          * anything else (including ``None``) — returns an empty entry

        This is the one-stop converter descriptors use at the top of
        ``build_input`` so the rest of the function can assume a typed
        entry.
        """
        if isinstance(value, cls):
            return value
        if isinstance(value, dict):
            raw_payload = value.get("payload")
            return cls(
                caption=str(value.get("caption", "") or ""),
                scope=str(value.get("scope", "") or ""),
                path=str(value.get("path", "") or ""),
                mime=str(value.get("mime", "") or ""),
                payload=raw_payload if isinstance(raw_payload, dict) else None,
            )
        return cls()

    @classmethod
    def coerce_list(cls, value: Any) -> list["ResolvedArtifactEntry"]:
        """Normalise a ``(collection)`` label value to a list of entries.

        Accepts a list of mixed dicts / entries / garbage and returns
        only the well-formed entries. Non-list inputs (including
        ``None``) yield an empty list.
        """
        if not isinstance(value, list):
            return []
        return [cls.coerce(v) for v in value]


class ImageReferenceEntry(BaseModel):
    """A single image reference that flows from the workspace into a sub-agent's
    typed input.

    Used by any agent that needs to receive image artifacts (character /
    location / style references for KeyFrameAgent, shot stills for
    VideoAgent, shot keyframes for UnivaVideoAgent, etc.) — the schema is
    deliberately generic so the same type works for all label categories.

    The shape mirrors the InputResolver-resolved entry: ``path`` is always
    populated with the workspace file path; the caption fields preserve
    the producer's natural-language description so the consuming agent's
    LLM can decide how to use each entry. ``scope`` is sometimes used by
    materializers to disambiguate per-shot images (e.g. ``"shot:sh_001"``).
    """

    path: str = ""
    caption: str = ""
    mime: str = ""
    scope: str = ""

    @classmethod
    def from_artifact_entry(
        cls, entry: ResolvedArtifactEntry
    ) -> "ImageReferenceEntry | None":
        """Build a typed image reference from a resolved entry, or ``None``
        if the entry has no usable path.

        Keeping the "has a path?" check here means every media consumer
        (KeyFrameAgent / VideoAgent / UnivaVideoAgent) gets the same
        filter — previously each re-implemented the same
        ``str(it.get("path", "") or "").strip()`` guard inline.
        """
        path = entry.path.strip()
        if not path:
            return None
        return cls(
            path=path,
            caption=entry.caption,
            mime=entry.mime,
            scope=entry.scope,
        )

    @classmethod
    def list_from_resolved(cls, value: Any) -> list["ImageReferenceEntry"]:
        """Extract typed image refs from a ``(collection)`` label value.

        Combines ``ResolvedArtifactEntry.coerce_list`` with
        ``from_artifact_entry`` so media-consumer descriptors can
        dispatch a single call per label instead of writing the
        ``for entry in coerce_list(...)`` loop inline.
        """
        entries = ResolvedArtifactEntry.coerce_list(value)
        out: list[ImageReferenceEntry] = []
        for entry in entries:
            ref = cls.from_artifact_entry(entry)
            if ref is not None:
                out.append(ref)
        return out


