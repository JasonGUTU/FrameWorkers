"""Workspace — facade unifying all per-workspace managers.

The ``Workspace`` class is the only public surface that ``service.py``
and ``routes.py`` use; all manager classes are wired internally and
exchange data through callbacks rather than direct cross-references.

Composition (one instance per workspace directory):

  * ``FileManager``      — raw file persistence + ``.file_metadata.json``
  * ``MemoryManager``    — semantic decisions + index
  * ``LogManager``       — append-only operation log
  * ``ArtifactRegistry`` — natural-language caption index per file
  * ``AssetManager``     — execution-aware persistence (wired with
                            callbacks into the four managers above)
  * ``InputResolver``    — built per-call inside
                            ``resolve_inputs_for_agent`` from the
                            registry + file_manager + an LLM client

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
from .memory_manager import MemoryManager
from .log_manager import LogManager
from .asset_manager import AssetManager
from .artifact_registry import ArtifactRegistry
from .input_resolver import InputResolver
from .models import FileMetadata, LogEntry


class Workspace:
    """
    Workspace - Manages file system, global memory, artifact registry, and logs.

    The workspace provides a unified interface for:
    - File management (images, videos, documents, etc.)
    - Global memory (semantic decisions — the "why")
    - Artifact registry (artifact index with captions — the "what")
    - Logs and records (operation stream — the "when")

    Each workspace has its own directory in Runtime/{workspace_id}/
    """

    def __init__(self, workspace_id: str, runtime_base_path: Path):
        self.id = workspace_id
        self.runtime_base_path = Path(runtime_base_path)
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

        # Core managers
        self.file_manager = FileManager(workspace_id, runtime_base_path)
        self.memory_manager = MemoryManager(workspace_id, runtime_base_path)
        self.log_manager = LogManager(workspace_id, runtime_base_path)
        self.artifact_registry = ArtifactRegistry(workspace_id, runtime_base_path)

        # AssetManager wired with artifact_registry callback
        self.asset_manager = AssetManager(
            self.store_file_at_relative_path,
            self._add_log,
            self.file_manager.read_binary_from_uri,
            self.list_files,
            self.delete_file,
            on_change=self._touch,
            register_artifacts=self._register_artifacts_callback,
            prune_artifact_registry=self._prune_artifact_registry_by_producer,
        )

        # Log workspace creation
        self.log_manager.add_log(
            operation_type="create",
            resource_type="workspace",
            resource_id=workspace_id,
            event="workspace.created",
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
        operation_type: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        task_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        event: Optional[str] = None,
        level: str = "INFO",
        execution_id: Optional[str] = None,
        duration_ms: Optional[int] = None,
    ) -> None:
        self.log_manager.add_log(
            operation_type=operation_type,
            resource_type=resource_type,
            resource_id=resource_id,
            agent_id=agent_id,
            task_id=task_id,
            details=details or {},
            event=event,
            level=level,
            execution_id=execution_id,
            duration_ms=duration_ms,
        )

    def _prune_artifact_registry_by_producer(
        self,
        *,
        task_id: str,
        agent_id: str,
    ) -> int:
        """Forward to ArtifactRegistry.prune_by_producer.

        Called by AssetManager when an agent re-runs in overwrite mode, so
        that stale registry entries (pointing at just-deleted files) don't
        leak into InputResolver's caption index.
        """
        return self.artifact_registry.prune_by_producer(
            task_id=task_id, agent_id=agent_id,
        )

    def _register_artifacts_callback(
        self,
        *,
        execution: Any,
        artifact_refs: List[Dict[str, Any]],
    ) -> None:
        """Called by AssetManager after persisting artifacts.

        ``artifact_refs`` is a list of dicts with keys: what, why, scope, path, mime.
        Each dict maps to one ArtifactRef in the registry.
        """
        from .models import ArtifactRef as _ArtifactRef
        refs = [
            _ArtifactRef(
                what=str(r.get("what") or ""),
                why=str(r.get("why") or ""),
                scope=str(r.get("scope") or "global"),
                path=str(r.get("path") or ""),
                mime=str(r.get("mime") or ""),
            )
            for r in artifact_refs
            if isinstance(r, dict)
        ]
        self.artifact_registry.register(
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
        filename: str,
        description: str,
        created_by: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> FileMetadata:
        """Write under ``Runtime/{workspace_id}/<relative_path>``."""
        file_metadata = self.file_manager.store_file_at_relative_path(
            relative_path,
            file_content=file_content,
            filename=filename,
            description=description,
            created_by=created_by,
            tags=tags,
            metadata=metadata,
        )
        self._add_log(
            operation_type="create",
            resource_type="file",
            resource_id=file_metadata.id,
            agent_id=created_by,
            event="file.created",
            details={
                "filename": filename,
                "description": description,
                "file_type": file_metadata.file_type,
                "size_bytes": file_metadata.size_bytes,
            },
        )
        self._touch()
        return file_metadata

    def persist_raw_upload(
        self,
        *,
        file_content: bytes,
        mime: str,
        user_intent: str,
        original_filename: str = "",
    ) -> Dict[str, Any]:
        """Persist a raw user upload as a workspace artifact with a placeholder caption.

        This is the entry point for the new B2 ``POST /api/workspace/upload``
        protocol. It writes the bytes to disk under ``inputs/<timestamp>_<filename>``
        and registers an ``ArtifactRef`` with a generic placeholder caption that
        signals "raw user upload, awaiting semantic analysis". A subsequent
        invocation of an Intake agent (text/image/video/audio) will pick this
        artifact up via its ``[raw_<kind>_upload]`` label and produce a
        caption-rich follow-up artifact for downstream content agents.

        Returns a dict describing the persisted artifact (id, path, caption).
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

        file_meta = self.store_file_at_relative_path(
            relative_path,
            file_content=file_content,
            filename=filename,
            description=f"Raw user upload (mime={mime or 'unknown'})",
            created_by="user",
            tags=["user_upload", "raw_pending"],
            metadata={
                "mime": mime,
                "user_intent": user_intent,
                "raw_pending": True,
            },
        )

        placeholder_what = (
            f"raw user upload, mime={mime or 'unknown'}, "
            f"awaiting semantic analysis"
        )
        placeholder_why = (user_intent or "").strip() or "(no user intent provided)"

        ref = _ArtifactRef(
            what=placeholder_what,
            why=placeholder_why,
            scope="raw_pending",
            path=file_meta.file_path,
            mime=mime,
        )
        self.artifact_registry.register(
            execution_id=f"upload_{ts}",
            agent_id="user",
            task_id="",  # uploads are not bound to a task at the moment of upload
            artifacts=[ref],
        )
        self._add_log(
            operation_type="create",
            resource_type="artifact",
            resource_id=file_meta.id,
            agent_id="user",
            event="user.upload",
            details={
                "filename": filename,
                "mime": mime,
                "user_intent": user_intent,
                "scope": "raw_pending",
            },
        )
        return {
            "file_id": file_meta.id,
            "path": file_meta.file_path,
            "filename": filename,
            "mime": mime,
            "caption": {
                "what": placeholder_what,
                "why": placeholder_why,
                "scope": "raw_pending",
            },
        }

    def get_file(self, file_id: str) -> Optional[FileMetadata]:
        return self.file_manager.get_file(file_id)

    def list_files(self) -> List[FileMetadata]:
        return self.file_manager.list_files()

    def delete_file(self, file_id: str) -> bool:
        file_meta = self.file_manager.get_file(file_id)
        if file_meta:
            success = self.file_manager.delete_file(file_id)
            if success:
                self._add_log(
                    operation_type="delete",
                    resource_type="file",
                    resource_id=file_id,
                    event="file.deleted",
                    details={"filename": file_meta.filename},
                )
                self._touch()
            return success
        return False

    # ------------------------------------------------------------------
    # Memory (semantic decisions — the "why")
    # ------------------------------------------------------------------

    def add_memory_entry(
        self,
        *,
        content: Any,
        task_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        supersedes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Append one semantic memory entry.

        ``content`` should be a dict with keys ``what``, ``why``, ``context_note``
        (or a plain string which is promoted to ``{"what": text}``).
        Artifact paths belong in artifact_registry, not here.
        """
        entry = self.memory_manager.add_memory_entry(
            content=content,
            task_id=task_id,
            agent_id=agent_id,
            execution_id=execution_id,
            supersedes=supersedes,
        )
        self._add_log(
            operation_type="write",
            resource_type="memory",
            resource_id=entry.get("created_at"),
            agent_id=agent_id,
            task_id=task_id,
            event="memory.written",
            execution_id=execution_id,
            details={"event_type": "memory_entry_added"},
        )
        self._touch()
        return entry

    def list_memory_entries(
        self,
        *,
        task_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        return self.memory_manager.list_memory_entries(
            task_id=task_id,
            agent_id=agent_id,
            limit=limit,
        )

    def get_memory_brief(
        self,
        *,
        task_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        return self.memory_manager.get_memory_brief(
            task_id=task_id,
            agent_id=agent_id,
            limit=limit,
        )

    def get_workspace_root_file_tree_text(self) -> str:
        return self.memory_manager.workspace_root_file_tree_text()

    # ------------------------------------------------------------------
    # Artifact Registry
    # ------------------------------------------------------------------

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
          resolved_artifacts        : list[{what, why, scope, path, mime, payload}]
          selected_artifact_paths   : list[str]
          rationale                 : str
        """
        resolver = InputResolver(self.artifact_registry, self.file_manager, llm_client)
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
        operation_type: Optional[str] = None,
        resource_type: Optional[str] = None,
        agent_id: Optional[str] = None,
        task_id: Optional[str] = None,
        limit: Optional[int] = None,
        level: Optional[str] = None,
        event: Optional[str] = None,
        execution_id: Optional[str] = None,
    ) -> List[LogEntry]:
        return self.log_manager.get_logs(
            operation_type=operation_type,
            resource_type=resource_type,
            agent_id=agent_id,
            task_id=task_id,
            limit=limit,
            level=level,
            event=event,
            execution_id=execution_id,
        )

    def log_execution_started(self, execution: Any) -> None:
        self._add_log(
            operation_type="write",
            resource_type="execution",
            resource_id=execution.id,
            agent_id=execution.agent_id,
            task_id=execution.task_id,
            event="execution.started",
            execution_id=execution.id,
            details={
                "event_type": "execution_started",
                "status": str(getattr(execution.status, "value", execution.status)),
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
            operation_type="write",
            resource_type="execution",
            resource_id=execution.id,
            agent_id=execution.agent_id,
            task_id=execution.task_id,
            event=event,
            execution_id=execution.id,
            level="INFO" if status == "COMPLETED" else "ERROR",
            details={
                "event_type": "execution_completed" if status == "COMPLETED" else "execution_failed",
                "status": status,
                "error": getattr(execution, "error", None),
                "has_results": getattr(execution, "results", None) is not None,
                "retry_attempts": retry_attempts,
                "eval_summary": eval_summary,
            },
        )

    # ------------------------------------------------------------------
    # Asset Methods
    # ------------------------------------------------------------------

    def hydrate_indexed_assets(self, assets: Dict[str, Any]) -> Dict[str, Any]:
        return self.asset_manager.hydrate_indexed_assets(assets)

    def collect_materialized_files(self, media_assets: list[Any]) -> Dict[str, Any]:
        return self.asset_manager.collect_materialized_files(media_assets)

    def persist_execution_from_plan(
        self,
        execution: Any,
        assignments: List[Dict[str, Any]],
        *,
        overwrite_existing: bool = False,
        manifest_extractors: Optional[Dict[str, Any]] = None,
    ) -> tuple[Dict[str, str], Optional[Dict[str, Any]], List[Dict[str, str]]]:
        return self.asset_manager.persist_execution_from_plan(
            execution,
            assignments,
            overwrite_existing=overwrite_existing,
            manifest_extractors=manifest_extractors,
        )
