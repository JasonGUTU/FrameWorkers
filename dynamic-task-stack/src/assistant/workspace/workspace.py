"""Workspace — facade unifying all per-workspace managers.

The ``Workspace`` class is the only public surface that ``service.py``
and ``routes.py`` use; all manager classes are wired internally and
exchange data through callbacks rather than direct cross-references.

Composition (one instance per workspace directory):

  * ``FileManager``    — stateless byte read/write under the runtime path
  * ``LogManager``     — append-only operation log (``logs.jsonl``)
  * ``GlobalMemory``   — per-execution artifact ledger (``global_memory.md``)
  * ``ArtifactWriter`` — execution-aware persistence (wired with callbacks
                          into the three managers above)
  * ``InputResolver``  — built per-call inside
                          ``resolve_inputs_for_agent`` from the
                          memory + file_manager + an LLM client

What it does NOT do:
  * Run agents — that is ``service.AssistantService``.
  * Decide persist plans — those are built in ``service`` and passed in.

Used by:
  * ``service.AssistantService`` (via ``self.workspace.X``)
  * ``routes.py`` (via the singleton workspace per request)
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from .file_manager import FileManager
from .log_manager import LogManager
from .artifact_writer import ArtifactWriter
from .global_memory import GlobalMemory
from .input_resolver import InputResolver
from .models import LogEntry, StoredFile


class Workspace:
    """Per-workspace facade composing the three storage managers.

    Each workspace has its own directory under
    ``Runtime/{workspace_id}/`` containing:

    * ``global_memory.md`` — per-execution artifact ledger (the only
      semantic record; written/read by ``GlobalMemory``)
    * ``logs.jsonl``       — namespaced ``event`` lifecycle log
    * ``artifacts/...``    — agent output files (organised by
      ``ArtifactWriter`` from a ``persist_execution_from_plan`` call)
    * ``inputs/...``       — raw user uploads
    """

    def __init__(self, workspace_id: str, runtime_base_path: Path):
        self.id = workspace_id
        self.runtime_base_path = Path(runtime_base_path)
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

        # Core managers
        self.file_manager = FileManager(workspace_id, runtime_base_path)
        self.log_manager = LogManager(workspace_id, runtime_base_path)
        self.global_memory = GlobalMemory(workspace_id, runtime_base_path)

        # ArtifactWriter wired with global_memory callbacks
        self.artifact_writer = ArtifactWriter(
            self.store_file_at_relative_path,
            self._add_log,
            self.file_manager.read_binary_from_uri,
            on_change=self._touch,
            register_artifacts=self._register_artifacts_callback,
            find_artifact_refs_for_producer=self.global_memory.find_by_producer,
            delete_file_at_path=self._delete_file_at_path,
            prune_global_memory_by_paths=self.global_memory.prune_by_paths,
        )

        # Log workspace creation
        self.log_manager.add_log(
            event="workspace.created",
            resource_id=workspace_id,
            details={"workspace_id": workspace_id},
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _touch(self) -> None:
        self.updated_at = datetime.now()

    def _add_log(
        self,
        *,
        event: str,
        resource_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        task_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        level: str = "INFO",
        execution_id: Optional[str] = None,
    ) -> None:
        self.log_manager.add_log(
            event=event,
            resource_id=resource_id,
            agent_id=agent_id,
            task_id=task_id,
            details=details or {},
            level=level,
            execution_id=execution_id,
        )

    def _delete_file_at_path(self, path: str) -> bool:
        """Unlink a workspace file by absolute path. Used by ArtifactWriter dedup."""
        try:
            from pathlib import Path as _Path
            p = _Path(path)
            if p.exists() and p.is_file():
                p.unlink()
                return True
        except OSError as exc:
            import logging as _logging
            _logging.getLogger(__name__).warning(
                "Workspace: failed to delete file at %s: %s", path, exc,
            )
        return False

    def _register_artifacts_callback(
        self,
        *,
        execution: Any,
        artifact_refs: List[Dict[str, Any]],
    ) -> None:
        """Called by ArtifactWriter after persisting artifacts.

        ``artifact_refs`` is a list of dicts with keys: caption, scope,
        path, mime. Each dict maps to one ArtifactRef in the registry.
        """
        from .models import ArtifactRef as _ArtifactRef
        refs = [
            _ArtifactRef(
                caption=str(r.get("caption") or ""),
                scope=str(r.get("scope") or "global"),
                path=str(r.get("path") or ""),
                mime=str(r.get("mime") or ""),
            )
            for r in artifact_refs
            if isinstance(r, dict)
        ]
        self.global_memory.register(
            execution_id=str(execution.id or ""),
            agent_id=str(execution.agent_id or ""),
            task_id=str(execution.task_id or ""),
            artifacts=refs,
        )

    # ------------------------------------------------------------------
    # File Management
    # ------------------------------------------------------------------

    def store_file_at_relative_path(
        self,
        relative_path: str,
        file_content: bytes,
        filename: str = "",
    ) -> StoredFile:
        """Write bytes under ``Runtime/{workspace_id}/<relative_path>``.

        This method is a thin wrapper around ``FileManager`` that does NOT
        emit any log entry on its own. Bytes hitting disk is a low-level
        side effect; the meaningful event ("an artifact has been
        persisted by an agent") is recorded one layer up in
        ``ArtifactWriter`` with an ``artifact.*`` event so log readers
        see exactly one entry per logical persistence.

        Returns a transient ``StoredFile`` (path/filename/size). The file
        becomes "discoverable" only after the caller registers it in the
        artifact registry — usually via ``ArtifactWriter`` doing that
        automatically as part of ``persist_execution_from_plan``.
        """
        stored = self.file_manager.store_file_at_relative_path(
            relative_path,
            file_content=file_content,
            filename=filename,
        )
        self._touch()
        return stored

    def persist_raw_upload(
        self,
        *,
        file_content: bytes,
        mime: str,
        original_filename: str = "",
    ) -> Dict[str, Any]:
        """Persist a raw user upload as a workspace artifact with a placeholder caption.

        Writes the bytes under ``inputs/<timestamp>_<filename>`` and
        registers an ``ArtifactRef`` with a generic placeholder caption
        (``scope=raw_pending``). A subsequent invocation of the matching
        Intake agent picks this artifact up via its
        ``[raw_<kind>_upload]`` label and produces a caption-rich
        follow-up artifact for downstream content agents.

        Returns a dict describing the persisted artifact: ``path``,
        ``filename``, ``mime``, ``caption``.
        """
        from datetime import datetime, UTC
        import os as _os
        from .models import ArtifactRef as _ArtifactRef

        ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S_%f")
        ext = ""
        if original_filename and "." in original_filename:
            ext = _os.path.splitext(original_filename)[1].lower()
        elif mime:
            mime_to_ext = {
                "text/plain": ".txt",
                "image/png": ".png",
                "image/jpeg": ".jpg",
                "image/webp": ".webp",
                "video/mp4": ".mp4",
                "video/quicktime": ".mov",
                "audio/wav": ".wav",
                "audio/mpeg": ".mp3",
                "application/json": ".json",
            }
            ext = mime_to_ext.get(mime, "")
        filename = f"upload_{ts}{ext}" if not original_filename else f"{ts}_{original_filename}"
        relative_path = f"inputs/{filename}"

        stored = self.store_file_at_relative_path(
            relative_path,
            file_content=file_content,
            filename=filename,
        )

        placeholder_caption = (
            f"Raw user upload (mime={mime or 'unknown'}). "
            "Pending intake processing — only visible to Intake* agents."
        )

        ref = _ArtifactRef(
            caption=placeholder_caption,
            scope="raw_pending",
            path=stored.path,
            mime=mime,
        )
        self.global_memory.register(
            execution_id=f"upload_{ts}",
            agent_id="user",
            task_id="",  # uploads are not bound to a task at the moment of upload
            artifacts=[ref],
        )
        self._add_log(
            event="user.upload",
            resource_id=stored.path,
            agent_id="user",
            details={
                "filename": filename,
                "mime": mime,
                "scope": "raw_pending",
            },
        )
        return {
            "path": stored.path,
            "filename": filename,
            "mime": mime,
            "caption": placeholder_caption,
            "scope": "raw_pending",
        }

    def list_workspace_artifacts(self) -> List[Dict[str, Any]]:
        """Return a flat list of all registered artifacts in this workspace.

        Each entry has the artifact's caption, scope, absolute path, mime,
        and the producing execution's agent_id/task_id/execution_id/created_at.
        """
        rows: List[Dict[str, Any]] = []
        for entry in self.global_memory.list_all():
            for ref in entry.artifacts:
                rows.append({
                    "path": ref.path,
                    "filename": Path(ref.path).name if ref.path else "",
                    "mime": ref.mime,
                    "caption": ref.caption,
                    "scope": ref.scope,
                    "agent_id": entry.agent_id,
                    "task_id": entry.task_id,
                    "execution_id": entry.execution_id,
                    "created_at": entry.created_at.isoformat() if entry.created_at else "",
                })
        return rows

    # ------------------------------------------------------------------
    # Global memory (semantic record — the only memory layer)
    # ------------------------------------------------------------------

    def get_global_memory_brief(
        self,
        *,
        task_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Return the director-facing rollup of ``global_memory``.

        Each row is one execution that successfully produced artifacts,
        projected down to ``{execution_id, agent_id, task_id, status,
        created_at}``, in chronological order (oldest → newest). Director
        uses this to plan next steps.

        Failed executions do not appear here (they leave no artifacts);
        if a director needs to see failures it should query
        ``GET /api/assistant/workspace/logs?event=execution.failed``.
        """
        entries = self.global_memory.list_all()
        if task_id:
            entries = [e for e in entries if e.task_id == task_id or not e.task_id]
        if agent_id:
            entries = [e for e in entries if e.agent_id == agent_id]
        entries.sort(
            key=lambda e: e.created_at.isoformat() if e.created_at else "",
        )
        if limit is None:
            entries = entries[-_global_memory_brief_default_limit():]
        elif limit > 0:
            entries = entries[-int(limit):]
        rows = [
            {
                "execution_id": e.execution_id,
                "agent_id": e.agent_id,
                "task_id": e.task_id,
                "status": "COMPLETED",
                "created_at": e.created_at.isoformat() if e.created_at else "",
            }
            for e in entries
        ]
        return rows

    def get_workspace_root_file_tree_text(self) -> str:
        """Human-readable tree of every file under the workspace runtime root."""
        return _build_file_tree_text(self.runtime_base_path / self.id)

    # ------------------------------------------------------------------
    # Input Resolution
    # ------------------------------------------------------------------

    def resolve_inputs_for_agent(
        self,
        *,
        agent_id: str,
        task_id: str,
        input_needs_description: str,
        llm_client: Any,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """LLM-based per-artifact semantic input resolution.

        Returns dict with keys:
          resolved_artifacts        : dict[str, ResolvedArtifactEntry | list[ResolvedArtifactEntry]]
                                      — keyed by consumer-declared label,
                                      ``(single)`` labels map to one entry,
                                      ``(collection)`` labels to a list.
                                      Entry shape lives in
                                      ``agents.common_schema.ResolvedArtifactEntry``.
          selected_artifact_paths   : list[str]
          rationale                 : str
        """
        resolver = InputResolver(self.global_memory, self.file_manager, llm_client)
        return resolver.resolve(
            agent_id=agent_id,
            task_id=task_id,
            input_needs_description=input_needs_description,
            model=model,
        )

    # ------------------------------------------------------------------
    # Log Methods
    # ------------------------------------------------------------------

    def get_logs(
        self,
        *,
        event: Optional[str] = None,
        agent_id: Optional[str] = None,
        task_id: Optional[str] = None,
        limit: Optional[int] = None,
        level: Optional[str] = None,
        execution_id: Optional[str] = None,
    ) -> List[LogEntry]:
        return self.log_manager.get_logs(
            event=event,
            agent_id=agent_id,
            task_id=task_id,
            limit=limit,
            level=level,
            execution_id=execution_id,
        )

    def log_execution_started(self, execution: Any) -> None:
        self._add_log(
            event="execution.started",
            resource_id=execution.id,
            agent_id=execution.agent_id,
            task_id=execution.task_id,
            execution_id=execution.id,
            details={
                "status": str(getattr(execution.status, "value", execution.status)),
            },
        )

    def log_artifact_materialize_failure(
        self,
        *,
        agent_id: str,
        task_id: str,
        execution_id: str,
        kind: str,
        sys_id: str,
        error: str,
    ) -> None:
        """Record a per-call materializer failure as a structured event.

        Materializers' inner ``except Exception`` blocks call this via
        ``MaterializeContext.report_failure`` so swallowed gen errors
        (image / video / audio) become findable in ``logs.jsonl`` for
        post-hoc analysis. Without this hook the only trace was a
        Python ``logger.error`` line that pytest captures and discards
        on test pass.
        """
        self._add_log(
            event="artifact.materialize_failed",
            resource_id=sys_id or "",
            agent_id=agent_id,
            task_id=task_id,
            execution_id=execution_id,
            level="ERROR",
            details={
                "kind": kind,
                "sys_id": sys_id,
                "error": error,
            },
        )

    def log_execution_result(self, execution: Any) -> None:
        status = str(getattr(execution.status, "value", execution.status))
        event = "execution.completed" if status == "COMPLETED" else "execution.failed"
        retry_attempts = None
        eval_summary = None
        results = getattr(execution, "results", None)
        if isinstance(results, dict):
            debug = results.get("_execution_debug", {})
            if isinstance(debug, dict):
                attempts = debug.get("attempts")
                if isinstance(attempts, int):
                    retry_attempts = attempts
                summary = debug.get("eval_summary")
                if isinstance(summary, str) and summary:
                    eval_summary = summary
        self._add_log(
            event=event,
            resource_id=execution.id,
            agent_id=execution.agent_id,
            task_id=execution.task_id,
            execution_id=execution.id,
            level="INFO" if status == "COMPLETED" else "ERROR",
            details={
                "status": status,
                "error": getattr(execution, "error", None),
                "has_results": getattr(execution, "results", None) is not None,
                "retry_attempts": retry_attempts,
                "eval_summary": eval_summary,
            },
        )

    # ------------------------------------------------------------------
    # Artifact Methods
    # ------------------------------------------------------------------

    def hydrate_indexed_assets(self, assets: Dict[str, Any]) -> Dict[str, Any]:
        return self.artifact_writer.hydrate_indexed_assets(assets)

    def collect_materialized_files(self, media_assets: list[Any]) -> Dict[str, Any]:
        return self.artifact_writer.collect_materialized_files(media_assets)

    def persist_execution_from_plan(
        self,
        execution: Any,
        assignments: List[Dict[str, Any]],
        *,
        overwrite_existing: bool = False,
        captions: Optional[Dict[str, Dict[str, str]]] = None,
    ) -> tuple[Dict[str, str], Optional[Dict[str, Any]]]:
        return self.artifact_writer.persist_execution_from_plan(
            execution,
            assignments,
            overwrite_existing=overwrite_existing,
            captions=captions,
        )


# ----------------------------------------------------------------------
# Module-level helpers
# ----------------------------------------------------------------------


def _global_memory_brief_default_limit() -> int:
    """Default cap on rows returned by ``get_global_memory_brief``.

    Reads ``ASSISTANT_GLOBAL_MEMORY_CONTEXT_ENTRIES_MAX`` (kept for
    backward compatibility with the previous brief implementation) and
    clamps to ``[1, 500]``.
    """
    import os as _os
    try:
        n = int(_os.getenv("ASSISTANT_GLOBAL_MEMORY_CONTEXT_ENTRIES_MAX", "20").strip())
        return max(1, min(n, 500))
    except ValueError:
        return 20


def _build_file_tree_text(root: Path) -> str:
    """Render a workspace runtime root as a flat indented file tree."""
    lines: List[str] = []
    max_lines = 800
    try:
        root = root.resolve()
        all_files = sorted(
            (p for p in root.rglob("*") if p.is_file()),
            key=lambda p: str(p.relative_to(root)).replace("\\", "/"),
        )
    except OSError as exc:
        return f"(unable to list files: {exc})"

    for p in all_files[:max_lines]:
        try:
            rel = p.relative_to(root)
        except ValueError:
            continue
        depth = len(rel.parts)
        indent = "  " * max(0, depth - 1)
        lines.append(f"{indent}{rel.parts[-1]}")
    if len(all_files) > max_lines:
        lines.append(f"... ({len(all_files) - max_lines} more files truncated)")
    return "\n".join(lines) if lines else "(no files yet)"
