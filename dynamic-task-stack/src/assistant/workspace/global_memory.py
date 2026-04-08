"""Artifact registry — per-file natural-language caption index.

Responsibilities:
  * Append one ``ArtifactRegistryEntry`` per execution to
    ``artifact_registry.jsonl`` (one JSON object per line).
  * Each entry contains a list of ``ArtifactRef`` objects — one per
    persisted file — carrying its own pure natural-language caption
    (``what`` / ``why`` / ``scope`` / ``path`` / ``mime``).
  * Serve a compact LLM-readable captions index for the InputResolver.
  * Look up ``ArtifactRef`` objects by exact file path.

What it does NOT do:
  * Store payloads — captions and paths only; payloads loaded on demand.
  * Apply any machine-readable typing — captions are pure natural language.
  * Filter, rank, or select artifacts — that is ``InputResolver``'s job.

Used by:
  * ``Workspace._register_artifacts_callback`` (called by AssetManager)
    appends entries after each successful execution persistence.
  * ``InputResolver.resolve`` reads ``get_captions_index`` (for LLM input)
    and ``get_by_paths`` (to materialize selections).
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import ArtifactRef, ArtifactRegistryEntry

logger = logging.getLogger(__name__)

ARTIFACT_REGISTRY_FILENAME = "artifact_registry.jsonl"


class ArtifactRegistry:
    """Append-only registry of persisted artifacts with per-artifact captions.

    Each ``register()`` call appends one JSON line to
    ``artifact_registry.jsonl``.  No in-place updates — a re-execution
    produces a new entry.

    Public API
    ----------
    register(execution_id, agent_id, task_id, artifacts)
        Append a new entry.
    list_all() -> list[ArtifactRegistryEntry]
        Return all entries (chronological order).
    get_captions_index(task_id=None) -> str
        Per-artifact LLM-readable index for InputResolver prompts.
    get_by_paths(paths) -> list[ArtifactRef]
        Look up ArtifactRef objects by file path.
    """

    def __init__(self, workspace_id: str, runtime_base_path: Path) -> None:
        self.workspace_id = workspace_id
        self.runtime_base_path = Path(runtime_base_path)
        self.workspace_runtime_path = self.runtime_base_path / workspace_id
        self.workspace_runtime_path.mkdir(parents=True, exist_ok=True)
        self._registry_path = self.workspace_runtime_path / ARTIFACT_REGISTRY_FILENAME

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _ref_to_dict(ref: ArtifactRef) -> Dict[str, Any]:
        return {
            "what": ref.what,
            "why": ref.why,
            "scope": ref.scope,
            "path": ref.path,
            "mime": ref.mime,
        }

    @staticmethod
    def _ref_from_dict(d: Any) -> ArtifactRef:
        if not isinstance(d, dict):
            return ArtifactRef()
        return ArtifactRef(
            what=str(d.get("what") or ""),
            why=str(d.get("why") or ""),
            scope=str(d.get("scope") or "global"),
            path=str(d.get("path") or ""),
            mime=str(d.get("mime") or ""),
        )

    @staticmethod
    def _entry_to_dict(entry: ArtifactRegistryEntry) -> Dict[str, Any]:
        return {
            "entry_id": entry.entry_id,
            "execution_id": entry.execution_id,
            "agent_id": entry.agent_id,
            "task_id": entry.task_id,
            "created_at": entry.created_at.isoformat(),
            "artifacts": [ArtifactRegistry._ref_to_dict(r) for r in entry.artifacts],
        }

    @staticmethod
    def _entry_from_dict(d: Dict[str, Any]) -> ArtifactRegistryEntry:
        created_raw = d.get("created_at") or ""
        try:
            created_at = datetime.fromisoformat(created_raw)
        except (ValueError, TypeError):
            created_at = datetime.now(UTC)
        return ArtifactRegistryEntry(
            entry_id=str(d.get("entry_id") or ""),
            execution_id=str(d.get("execution_id") or ""),
            agent_id=str(d.get("agent_id") or ""),
            task_id=str(d.get("task_id") or ""),
            created_at=created_at,
            artifacts=[
                ArtifactRegistry._ref_from_dict(r)
                for r in (d.get("artifacts") or [])
            ],
        )

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _append_entry(self, entry: ArtifactRegistryEntry) -> None:
        try:
            with open(self._registry_path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(self._entry_to_dict(entry), ensure_ascii=False) + "\n")
        except Exception as exc:
            logger.warning("ArtifactRegistry: failed to append entry: %s", exc)
            raise

    def _read_all(self) -> List[ArtifactRegistryEntry]:
        if not self._registry_path.exists():
            return []
        entries: List[ArtifactRegistryEntry] = []
        try:
            with open(self._registry_path, "r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        d = json.loads(line)
                        entries.append(self._entry_from_dict(d))
                    except Exception as exc:
                        logger.warning("ArtifactRegistry: skipping malformed line: %s", exc)
        except Exception as exc:
            logger.warning("ArtifactRegistry: failed to read registry: %s", exc)
        return entries

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def register(
        self,
        *,
        execution_id: str,
        agent_id: str,
        task_id: str,
        artifacts: List[ArtifactRef],
    ) -> ArtifactRegistryEntry:
        """Append a new registry entry and return it."""
        entry = ArtifactRegistryEntry(
            entry_id=f"art_{uuid.uuid4().hex[:12]}",
            execution_id=execution_id,
            agent_id=agent_id,
            task_id=task_id,
            created_at=datetime.now(UTC),
            artifacts=artifacts,
        )
        self._append_entry(entry)
        return entry

    def list_all(self) -> List[ArtifactRegistryEntry]:
        """Return all entries in chronological order."""
        return self._read_all()

    def prune_by_producer(self, *, task_id: str, agent_id: str) -> int:
        """Remove all entries matching ``task_id`` AND ``agent_id``.

        Called when an agent is re-running and its old outputs are being
        purged from the file system. Without this, the registry would leak
        stale entries pointing at deleted files, and InputResolver would
        surface dangling paths to downstream agents.

        This intentionally breaks the append-only semantics. The trade-off
        is correctness: the file_manager-side overwrite already deletes the
        old files, so the registry MUST stay in sync or it lies about
        what's available in the workspace.

        Returns the number of entries removed.

        Note: ``user`` uploads (registered with ``agent_id="user"``) are
        only pruned if the caller passes ``agent_id="user"`` explicitly,
        so re-running a content sub-agent will NOT remove user uploads
        sitting in the workspace.
        """
        if not agent_id:
            return 0
        entries = self._read_all()
        kept = [
            e for e in entries
            if not (e.task_id == task_id and e.agent_id == agent_id)
        ]
        removed = len(entries) - len(kept)
        if removed > 0:
            try:
                with open(self._registry_path, "w", encoding="utf-8") as fh:
                    for e in kept:
                        fh.write(
                            json.dumps(self._entry_to_dict(e), ensure_ascii=False)
                            + "\n"
                        )
            except Exception as exc:
                logger.warning("ArtifactRegistry: failed to rewrite after prune: %s", exc)
        return removed

    def get_by_paths(self, paths: List[str]) -> List[ArtifactRef]:
        """Return ArtifactRef objects matching the given file paths."""
        want = set(paths)
        result: List[ArtifactRef] = []
        for entry in self._read_all():
            for ref in entry.artifacts:
                if ref.path in want:
                    result.append(ref)
        return result

    def get_captions_index(self, *, task_id: Optional[str] = None) -> str:
        """Return a compact LLM-readable index of all individual artifacts.

        Each artifact is rendered as one block with its caption, scope, MIME,
        and path so that InputResolver's LLM can select individual files by
        semantic meaning without traversing JSON manifests.

        Example output::

            [/path/to/screenplay.json]  scope=global  mime=application/json
              agent: ScreenplayAgent | exec_2_xxx | 2026-04-05
              what: 1 scene, 9 shots, intimate workshop drama, warm nostalgic palette
              why: tight framing and warm lamplight to convey urgency and memory

            [/path/to/img_char_001.png]  scope=global  mime=image/png
              agent: KeyFrameAgent | exec_3_xxx | 2026-04-05
              what: Elias Vance full-body reference, warm workshop lighting, age 70
              why: global character anchor for visual consistency across all shots
        """
        entries = self._read_all()
        if task_id:
            # Include workspace-global entries (task_id="") in every task's
            # view. Raw user uploads via ``persist_raw_upload`` are
            # registered with task_id="" because uploads happen before any
            # task — they belong to the whole workspace and must be visible
            # to whichever task subsequently runs an intake / content agent.
            entries = [
                e for e in entries
                if e.task_id == task_id or not e.task_id
            ]
        if not entries:
            return "(no artifacts registered yet)"

        lines: List[str] = []
        for e in entries:
            date_str = e.created_at.strftime("%Y-%m-%d") if e.created_at else "?"
            for ref in e.artifacts:
                if not ref.path:
                    continue
                lines.append(
                    f"[{ref.path}]  scope={ref.scope}  mime={ref.mime or '?'}\n"
                    f"  agent: {e.agent_id} | {e.execution_id} | {date_str}\n"
                    f"  what: {ref.what or '—'}\n"
                    f"  why: {ref.why or '—'}"
                )
        return "\n\n".join(lines) if lines else "(no artifacts registered yet)"
