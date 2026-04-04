# Assistant Service - Core business logic for agent orchestration

import asyncio
import hashlib
import json
import logging
import os
import shutil
import tempfile
from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path

from .models import AgentExecution, ExecutionStatus
from .keyframes_manifest import build_keyframes_manifest_items
from .workspace import Workspace
from .workspace.asset_manager import AssetManager
from agents import get_agent_registry
from agents.contracts import ArtifactRefV2, InputBundleV2
from agents.base_agent import MaterializeContext
from inference.clients import LLMClient as PipelineLLMClient

logger = logging.getLogger(__name__)


def _parse_positive_int_list(env_name: str, default: tuple[int, ...]) -> tuple[int, ...]:
    """Comma-separated positive ints, e.g. ``4096,8192,16384`` for chat_json retry caps."""
    raw = os.getenv(env_name, "").strip()
    if not raw:
        return default
    out: list[int] = []
    for part in raw.split(","):
        p = part.strip()
        if not p:
            continue
        try:
            n = int(p)
        except ValueError:
            continue
        if n > 0:
            out.append(n)
    return tuple(out) if out else default


def _env_int(name: str, default: int, *, lo: int, hi: int) -> int:
    try:
        n = int(os.getenv(name, str(default)).strip())
        return max(lo, min(n, hi))
    except ValueError:
        return default


def _global_memory_context_entries_limit() -> int:
    """Recent N memory rows for packaging LLMs (default 20). Full history stays on disk."""
    return _env_int("ASSISTANT_GLOBAL_MEMORY_CONTEXT_ENTRIES_MAX", 20, lo=1, hi=500)


class AssistantBadExecuteFieldsError(Exception):
    """``execute_fields`` violated a strict wire rule (e.g. ``text`` must be a string)."""


class AssistantGlobalMemorySyncError(Exception):
    """global_memory summary LLM failed or returned invalid JSON (strict mode; no silent fallback)."""


