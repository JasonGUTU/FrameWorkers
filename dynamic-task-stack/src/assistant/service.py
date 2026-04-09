# Assistant Service - Core business logic for agent orchestration

import asyncio
import json
import logging
import os
import shutil
import tempfile
from typing import Any, Dict, List, Optional
from datetime import datetime

from .models import AgentExecution, ExecutionStatus
from .workspace import Workspace
from .workspace.artifact_writer import ArtifactWriter
from agents import get_agent_registry
from agents.contracts import InputBundleV2
from agents.base_agent import MaterializeContext
from inference.clients import LLMClient as PipelineLLMClient

logger = logging.getLogger(__name__)


class AssistantBadExecuteFieldsError(Exception):
    """``execute_fields`` violated a strict wire rule (e.g. ``text`` must be a string)."""


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
        _default_model = os.getenv(
            "INFERENCE_DEFAULT_MODEL", "google-ai-studio/gemini-2.5-flash"
        ).strip()
        self.input_package_model = (
            os.getenv("ASSISTANT_INPUT_PACKAGE_MODEL", "").strip() or _default_model
        )
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
    def _run_async(coro):
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    @staticmethod
    def _mapping_to_input_bundle_v2(task_id: str, data: Dict[str, Any]) -> InputBundleV2:
        """Build an ``InputBundleV2`` from the per-execution input mapping.

        Single recognized key:
          * ``resolved_artifacts`` / ``_resolved_artifacts`` (dict, keyed by
            consumer label name) → ``context["resolved_artifacts"]``

        Any other key is silently ignored. Sub-agent inputs flow ONLY through
        the InputResolver-selected ``resolved_artifacts``.  There is no
        ``hints`` slot.  Any user-supplied raw input (text/image/video/audio)
        must already have been persisted into the workspace as an artifact
        (typically by an Intake agent) before this method is called.
        """
        context: Dict[str, Any] = {}
        for key, value in data.items():
            if key in ("_resolved_artifacts", "resolved_artifacts") and isinstance(value, (list, dict)):
                context["resolved_artifacts"] = value
        return InputBundleV2(task_id=task_id, context=context)

    @staticmethod
    def _map_pipeline_inputs(
        inputs: Dict[str, Any],
    ) -> tuple[str, InputBundleV2]:
        task_id = inputs.get("task_id") or ""
        raw = inputs.get("input_bundle_v2")
        flat: Dict[str, Any] = dict(raw) if isinstance(raw, dict) else {}
        return task_id, AssistantService._mapping_to_input_bundle_v2(task_id, flat)

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
    def _build_descriptor_input(
        descriptor: Any,
        task_id: str,
        readonly_bundle: Any,
    ) -> Any:
        return descriptor.build_input(task_id, readonly_bundle)

    def _execute_pipeline_descriptor(
        self,
        descriptor: Any,
        inputs: Dict[str, Any],
        execution: Optional[AgentExecution] = None,
    ) -> Dict[str, Any]:
        task_id, ib_mapped = self._map_pipeline_inputs(inputs)
        # Hydrate any indexed asset entries within resolved_artifacts.
        # The bundle now only carries resolved_artifacts (no hints slot).
        hydrated = self.workspace.hydrate_indexed_assets(ib_mapped.context)
        input_bundle_v2 = self._mapping_to_input_bundle_v2(task_id, hydrated)

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

            def _report_failure(*, kind: str, sys_id: str, error: str) -> None:
                """Surface a per-call materializer failure into logs.jsonl.

                Each materializer's inner ``except Exception`` calls this so
                the swallow-and-continue policy still leaves a structured
                trace. Closes over ``execution`` so the log entry carries
                the agent_id / task_id / execution_id triple.
                """
                if execution is None:
                    return
                try:
                    self.workspace.log_artifact_materialize_failure(
                        agent_id=execution.agent_id,
                        task_id=execution.task_id,
                        execution_id=execution.id,
                        kind=kind,
                        sys_id=sys_id,
                        error=error,
                    )
                except Exception:
                    # Never let failure logging crash the materializer.
                    pass

            materialize_ctx = MaterializeContext(
                task_id=task_id,
                typed_input=typed_input,
                persist_binary=_persist,
                report_failure=_report_failure,
            )

        try:
            result = self._run_async(
                agent.run(
                    typed_input,
                    materialize_ctx=materialize_ctx,
                )
            )
            output: Dict[str, Any] = {}
            asset_dict = getattr(result, "asset_dict", None)
            raw_output = getattr(result, "output", None)
            media_assets = getattr(result, "media_assets", [])
            attempts = getattr(result, "attempts", None)
            eval_result = getattr(result, "eval_result", None)
            # ``passed`` is the agent's quality-gate verdict from
            # base_agent.run() — False when L1/L2/L3 evaluation failed
            # all retries OR materialization raised. The previous code
            # silently dropped this and let execute_agent stamp
            # status=COMPLETED, producing the "0/5 shot clips, status
            # COMPLETED" silent-failure pattern. Surface it via the
            # output dict so execute_agent can translate False → FAILED.
            passed = bool(getattr(result, "passed", True))

            if asset_dict is not None:
                output = asset_dict
            elif raw_output is not None:
                output = raw_output.model_dump() if hasattr(raw_output, "model_dump") else dict(raw_output)

            if media_assets:
                output["_media_files"] = self.workspace.collect_materialized_files(media_assets)
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
            output["_quality_gate_passed"] = passed
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
    ) -> Dict[str, Any]:
        """Package the empty execution bundle for an agent.

        After the input-channel unification, sub-agents have only one input
        source: ``InputResolver``-selected ``resolved_artifacts``. ``package_data``
        no longer accepts a text seed; the user's text instruction (if any)
        is persisted as an artifact by IntakeTextAgent and reaches the agent
        via the normal label-matching path.

        Args:
            agent_id: ID of the agent to execute
            task_id: ID of the task

        Returns:
            ``task_id`` plus an empty ``input_bundle_v2`` seed mapping.

        Raises:
            ValueError: If agent not found in registry
        """
        descriptor = self.agent_registry.get_descriptor(agent_id)
        if not self._is_executable_pipeline_descriptor(descriptor):
            raise ValueError(f"Agent {agent_id} not found in registry")

        return {
            "task_id": task_id,
            "input_bundle_v2": {},
        }

    def _resolve_inputs_for_agent_with_llm(
        self,
        agent_id: str,
        task_id: str,
        workspace: Workspace,
    ) -> Dict[str, Any]:
        """Semantic input resolution via the global_memory caption index.

        Uses the agent's ``input_needs_description`` and the global_memory
        caption index to let an LLM select which artifacts the agent needs.
        Provides only the agent_id and task_id; no text seed or hint data.
        """
        try:
            descriptor = self.agent_registry.get_descriptor(agent_id)
        except Exception:
            raise AssistantBadExecuteFieldsError(f"unknown agent_id: {agent_id}")

        input_needs = getattr(descriptor, "input_needs_description", "") or ""

        resolved = workspace.resolve_inputs_for_agent(
            agent_id=agent_id,
            task_id=task_id,
            input_needs_description=input_needs,
            llm_client=self.pipeline_llm_client,
            model=self.input_package_model,
        )
        return resolved

    def _apply_resolved_inputs(
        self,
        packaged_data: Dict[str, Any],
        resolved: Dict[str, Any],
    ) -> None:
        """Write InputResolver output into the input_bundle_v2 mapping."""
        bundle = packaged_data.get("input_bundle_v2")
        if not isinstance(bundle, dict):
            return
        resolved_artifacts = resolved.get("resolved_artifacts")
        if isinstance(resolved_artifacts, (list, dict)) and resolved_artifacts:
            bundle["_resolved_artifacts"] = resolved_artifacts
        bundle["input_package"] = {
            "rationale": resolved.get("rationale"),
            "selected_artifact_paths": resolved.get("selected_artifact_paths"),
        }

    def _has_existing_assets(self, *, task_id: str, agent_id: str) -> bool:
        """True if this agent has already produced any artifact for the task."""
        return self.workspace.global_memory.has_producer_run(
            task_id=task_id, agent_id=agent_id,
        )
    
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
            results = self._execute_pipeline_descriptor(descriptor, inputs, execution)

            # Translate the agent's quality-gate verdict into execution
            # status. base_agent.run() returns ExecutionResult.passed=False
            # when L1/L2/L3 evaluation failed every retry; surfacing it
            # here turns the previously-silent "0/N clips, status COMPLETED"
            # case into an honest FAILED. Partial results (any media that
            # did materialize) are still attached, so process_results can
            # persist whatever survived.
            quality_gate_passed = bool(results.pop("_quality_gate_passed", True))
            execution.results = results
            execution.completed_at = datetime.now()
            if quality_gate_passed:
                execution.status = ExecutionStatus.COMPLETED
            else:
                execution.status = ExecutionStatus.FAILED
                debug = results.get("_execution_debug", {}) if isinstance(results, dict) else {}
                summary = (
                    debug.get("eval_summary")
                    if isinstance(debug, dict)
                    else ""
                ) or "agent quality gate failed (no eval summary)"
                execution.error = f"quality gate failed: {summary}"
            self.storage.update_execution(execution)
        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.error = str(e)
            execution.completed_at = datetime.now()
            self.storage.update_execution(execution)
            # Failure shows up in logs.jsonl as event=execution.failed via
            # log_execution_result during process_results; nothing else to
            # mirror — global_memory is auto-populated by ArtifactWriter
            # when (and only when) artifacts actually hit disk.
            raise e

        return execution

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
        descriptor: Any,
    ) -> List[Dict[str, Any]]:
        """Default relative paths under workspace ``artifacts/``.

        Binary/media files land under
        ``artifacts/media/<agent_id>/<type>/<task_id>_<base_filename>``.
        JSON snapshots land under
        ``artifacts/<agent_id>/<task_id>_<agent_id_lower>_exec_<n>.json``
        — the producer ``agent_id`` is the slug for both the directory and
        (lowercased) the filename. Every filename gets a ``<task_id>_``
        prefix so multi-task workspaces can never collide.
        """
        assignments: List[Dict[str, Any]] = []
        results = execution.results
        if not isinstance(results, dict):
            return assignments
        producer = execution.agent_id or "agent"
        task_id = (execution.task_id or "").strip()

        def _prefix(fn: str) -> str:
            """Bake the task_id into the filename so multi-task workspaces are collision-free."""
            return f"{task_id}_{fn}" if task_id else fn

        for key, value in results.items():
            if key.startswith("_"):
                continue
            if isinstance(value, dict) and "file_content" in value:
                fn = value.get("filename") or f"{key}.bin"
                sub = self._artifact_media_type_subdir(fn)
                rel = f"artifacts/media/{producer}/{sub}/{_prefix(fn)}"
                assignments.append({"kind": "binary", "source_key": key, "relative_path": rel})

        media = results.get("_media_files")
        if isinstance(media, dict):
            for key, value in media.items():
                if isinstance(value, dict) and "file_content" in value:
                    fn = value.get("filename") or f"{key}.bin"
                    sub = self._artifact_media_type_subdir(fn)
                    rel = f"artifacts/media/{producer}/{sub}/{_prefix(fn)}"
                    assignments.append({"kind": "media", "source_key": key, "relative_path": rel})

        snap_payload = ArtifactWriter._build_json_snapshot_payload(results)
        if snap_payload:
            filename = ArtifactWriter.snapshot_filename(producer, execution.id)
            rel = f"artifacts/{producer}/{_prefix(filename)}"
            assignments.append(
                {
                    "kind": "json_snapshot",
                    "source_key": "",
                    "relative_path": rel,
                }
            )
        return assignments

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
            ``workspace_id``, and ``global_memory_brief`` (a list of slim
            rows ``[{execution_id, agent_id, task_id, status, created_at}, ...]``
            in chronological order; same shape as the ``global_memory_brief``
            field returned by ``GET /api/assistant/workspace/memory/brief``).
            Full sub-agent payload remains on the stored
            ``AgentExecution.results``; clients fetch it via
            ``GET /api/assistant/executions/task/{task_id}`` when needed.
        """
        workspace.log_execution_result(execution)
        descriptor = self.agent_registry.get_descriptor(execution.agent_id)
        base_plan = self._deterministic_output_persist_plan(execution, descriptor)
        # Persist plan is fully deterministic — no LLM rewrite, no
        # naming policy file, no plan digest meta. The base plan from
        # _deterministic_output_persist_plan already produces the final
        # paths (artifacts/<Agent>/<task_id>_<lowercase>_exec_n.json
        # for snapshots; artifacts/media/<Agent>/<type>/<task_id>_<base>
        # for binaries).
        persisted_paths, asset_index = workspace.persist_execution_from_plan(
            execution,
            base_plan,
            overwrite_existing=overwrite_existing_assets,
        )
        if asset_index and isinstance(execution.results, dict):
            execution.results["_asset_index"] = asset_index
        if persisted_paths or asset_index:
            self.storage.update_execution(execution)
        # global_memory is auto-populated by ArtifactWriter via the
        # workspace's _register_artifacts_callback during the persist
        # call above; the brief here is just a derived view.
        global_memory_brief = workspace.get_global_memory_brief(task_id=execution.task_id)
        return {
            "task_id": execution.task_id,
            "execution_id": execution.id,
            "status": execution.status.value,
            "error": execution.error,
            "error_reasoning": None,
            "workspace_id": workspace.id,
            "global_memory_brief": global_memory_brief,
        }

    def build_execution_inputs(
        self,
        agent_id: str,
        task_id: str,
        workspace: Workspace,
        execute_fields: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Boundary 1: build final execution inputs for a sub-agent.

        After the input-channel unification, this method only:
          1. Constructs an empty input bundle.
          2. Runs ``InputResolver`` to semantically select artifacts from
             the global_memory caption index based on the agent's
             ``input_needs_description``.
          3. Writes the resolved selection into the bundle.

        ``execute_fields`` is retained as an opaque overlay for any future
        per-call hooks (e.g. ``overwrite``), but its ``text`` / ``image`` /
        ``video`` / ``audio`` keys are NO LONGER read here.  Any raw user
        input must be persisted into the workspace as an artifact (via an
        Intake agent or ``POST /api/workspace/upload``) BEFORE the target
        sub-agent runs, so that InputResolver can find it through the
        normal caption-driven label match.
        """
        runtime = dict(execute_fields or {})
        runtime.pop("_memory_brief", None)
        packaged_data = self.package_data(
            agent_id=agent_id,
            task_id=task_id,
        )
        resolved = self._resolve_inputs_for_agent_with_llm(
            agent_id, task_id, workspace,
        )
        self._apply_resolved_inputs(packaged_data, resolved)
        return self._merge_execution_inputs(packaged_data, {"execute_fields": runtime})

    def intake_user_text(
        self,
        *,
        task_id: str,
        text: str,
        user_intent: str = "",
    ) -> Dict[str, Any]:
        """Persist a raw user text + run IntakeTextAgent over it.

        This is the canonical Phase D path: callers (the director loop, the
        chat-message handler, or any other ingestion point) hand the user's
        natural-language input to this method, and the result is a
        caption-rich workspace artifact that downstream content agents will
        find via their ``[creative_brief]`` (or similar) labels.

        The method does two things:
          1. ``workspace.persist_raw_upload`` registers the raw text with a
             placeholder caption (``scope=raw_pending``).
          2. ``execute_agent_for_task("IntakeTextAgent", ...)`` runs the
             intake agent against the placeholder, producing the
             caption-rich follow-up artifact.

        Returns the standard execution-summary dict from
        ``execute_agent_for_task``.
        """
        if not isinstance(text, str) or not text.strip():
            raise AssistantBadExecuteFieldsError("text must be a non-empty string")
        # Persist as raw upload first; the resulting artifact has a
        # placeholder caption that IntakeTextAgent's [raw_text_upload]
        # label will match in the next step.
        self.workspace.persist_raw_upload(
            file_content=text.encode("utf-8"),
            mime="text/plain",
            user_intent=user_intent or "user-provided text input",
        )
        # Run IntakeTextAgent over the placeholder.
        return self.execute_agent_for_task(
            agent_id="IntakeTextAgent",
            task_id=task_id,
            execute_fields=None,
        )

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
