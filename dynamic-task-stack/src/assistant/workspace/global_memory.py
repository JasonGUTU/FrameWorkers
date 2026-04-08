"""Global memory — per-execution record of every persisted artifact.

The global memory is a workspace-wide ledger:

  * Each entry corresponds to one **agent execution** that produced one or
    more files. Its ``artifacts`` array carries a natural-language caption
    (``what`` / ``why`` / ``scope``), absolute ``path`` and ``mime`` for
    every file that execution wrote.
  * Stored on disk at ``Runtime/{workspace_id}/global_memory.md`` — a
    markdown wrapper around a JSON ``Entries`` block so the file is both
    human-readable and round-trippable.
  * The single source of truth for "what's in this workspace, who put it
    there, and what does it mean". Both ``InputResolver`` (for caption-
    driven input matching) and ``ArtifactWriter`` (for overwrite-mode
    dedup) read from here.

A lightweight director-facing rollup ({execution_id, agent_id, task_id,
status, created_at}) is exposed via ``Workspace.get_global_memory_brief()``;
that brief is **computed on read** from these entries — there is no
separate brief file on disk.

Renamed from ``ArtifactRegistry`` / ``artifact_registry.jsonl``: same data
shape, friendlier on-disk format, and the name now reflects its real role
as the workspace's semantic record. Old workspaces written before the
rename are still readable via the legacy filename fallback below.

What it does NOT do:
  * Store payloads — captions and paths only; payloads loaded on demand.
  * Apply any machine-readable typing — captions are pure natural language.
  * Filter, rank, or select artifacts — that is ``InputResolver``'s job.

Used by:
  * ``Workspace._register_artifacts_callback`` (called by ArtifactWriter)
    appends entries after each successful execution persistence.
  * ``InputResolver.resolve`` reads ``get_captions_index`` (for LLM input)
    and ``get_by_paths`` (to materialize selections).
"""

from __future__ import annotations

import json
import logging
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import ArtifactRef, GlobalMemoryEntry

logger = logging.getLogger(__name__)

GLOBAL_MEMORY_FILENAME = "global_memory.md"
LEGACY_REGISTRY_FILENAME = "artifact_registry.jsonl"

ENTRIES_HEADER = "## Entries"
JSON_FENCE_RE = re.compile(r"```json\s*\n([\s\S]*?)\n```", re.MULTILINE)