class AssistantService:
    """
    Service class for managing assistant operations
    
    There should be only one assistant instance that manages all sub-agents.
    All agents share a single workspace (file system).
    """
    
    def __init__(self, assistant_state_store):
        """
        Initialize assistant service
        
        Args:
            assistant_state_store: Runtime state store instance for assistant data
        """
        self.storage = assistant_state_store
        self.agent_registry = get_agent_registry()
        self.pipeline_llm_client = PipelineLLMClient()
        self.global_memory_summary_model = (
            os.getenv("ASSISTANT_MEMORY_MODEL", "").strip()
            or os.getenv("DIRECTOR_MEMORY_MODEL", "").strip()
            or os.getenv("INFERENCE_DEFAULT_MODEL", "google-ai-studio/gemini-2.5-flash")
        ).strip()
        self.input_package_model = (
            os.getenv("ASSISTANT_INPUT_PACKAGE_MODEL", "").strip()
            or self.global_memory_summary_model
        ).strip()
        self.output_persist_model = (
            os.getenv("ASSISTANT_OUTPUT_PERSIST_MODEL", "").strip()
            or self.global_memory_summary_model
        ).strip()
        # Get or create the global workspace
        self.workspace = self._get_global_workspace()

    def _get_global_workspace(self) -> Workspace:
        """
        Get or create the global workspace
        
        Returns:
            The global workspace instance
        """
        # Try to get existing workspace
        workspace = self.storage.get_global_workspace()
        if workspace is None:
            # Create global workspace if it doesn't exist
            workspace = self.storage.create_global_workspace()
        return workspace

    @staticmethod
    def _is_executable_pipeline_descriptor(descriptor: Any) -> bool:
        return bool(
            descriptor
            and hasattr(descriptor, "build_equipped_agent")
            and hasattr(descriptor, "build_input")
        )

    @staticmethod
    def _json_preview(value: Any, *, max_chars: int = 14_000) -> Any:
        """Shrink large dicts for LLM prompts (avoid token blow-up)."""
        try:
            raw = json.dumps(value, ensure_ascii=False)
        except (TypeError, ValueError):
            return str(value)[:max_chars]
        if len(raw) <= max_chars:
            return json.loads(raw) if raw.startswith("{") or raw.startswith("[") else raw
        return raw[:max_chars] + "\n…(truncated)"

    @staticmethod
    def _naming_policy_path() -> Path:
        return Path(__file__).resolve().parent / "persist_naming_policy.json"

    def _load_persist_naming_policy(self) -> Dict[str, Any]:
        path = self._naming_policy_path()
        if not path.exists():
            return {"version": "default-1", "allowed_extensions": []}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {"version": "default-1", "allowed_extensions": []}
        except Exception:
            return {"version": "default-1", "allowed_extensions": []}

    @staticmethod
    def _deterministic_artifact_bundle(
        execution: AgentExecution,
        persisted_media_paths: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        """Paths produced by workspace persistence (authoritative)."""
        out: List[Dict[str, Any]] = []
        results = execution.results if isinstance(execution.results, dict) else {}
        idx = results.get("_asset_index")
        if isinstance(idx, dict) and str(idx.get("json_uri") or "").strip():
            role = str(idx.get("asset_key") or "json_snapshot").strip() or "json_snapshot"
            out.append(
                {
                    "role": role,
                    "path": str(idx.get("json_uri") or ""),
                }
            )
        for key, path in (persisted_media_paths or {}).items():
            p = str(path or "").strip()
            if not p:
                continue
            out.append(
                {
                    "role": str(key),
                    "path": p,
                }
            )
        return out

    @staticmethod
    def _merge_artifact_locations(
        deterministic: List[Dict[str, Any]],
        llm_locs: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        seen_paths = {str(x.get("path") or "") for x in deterministic if x.get("path")}
        merged = list(deterministic)
        for row in llm_locs:
            if not isinstance(row, dict):
                continue
            p = str(row.get("path") or row.get("uri") or "").strip()
            if not p or p in seen_paths:
                continue
            seen_paths.add(p)
            merged.append(
                {
                    "role": str(row.get("role") or "note").strip() or "note",
                    "path": p,
                    **(
                        {"description": str(row["description"]).strip()}
                        if isinstance(row.get("description"), str) and row.get("description")
                        else {}
                    ),
                }
            )
        return merged

    @staticmethod
    def _run_async(coro):
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    @staticmethod
    def _mapping_to_input_bundle_v2(task_id: str, data: Dict[str, Any]) -> InputBundleV2:
        artifacts: List[ArtifactRefV2] = []
        context: Dict[str, Any] = {}
        hints: Dict[str, Any] = {}
        for key, value in data.items():
            if key in {"source_text", "image", "video", "audio", "input_package"}:
                hints[key] = value
                continue
            if key in ("_resolved_inputs", "resolved_inputs") and isinstance(value, dict):
                context["resolved_inputs"] = value
                continue
            if isinstance(value, dict) and "json_uri" in value and "asset_key" in value:
                # keep indexed entry; hydration happens before conversion in call sites.
                hints[key] = value
                continue
            artifacts.append(
                ArtifactRefV2(
                    artifact_id=f"{task_id}:{key}",
                    semantic_type=key,
                    schema_ref=f"{key}.v1",
                    payload=value,
                    tags=[task_id],
                )
            )
        return InputBundleV2(task_id=task_id, artifacts=artifacts, context=context, hints=hints)

    @staticmethod
    def _map_pipeline_inputs(
        inputs: Dict[str, Any],
    ) -> tuple[str, InputBundleV2]:
        task_id = inputs.get("task_id") or ""

        raw = inputs.get("input_bundle_v2")
        if isinstance(raw, InputBundleV2):
            hydrated = dict(raw)
        elif isinstance(raw, dict):
            hydrated = dict(raw)
        else:
            hydrated = {}
        ef = inputs.get("execute_fields")
        text = ef.get("text") if isinstance(ef, dict) else None
        if text and "source_text" not in hydrated:
            hydrated["source_text"] = AssistantService._text_for_source_text(text)
        return task_id, AssistantService._mapping_to_input_bundle_v2(task_id, hydrated)

    @staticmethod
    def _merge_execution_inputs(
        packaged_data: Dict[str, Any],
        overlay: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Overlay extra keys onto packaged execution payload (e.g. ``execute_fields`` wrapper)."""
        merged = dict(packaged_data)
        if not overlay:
            return merged

        for key, value in overlay.items():
            merged[key] = value
        return merged

    @staticmethod
    def _text_for_source_text(text: Any) -> str:
        """Map ``execute_fields[\"text\"]`` → ``input_bundle_v2[\"source_text\"]`` (must be a string)."""
        if text is None or text == "":
            return ""
        if not isinstance(text, str):
            raise AssistantBadExecuteFieldsError("execute_fields.text must be a string")
        return text.strip()

    @staticmethod
    def _normalize_media_uri(raw: str, *, kind: str) -> str:
        """Light normalization for optional ``image`` / ``video`` strings (e.g. data URIs)."""
        if kind == "image" and raw and not raw.startswith("data:"):
            return f"data:image/png;base64,{raw}"
        return raw

    def _inject_execute_media_into_bundle(
        self,
        bundle: Dict[str, Any],
        execute_fields: Dict[str, Any],
    ) -> None:
        """Copy optional ``image`` / ``video`` (and ``audio``) into input bundle mapping."""
        for key in ("image", "video", "audio"):
            val = execute_fields.get(key)
            if val is None or val == "":
                continue
            if isinstance(val, str):
                bundle[key] = self._normalize_media_uri(val, kind=key if key == "image" else "video")
            else:
                bundle[key] = val

    @staticmethod
    def _build_descriptor_input(
        descriptor: Any,
        task_id: str,
        readonly_bundle: Any,
    ) -> Any:
        return descriptor.build_input(task_id, readonly_bundle)

    def _execute_pipeline_descriptor(self, descriptor: Any, inputs: Dict[str, Any]) -> Dict[str, Any]:
        task_id, ib_mapped = self._map_pipeline_inputs(inputs)
        hydrated = self.workspace.hydrate_indexed_assets(dict(ib_mapped))
        ib_after = self._mapping_to_input_bundle_v2(task_id, hydrated)
        # Preserve Assistant-filled context (e.g. resolved_inputs); hydrate only expands json_uri indexes into payloads.
        input_bundle_v2 = InputBundleV2(
            task_id=task_id,
            artifacts=ib_after.artifacts,
            context=dict(ib_mapped.context),
            hints=ib_after.hints,
        )

        agent = descriptor.build_equipped_agent(self.pipeline_llm_client)
        typed_input = self._build_descriptor_input(
            descriptor,
            task_id,
            input_bundle_v2,
        )

        materialize_ctx = None
        temp_dir: Optional[str] = None
        if getattr(agent, "materializer", None) is not None:
            temp_dir = tempfile.mkdtemp(prefix="fw_media_")

            def _persist(media_asset):
                path = os.path.join(temp_dir, f"{media_asset.sys_id}.{media_asset.extension}")
                with open(path, "wb") as fh:
                    fh.write(media_asset.data)
                return path

            materialize_ctx = MaterializeContext(
                task_id=task_id,
                input_bundle_v2=input_bundle_v2,
                persist_binary=_persist,
            )

        try:
            result = self._run_async(
                agent.run(
                    typed_input,
                    input_bundle_v2=input_bundle_v2,
                    materialize_ctx=materialize_ctx,
                )
            )
            output: Dict[str, Any] = {}
            asset_dict = getattr(result, "asset_dict", None)
            raw_output = getattr(result, "output", None)
            media_assets = getattr(result, "media_assets", [])
            attempts = getattr(result, "attempts", None)
            eval_result = getattr(result, "eval_result", None)

            if asset_dict is not None:
                output = asset_dict
            elif raw_output is not None:
                output = raw_output.model_dump() if hasattr(raw_output, "model_dump") else dict(raw_output)

            if media_assets:
                output["_media_files"] = self.workspace.collect_materialized_files(media_assets)
            materializer = getattr(agent, "materializer", None)
            if materializer is not None and hasattr(materializer, "naming_spec_v2"):
                try:
                    spec = materializer.naming_spec_v2()
                    if isinstance(spec, dict):
                        output["_naming_specs"] = [spec]
                except Exception:
                    logger.debug("materializer naming spec unavailable", exc_info=True)
            debug_payload: Dict[str, Any] = {}
            if isinstance(attempts, int):
                debug_payload["attempts"] = attempts
                if isinstance(eval_result, dict):
                    debug_payload["overall_pass"] = bool(
                        eval_result.get("overall_pass", True)
                    )
                    summary = eval_result.get("summary")
                    if isinstance(summary, str) and summary:
                        debug_payload["eval_summary"] = summary
            if debug_payload:
                output["_execution_debug"] = debug_payload
            return output
        finally:
            if temp_dir:
                shutil.rmtree(temp_dir, ignore_errors=True)

    def prepare_environment(self) -> Workspace:
        """
        Prepare workspace environment for agent execution
        
        Uses the global workspace shared by all agents.
        
        Returns:
            Global workspace instance
        """
        return self.workspace

    def package_data(
        self,
        agent_id: str,
        task_id: str,
        *,
        text_seed: Any,
    ) -> Dict[str, Any]:
        """
        Package relevant resources for agent execution.

        Seed bundle only carries request-time hints (e.g. ``source_text``).
        Artifact payload selection is delegated to the role-selection LLM pass.

        Args:
            agent_id: ID of the agent to execute
            task_id: ID of the task
            text_seed: ``execute_fields[\"text\"]`` (optional; str or structured dict)

        Returns:
            ``task_id`` plus ``input_bundle_v2`` seed mapping for downstream execution input assembly

        Raises:
            ValueError: If agent not found in registry
        """
        descriptor = self.agent_registry.get_descriptor(agent_id)
        if not self._is_executable_pipeline_descriptor(descriptor):
            raise ValueError(f"Agent {agent_id} not found in registry")

        bundle: Dict[str, Any] = {}
        if text_seed:
            bundle["source_text"] = self._text_for_source_text(text_seed)

        return {
            "task_id": task_id,
            "input_bundle_v2": bundle,
        }

    @staticmethod
    def _available_roles_from_memory(memory_entries: List[Dict[str, Any]]) -> List[str]:
        roles: List[str] = []
        seen: set[str] = set()
        for entry in memory_entries:
            if not isinstance(entry, dict):
                continue
            for loc in entry.get("artifact_locations") or []:
                if not isinstance(loc, dict):
                    continue
                role = str(loc.get("role") or "").strip()
                if not role or role in seen:
                    continue
                seen.add(role)
                roles.append(role)
        return roles

    def _resolve_inputs_for_agent_with_llm(
        self,
        agent_id: str,
        task_id: str,
        workspace: Workspace,
        packaged_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """LLM pass: pick semantic roles from global_memory artifact_locations + file tree."""
        try:
            descriptor = self.agent_registry.get_descriptor(agent_id)
        except Exception:
            raise AssistantBadExecuteFieldsError(f"unknown agent_id: {agent_id}")
        desc_text = getattr(descriptor, "catalog_entry", "") or ""
        gm = packaged_data.get("global_memory") or []
        if not isinstance(gm, list):
            gm = []
        available_roles = self._available_roles_from_memory(gm)
        if not available_roles:
            # Cold start: no prior artifacts for this task_id. Most agents can run from source_text
            # alone, so skip the role-selection LLM pass entirely.
            return {
                "required_roles": [],
                "selected_roles": [],
                "append_to_source_text": "",
                "rationale": "no available_roles in global_memory (cold start)",
            }
        blob = {
            "target_agent_id": agent_id,
            "descriptor_hint": desc_text,
            "available_roles": available_roles,
            "global_memory": gm,
            "workspace_file_tree": workspace.get_workspace_root_file_tree_text(),
        }
        system_prompt = (
            "You select which semantic artifacts this sub-agent needs next. "
            "Use only role values from available_roles. "
            "Use global_memory entries: read each entry's content (planning summary) to understand "
            "what was produced and why, and use artifact_locations (role+path) to find the file paths. "
            "Use workspace_file_tree as on-disk ground truth (includes artifacts/). "
            "You MUST infer required_roles from descriptor_hint and include every required_roles value in selected_roles. "
            "Return strict JSON only."
        )
        user_prompt = (
            "Context (JSON):\n"
            f"{json.dumps(blob, ensure_ascii=False)}\n\n"
            "Return JSON:\n"
            "{\n"
            '  "required_roles": ["subset of available_roles"],\n'
            '  "selected_roles": ["subset of available_roles"],\n'
            '  "append_to_source_text": "optional short prefix merged before existing source_text",\n'
            '  "rationale": "one short sentence"\n'
            "}\n"
        )
        parsed: Dict[str, Any] | None = None
        last_exc: Exception | None = None
        for max_tok in (16384, 32768, 65536):
            try:
                parsed = self._run_async(
                    self.pipeline_llm_client.chat_json(
                        system_prompt=system_prompt,
                        user_prompt=user_prompt,
                        max_tokens=max_tok,
                        reasoning_effort="low",
                        model=self.input_package_model,
                    )
                )
                break
            except Exception as exc:
                last_exc = exc
                continue
        if parsed is None:
            raise AssistantBadExecuteFieldsError(
                f"input package LLM failed: {last_exc}"
            ) from last_exc
        if not isinstance(parsed, dict):
            raise AssistantBadExecuteFieldsError("input package LLM returned non-object JSON")
        rr = parsed.get("required_roles")
        if not isinstance(rr, list):
            raise AssistantBadExecuteFieldsError("input package LLM must return required_roles list")
        picked = parsed.get("selected_roles")
        if not isinstance(picked, list):
            raise AssistantBadExecuteFieldsError("input package LLM must return selected_roles list")
        picked_set = {str(x).strip() for x in picked if str(x).strip()}
        required_set = {str(x).strip() for x in rr if str(x).strip()}
        missing = [r for r in sorted(required_set) if r and r not in picked_set]
        if missing:
            raise AssistantBadExecuteFieldsError(
                f"input package LLM missing required roles in selected_roles: {', '.join(missing)}"
            )
        return parsed

    @staticmethod
    def _read_json_file_uri(workspace: Workspace, path: str) -> Optional[Dict[str, Any]]:
        raw = workspace.file_manager.read_binary_from_uri(path)
        if raw is None:
            return None
        try:
            data = json.loads(raw.decode("utf-8"))
            return data if isinstance(data, dict) else None
        except Exception:
            return None

    @staticmethod
    def _find_latest_artifact_path_for_role(
        memory_entries: List[Dict[str, Any]],
        role: str,
    ) -> Optional[str]:
        want = str(role or "").strip()
        if not want:
            return None
        for entry in memory_entries:
            if not isinstance(entry, dict):
                continue
            for loc in entry.get("artifact_locations") or []:
                if not isinstance(loc, dict):
                    continue
                if str(loc.get("role") or "").strip() != want:
                    continue
                p = str(loc.get("path") or "").strip()
                if p:
                    return p
        return None

    def _apply_input_package_merge(
        self,
        packaged_data: Dict[str, Any],
        pkg: Dict[str, Any],
        workspace: Workspace,
        *,
        required_roles: Optional[List[str]] = None,
    ) -> None:
        """Apply LLM-selected artifacts: load JSON from memory paths into input bundle mapping."""
        bundle = packaged_data.get("input_bundle_v2")
        if not isinstance(bundle, dict) or not pkg:
            return
        roles = pkg.get("selected_roles")
        if not isinstance(roles, list):
            raise AssistantBadExecuteFieldsError("input package selected_roles must be a list")
        if not roles:
            # Nothing to merge for cold-start or agents that don't need prior artifacts.
            return

        mem = packaged_data.get("global_memory") or []
        if not isinstance(mem, list):
            mem = []
        for role in roles:
            r = str(role).strip()
            if not r or r == "source_text":
                continue
            path = self._find_latest_artifact_path_for_role(mem, r)
            if not path:
                continue
            if path.lower().endswith(".json"):
                loaded = self._read_json_file_uri(workspace, path)
                if loaded is not None:
                    bundle[r] = loaded
        # Create agent-scoped resolved inputs view.
        resolved_inputs: Dict[str, Any] = {}
        for r in roles:
            if isinstance(r, str) and r.strip() and r.strip() in bundle:
                resolved_inputs[r.strip()] = bundle.get(r.strip())
        if resolved_inputs:
            bundle["_resolved_inputs"] = resolved_inputs
        must = [x for x in (required_roles or []) if isinstance(x, str) and x.strip()]
        if must:
            missing_loaded = [r for r in must if r not in bundle or not isinstance(bundle.get(r), dict)]
            if missing_loaded:
                raise AssistantBadExecuteFieldsError(
                    f"required roles not loaded from artifact_locations: {', '.join(missing_loaded)}"
                )
        extra = pkg.get("append_to_source_text")
        if isinstance(extra, str) and extra.strip():
            st = bundle.get("source_text", "")
            if isinstance(st, str):
                bundle["source_text"] = (extra.strip() + "\n\n" + st).strip()
        bundle["input_package"] = {
            "rationale": pkg.get("rationale"),
            "selected_roles": pkg.get("selected_roles"),
            "append_to_source_text": pkg.get("append_to_source_text"),
        }

    def _has_existing_assets(self, *, task_id: str, agent_id: str) -> bool:
        files = self.workspace.list_files()
        if not files:
            return False
        for file_item in files:
            metadata = file_item.metadata if hasattr(file_item, "metadata") else {}
            if not isinstance(metadata, dict):
                continue
            if metadata.get("task_id") != task_id:
                continue
            if metadata.get("producer_agent_id") != agent_id:
                continue
            if metadata.get("asset_key"):
                return True
        return False
    
    def execute_agent(
        self,
        agent_id: str,
        task_id: str,
        inputs: Dict[str, Any],
    ) -> AgentExecution:
        """
        Execute an agent and retrieve results
        
        Args:
            agent_id: ID of the agent to execute
            task_id: ID of the task
            inputs: Input data for the agent
            
        Returns:
            AgentExecution instance with results
            
        Raises:
            ValueError: If agent or task not found
        """
        # Ensure global assistant singleton exists.
        self.storage.get_global_assistant()

        descriptor = self.agent_registry.get_descriptor(agent_id)
        if not self._is_executable_pipeline_descriptor(descriptor):
            raise ValueError(f"Agent {agent_id} not found in registry")
        
        # Create execution record
        execution = self.storage.create_execution(
            agent_id=agent_id,
            task_id=task_id,
            inputs=inputs
        )
        
        try:
            # Update execution status
            execution.status = ExecutionStatus.IN_PROGRESS
            execution.started_at = datetime.now()
            self.storage.update_execution(execution)
            self.workspace.log_execution_started(execution)
            
            # Execute selected descriptor-based pipeline agent.
            results = self._execute_pipeline_descriptor(descriptor, inputs)
            
            # Update execution with results
            execution.status = ExecutionStatus.COMPLETED
            execution.results = results
            execution.completed_at = datetime.now()
            self.storage.update_execution(execution)
        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.error = str(e)
            execution.completed_at = datetime.now()
            self.storage.update_execution(execution)
            self._sync_global_memory_after_execution(
                self.workspace,
                execution,
                persisted_media_paths=None,
                extra_artifact_locations=None,
            )
            raise e
        
        return execution

    @staticmethod
    def _global_memory_execution_snapshot(execution: AgentExecution) -> Dict[str, Any]:
        snap: Dict[str, Any] = {
            "status": execution.status.value,
            "execution_id": execution.id,
        }
        if isinstance(execution.results, dict):
            meta = execution.results.get("_persist_plan_meta")
            if isinstance(meta, dict):
                snap["persist_plan_meta"] = dict(meta)
        if execution.error and str(execution.error).strip():
            snap["error"] = execution.error
        return snap

    def _extract_global_memory_summary_with_llm(
        self,
        execution: AgentExecution,
        deterministic_artifacts: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        payload = {
            "task_id": execution.task_id,
            "execution_id": execution.id,
            "status": execution.status.value,
            "agent_id": execution.agent_id,
            "error": execution.error,
            "results": self._json_preview(execution.results),
            "deterministic_artifact_paths": deterministic_artifacts,
            "naming_specs": (
                execution.results.get("_naming_specs", [])
                if isinstance(execution.results, dict)
                else []
            ),
        }
        system_prompt = (
            "You convert one agent execution record into a global_memory planning row. "
            "Deterministic artifact paths are merged server-side — do NOT echo long path strings "
            "unless you add an optional extra location; prefer \"artifact_locations\": []. "
            "Return strict JSON only."
        )
        user_prompt = (
            "Execution payload (JSON):\n"
            f"{json.dumps(payload, ensure_ascii=False)}\n\n"
            "Return JSON with shape:\n"
            "{\n"
            '  "content": "one concise planning summary sentence",\n'
            '  "artifact_locations": [],\n'
            '  "artifact_briefs": [{"path": "short basename or relative", "brief": "what this file is"}]\n'
            "}\n"
            "Use artifact_locations [] unless you must add a path not already in deterministic_artifact_paths; "
            "never paste full workspace paths to save tokens."
        )
        parsed: Dict[str, Any] | None = None
        last_exc: Exception | None = None
        # ``max_tokens`` = completion budget (provider-dependent; reasoning models also consume it).
        # Retry with larger caps when JSON is truncated. Override:
        # ``ASSISTANT_GLOBAL_MEMORY_MAX_TOKENS_RETRIES=4096,8192,16384,32768``
        mem_retries = _parse_positive_int_list(
            "ASSISTANT_GLOBAL_MEMORY_MAX_TOKENS_RETRIES",
            (32768, 65536),
        )
        for max_tok in mem_retries:
            try:
                parsed = self._run_async(
                    self.pipeline_llm_client.chat_json(
                        system_prompt=system_prompt,
                        user_prompt=user_prompt,
                        max_tokens=max_tok,
                        reasoning_effort="medium",
                        model=self.global_memory_summary_model,
                    )
                )
                break
            except Exception as exc:
                last_exc = exc
                continue
        if parsed is None:
            raise AssistantGlobalMemorySyncError(
                f"global_memory summary LLM failed: {last_exc}"
            ) from last_exc
        if not isinstance(parsed, dict):
            raise AssistantGlobalMemorySyncError(
                "global_memory summary LLM returned non-object JSON"
            )
        content = str(parsed.get("content", "") or "").strip()
        if not content:
            raise AssistantGlobalMemorySyncError(
                "global_memory summary LLM must return non-empty content"
            )
        raw_locs = parsed.get("artifact_locations")
        if raw_locs is not None and not isinstance(raw_locs, list):
            raise AssistantGlobalMemorySyncError(
                "global_memory summary LLM artifact_locations must be a list or omitted"
            )
        raw_briefs = parsed.get("artifact_briefs")
        if raw_briefs is not None and not isinstance(raw_briefs, list):
            raise AssistantGlobalMemorySyncError(
                "global_memory summary LLM artifact_briefs must be a list or omitted"
            )
        llm_locs: List[Dict[str, Any]] = raw_locs if isinstance(raw_locs, list) else []
        llm_briefs: List[Dict[str, Any]] = raw_briefs if isinstance(raw_briefs, list) else []
        merged = self._merge_artifact_locations(deterministic_artifacts, llm_locs)
        det_paths = {
            str(x.get("path") or "").strip()
            for x in deterministic_artifacts
            if isinstance(x, dict) and str(x.get("path") or "").strip()
        }
        merged_paths = {
            str(x.get("path") or "").strip()
            for x in merged
            if isinstance(x, dict) and str(x.get("path") or "").strip()
        }
        missing = det_paths - merged_paths
        if missing:
            raise AssistantGlobalMemorySyncError(
                f"global_memory summary LLM merged artifact_locations missing paths: {sorted(missing)}"
            )
        return {"content": content, "artifact_locations": merged, "artifact_briefs": llm_briefs}

    def _sync_global_memory_after_execution(
        self,
        workspace: Workspace,
        execution: AgentExecution,
        *,
        persisted_media_paths: Optional[Dict[str, str]] = None,
        extra_artifact_locations: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Append one entry to workspace ``global_memory.md`` (LLM summary + execution snapshot)."""
        if execution.status not in (ExecutionStatus.COMPLETED, ExecutionStatus.FAILED):
            return
        det = self._deterministic_artifact_bundle(execution, persisted_media_paths)
        if extra_artifact_locations:
            det = list(det) + list(extra_artifact_locations)
        extracted = self._extract_global_memory_summary_with_llm(execution, det)
        summary = str(extracted["content"]).strip()
        artifact_locations = extracted["artifact_locations"]
        artifact_briefs = extracted.get("artifact_briefs")
        execution_result = self._global_memory_execution_snapshot(execution)
        if isinstance(artifact_briefs, list) and artifact_briefs:
            execution_result["artifact_briefs"] = artifact_briefs
        workspace.add_memory_entry(
            content=summary,
            task_id=execution.task_id,
            agent_id=execution.agent_id or None,
            execution_result=execution_result,
            artifact_locations=artifact_locations,
        )

    @staticmethod
    def _persist_assignment_key(item: Dict[str, Any]) -> tuple[str, str]:
        return (str(item.get("kind") or ""), str(item.get("source_key") or ""))

    @staticmethod
    def _artifact_media_type_subdir(filename: str) -> str:
        """Subfolder under ``artifacts/media/<agent>/`` from file extension (video/audio/image/other)."""
        fn = (filename or "").lower().strip()
        if fn.endswith((".mp4", ".mov", ".webm", ".mkv")):
            return "video"
        if fn.endswith((".wav", ".mp3", ".aac", ".flac", ".ogg", ".m4a")):
            return "audio"
        if fn.endswith((".png", ".jpg", ".jpeg", ".webp", ".gif")):
            return "image"
        return "other"

    def _deterministic_output_persist_plan(
        self,
        execution: AgentExecution,
        asset_key: str,
    ) -> List[Dict[str, Any]]:
        """Default relative paths under workspace ``artifacts/``."""
        assignments: List[Dict[str, Any]] = []
        results = execution.results
        if not isinstance(results, dict):
            return assignments
        # Binary/media: artifacts/media/<sub_agent_id>/<video|audio|image|other>/<filename>
        # JSON snapshots stay under artifacts/<asset_key>/ (see json_snapshot below).
        producer = execution.agent_id or "agent"

        for key, value in results.items():
            if key.startswith("_"):
                continue
            if isinstance(value, dict) and "file_content" in value:
                fn = value.get("filename") or f"{key}.bin"
                sub = self._artifact_media_type_subdir(fn)
                rel = f"artifacts/media/{producer}/{sub}/{fn}"
                assignments.append({"kind": "binary", "source_key": key, "relative_path": rel})

        media = results.get("_media_files")
        if isinstance(media, dict):
            for key, value in media.items():
                if isinstance(value, dict) and "file_content" in value:
                    fn = value.get("filename") or f"{key}.bin"
                    sub = self._artifact_media_type_subdir(fn)
                    rel = f"artifacts/media/{producer}/{sub}/{fn}"
                    assignments.append({"kind": "media", "source_key": key, "relative_path": rel})

        if execution.agent_id == "KeyFrameAgent" and execution.status == ExecutionStatus.COMPLETED:
            items = build_keyframes_manifest_items(results)
            if items:
                payload = {
                    "schema_version": "1.0",
                    "role": "keyframes_manifest",
                    "task_id": execution.task_id,
                    "execution_id": execution.id,
                    "items": items,
                }
                assignments.append(
                    {
                        "kind": "keyframes_manifest",
                        "source_key": "",
                        "relative_path": "artifacts/keyframes/keyframes_manifest.json",
                        "manifest_document": payload,
                    }
                )

        snap_payload = AssetManager._build_json_snapshot_payload(results)
        if snap_payload:
            filename = AssetManager.snapshot_filename(asset_key, execution.id)
            rel = f"artifacts/{asset_key}/{filename}"
            assignments.append(
                {
                    "kind": "json_snapshot",
                    "source_key": "",
                    "role": asset_key,
                    "relative_path": rel,
                }
            )
        return assignments

    def _merge_persist_assignments(
        self,
        base: List[Dict[str, Any]],
        overrides: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        idx: Dict[tuple[str, str], Dict[str, Any]] = {}
        for o in overrides:
            if not isinstance(o, dict):
                continue
            idx[self._persist_assignment_key(o)] = o
        out: List[Dict[str, Any]] = []
        for b in base:
            if not isinstance(b, dict):
                continue
            key = self._persist_assignment_key(b)
            o = idx.get(key)
            if o:
                rel = str(o.get("relative_path") or "").strip().replace("\\", "/")
                if AssetManager.is_safe_artifacts_relative_path(rel):
                    merged = dict(b)
                    merged["relative_path"] = rel
                    role = o.get("role")
                    if str(merged.get("kind") or "") == "json_snapshot":
                        if not (isinstance(role, str) and role.strip()):
                            raise AssistantBadExecuteFieldsError(
                                "output persist plan must provide non-empty role for json_snapshot"
                            )
                        merged["role"] = role.strip()
                    elif isinstance(role, str) and role.strip():
                        merged["role"] = role.strip()
                    out.append(merged)
                    continue
            out.append(dict(b))
        return out

    def _refine_output_persist_plan_with_llm(
        self,
        workspace: Workspace,
        execution: AgentExecution,
        descriptor: Any,
        base_plan: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        if not base_plan:
            return []
        desc_text = getattr(descriptor, "catalog_entry", "") or ""
        blob = {
            "target_agent_id": execution.agent_id,
            "task_id": execution.task_id,
            "descriptor_hint": desc_text,
            "proposed_assignments": base_plan,
            "naming_specs": (
                execution.results.get("_naming_specs", [])
                if isinstance(execution.results, dict)
                else []
            ),
            "naming_policy": self._load_persist_naming_policy(),
            # Ground truth for layout: full workspace runtime tree (includes artifacts/).
            "workspace_file_tree": workspace.get_workspace_root_file_tree_text(),
        }
        system_prompt = (
            "You orchestrate workspace-relative output paths for ONE agent execution. "
            "Use workspace_file_tree as ground truth: see what "
            "already exists under artifacts/, avoid name collisions, and align new paths with "
            "the current layout (e.g. artifacts/media/<Agent>/<video|audio|image|other>/). "
            "proposed_assignments is the deterministic starting point—adjust relative_path when "
            "the tree or naming_policy suggests a better fit; keep the same number of entries "
            "and each kind/source_key unchanged. "
            "Every relative_path must start with artifacts/ and must not use '..'. "
            "Return strict JSON only."
        )
        user_prompt = (
            "Orchestrate paths using workspace_file_tree above. Context:\n"
            f"{json.dumps(blob, ensure_ascii=False)}\n\n"
            "Return JSON:\n"
            '{"assignments": [\n'
            '  {"kind": "binary|media|json_snapshot|keyframes_manifest", '
            '"source_key": "match proposed (empty string if none)", '
            '"relative_path": "artifacts/...", "role": "required for json_snapshot"}\n'
            "]}\n"
        )
        parsed: Dict[str, Any] | None = None
        last_exc: Exception | None = None
        for max_tok in (16384, 32768, 65536):
            try:
                parsed = self._run_async(
                    self.pipeline_llm_client.chat_json(
                        system_prompt=system_prompt,
                        user_prompt=user_prompt,
                        max_tokens=max_tok,
                        reasoning_effort="low",
                        model=self.output_persist_model,
                    )
                )
                break
            except Exception as exc:
                last_exc = exc
                continue
        if parsed is None:
            raise AssistantBadExecuteFieldsError(
                f"output persist plan LLM failed: {last_exc}"
            ) from last_exc
        if not isinstance(parsed, dict):
            raise AssistantBadExecuteFieldsError("output persist plan LLM returned non-object JSON")
        ov = parsed.get("assignments")
        if not isinstance(ov, list):
            raise AssistantBadExecuteFieldsError(
                "output persist plan LLM response missing assignments list"
            )
        return self._merge_persist_assignments(base_plan, ov)

    def process_results(
        self,
        execution: AgentExecution,
        workspace: Workspace,
        *,
        overwrite_existing_assets: bool = False,
    ) -> Dict[str, Any]:
        """
        Process execution results and store in workspace
        
        Args:
            execution: AgentExecution instance with results
            workspace: Workspace instance
            
        Returns:
            Dictionary with ``task_id``, ``execution_id``, ``status``,
            ``error``, ``error_reasoning`` (reserved for richer failure context; often ``null``),
            ``workspace_id``, and ``global_memory_brief`` (same shape as
            ``GET /api/assistant/workspace/memory/brief`` — ``{"global_memory": [...]}`` without
            ``content`` keys). Full sub-agent payload remains on the stored
            ``AgentExecution.results``; clients fetch it via
            ``GET /api/assistant/executions/task/{task_id}`` when needed.
        """
        workspace.log_execution_result(execution)
        descriptor = self.agent_registry.get_descriptor(execution.agent_id)
        asset_key = getattr(descriptor, "asset_key", execution.agent_id)
        base_plan = self._deterministic_output_persist_plan(execution, asset_key)
        plan = self._refine_output_persist_plan_with_llm(
            workspace, execution, descriptor, base_plan
        )
        policy = self._load_persist_naming_policy()
        plan_digest = hashlib.sha256(
            json.dumps(plan, ensure_ascii=False, sort_keys=True).encode("utf-8")
        ).hexdigest()
        if isinstance(execution.results, dict):
            execution.results["_persist_plan_meta"] = {
                "naming_policy_version": str(policy.get("version") or "default-1"),
                "persist_plan_digest": plan_digest,
            }
        persisted_paths, asset_index, extra_locs = workspace.persist_execution_from_plan(
            execution,
            plan,
            overwrite_existing=overwrite_existing_assets,
        )
        if asset_index and isinstance(execution.results, dict):
            execution.results["_asset_index"] = asset_index
        if persisted_paths or asset_index:
            self.storage.update_execution(execution)
        self._sync_global_memory_after_execution(
            workspace,
            execution,
            persisted_media_paths=persisted_paths or None,
            extra_artifact_locations=extra_locs or None,
        )
        memory_brief = workspace.get_memory_brief(task_id=execution.task_id)
        return {
            "task_id": execution.task_id,
            "execution_id": execution.id,
            "status": execution.status.value,
            "error": execution.error,
            "error_reasoning": None,
            "workspace_id": workspace.id,
            "global_memory_brief": memory_brief,
        }

    def build_execution_inputs(
        self,
        agent_id: str,
        task_id: str,
        workspace: Workspace,
        execute_fields: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Boundary 1: build final execution inputs for a sub-agent.

        *execute_fields* is the JSON object from ``POST ... {"execute_fields": {...}}``:
        optional keys ``text``, ``image``, ``video``, ``audio``, etc.

        Loads persisted global memory via ``list_memory_entries`` (includes ``content``)
        so that ``_resolve_inputs_for_agent_with_llm`` can use the planning summaries
        alongside ``artifact_locations`` when selecting artifact roles.

        """
        runtime = dict(execute_fields or {})
        runtime.pop("_memory_brief", None)
        text_seed = runtime.get("text")
        packaged_data = self.package_data(
            agent_id=agent_id,
            task_id=task_id,
            text_seed=text_seed,
        )
        packaged_data["global_memory"] = workspace.list_memory_entries(
            task_id=task_id,
            limit=_global_memory_context_entries_limit(),
        )
        self._inject_execute_media_into_bundle(packaged_data["input_bundle_v2"], runtime)
        pkg = self._resolve_inputs_for_agent_with_llm(
            agent_id, task_id, workspace, packaged_data
        )
        required_roles = pkg.get("required_roles") if isinstance(pkg, dict) else None
        self._apply_input_package_merge(
            packaged_data,
            pkg,
            workspace,
            required_roles=required_roles,
        )
        return self._merge_execution_inputs(packaged_data, {"execute_fields": runtime})

    def execute_agent_for_task(
        self,
        agent_id: str,
        task_id: str,
        execute_fields: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete workflow: Execute an agent for a task.

        ``execute_fields`` is the dict from the HTTP body key ``execute_fields``
        (``text``, ``image``, ``video``, …). Assistant does not read Task Stack storage.

        This method orchestrates three boundary responsibilities:
        1. Build execution inputs
        2. Run agent
        3. Persist execution results

        Returns:
            Execution summary dict (``task_id``, ``execution_id``, ``status``,
            ``error``, ``error_reasoning``, ``workspace_id``, ``global_memory_brief``).
            Sub-agent ``results`` are not included; use executions list API to load them.
        """
        # Prepare environment
        workspace = self.prepare_environment()
        auto_overwrite = self._has_existing_assets(task_id=task_id, agent_id=agent_id)
        overwrite_existing_assets = auto_overwrite
        
        # 1) Build inputs (task metadata + input_bundle_v2 + execute_fields overlays)
        inputs = self.build_execution_inputs(
            agent_id=agent_id,
            task_id=task_id,
            workspace=workspace,
            execute_fields=execute_fields,
        )
        
        # 2) Run selected agent
        execution = self.execute_agent(
            agent_id=agent_id,
            task_id=task_id,
            inputs=inputs,
        )
        
        # 3) Persist results and return task-running summary payload
        return self.process_results(
            execution,
            workspace,
            overwrite_existing_assets=overwrite_existing_assets,
        )
