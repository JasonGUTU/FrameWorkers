"""Asset manager for execution outputs and indexed asset payloads."""

from __future__ import annotations

import json
from typing import Any, Callable, Dict, Optional, List

from .models import FileMetadata


class AssetManager:
    """Manage asset persistence, indexing, and hydration inside a workspace."""

    def __init__(
        self,
        store_file: Callable[..., FileMetadata],
        add_log: Callable[..., None],
        read_binary_from_uri: Callable[[str], Optional[bytes]],
        list_files: Callable[..., List[FileMetadata]],
        delete_file: Callable[[str], bool],
        *,
        on_change: Optional[Callable[[], None]] = None,
    ):
        self._store_file = store_file
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

    def build_pipeline_asset_value(
        self,
        *,
        execution_results: Optional[Dict[str, Any]],
        descriptor_asset_key: str,
        execution_id: str,
    ) -> Dict[str, Any]:
        """Build execution result payload for the shared pipeline ``assets`` dict."""
        if not execution_results or not isinstance(execution_results, dict):
            return {}

        index = execution_results.get("_asset_index")
        if self.is_asset_index_entry(index):
            return {
                "asset_key": index.get("asset_key", descriptor_asset_key),
                "json_uri": index.get("json_uri", ""),
                "file_id": index.get("file_id", ""),
                "execution_id": index.get("execution_id", execution_id),
            }

        # Backward-compatible fallback for legacy executions/tests without index.
        return {
            key: value
            for key, value in execution_results.items()
            if not key.startswith("_")
        }

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

    def _store_file_asset(self, execution: Any, key: str, value: Dict[str, Any]) -> FileMetadata:
        file_metadata = {
            "execution_id": execution.id,
            "task_id": execution.task_id,
            "producer_agent_id": execution.agent_id,
            "asset_key": key,
            "asset_variant": "binary",
        }
        file_meta = self._store_file(
            file_content=value["file_content"],
            filename=value.get("filename", f"{key}.bin"),
            description=value.get("description", f"File from execution {execution.id}"),
            created_by=execution.agent_id,
            tags=[execution.agent_id, execution.task_id],
            metadata=file_metadata,
        )
        self._add_log(
            operation_type="write",
            resource_type="asset",
            resource_id=file_meta.id,
            agent_id=execution.agent_id,
            task_id=execution.task_id,
            details={
                "event_type": "asset_persisted",
                "asset_key": key,
                "asset_status": "ready",
                "file_type": file_meta.file_type,
                "filename": file_meta.filename,
            },
        )
        self._touch()
        return file_meta

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
        files = self._list_files(
            created_by=execution.agent_id,
            tags=[execution.task_id],
        )
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

    def persist_execution_assets(
        self,
        execution: Any,
        *,
        overwrite_existing: bool = False,
    ) -> Dict[str, str]:
        if not execution.results or not isinstance(execution.results, dict):
            return {}

        persisted_media_paths: Dict[str, str] = {}
        for key, value in execution.results.items():
            if isinstance(value, dict) and "file_content" in value:
                if overwrite_existing:
                    self._purge_existing_asset_files(
                        execution=execution,
                        asset_key=key,
                        asset_variant="binary",
                    )
                self._store_file_asset(execution, key, value)

        media_files = execution.results.get("_media_files")
        if isinstance(media_files, dict):
            for key, value in media_files.items():
                if overwrite_existing:
                    self._purge_existing_asset_files(
                        execution=execution,
                        asset_key=key,
                        asset_variant="binary",
                    )
                file_meta = self._store_file_asset(execution, key, value)
                persisted_media_paths[key] = file_meta.file_path

        if persisted_media_paths:
            self._rewrite_asset_uris_with_persisted_paths(
                execution.results,
                persisted_media_paths,
            )
        return persisted_media_paths

    def persist_execution_json_snapshot(
        self,
        execution: Any,
        *,
        asset_key: str,
        overwrite_existing: bool = False,
    ) -> Optional[Dict[str, Any]]:
        if not execution.results or not isinstance(execution.results, dict):
            return None

        payload = self._build_json_snapshot_payload(execution.results)
        if not payload:
            return None

        try:
            json_bytes = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        except Exception:
            return None

        if overwrite_existing:
            self._purge_existing_asset_files(
                execution=execution,
                asset_key=asset_key,
                asset_variant="json_snapshot",
            )

        agent_name = str(getattr(execution, "agent_id", "agent") or "agent").strip()
        safe_agent = "".join(
            ch.lower() if ch.isalnum() or ch in {"_", "-"} else "_"
            for ch in agent_name
        ).strip("_") or "agent"
        filename = f"{safe_agent}_{asset_key}_{execution.id}.json"
        file_meta = self._store_file(
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
                "filename": file_meta.filename,
            },
        )
        self._touch()
        return {
            "asset_key": asset_key,
            "json_uri": file_meta.file_path,
            "file_id": file_meta.id,
            "execution_id": execution.id,
        }
