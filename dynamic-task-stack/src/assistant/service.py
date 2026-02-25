# Assistant Service - Core business logic for agent orchestration

import asyncio
import os
import shutil
import tempfile
from typing import Dict, Any, Optional
from datetime import datetime

from .models import AgentExecution, ExecutionStatus
from .workspace import Workspace
from ..task_stack.storage import storage as task_storage  # Read-only access to task storage
from agents import get_agent_registry
from agents.base_agent import MaterializeContext
from inference.runtime.base_client import LLMClient as PipelineLLMClient
from .retrieval import WorkspaceRetriever


class AssistantService:
    """
    Service class for managing assistant operations
    
    There should be only one assistant instance that manages all sub-agents.
    All agents share a single workspace (file system).
    """
    
    def __init__(self, assistant_storage):
        """
        Initialize assistant service
        
        Args:
            assistant_storage: Storage instance for assistant data
        """
        self.storage = assistant_storage
        self.agent_registry = get_agent_registry()
        self.pipeline_llm_client = PipelineLLMClient()
        # Get or create the global workspace
        self.workspace = self._get_global_workspace()
        self.retriever = WorkspaceRetriever(self.workspace)
    
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
            and hasattr(descriptor, "build_upstream")
        )

    @staticmethod
    def _new_pipeline_config(config: Optional[Dict[str, Any]]) -> Any:
        defaults = {
            "target_total_duration_sec": 60,
            "language": "en",
        }
        merged = {**defaults, **(config or {})}

        class _AttrDict:
            def __init__(self, data: Dict[str, Any]):
                self._data = data

            def __getattr__(self, name: str) -> Any:
                if name.startswith("_") or name not in self._data:
                    raise AttributeError(name)
                return self._data[name]

        return _AttrDict(merged)

    @staticmethod
    def _run_async(coro):
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    @staticmethod
    def _map_pipeline_inputs(inputs: Dict[str, Any]) -> tuple[str, str, Dict[str, Any], Any]:
        project_id = inputs.get("project_id") or inputs.get("task_id", "")
        draft_id = inputs.get("draft_id") or inputs.get("task_id", "")

        if "assets" in inputs and isinstance(inputs["assets"], dict):
            assets = dict(inputs["assets"])
        else:
            assets = {}
            task_desc = inputs.get("task_description", "")
            if task_desc:
                assets["draft_idea"] = task_desc
                assets["source_text"] = task_desc
            ctx = inputs.get("workspace_context")
            if isinstance(ctx, dict):
                assets.update(ctx)

        raw_config = inputs.get("config")
        if raw_config is not None and not isinstance(raw_config, dict):
            config = raw_config
        else:
            config = AssistantService._new_pipeline_config(raw_config)
        return project_id, draft_id, assets, config

    @staticmethod
    def _collect_materialized_files(media_assets: list[Any]) -> Dict[str, Any]:
        files: Dict[str, Any] = {}
        for asset in media_assets:
            uri = getattr(asset, "uri_holder", {}).get("uri", "")
            if not uri or not os.path.isfile(uri):
                continue
            with open(uri, "rb") as fh:
                data = fh.read()
            sys_id = getattr(asset, "sys_id", "")
            extension = getattr(asset, "extension", "bin")
            files[sys_id] = {
                "file_content": data,
                "filename": f"{sys_id}.{extension}",
                "description": f"Media asset {sys_id}",
            }
        return files

    @staticmethod
    def _should_keep_materialize_temp_dir() -> bool:
        raw = os.getenv("FW_KEEP_ASSISTANT_TEMP", "").strip().lower()
        return raw in {"1", "true", "yes", "on"}

    def _execute_pipeline_descriptor(self, descriptor: Any, inputs: Dict[str, Any]) -> Dict[str, Any]:
        project_id, draft_id, assets, config = self._map_pipeline_inputs(inputs)

        agent = descriptor.build_equipped_agent(self.pipeline_llm_client)
        typed_input = descriptor.build_input(project_id, draft_id, assets, config)
        upstream = descriptor.build_upstream(assets)

        materialize_ctx = None
        temp_dir: Optional[str] = None
        keep_temp_dir = False
        if getattr(agent, "materializer", None) is not None:
            temp_dir = tempfile.mkdtemp(prefix="fw_media_")
            keep_temp_dir = self._should_keep_materialize_temp_dir()

            def _persist(media_asset):
                path = os.path.join(temp_dir, f"{media_asset.sys_id}.{media_asset.extension}")
                with open(path, "wb") as fh:
                    fh.write(media_asset.data)
                return path

            materialize_ctx = MaterializeContext(
                project_id=project_id,
                assets=assets,
                persist_binary=_persist,
            )

        try:
            result = self._run_async(
                agent.run(
                    typed_input,
                    upstream=upstream,
                    materialize_ctx=materialize_ctx,
                )
            )
            output: Dict[str, Any] = {}
            asset_dict = getattr(result, "asset_dict", None)
            raw_output = getattr(result, "output", None)
            media_assets = getattr(result, "media_assets", [])

            if asset_dict is not None:
                output = asset_dict
            elif raw_output is not None:
                output = raw_output.model_dump() if hasattr(raw_output, "model_dump") else dict(raw_output)

            if media_assets:
                output["_media_files"] = self._collect_materialized_files(media_assets)
            if temp_dir and keep_temp_dir:
                output["_materialize_temp_dir"] = temp_dir
            return output
        finally:
            if temp_dir and not keep_temp_dir:
                shutil.rmtree(temp_dir, ignore_errors=True)

    def _get_task_or_raise(self, task_id: str):
        task = task_storage.get_task(task_id)
        if task is None:
            raise ValueError(f"Task {task_id} not found")
        return task

    def query_agent_inputs(self, agent_id: str) -> Dict[str, Any]:
        """
        Query the required input parameters for an agent
        
        Args:
            agent_id: ID of the agent to query
            
        Returns:
            Dictionary containing input schema and requirements
            
        Raises:
            ValueError: If agent not found
        """
        descriptor = self.agent_registry.get_descriptor(agent_id)
        if not self._is_executable_pipeline_descriptor(descriptor):
            raise ValueError(f"Agent {agent_id} not found in registry")
        return {
            "agent_id": agent_id,
            "agent_name": agent_id,
            "input_schema": {},
            "output_schema": {},
            "capabilities": ["pipeline_agent", descriptor.asset_key],
            "description": (getattr(descriptor, "catalog_entry", "") or "")[:200],
        }
    
    def prepare_environment(self, task_id: Optional[str] = None) -> Workspace:
        """
        Prepare workspace environment for agent execution
        
        Uses the global workspace shared by all agents.
        
        Returns:
            Global workspace instance
        """
        # task_id is intentionally unused: workspace is global/shared.
        return self.workspace

    @staticmethod
    def _latest_executions_by_agent(executions: list[AgentExecution]) -> Dict[str, AgentExecution]:
        latest: Dict[str, AgentExecution] = {}
        for execution in executions:
            if execution.status != ExecutionStatus.COMPLETED:
                continue
            if not execution.results:
                continue
            prev = latest.get(execution.agent_id)
            if prev is None or (execution.completed_at or execution.created_at) > (prev.completed_at or prev.created_at):
                latest[execution.agent_id] = execution
        return latest
    
    def _build_pipeline_assets(
        self,
        task_id: str,
        task_description: str,
    ) -> Dict[str, Any]:
        """Build the shared ``assets`` dict from historical execution results.

        Scans all completed executions under *task_id*, maps each
        ``agent_id`` to its ``asset_key`` via the registry descriptor,
        and stores the execution results under that key.  When the same
        agent was executed multiple times, only the latest successful
        result is kept.

        Also seeds ``draft_idea`` / ``source_text`` from the task
        description so that first-in-pipeline agents (StoryAgent,
        ExampleAgent) have their input ready.
        """
        assets: Dict[str, Any] = {}

        if task_description:
            assets["draft_idea"] = task_description
            assets["source_text"] = task_description

        past_executions = self.storage.get_executions_by_task(task_id)
        for agent_id, execution in self._latest_executions_by_agent(past_executions).items():
            descriptor = self.agent_registry.get_descriptor(agent_id)
            if descriptor is None:
                continue
            results = {
                k: v for k, v in execution.results.items()
                if not k.startswith("_")
            }
            assets[descriptor.asset_key] = results

        return assets

    def package_data(
        self,
        agent_id: str,
        task_id: str,
        workspace: Workspace,
    ) -> Dict[str, Any]:
        """
        Package relevant resources for agent execution
        
        The assistant retrieves information from the workspace file system
        and packages it for distribution to the agent.
        
        Args:
            agent_id: ID of the agent to execute
            task_id: ID of the task
            workspace: Global workspace instance
            
        Returns:
            Dictionary containing packaged data for agent
            
        Raises:
            ValueError: If agent or task not found
        """
        # Step 1: validate selected agent descriptor exists.
        descriptor = self.agent_registry.get_descriptor(agent_id)
        if not self._is_executable_pipeline_descriptor(descriptor):
            raise ValueError(f"Agent {agent_id} not found in registry")
        # Step 2: load task metadata.
        task = self._get_task_or_raise(task_id)
        
        # Retrieve relevant context from workspace using the retriever
        # The assistant searches the workspace and distributes information to agents
        retriever = self.retriever if workspace is self.workspace else WorkspaceRetriever(workspace)
        context = retriever.get_context_for_agent(
            agent_id=agent_id,
            task_id=task_id,
            context_keys=None  # Could be customized based on agent requirements
        )
        
        # Build pipeline assets from historical execution results
        assets = self._build_pipeline_assets(task_id, task.description)
        
        # Package data: task metadata + unified workspace context + pipeline assets.
        return {
            "task_id": task_id,
            "task_description": task.description,
            "task_progress": task.progress,
            "workspace_context": context,
            "assets": assets,
        }
    
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
            raise
        
        return execution

    def _log_execution_result(self, execution: AgentExecution, workspace: Workspace) -> None:
        workspace.log_manager.add_log(
            operation_type="write",
            resource_type="execution",
            resource_id=execution.id,
            agent_id=execution.agent_id,
            task_id=execution.task_id,
            details={
                "status": execution.status.value,
                "error": execution.error,
                "has_results": execution.results is not None,
            },
        )

    def _store_file_result(self, workspace: Workspace, execution: AgentExecution, key: str, value: Dict[str, Any]) -> None:
        workspace.store_file(
            file_content=value["file_content"],
            filename=value.get("filename", f"{key}.bin"),
            description=value.get("description", f"File from execution {execution.id}"),
            created_by=execution.agent_id,
            tags=[execution.agent_id, execution.task_id],
            metadata={"execution_id": execution.id},
        )

    def _store_execution_files(self, execution: AgentExecution, workspace: Workspace) -> None:
        if not execution.results or not isinstance(execution.results, dict):
            return

        for key, value in execution.results.items():
            if isinstance(value, dict) and "file_content" in value:
                self._store_file_result(workspace, execution, key, value)

        media_files = execution.results.get("_media_files")
        if isinstance(media_files, dict):
            for key, value in media_files.items():
                self._store_file_result(workspace, execution, key, value)

    def process_results(
        self,
        execution: AgentExecution,
        workspace: Workspace
    ) -> Dict[str, Any]:
        """
        Process execution results and store in workspace
        
        Args:
            execution: AgentExecution instance with results
            workspace: Workspace instance
            
        Returns:
            Dictionary containing processed results
        """
        self._log_execution_result(execution, workspace)
        self._store_execution_files(execution, workspace)
        return {
            "execution_id": execution.id,
            "status": execution.status.value,
            "results": execution.results,
            "error": execution.error,
            "workspace_id": workspace.id,
        }

    def build_execution_inputs(
        self,
        agent_id: str,
        task_id: str,
        workspace: Workspace,
        additional_inputs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Boundary 1: build final execution inputs for a sub-agent."""
        packaged_data = self.package_data(
            agent_id=agent_id,
            task_id=task_id,
            workspace=workspace,
        )
        if additional_inputs:
            packaged_data.update(additional_inputs)
        return packaged_data

    def execute_agent_for_task(
        self,
        agent_id: str,
        task_id: str,
        additional_inputs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete workflow: Execute an agent for a task
        
        This method orchestrates three boundary responsibilities:
        1. Build execution inputs
        2. Run agent
        3. Persist execution results
        
        Args:
            agent_id: ID of the agent to execute
            task_id: ID of the task
            additional_inputs: Optional additional inputs to merge
            
        Returns:
            Dictionary containing execution results
        """
        # Prepare environment
        workspace = self.prepare_environment()
        
        # 1) Build inputs (agent requirements + workspace context + task metadata)
        inputs = self.build_execution_inputs(
            agent_id=agent_id,
            task_id=task_id,
            workspace=workspace,
            additional_inputs=additional_inputs,
        )
        
        # 2) Run selected agent
        execution = self.execute_agent(
            agent_id=agent_id,
            task_id=task_id,
            inputs=inputs,
        )
        
        # 3) Persist results and return task-running summary payload
        return self.process_results(execution, workspace)
