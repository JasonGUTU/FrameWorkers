"""Asset manager — execution-aware persistence of agent outputs.

Responsibilities:
  * Take an execution's results dict + a deterministic "persist plan"
    (list of {kind, source_key, relative_path}) and write each output to
    the workspace under ``Runtime/{workspace_id}/artifacts/...``.
  * Hydrate ``json_uri`` indexed assets back into full payloads.
  * Collect materialized media (binary asset list) into workspace files.
  * After persistence, register every persisted file in the artifact
    registry with its natural-language caption.

What it does NOT do:
  * Raw file I/O — delegated to ``FileManager`` via callback.
  * Logging — delegated to ``LogManager`` via callback.
  * Caption authoring — captions come from the agent's
    ``per_artifact_captions`` dict and ``artifact_caption`` field.
  * Artifact selection / resolution — that is ``InputResolver``'s job
    on the read side, not the write side.

Used by:
  * ``Workspace`` (the facade) wires this manager with callbacks at init.
  * ``service.AssistantService`` calls it indirectly via Workspace methods.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Callable, Dict, Optional, List

logger = logging.getLogger(__name__)

from .models import FileMetadata


class AssetManager:
    """Manage asset persistence, indexing, and hydration inside a workspace."""

    def __init__(
        self,
        store_file_at_relative_path: Callable[..., FileMetadata],
        add_log: Callable[..., None],
        read_binary_from_uri: Callable[[str], Optional[bytes]],
        list_files: Callable[..., List[FileMetadata]],
        delete_file: Callable[[str], bool],
        *,
        on_change: Optional[Callable[[], None]] = None,
        register_artifacts: Optional[Callable[..., None]] = None,
        prune_artifact_registry: Optional[Callable[..., int]] = None,
    ):
        self._store_file_at_relative_path = store_file_at_relative_path
        self._add_log = add_log
        self._read_binary_from_uri = read_binary_from_uri
        self._list_files = list_files
        self._delete_file = delete_file
        self._on_change = on_change
        # Optional callback: register_artifacts(execution, artifacts_list, caption_dict)
        self._register_artifacts = register_artifacts
        # Optional callback: prune_artifact_registry(task_id=, agent_id=) -> int
        # Called once before overwrite mode persistence to drop stale registry
        # entries left over by a previous run of the same agent on this task.
        self._prune_artifact_registry = prune_artifact_registry

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
        return f"{safe_role}_{AssetManager._short_execution_label(execution_id)}.json"

    @staticmethod
    def _rewrite_asset_uris_with_persisted_paths(node: Any, persisted_media_paths: Dict[str, str]) -> None:
        if isinstance(node, dict):
            asset_id = node.get("asset_id")
            if isinstance(asset_id, str) and asset_id in persisted_media_paths:
                node["uri"] = persisted_media_paths[asset_id]
            for value in node.values():
                AssetManager._rewrite_asset_uris_with_persisted_paths(value, persisted_media_paths)
            return

        if isinstance(node, list):
            for item in node:
                AssetManager._rewrite_asset_uris_with_persisted_paths(item, persisted_media_paths)

    def _matches_asset_metadata(
        self,
        file_meta: FileMetadata,
        *,
        execution: Any,
        asset_key: str,
        asset_variant: str,
    ) -> bool:
        metadata = file_meta.metadata if isinstance(file_meta.metadata, dict) else {}
        if metadata.get("task_id") != execution.task_id:
            return False
        if metadata.get("producer_agent_id") != execution.agent_id:
            return False
        if metadata.get("asset_key") != asset_key:
            return False
        variant = metadata.get("asset_variant")
        if variant:
            return variant == asset_variant
        # Legacy records: binary assets have no explicit variant.
        return asset_variant == "binary"

    def _purge_existing_asset_files(
        self,
        *,
        execution: Any,
        asset_key: str,
        asset_variant: str,
    ) -> None:
        files = self._list_files()
        deleted_file_ids: List[str] = []
        deleted_filenames: List[str] = []
        for file_meta in files:
            if not self._matches_asset_metadata(
                file_meta,
                execution=execution,
                asset_key=asset_key,
                asset_variant=asset_variant,
            ):
                continue
            if self._delete_file(file_meta.id):
                deleted_file_ids.append(file_meta.id)
                deleted_filenames.append(file_meta.filename)

        if deleted_file_ids:
            self._add_log(
                operation_type="write",
                resource_type="asset",
                resource_id=execution.id,
                agent_id=execution.agent_id,
                task_id=execution.task_id,
                details={
                    "event_type": "asset_overwritten",
                    "asset_key": asset_key,
                    "asset_variant": asset_variant,
                    "deleted_file_ids": deleted_file_ids,
                    "deleted_filenames": deleted_filenames,
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
        manifest_extractors: Optional[Dict[str, Callable[[Dict[str, Any]], List[Dict[str, Any]]]]] = None,
    ) -> tuple[Dict[str, str], Optional[Dict[str, Any]], List[Dict[str, str]]]:
        """Write execution outputs using an explicit path plan.

        Each assignment is a dict with:
          - ``kind``: ``binary`` | ``media`` | ``json_snapshot`` | ``manifest``
          - ``relative_path``: must start with ``artifacts/``
          - ``source_key``: for ``binary`` / ``media``
          - ``asset_key``: for ``json_snapshot``
          - ``manifest_kind``: for ``manifest`` (key into ``manifest_extractors``)

        ``manifest_extractors`` is a generic registry of ``kind -> extractor_callable``
        provided by the caller (typically built from ``descriptor.output_manifests``).
        AssetManager calls each extractor on the rewritten ``results`` and writes the
        returned items as a JSON document — it has zero knowledge of which agent the
        manifest belongs to.

        Order of operations:
          1. Persist all binary + media assignments first (in plan order).
          2. Rewrite asset URIs in the results tree to point at workspace files.
          3. Persist deferred manifests (need rewritten URIs).
          4. Persist deferred json_snapshot (needs rewritten URIs).
          5. Register every persisted file in the artifact registry.

        Returns:
            ``(persisted_media_paths, asset_index, extra_artifact_locations)``
        """
        if not execution.results or not isinstance(execution.results, dict):
            return {}, None, []

        results: Dict[str, Any] = execution.results
        persisted_media_paths: Dict[str, str] = {}
        asset_index: Optional[Dict[str, Any]] = None
        extra_locs: List[Dict[str, str]] = []
        deferred_json_snapshots: List[Dict[str, Any]] = []
        deferred_manifests: List[Dict[str, Any]] = []

        # ── Pass 0: prune stale artifact_registry entries from a previous run ──
        # When an agent is re-running with overwrite_existing=True, the old
        # files have already been (or will be) deleted by _purge_existing_asset_files.
        # We must also remove the matching ArtifactRegistry entries so the
        # caption index doesn't keep dangling paths.
        if overwrite_existing and self._prune_artifact_registry is not None:
            try:
                removed = self._prune_artifact_registry(
                    task_id=execution.task_id,
                    agent_id=execution.agent_id,
                )
                if removed:
                    self._add_log(
                        operation_type="delete",
                        resource_type="artifact",
                        resource_id=execution.id,
                        agent_id=execution.agent_id,
                        task_id=execution.task_id,
                        details={
                            "event_type": "artifact_registry_pruned",
                            "removed_entries": removed,
                        },
                    )
            except Exception as exc:
                logger.warning(
                    "AssetManager: artifact_registry prune failed: %s", exc,
                )

        # ── Pass 1: split assignments and persist binary/media in order ──
        for raw in assignments:
            if not isinstance(raw, dict):
                continue
            kind = str(raw.get("kind") or "").strip()
            if kind == "json_snapshot":
                deferred_json_snapshots.append(raw)
                continue
            if kind == "manifest":
                deferred_manifests.append(raw)
                continue
            if not self._validate_relative_path(raw):
                continue
            if kind == "binary":
                self._persist_binary(execution, raw, results, overwrite_existing)
            elif kind == "media":
                self._persist_media(execution, raw, results, persisted_media_paths, overwrite_existing)

        # ── Pass 2: rewrite URIs so deferred kinds see real workspace paths ──
        if persisted_media_paths:
            self._rewrite_asset_uris_with_persisted_paths(results, persisted_media_paths)

        # ── Pass 3: deferred kinds (need rewritten URIs) ──
        for raw in deferred_manifests:
            if not self._validate_relative_path(raw):
                continue
            self._persist_manifest(
                execution, raw, results, extra_locs, overwrite_existing,
                extractors=manifest_extractors or {},
            )

        for raw in deferred_json_snapshots:
            if not self._validate_relative_path(raw):
                continue
            new_index = self._persist_json_snapshot(execution, raw, results, overwrite_existing)
            if new_index is not None:
                asset_index = new_index

        # ── Pass 4: register every persisted file in the artifact registry ──
        self._register_persisted_artifacts(
            execution, persisted_media_paths, asset_index, extra_locs,
        )

        return persisted_media_paths, asset_index, extra_locs

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
        overwrite_existing: bool,
    ) -> None:
        """Write a non-media binary file (e.g. text, generic blob)."""
        sk = str(raw.get("source_key") or "").strip()
        if not sk:
            return
        val = results.get(sk)
        if not isinstance(val, dict) or "file_content" not in val:
            return
        if overwrite_existing:
            self._purge_existing_asset_files(
                execution=execution, asset_key=sk, asset_variant="binary",
            )
        rel = str(raw.get("relative_path") or "").strip().replace("\\", "/")
        fn = val.get("filename") or f"{sk}.bin"
        file_meta = self._store_file_at_relative_path(
            rel,
            file_content=val["file_content"],
            filename=fn,
            description=val.get("description", f"File from execution {execution.id}"),
            created_by=execution.agent_id,
            tags=[execution.agent_id, execution.task_id],
            metadata={
                "execution_id": execution.id,
                "task_id": execution.task_id,
                "producer_agent_id": execution.agent_id,
                "asset_key": sk,
                "asset_variant": "binary",
            },
        )
        self._add_log(
            operation_type="write",
            resource_type="asset",
            resource_id=file_meta.id,
            agent_id=execution.agent_id,
            task_id=execution.task_id,
            details={
                "event_type": "asset_persisted",
                "asset_key": sk,
                "asset_status": "ready",
                "file_type": file_meta.file_type,
                "filename": file_meta.filename,
                "persist_plan": True,
            },
        )
        self._touch()

    def _persist_media(
        self,
        execution: Any,
        raw: Dict[str, Any],
        results: Dict[str, Any],
        persisted_media_paths: Dict[str, str],
        overwrite_existing: bool,
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
        if overwrite_existing:
            self._purge_existing_asset_files(
                execution=execution, asset_key=sk, asset_variant="binary",
            )
        rel = str(raw.get("relative_path") or "").strip().replace("\\", "/")
        fn = val.get("filename") or f"{sk}.bin"
        file_meta = self._store_file_at_relative_path(
            rel,
            file_content=val["file_content"],
            filename=fn,
            description=val.get("description", f"Media asset {sk}"),
            created_by=execution.agent_id,
            tags=[execution.agent_id, execution.task_id],
            metadata={
                "execution_id": execution.id,
                "task_id": execution.task_id,
                "producer_agent_id": execution.agent_id,
                "asset_key": sk,
                "asset_variant": "binary",
            },
        )
        persisted_media_paths[sk] = file_meta.file_path
        self._add_log(
            operation_type="write",
            resource_type="asset",
            resource_id=file_meta.id,
            agent_id=execution.agent_id,
            task_id=execution.task_id,
            details={
                "event_type": "asset_persisted",
                "asset_key": sk,
                "persist_plan": True,
            },
        )
        self._touch()

    def _persist_manifest(
        self,
        execution: Any,
        raw: Dict[str, Any],
        results: Dict[str, Any],
        extra_locs: List[Dict[str, str]],
        overwrite_existing: bool,
        *,
        extractors: Dict[str, Callable[[Dict[str, Any]], List[Dict[str, Any]]]],
    ) -> None:
        """Build and write a side-output manifest JSON file (after URI rewrites).

        Generic over manifest kinds: ``manifest_kind`` selects which extractor in
        ``extractors`` to call, and the resulting items are wrapped in a JSON
        document and written to ``relative_path``. AssetManager has no knowledge
        of which agent owns the manifest or what its schema looks like.
        """
        manifest_kind = str(raw.get("manifest_kind") or "").strip()
        extractor = extractors.get(manifest_kind) if manifest_kind else None
        if extractor is None:
            return
        try:
            items = extractor(results)
        except Exception as exc:
            logger.warning(
                "manifest extractor for %s raised: %s", manifest_kind, exc,
            )
            return
        if not items:
            return
        doc = {
            "schema_version": "1.0",
            "document_type": manifest_kind,
            "task_id": execution.task_id,
            "execution_id": execution.id,
            "items": items,
        }
        try:
            body = json.dumps(doc, ensure_ascii=False, indent=2).encode("utf-8")
        except (TypeError, ValueError):
            return
        if overwrite_existing:
            self._purge_existing_asset_files(
                execution=execution,
                asset_key=manifest_kind,
                asset_variant="manifest",
            )
        rel = str(raw.get("relative_path") or "").strip().replace("\\", "/")
        import os as _os
        filename = _os.path.basename(rel) or f"{manifest_kind}.json"
        file_meta = self._store_file_at_relative_path(
            rel,
            file_content=body,
            filename=filename,
            description=f"{manifest_kind} ({execution.task_id})",
            created_by=execution.agent_id,
            tags=[execution.task_id, execution.agent_id, manifest_kind],
            metadata={
                "task_id": execution.task_id,
                "execution_id": execution.id,
                "producer_agent_id": execution.agent_id,
                "asset_variant": "manifest",
                "document_type": manifest_kind,
            },
        )
        self._add_log(
            operation_type="write",
            resource_type="asset",
            resource_id=file_meta.id,
            agent_id=execution.agent_id,
            task_id=execution.task_id,
            details={
                "event_type": "manifest_persisted",
                "manifest_kind": manifest_kind,
                "persist_plan": True,
            },
        )
        self._touch()
        extra_locs.append({"path": file_meta.file_path})

    def _persist_json_snapshot(
        self,
        execution: Any,
        raw: Dict[str, Any],
        results: Dict[str, Any],
        overwrite_existing: bool,
    ) -> Optional[Dict[str, Any]]:
        """Build and write the agent's top-level JSON snapshot.

        ``raw['asset_key']`` is required (producer's OUTPUT_ASSET_KEY,
        e.g. ``"screenplay"``).  It controls:
          * the snapshot filename (``screenplay_exec_2.json``)
          * the file metadata's ``asset_key`` field (used for dedup /
            overwrite and for downstream queries)
          * the asset_index returned to the caller

        Returns the asset_index dict for this execution, or ``None`` if
        nothing was persisted.
        """
        asset_key = str(raw.get("asset_key") or execution.agent_id or "json_snapshot").strip()
        payload = self._build_json_snapshot_payload(results)
        if not payload:
            return None
        try:
            json_bytes = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        except (TypeError, ValueError):
            return None
        if overwrite_existing:
            self._purge_existing_asset_files(
                execution=execution, asset_key=asset_key, asset_variant="json_snapshot",
            )
        rel = str(raw.get("relative_path") or "").strip().replace("\\", "/")
        filename = self.snapshot_filename(asset_key, execution.id)
        file_meta = self._store_file_at_relative_path(
            rel,
            file_content=json_bytes,
            filename=filename,
            description=f"Structured JSON snapshot for {execution.agent_id} ({execution.id})",
            created_by=execution.agent_id,
            tags=[execution.agent_id, execution.task_id, "asset_json"],
            metadata={
                "execution_id": execution.id,
                "task_id": execution.task_id,
                "producer_agent_id": execution.agent_id,
                "asset_key": asset_key,
                "asset_variant": "json_snapshot",
            },
        )
        self._add_log(
            operation_type="write",
            resource_type="asset",
            resource_id=file_meta.id,
            agent_id=execution.agent_id,
            task_id=execution.task_id,
            details={
                "event_type": "asset_json_snapshot_persisted",
                "asset_key": asset_key,
                "persist_plan": True,
            },
        )
        self._touch()
        return {
            "asset_key": asset_key,
            "json_uri": file_meta.file_path,
            "file_id": file_meta.id,
            "execution_id": execution.id,
        }

    def _register_persisted_artifacts(
        self,
        execution: Any,
        persisted_media_paths: Dict[str, str],
        asset_index: Optional[Dict[str, Any]],
        extra_locs: List[Dict[str, str]],
    ) -> None:
        """Build ArtifactRef list and register everything in the artifact registry."""
        if self._register_artifacts is None:
            return
        results_dict = execution.results if isinstance(execution.results, dict) else {}
        per_ac: Dict[str, Any] = {}
        if isinstance(results_dict.get("_per_artifact_captions"), dict):
            per_ac = results_dict["_per_artifact_captions"]
        # Entry-level caption used as fallback for the JSON snapshot.
        entry_caption_raw = results_dict.get("artifact_caption") or {}

        def _make_ref(path: str, sys_id: str, mime: str) -> Dict[str, Any]:
            """Build a registry entry from the agent's per-artifact caption.

            Looks up ``per_artifact_captions[sys_id]``; for the JSON snapshot
            falls back to the top-level ``artifact_caption``.
            """
            cap = per_ac.get(sys_id) or {}
            if not isinstance(cap, dict):
                cap = {}
            if not cap and mime == "application/json" and isinstance(entry_caption_raw, dict):
                cap = entry_caption_raw
            return {
                "what": str(cap.get("what") or ""),
                "why": str(cap.get("why") or ""),
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
            asset_key = str(asset_index.get("asset_key") or "json_snapshot").strip()
            if json_uri:
                all_artifact_refs.append(_make_ref(json_uri, asset_key, "application/json"))

        for loc in extra_locs:
            p = str(loc.get("path") or "").strip()
            if p and not any(a["path"] == p for a in all_artifact_refs):
                import os as _os
                sys_id_guess = _os.path.splitext(_os.path.basename(p))[0]
                all_artifact_refs.append(_make_ref(p, sys_id_guess, _mime_from_path(p)))

        if not all_artifact_refs:
            return
        try:
            self._register_artifacts(
                execution=execution,
                artifact_refs=all_artifact_refs,
            )
        except Exception as exc:
            logger.warning("AssetManager: artifact_registry registration failed: %s", exc)


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
