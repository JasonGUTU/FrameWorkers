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
from agents.base_agent import MaterializeContext
from inference.clients import LLMClient as PipelineLLMClient

logger = logging.getLogger(__name__)


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

    def _execute_pipeline_descriptor(
        self,
        descriptor: Any,
        inputs: Dict[str, Any],
        execution: Optional[AgentExecution] = None,
    ) -> Dict[str, Any]:
        step_id = inputs.get("step_id") or ""
        resolved_artifacts = inputs.get("resolved_artifacts") or {}
        if not isinstance(resolved_artifacts, dict):
            resolved_artifacts = {}

        agent = descriptor.build_equipped_agent(self.pipeline_llm_client)
        typed_input = descriptor.build_input(step_id, resolved_artifacts)

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
                the agent_id / step_id / execution_id triple.
                """
                if execution is None:
                    return
                try:
                    self.workspace.log_artifact_materialize_failure(
                        agent_id=execution.agent_id,
                        step_id=execution.step_id,
                        execution_id=execution.id,
                        kind=kind,
                        sys_id=sys_id,
                        error=error,
                    )
                except Exception:
                    # Never let failure logging crash the materializer.
                    pass

            materialize_ctx = MaterializeContext(
                step_id=step_id,
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

    def _resolve_inputs_for_agent_with_llm(
        self,
        descriptor: Any,
        step_id: str,
        workspace: Workspace,
    ) -> Dict[str, Any]:
        """Semantic input resolution via the global_memory caption index.

        Uses the agent's ``input_needs_description`` and the global_memory
        caption index to let an LLM select which artifacts the agent needs.
        Caller passes the already-validated descriptor so we don't re-look
        it up — the only callsite (``build_execution_inputs``) has already
        validated it via ``_is_executable_pipeline_descriptor``.
        """
        agent_id = getattr(descriptor, "agent_id", "") or ""
        input_needs = getattr(descriptor, "input_needs_description", "") or ""

        resolved = workspace.resolve_inputs_for_agent(
            agent_id=agent_id,
            step_id=step_id,
            input_needs_description=input_needs,
            llm_client=self.pipeline_llm_client,
            model=self.input_package_model,
        )
        return resolved

    def _has_existing_assets(self, *, step_id: str, agent_id: str) -> bool:
        """True if this agent has already produced any artifact for the task."""
        return self.workspace.global_memory.has_producer_run(
            step_id=step_id, agent_id=agent_id,
        )

    def execute_agent(
        self,
        agent_id: str,
        step_id: str,
        inputs: Dict[str, Any],
    ) -> AgentExecution:
        """
        Execute an agent and retrieve results
        
        Args:
            agent_id: ID of the agent to execute
            step_id: ID of the task
            inputs: Input data for the agent
            
        Returns:
            AgentExecution instance with results
            
        Raises:
            ValueError: If agent or task not found
        """
        descriptor = self.agent_registry.get_descriptor(agent_id)
        if not self._is_executable_pipeline_descriptor(descriptor):
            raise ValueError(f"Agent {agent_id} not found in registry")
        
        # Create execution record
        execution = self.storage.create_execution(
            agent_id=agent_id,
            step_id=step_id,
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
        ``artifacts/media/<agent_id>/<type>/<step_id>_<base_filename>``.
        JSON snapshots land under
        ``artifacts/<agent_id>/<step_id>_<agent_id_lower>_exec_<n>.json``
        — the producer ``agent_id`` is the slug for both the directory and
        (lowercased) the filename. Every filename gets a ``<step_id>_``
        prefix so multi-task workspaces can never collide.
        """
        assignments: List[Dict[str, Any]] = []
        results = execution.results
        if not isinstance(results, dict):
            return assignments
        producer = execution.agent_id or "agent"
        step_id = (execution.step_id or "").strip()

        def _prefix(fn: str) -> str:
            """Bake the step_id into the filename so multi-task workspaces are collision-free."""
            return f"{step_id}_{fn}" if step_id else fn

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
    ) -> AgentExecution:
        """Persist the execution's artifacts and return the execution itself.

        ``global_memory`` is auto-populated by ArtifactWriter via the
        workspace's ``_register_artifacts_callback`` during ``persist_execution_from_plan``;
        directors that need cross-turn execution history query
        ``GET /api/assistant/executions/step/<step_id>`` directly.
        """
        workspace.log_execution_result(execution)
        descriptor = self.agent_registry.get_descriptor(execution.agent_id)
        base_plan = self._deterministic_output_persist_plan(execution, descriptor)
        output_dict = execution.results if isinstance(execution.results, dict) else {}
        _bc = getattr(descriptor, "build_captions", None)
        captions = _bc(execution.agent_id, output_dict) if callable(_bc) else {}
        # Handle _update: keys — update existing captions instead of creating new entries.
        update_keys = [k for k in captions if k.startswith("_update:")]
        for uk in update_keys:
            entry = captions.pop(uk)
            path = entry.get("path", "")
            if path:
                workspace.global_memory.update_caption_by_path(
                    path,
                    caption=entry.get("caption", ""),
                    scope=entry.get("scope"),
                )
        persisted_paths, asset_index = workspace.persist_execution_from_plan(
            execution,
            base_plan,
            overwrite_existing=overwrite_existing_assets,
            captions=captions,
        )
        if asset_index and isinstance(execution.results, dict):
            execution.results["_asset_index"] = asset_index
        if persisted_paths or asset_index:
            self.storage.update_execution(execution)
        return execution

    def build_execution_inputs(
        self,
        agent_id: str,
        step_id: str,
        workspace: Workspace,
    ) -> Dict[str, Any]:
        """Boundary 1: build final execution inputs for a sub-agent.

        Steps:
          1. Validates the agent exists in the registry.
          2. Runs ``InputResolver`` to semantically select artifacts from
             the global_memory caption index based on the agent's
             ``input_needs_description``.
          3. Returns a flat ``{step_id, resolved_artifacts}`` dict.
             ``resolved_artifacts`` is the only channel sub-agents see —
             ``_execute_pipeline_descriptor`` hands it straight to
             ``descriptor.build_input``.

        Any raw user input must be persisted into the workspace as an
        artifact (via an Intake agent or ``POST /api/workspace/upload``)
        BEFORE the target sub-agent runs, so that InputResolver can find
        it through the normal caption-driven label match.
        """
        descriptor = self.agent_registry.get_descriptor(agent_id)
        if not self._is_executable_pipeline_descriptor(descriptor):
            raise ValueError(f"Agent {agent_id} not found in registry")

        resolved = self._resolve_inputs_for_agent_with_llm(
            descriptor, step_id, workspace,
        )
        resolved_artifacts = resolved.get("resolved_artifacts") or {}
        if not isinstance(resolved_artifacts, dict):
            resolved_artifacts = {}

        return {
            "step_id": step_id,
            "resolved_artifacts": resolved_artifacts,
        }

    def execute_agent_for_step(
        self,
        agent_id: str,
        step_id: str,
    ) -> AgentExecution:
        """
        Complete workflow: Execute an agent for a task.

        The HTTP body has only ``agent_id`` and ``step_id``. Any user-side
        text / image / video / audio input must already exist in the
        workspace as a caption-rich artifact (e.g. via Intake agents);
        InputResolver picks it up by label.

        This method orchestrates three boundary responsibilities:
        1. Build execution inputs
        2. Run agent
        3. Persist execution results

        Returns the current :class:`AgentExecution` (COMPLETED / FAILED etc.).
        Directors pull cross-turn history from ``GET /api/assistant/executions/step/<step_id>``.
        """
        # Prepare environment
        workspace = self.prepare_environment()
        auto_overwrite = self._has_existing_assets(step_id=step_id, agent_id=agent_id)
        overwrite_existing_assets = auto_overwrite

        # 1) Build inputs (step_id + resolved_artifacts)
        inputs = self.build_execution_inputs(
            agent_id=agent_id,
            step_id=step_id,
            workspace=workspace,
        )
        
        # 2) Run selected agent
        execution = self.execute_agent(
            agent_id=agent_id,
            step_id=step_id,
            inputs=inputs,
        )
        
        # 3) Persist results and return task-running summary payload
        return self.process_results(
            execution,
            workspace,
            overwrite_existing_assets=overwrite_existing_assets,
        )
