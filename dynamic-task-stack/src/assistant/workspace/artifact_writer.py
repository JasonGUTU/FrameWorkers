"""Artifact writer — execution-aware persistence of agent outputs.

Responsibilities:
  * Take an execution's results dict + a deterministic "persist plan"
    (list of {kind, source_key, relative_path}) and write each output to
    the workspace under ``Runtime/{workspace_id}/artifacts/...``.
  * Hydrate ``json_uri`` indexed assets back into full payloads.
  * Collect materialized media (binary asset list) into workspace files.
  * After persistence, register every persisted file in the artifact
    registry with its natural-language caption.
  * Emit one ``artifact.*`` log entry per logical persistence operation.

Naming:
  The word "asset" is reserved for agent-internal types (``MediaAsset``,
  ``asset_dict``). Anything written into the workspace and registered
  with a caption is an "artifact". This module is the single semantic
  layer that turns agent outputs into workspace artifacts — hence
  ``ArtifactWriter``.

What it does NOT do:
  * Raw file I/O — delegated to ``FileManager`` via callback.
  * Low-level log writing — delegated to ``LogManager`` via callback.
  * Caption authoring — captions come from the agent's
    ``per_artifact_captions`` dict and ``artifact_caption`` field.
  * Artifact selection / resolution — that is ``InputResolver``'s job
    on the read side, not the write side.

Used by:
  * ``Workspace`` (the facade) wires this writer with callbacks at init.
  * ``service.AssistantService`` calls it indirectly via Workspace methods.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Callable, Dict, Optional, List

logger = logging.getLogger(__name__)

from .models import StoredFile


class ArtifactWriter:
    """Persist agent outputs into the workspace as registered artifacts.

    Dedup model: in overwrite mode, before writing anything new,
    ArtifactWriter asks the artifact registry for every ref this producer
    has on this task, unlinks each physical file, and prunes the
    registry rows. The new run then writes its outputs normally. This is
    a coarse "wipe + redo" by ``(task, agent)`` — no per-slot logic. The
    registry is the only source of truth for "what's already here".
    """

    def __init__(
        self,
        store_file_at_relative_path: Callable[..., StoredFile],
        add_log: Callable[..., None],
        read_binary_from_uri: Callable[[str], Optional[bytes]],
        *,
        on_change: Optional[Callable[[], None]] = None,
        register_artifacts: Optional[Callable[..., None]] = None,
        find_artifact_refs_for_producer: Optional[Callable[..., List[Any]]] = None,
        delete_file_at_path: Optional[Callable[[str], bool]] = None,
        prune_global_memory_by_paths: Optional[Callable[[List[str]], int]] = None,
    ):
        self._store_file_at_relative_path = store_file_at_relative_path
        self._add_log = add_log
        self._read_binary_from_uri = read_binary_from_uri
        self._on_change = on_change
        # register_artifacts(execution, artifact_refs) — called after persistence
        self._register_artifacts = register_artifacts
        # find_artifact_refs_for_producer(task_id, agent_id) → list[ArtifactRef]
        # of every prior file this producer wrote on this task.
        self._find_artifact_refs_for_producer = find_artifact_refs_for_producer
        # delete_file_at_path(absolute_path) → bool. Used to unlink old files.
        self._delete_file_at_path = delete_file_at_path
        # prune_global_memory_by_paths(list[str]) → int removed.
        self._prune_global_memory_by_paths = prune_global_memory_by_paths

    def _touch(self) -> None:
        if self._on_change is not None:
            self._on_change()

    @staticmethod
    def is_asset_index_entry(value: Any) -> bool:
        return isinstance(value, dict) and isinstance(value.get("json_uri"), str)

    def _load_asset_json_from_uri(self, json_uri: str) -> Dict[str, Any]:
        if not json_uri:
            return {}
        try:
            payload = self._read_binary_from_uri(json_uri)
            if payload is None:
                return {}
            data = json.loads(payload.decode("utf-8"))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def hydrate_indexed_assets(self, assets: Dict[str, Any]) -> Dict[str, Any]:
        hydrated: Dict[str, Any] = {}
        for key, value in assets.items():
            if self.is_asset_index_entry(value):
                hydrated[key] = self._load_asset_json_from_uri(value.get("json_uri", ""))
            else:
                hydrated[key] = value
        return hydrated

    def collect_materialized_files(self, media_assets: list[Any]) -> Dict[str, Any]:
        """Collect binary media files from asset uris into workspace-ready payloads."""
        files: Dict[str, Any] = {}
        for asset in media_assets:
            uri = getattr(asset, "uri_holder", {}).get("uri", "")
            if not uri:
                continue
            data = self._read_binary_from_uri(uri)
            if data is None:
                continue
            sys_id = getattr(asset, "sys_id", "")
            extension = getattr(asset, "extension", "bin")
            files[sys_id] = {
                "file_content": data,
                "filename": f"{sys_id}.{extension}",
                "description": f"Media asset {sys_id}",
            }
        return files

    @staticmethod
    def _build_json_snapshot_payload(results: Dict[str, Any]) -> Dict[str, Any]:
        payload: Dict[str, Any] = {}
        for key, value in results.items():
            if key.startswith("_"):
                continue
            if isinstance(value, dict) and "file_content" in value:
                continue
            payload[key] = value
        return payload

    @staticmethod
    def _short_execution_label(execution_id: str) -> str:
        raw = str(execution_id or "").strip()
        if not raw:
            return "exec"
        parts = raw.split("_")
        if len(parts) >= 2 and parts[0] == "exec" and parts[1]:
            return f"exec_{parts[1]}"
        return raw

    @staticmethod
    def snapshot_filename(role: str, execution_id: str) -> str:
        safe_role = "".join(
            ch.lower() if ch.isalnum() or ch in {"_", "-"} else "_"
            for ch in str(role or "snapshot")
        ).strip("_") or "snapshot"
        return f"{safe_role}_{ArtifactWriter._short_execution_label(execution_id)}.json"

    @staticmethod
    def _rewrite_asset_uris_with_persisted_paths(node: Any, persisted_media_paths: Dict[str, str]) -> None:
        if isinstance(node, dict):
            asset_id = node.get("asset_id")
            if isinstance(asset_id, str) and asset_id in persisted_media_paths:
                node["uri"] = persisted_media_paths[asset_id]
            for value in node.values():
                ArtifactWriter._rewrite_asset_uris_with_persisted_paths(value, persisted_media_paths)
            return

        if isinstance(node, list):
            for item in node:
                ArtifactWriter._rewrite_asset_uris_with_persisted_paths(item, persisted_media_paths)

    def _purge_all_for_producer(self, execution: Any) -> None:
        """Wipe every prior file + registry row for this ``(task, agent)``.

        Called once at the top of ``persist_execution_from_plan`` when
        ``overwrite_existing`` is true. Coarse on purpose: this is the only
        way to also catch "orphan" files from previous runs whose slots
        the new run no longer produces. The new run then writes its
        outputs normally; ``Path.write_bytes`` would naturally overwrite
        any survivors, but with this wipe-first model there are none.
        """
        if (
            self._find_artifact_refs_for_producer is None
            or self._delete_file_at_path is None
            or self._prune_global_memory_by_paths is None
        ):
            return
        try:
            matches = self._find_artifact_refs_for_producer(
                task_id=execution.task_id,
                agent_id=execution.agent_id,
            )
        except Exception as exc:
            logger.warning("ArtifactWriter: find_artifact_refs_for_producer failed: %s", exc)
            return
        if not matches:
            return

        deleted_paths: List[str] = []
        for ref in matches:
            path = str(getattr(ref, "path", "") or "").strip()
            if not path:
                continue
            try:
                if self._delete_file_at_path(path):
                    deleted_paths.append(path)
            except Exception as exc:
                logger.warning("ArtifactWriter: failed to delete %s: %s", path, exc)

        if not deleted_paths:
            return

        try:
            self._prune_global_memory_by_paths(deleted_paths)
        except Exception as exc:
            logger.warning(
                "ArtifactWriter: prune_global_memory_by_paths failed: %s", exc,
            )

        import os as _os
        self._add_log(
            event="artifact.purged_for_producer",
            resource_id=execution.id,
            agent_id=execution.agent_id,
            task_id=execution.task_id,
            execution_id=execution.id,
            details={
                "deleted_paths": deleted_paths,
                "deleted_filenames": [_os.path.basename(p) for p in deleted_paths],
            },
        )
        self._touch()

    @staticmethod
    def is_safe_artifacts_relative_path(rel_path: str) -> bool:
        rel = (rel_path or "").strip().replace("\\", "/")
        if not rel:
            return False
        if ".." in rel.split("/"):
            return False
        return rel.startswith("artifacts/")

    @staticmethod
    def _has_allowed_extension(rel_path: str) -> bool:
        allowed = {
            ".json", ".png", ".jpg", ".jpeg", ".webp", ".wav", ".mp3", ".mp4", ".mov", ".bin", ".txt"
        }
        path = (rel_path or "").strip().lower()
        for ext in allowed:
            if path.endswith(ext):
                return True
        return False

    def persist_execution_from_plan(
        self,
        execution: Any,
        assignments: List[Dict[str, Any]],
        *,
        overwrite_existing: bool = False,
        captions: Optional[Dict[str, Dict[str, str]]] = None,
    ) -> tuple[Dict[str, str], Optional[Dict[str, Any]]]:
        """Write execution outputs using an explicit path plan.

        Each assignment is a dict with:
          - ``kind``: ``binary`` | ``media`` | ``json_snapshot``
          - ``relative_path``: must start with ``artifacts/``
          - ``source_key``: for ``binary`` / ``media`` — the per-file sys_id
            in the agent's ``results`` dict (e.g. ``"img_char_001_global"``)

        ``json_snapshot`` assignments need only ``relative_path`` — the snapshot
        filename is derived from ``execution.agent_id``.

        Order of operations:
          1. Persist all binary + media assignments first (in plan order).
          2. Rewrite asset URIs in the results tree to point at workspace files.
          3. Persist deferred json_snapshot (needs rewritten URIs).
          4. Register every persisted file in the artifact registry.

        Returns:
            ``(persisted_media_paths, asset_index)``
        """
        if not execution.results or not isinstance(execution.results, dict):
            return {}, None

        results: Dict[str, Any] = execution.results
        persisted_media_paths: Dict[str, str] = {}
        asset_index: Optional[Dict[str, Any]] = None
        deferred_json_snapshots: List[Dict[str, Any]] = []

        # ── Pass 0: in overwrite mode, wipe every prior file from this
        # producer (task, agent) so the new run starts from a clean slate.
        # This catches orphans (slots the old run had but the new run
        # doesn't) that per-slot dedup would miss.
        if overwrite_existing:
            self._purge_all_for_producer(execution)

        # ── Pass 1: split assignments and persist binary/media in order ──
        for raw in assignments:
            if not isinstance(raw, dict):
                continue
            kind = str(raw.get("kind") or "").strip()
            if kind == "json_snapshot":
                deferred_json_snapshots.append(raw)
                continue
            if not self._validate_relative_path(raw):
                continue
            if kind == "binary":
                self._persist_binary(execution, raw, results, persisted_media_paths)
            elif kind == "media":
                self._persist_media(execution, raw, results, persisted_media_paths)

        # ── Pass 2: rewrite URIs so deferred kinds see real workspace paths ──
        if persisted_media_paths:
            self._rewrite_asset_uris_with_persisted_paths(results, persisted_media_paths)

        # ── Pass 3: deferred json_snapshot (needs rewritten URIs) ──
        for raw in deferred_json_snapshots:
            if not self._validate_relative_path(raw):
                continue
            new_index = self._persist_json_snapshot(execution, raw, results)
            if new_index is not None:
                asset_index = new_index

        # ── Pass 4: register every persisted file in the artifact registry ──
        self._register_persisted_artifacts(
            execution, persisted_media_paths, asset_index, captions,
        )

        return persisted_media_paths, asset_index

    # ------------------------------------------------------------------
    # Per-kind handlers
    # ------------------------------------------------------------------

    def _validate_relative_path(self, raw: Dict[str, Any]) -> bool:
        """Validate ``raw['relative_path']`` is safe + allowed extension."""
        rel = str(raw.get("relative_path") or "").strip().replace("\\", "/")
        if not self.is_safe_artifacts_relative_path(rel):
            logger.warning("persist plan: skip unsafe path %r", rel)
            return False
        if not self._has_allowed_extension(rel):
            logger.warning("persist plan: skip disallowed extension path %r", rel)
            return False
        return True

    def _persist_binary(
        self,
        execution: Any,
        raw: Dict[str, Any],
        results: Dict[str, Any],
        persisted_media_paths: Dict[str, str],
    ) -> None:
        """Write a non-media binary file (e.g. text, generic blob)."""
        sk = str(raw.get("source_key") or "").strip()
        if not sk:
            return
        val = results.get(sk)
        if not isinstance(val, dict) or "file_content" not in val:
            return
        rel = str(raw.get("relative_path") or "").strip().replace("\\", "/")
        fn = val.get("filename") or f"{sk}.bin"
        stored = self._store_file_at_relative_path(
            rel,
            file_content=val["file_content"],
            filename=fn,
        )
        # Track this file so the registration step picks it up. Without this
        # entry the file would never appear in global_memory — and the
        # next overwrite-mode run could not find it for dedup.
        persisted_media_paths[sk] = stored.path
        self._add_log(
            event="artifact.persisted",
            resource_id=stored.path,
            agent_id=execution.agent_id,
            task_id=execution.task_id,
            execution_id=execution.id,
            details={
                "kind": "binary",
                "source_key": sk,
                "filename": stored.filename,
            },
        )
        self._touch()

    def _persist_media(
        self,
        execution: Any,
        raw: Dict[str, Any],
        results: Dict[str, Any],
        persisted_media_paths: Dict[str, str],
    ) -> None:
        """Write a materialized media file (image / video / audio)."""
        sk = str(raw.get("source_key") or "").strip()
        if not sk:
            return
        media = results.get("_media_files")
        if not isinstance(media, dict):
            return
        val = media.get(sk)
        if not isinstance(val, dict) or "file_content" not in val:
            return
        rel = str(raw.get("relative_path") or "").strip().replace("\\", "/")
        fn = val.get("filename") or f"{sk}.bin"
        stored = self._store_file_at_relative_path(
            rel,
            file_content=val["file_content"],
            filename=fn,
        )
        persisted_media_paths[sk] = stored.path
        self._add_log(
            event="artifact.persisted",
            resource_id=stored.path,
            agent_id=execution.agent_id,
            task_id=execution.task_id,
            execution_id=execution.id,
            details={
                "kind": "media",
                "source_key": sk,
                "filename": stored.filename,
            },
        )
        self._touch()

    def _persist_json_snapshot(
        self,
        execution: Any,
        raw: Dict[str, Any],
        results: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Build and write the agent's top-level JSON snapshot.

        The snapshot filename is derived from ``execution.agent_id``
        (e.g. ``screenplayagent_exec_2.json``). The returned ``asset_index``
        carries the producer ``agent_id`` so downstream consumers (and
        ``hydrate_indexed_assets``) can identify it. Dedup is by
        ``(task, agent)`` at the registry level — no per-snapshot key.

        Returns the asset_index dict for this execution, or ``None`` if
        nothing was persisted.
        """
        agent_id = str(execution.agent_id or "json_snapshot").strip()
        payload = self._build_json_snapshot_payload(results)
        if not payload:
            return None
        try:
            json_bytes = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        except (TypeError, ValueError):
            return None
        rel = str(raw.get("relative_path") or "").strip().replace("\\", "/")
        filename = self.snapshot_filename(agent_id, execution.id)
        stored = self._store_file_at_relative_path(
            rel,
            file_content=json_bytes,
            filename=filename,
        )
        self._add_log(
            event="artifact.snapshot_persisted",
            resource_id=stored.path,
            agent_id=execution.agent_id,
            task_id=execution.task_id,
            execution_id=execution.id,
            details={
                "agent_id": agent_id,
                "filename": filename,
            },
        )
        self._touch()
        return {
            "agent_id": agent_id,
            "json_uri": stored.path,
            "execution_id": execution.id,
        }

    def _register_persisted_artifacts(
        self,
        execution: Any,
        persisted_media_paths: Dict[str, str],
        asset_index: Optional[Dict[str, Any]],
        captions: Optional[Dict[str, Dict[str, str]]] = None,
    ) -> None:
        """Build ArtifactRef list and register everything in the artifact registry."""
        if self._register_artifacts is None:
            return
        caps = captions or {}

        def _make_ref(path: str, sys_id: str, mime: str) -> Dict[str, Any]:
            cap = caps.get(sys_id) or {}
            return {
                "caption": str(cap.get("caption") or ""),
                "scope": str(cap.get("scope") or "global"),
                "path": path,
                "mime": mime,
            }

        all_artifact_refs: List[Dict[str, Any]] = []
        for key, path in persisted_media_paths.items():
            p = str(path or "").strip()
            if p:
                all_artifact_refs.append(_make_ref(p, key, _mime_from_path(p)))

        if asset_index and isinstance(asset_index, dict):
            json_uri = str(asset_index.get("json_uri") or "").strip()
            sys_id = str(asset_index.get("agent_id") or "json_snapshot").strip()
            if json_uri:
                all_artifact_refs.append(_make_ref(json_uri, sys_id, "application/json"))

        # External refs: caption entries with an explicit ``path`` key
        # register additional artifact refs for files the agent did NOT
        # persist itself (e.g. BriefEnricherAgent classifying images that
        # IntakeImageAgent already persisted — it adds role-specific
        # captions without duplicating the file bytes).
        for cap_key, cap_val in caps.items():
            if isinstance(cap_val, dict) and "path" in cap_val:
                ext_path = str(cap_val["path"]).strip()
                if ext_path:
                    all_artifact_refs.append({
                        "caption": str(cap_val.get("caption") or ""),
                        "scope": str(cap_val.get("scope") or "global"),
                        "path": ext_path,
                        "mime": str(cap_val.get("mime") or _mime_from_path(ext_path)),
                    })

        if not all_artifact_refs:
            return
        try:
            self._register_artifacts(
                execution=execution,
                artifact_refs=all_artifact_refs,
            )
        except Exception as exc:
            logger.warning("ArtifactWriter: global_memory registration failed: %s", exc)


def _mime_from_path(path: str) -> str:
    """Infer MIME type from file extension."""
    p = (path or "").lower()
    if p.endswith(".json"):
        return "application/json"
    if p.endswith(".png"):
        return "image/png"
    if p.endswith((".jpg", ".jpeg")):
        return "image/jpeg"
    if p.endswith(".webp"):
        return "image/webp"
    if p.endswith(".mp4"):
        return "video/mp4"
    if p.endswith(".mov"):
        return "video/quicktime"
    if p.endswith(".wav"):
        return "audio/wav"
    if p.endswith(".mp3"):
        return "audio/mpeg"
    return "application/octet-stream"
