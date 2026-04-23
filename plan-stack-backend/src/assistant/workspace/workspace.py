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
        step_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        level: str = "INFO",
        execution_id: Optional[str] = None,
    ) -> None:
        self.log_manager.add_log(
            event=event,
            resource_id=resource_id,
            agent_id=agent_id,
            step_id=step_id,
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
            step_id=str(execution.step_id or ""),
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
        """Persist a raw user upload as a workspace artifact.

        **text/plain** takes a direct-to-global path: the upload is
        wrapped in the same ``{meta, content: {text}, metrics}`` JSON
        shape the retired IntakeTextAgent used to produce, written as
        a ``brief_<ts>.json`` artifact, and registered at
        ``scope=global`` with the story/screenplay/narration-facing
        caption. This replaces the retired IntakeTextAgent step; chat
        messages and text uploads become immediately consumable without
        a dedicated intake pass.

        **Binary uploads (image/video/audio)** keep the two-step path:
        bytes are saved, registered at ``scope=raw_pending`` with a
        placeholder caption, and the matching IntakeXxxAgent runs next
        to produce the caption-rich artifact (IntakeImage / IntakeVideo
        still carry real LLM work — captioning, scene probing — so the
        intake pattern stays load-bearing for them).

        Returns a dict describing the persisted artifact: ``path``,
        ``filename``, ``mime``, ``caption``, ``scope``.
        """
        from datetime import datetime, UTC
        import json as _json
        import os as _os
        from .models import ArtifactRef as _ArtifactRef

        ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S_%f")

        if mime == "text/plain":
            return self._persist_text_brief(
                ts=ts,
                text=(file_content.decode("utf-8", errors="replace") if file_content else ""),
                original_filename=original_filename,
            )

        ext = ""
        if original_filename and "." in original_filename:
            ext = _os.path.splitext(original_filename)[1].lower()
        elif mime:
            mime_to_ext = {
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
            step_id="",  # uploads are not bound to a task at the moment of upload
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

    def _persist_text_brief(
        self,
        *,
        ts: str,
        text: str,
        original_filename: str = "",
    ) -> Dict[str, Any]:
        """Register a user text brief straight at scope=global.

        Shape matches the retired IntakeTextAgent's output: the
        ``{content: {text}}`` payload is the contract story/screenplay/
        narration agents already read via ``entry.payload``.
        """
        from datetime import datetime, UTC
        import json as _json
        from .models import ArtifactRef as _ArtifactRef

        text = (text or "").strip()
        doc = {
            "meta": {
                "asset_type": "text_brief",
                "created_at": datetime.now(UTC).isoformat(),
            },
            "content": {"text": text},
            "metrics": {"char_count": len(text)},
        }
        doc_bytes = _json.dumps(doc, ensure_ascii=False, indent=2).encode("utf-8")

        base = "brief"
        if original_filename:
            # keep the user's stem but force a .json extension (we're
            # registering the structured wrapper, not the raw .txt).
            import os as _os
            stem = _os.path.splitext(original_filename)[0] or base
            filename = f"{ts}_{stem}.json"
        else:
            filename = f"{base}_{ts}.json"
        relative_path = f"inputs/{filename}"

        stored = self.store_file_at_relative_path(
            relative_path,
            file_content=doc_bytes,
            filename=filename,
        )

        caption = (
            "Structured metadata document (JSON) for a user-submitted "
            "text brief. Payload carries the raw text verbatim. "
            "Pipeline entry point — consumed by story / screenplay / "
            "narration agents."
        )
        ref = _ArtifactRef(
            caption=caption,
            scope="global",
            path=stored.path,
            mime="application/json",
        )
        self.global_memory.register(
            execution_id=f"brief_{ts}",
            agent_id="user",
            step_id="",
            artifacts=[ref],
        )
        self._add_log(
            event="user.upload",
            resource_id=stored.path,
            agent_id="user",
            details={
                "filename": filename,
                "mime": "application/json",
                "scope": "global",
                "source": "text_brief",
                "char_count": len(text),
            },
        )
        return {
            "path": stored.path,
            "filename": filename,
            "mime": "application/json",
            "caption": caption,
            "scope": "global",
        }

    def list_workspace_artifacts(self) -> List[Dict[str, Any]]:
        """Return a flat list of all registered artifacts in this workspace.

        Each entry has the artifact's caption, scope, absolute path, mime,
        and the producing execution's agent_id/step_id/execution_id/created_at.
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
                    "step_id": entry.step_id,
                    "execution_id": entry.execution_id,
                    "created_at": entry.created_at.isoformat() if entry.created_at else "",
                })
        return rows

    # ------------------------------------------------------------------
    # Input Resolution
    # ------------------------------------------------------------------

    def resolve_inputs_for_agent(
        self,
        *,
        agent_id: str,
        step_id: str,
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
            step_id=step_id,
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
        step_id: Optional[str] = None,
        limit: Optional[int] = None,
        level: Optional[str] = None,
        execution_id: Optional[str] = None,
    ) -> List[LogEntry]:
        return self.log_manager.get_logs(
            event=event,
            agent_id=agent_id,
            step_id=step_id,
            limit=limit,
            level=level,
            execution_id=execution_id,
        )

    def log_execution_started(self, execution: Any) -> None:
        self._add_log(
            event="execution.started",
            resource_id=execution.id,
            agent_id=execution.agent_id,
            step_id=execution.step_id,
            execution_id=execution.id,
            details={
                "status": str(getattr(execution.status, "value", execution.status)),
            },
        )

    def log_artifact_materialize_failure(
        self,
        *,
        agent_id: str,
        step_id: str,
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
            step_id=step_id,
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
            step_id=execution.step_id,
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


