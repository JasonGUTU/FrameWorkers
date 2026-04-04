"""Asset manager for execution outputs and indexed asset payloads."""

from __future__ import annotations

import json
import logging
from typing import Any, Callable, Dict, Optional, List

logger = logging.getLogger(__name__)

from ..keyframes_manifest import build_keyframes_manifest_items
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
    ):
        self._store_file_at_relative_path = store_file_at_relative_path
        self._add_log = add_log
        self._read_binary_from_uri = read_binary_from_uri
        self._list_files = list_files
        self._delete_file = delete_file
        self._on_change = on_change

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
    ) -> tuple[Dict[str, str], Optional[Dict[str, Any]], List[Dict[str, str]]]:
        """Write execution outputs using an explicit path plan (LLM and/or deterministic).

        Each assignment is a dict with:
          - ``kind``: ``binary`` | ``media`` | ``json_snapshot`` | ``keyframes_manifest``
          - ``relative_path``: must start with ``artifacts/``
          - ``source_key``: for ``binary`` / ``media``
          - ``role`` / ``asset_key``: for ``json_snapshot`` (defaults to descriptor asset_key)
          - ``keyframes_manifest``: path comes from the plan; the manifest body is
            rebuilt **after** media URIs are rewritten so ``path`` rows match workspace files.

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
        deferred_keyframes_manifests: List[Dict[str, Any]] = []

        for raw in assignments:
            if not isinstance(raw, dict):
                continue
            kind_early = str(raw.get("kind") or "").strip()
            if kind_early == "json_snapshot":
                deferred_json_snapshots.append(raw)
                continue
            if kind_early == "keyframes_manifest":
                deferred_keyframes_manifests.append(raw)
                continue

            rel = str(raw.get("relative_path") or "").strip().replace("\\", "/")
            if not self.is_safe_artifacts_relative_path(rel):
                logger.warning("persist plan: skip unsafe path %r", rel)
                continue
            if not self._has_allowed_extension(rel):
                logger.warning("persist plan: skip disallowed extension path %r", rel)
                continue
            kind = str(raw.get("kind") or "").strip()

            if kind == "binary":
                sk = str(raw.get("source_key") or "").strip()
                if not sk:
                    continue
                val = results.get(sk)
                if not isinstance(val, dict) or "file_content" not in val:
                    continue
                if overwrite_existing:
                    self._purge_existing_asset_files(
                        execution=execution,
                        asset_key=sk,
                        asset_variant="binary",
                    )
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

            elif kind == "media":
                sk = str(raw.get("source_key") or "").strip()
                if not sk:
                    continue
                media = results.get("_media_files")
                if not isinstance(media, dict):
                    continue
                val = media.get(sk)
                if not isinstance(val, dict) or "file_content" not in val:
                    continue
                if overwrite_existing:
                    self._purge_existing_asset_files(
                        execution=execution,
                        asset_key=sk,
                        asset_variant="binary",
                    )
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

        if persisted_media_paths:
            self._rewrite_asset_uris_with_persisted_paths(results, persisted_media_paths)

        for raw in deferred_keyframes_manifests:
            if not isinstance(raw, dict):
                continue
            rel = str(raw.get("relative_path") or "").strip().replace("\\", "/")
            if not self.is_safe_artifacts_relative_path(rel):
                logger.warning("persist plan: skip unsafe path %r", rel)
                continue
            if not self._has_allowed_extension(rel):
                logger.warning("persist plan: skip disallowed extension path %r", rel)
                continue
            items = build_keyframes_manifest_items(results)
            if not items:
                continue
            doc = {
                "schema_version": "1.0",
                "role": "keyframes_manifest",
                "task_id": execution.task_id,
                "execution_id": execution.id,
                "items": items,
            }
            try:
                body = json.dumps(doc, ensure_ascii=False, indent=2).encode("utf-8")
            except (TypeError, ValueError):
                continue
            if overwrite_existing:
                self._purge_existing_asset_files(
                    execution=execution,
                    asset_key="keyframes_manifest",
                    asset_variant="manifest",
                )
            file_meta = self._store_file_at_relative_path(
                rel,
                file_content=body,
                filename="keyframes_manifest.json",
                description=f"Keyframe manifest ({execution.task_id})",
                created_by=execution.agent_id,
                tags=[execution.task_id, execution.agent_id, "keyframes_manifest"],
                metadata={
                    "task_id": execution.task_id,
                    "execution_id": execution.id,
                    "producer_agent_id": execution.agent_id,
                    "asset_variant": "manifest",
                    "role": "keyframes_manifest",
                },
            )
            self._add_log(
                operation_type="write",
                resource_type="asset",
                resource_id=file_meta.id,
                agent_id=execution.agent_id,
                task_id=execution.task_id,
                details={"event_type": "keyframes_manifest_persisted", "persist_plan": True},
            )
            self._touch()
            extra_locs.append({"role": "keyframes_manifest", "path": file_meta.file_path})

        for raw in deferred_json_snapshots:
            if not isinstance(raw, dict):
                continue
            rel = str(raw.get("relative_path") or "").strip().replace("\\", "/")
            if not self.is_safe_artifacts_relative_path(rel):
                logger.warning("persist plan: skip unsafe path %r", rel)
                continue
            if not self._has_allowed_extension(rel):
                logger.warning("persist plan: skip disallowed extension path %r", rel)
                continue
            role = str(
                raw.get("role") or raw.get("asset_key") or execution.agent_id or "json_snapshot"
            ).strip()
            payload = self._build_json_snapshot_payload(results)
            if not payload:
                continue
            try:
                json_bytes = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
            except (TypeError, ValueError):
                continue
            if overwrite_existing:
                self._purge_existing_asset_files(
                    execution=execution,
                    asset_key=role,
                    asset_variant="json_snapshot",
                )
            filename = self.snapshot_filename(role, execution.id)
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
                    "asset_key": role,
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
                    "asset_key": role,
                    "persist_plan": True,
                },
            )
            self._touch()
            asset_index = {
                "asset_key": role,
                "json_uri": file_meta.file_path,
                "file_id": file_meta.id,
                "execution_id": execution.id,
            }

        return persisted_media_paths, asset_index, extra_locs