class GlobalMemory:
    """Per-execution artifact ledger for one workspace.

    Storage: ``Runtime/{workspace_id}/global_memory.md`` — a markdown
    document whose ``## Entries`` section contains a single JSON array of
    ``GlobalMemoryEntry`` objects (one element per execution).

    Each ``register()`` call rewrites the file with the appended entry.
    Re-execution of the same ``(task, agent)`` is handled by
    ``ArtifactWriter._purge_all_for_producer`` calling ``prune_by_paths``
    to wipe stale rows before the new run writes.

    Public API
    ----------
    register(execution_id, agent_id, task_id, artifacts)
        Append a new entry and return it.
    list_all() -> list[GlobalMemoryEntry]
        Return all entries (chronological order).
    get_captions_index(task_id=None) -> str
        Per-artifact LLM-readable index for InputResolver prompts.
    get_by_paths(paths) -> list[ArtifactRef]
        Look up ArtifactRef objects by file path.
    find_by_producer(task_id, agent_id) -> list[ArtifactRef]
        Every ref this producer wrote on this task (for dedup).
    has_producer_run(task_id, agent_id) -> bool
        True iff the producer has any registered entry on this task.
    prune_by_paths(paths) -> int
        Remove ArtifactRefs whose path is in ``paths``; entries that
        become empty are removed entirely.
    """

    def __init__(self, workspace_id: str, runtime_base_path: Path) -> None:
        self.workspace_id = workspace_id
        self.runtime_base_path = Path(runtime_base_path)
        self.workspace_runtime_path = self.runtime_base_path / workspace_id
        self.workspace_runtime_path.mkdir(parents=True, exist_ok=True)
        self._memory_path = self.workspace_runtime_path / GLOBAL_MEMORY_FILENAME
        self._legacy_registry_path = (
            self.workspace_runtime_path / LEGACY_REGISTRY_FILENAME
        )

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
    def _entry_to_dict(entry: GlobalMemoryEntry) -> Dict[str, Any]:
        return {
            "execution_id": entry.execution_id,
            "agent_id": entry.agent_id,
            "task_id": entry.task_id,
            "created_at": entry.created_at.isoformat(),
            "artifacts": [GlobalMemory._ref_to_dict(r) for r in entry.artifacts],
        }

    @staticmethod
    def _entry_from_dict(d: Dict[str, Any]) -> GlobalMemoryEntry:
        created_raw = d.get("created_at") or ""
        try:
            created_at = datetime.fromisoformat(created_raw)
        except (ValueError, TypeError):
            created_at = datetime.now(UTC)
        return GlobalMemoryEntry(
            execution_id=str(d.get("execution_id") or ""),
            agent_id=str(d.get("agent_id") or ""),
            task_id=str(d.get("task_id") or ""),
            created_at=created_at,
            artifacts=[
                GlobalMemory._ref_from_dict(r)
                for r in (d.get("artifacts") or [])
            ],
        )

    # ------------------------------------------------------------------
    # Markdown document composition
    # ------------------------------------------------------------------

    def _compose_document(self, entries: List[GlobalMemoryEntry]) -> str:
        body = json.dumps(
            [self._entry_to_dict(e) for e in entries],
            ensure_ascii=False,
            indent=2,
        )
        return (
            f"# Global memory — `{self.workspace_id}`\n\n"
            f"Per-execution record of every artifact persisted in this workspace. "
            f"Each entry below is one agent execution; its `artifacts` array carries "
            f"the natural-language caption (`what` / `why` / `scope`), absolute "
            f"`path` and `mime` for every file that execution wrote.\n\n"
            f"`InputResolver` reads this index to match artifacts against each "
            f"consumer agent's `[label]` slots. The lightweight director-facing "
            f"rollup is exposed via `Workspace.get_global_memory_brief()` — there "
            f"is no separate brief file on disk.\n\n"
            f"{ENTRIES_HEADER}\n\n"
            f"```json\n{body}\n```\n"
        )

    @staticmethod
    def _parse_entries_from_markdown(text: str) -> Optional[List[Dict[str, Any]]]:
        if not text.strip():
            return None
        idx = text.find(ENTRIES_HEADER)
        segment = text[idx:] if idx >= 0 else text
        match = JSON_FENCE_RE.search(segment)
        if not match:
            return None
        try:
            data = json.loads(match.group(1).strip())
            if isinstance(data, list):
                return [d for d in data if isinstance(d, dict)]
        except json.JSONDecodeError as exc:
            logger.warning("GlobalMemory: failed to parse Entries JSON: %s", exc)
        return None

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _read_all(self) -> List[GlobalMemoryEntry]:
        # Preferred: new global_memory.md (markdown wrapper).
        if self._memory_path.exists():
            try:
                text = self._memory_path.read_text(encoding="utf-8")
            except OSError as exc:
                logger.warning("GlobalMemory: failed to read %s: %s", self._memory_path, exc)
                return []
            parsed = self._parse_entries_from_markdown(text)
            if parsed is None:
                logger.warning(
                    "GlobalMemory: %s present but Entries block missing or invalid",
                    self._memory_path,
                )
                return []
            return [self._entry_from_dict(d) for d in parsed]

        # Backward compatibility: workspaces written before the rename
        # have an append-only ``artifact_registry.jsonl``. Read it
        # transparently so old runs still load. The next ``register()``
        # / ``prune_by_paths()`` call will rewrite into the new
        # markdown file.
        if self._legacy_registry_path.exists():
            entries: List[GlobalMemoryEntry] = []
            try:
                with open(self._legacy_registry_path, "r", encoding="utf-8") as fh:
                    for line in fh:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            d = json.loads(line)
                            entries.append(self._entry_from_dict(d))
                        except Exception as exc:
                            logger.warning(
                                "GlobalMemory: skipping malformed legacy line: %s", exc,
                            )
            except OSError as exc:
                logger.warning(
                    "GlobalMemory: failed to read legacy registry %s: %s",
                    self._legacy_registry_path, exc,
                )
            return entries

        return []

    def _write_all(self, entries: List[GlobalMemoryEntry]) -> None:
        try:
            self._memory_path.parent.mkdir(parents=True, exist_ok=True)
            self._memory_path.write_text(
                self._compose_document(entries),
                encoding="utf-8",
            )
        except OSError as exc:
            logger.warning("GlobalMemory: failed to write %s: %s", self._memory_path, exc)
            raise

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
    ) -> GlobalMemoryEntry:
        """Append a new entry and rewrite ``global_memory.md``."""
        entry = GlobalMemoryEntry(
            execution_id=execution_id,
            agent_id=agent_id,
            task_id=task_id,
            created_at=datetime.now(UTC),
            artifacts=artifacts,
        )
        entries = self._read_all()
        entries.append(entry)
        self._write_all(entries)
        return entry

    def list_all(self) -> List[GlobalMemoryEntry]:
        """Return all entries in chronological order."""
        return self._read_all()

    def get_by_paths(self, paths: List[str]) -> List[ArtifactRef]:
        """Return ArtifactRef objects matching the given file paths."""
        want = set(paths)
        result: List[ArtifactRef] = []
        for entry in self._read_all():
            for ref in entry.artifacts:
                if ref.path in want:
                    result.append(ref)
        return result

    def find_by_producer(
        self,
        *,
        task_id: str,
        agent_id: str,
    ) -> List[ArtifactRef]:
        """Return every ArtifactRef registered by ``agent_id`` on ``task_id``.

        Used by ArtifactWriter overwrite-mode dedup to locate every prior
        artifact this producer wrote on this task — across binary, manifest
        and json_snapshot — so they can be wiped before the new run writes.
        """
        result: List[ArtifactRef] = []
        for entry in self._read_all():
            if entry.task_id != task_id or entry.agent_id != agent_id:
                continue
            result.extend(entry.artifacts)
        return result

    def has_producer_run(self, *, task_id: str, agent_id: str) -> bool:
        """True if any registered entry was produced by ``agent_id`` on ``task_id``.

        Used by AssistantService to auto-flip overwrite mode when an agent
        re-runs on a task it has already executed against.
        """
        for entry in self._read_all():
            if entry.task_id == task_id and entry.agent_id == agent_id:
                return True
        return False

    def prune_by_paths(self, paths: List[str]) -> int:
        """Remove every ArtifactRef whose ``path`` is in ``paths``.

        Entries that become empty after pruning are themselves removed.
        Returns the number of refs deleted (not entries).
        """
        if not paths:
            return 0
        drop = set(paths)
        entries = self._read_all()
        kept_entries: List[GlobalMemoryEntry] = []
        removed_refs = 0
        for e in entries:
            kept_refs = [r for r in e.artifacts if r.path not in drop]
            removed_refs += len(e.artifacts) - len(kept_refs)
            if kept_refs:
                e.artifacts = kept_refs
                kept_entries.append(e)
        if removed_refs > 0:
            self._write_all(kept_entries)
        return removed_refs

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
