# Assistant Service - Core business logic for agent orchestration

from typing import Dict, Any, Optional, List
from datetime import datetime

from .models import AgentExecution, ExecutionStatus
from .workspace import Workspace
from ..task_stack.storage import storage as task_storage  # Read-only access to task storage
from agents import get_agent_registry
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

    def _get_agent_or_raise(self, agent_id: str):
        """Resolve a sub-agent once and raise on missing IDs."""
        agent_instance = self.agent_registry.get_agent(agent_id)
        if agent_instance is None:
            raise ValueError(f"Agent {agent_id} not found in registry")
        return agent_instance
    
    def query_agent_inputs(self, agent_id: str, agent_instance=None) -> Dict[str, Any]:
        """
        Query the required input parameters for an agent
        
        Args:
            agent_id: ID of the agent to query
            
        Returns:
            Dictionary containing input schema and requirements
            
        Raises:
            ValueError: If agent not found
        """
        # Reuse the provided agent instance to avoid repeated registry lookups.
        if agent_instance is None:
            agent_instance = self._get_agent_or_raise(agent_id)
        
        return {
            "agent_id": agent_id,
            "agent_name": agent_instance.metadata.name,
            "input_schema": agent_instance.get_input_schema(),
            "output_schema": agent_instance.get_output_schema(),
            "capabilities": agent_instance.get_capabilities(),
            "description": agent_instance.metadata.description
        }
    
    def prepare_environment(self, task_id: str) -> Workspace:
        """
        Prepare workspace environment for agent execution
        
        Uses the global workspace shared by all agents.
        
        Args:
            task_id: ID of the task being executed
            
        Returns:
            Global workspace instance
        """
        # Use the global workspace (already initialized in __init__)
        return self.workspace
    
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

        latest: Dict[str, AgentExecution] = {}
        for execution in past_executions:
            if execution.status != ExecutionStatus.COMPLETED:
                continue
            if not execution.results:
                continue
            prev = latest.get(execution.agent_id)
            if prev is None or (execution.completed_at or execution.created_at) > (prev.completed_at or prev.created_at):
                latest[execution.agent_id] = execution

        for agent_id, execution in latest.items():
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
        agent_instance=None
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
        # Keep this validation explicit, but reuse the already-resolved agent.
        if agent_instance is None:
            agent_instance = self._get_agent_or_raise(agent_id)
        
        # Get task from task storage (read-only)
        task = task_storage.get_task(task_id)
        if task is None:
            raise ValueError(f"Task {task_id} not found")
        
        # Retrieve relevant context from workspace using the retriever
        # The assistant searches the workspace and distributes information to agents
        context = self.retriever.get_context_for_agent(
            agent_id=agent_id,
            task_id=task_id,
            context_keys=None  # Could be customized based on agent requirements
        )
        
        # Build pipeline assets from historical execution results
        assets = self._build_pipeline_assets(task_id, task.description)
        
        # Package data: combine task data with retrieved workspace context
        packaged_data = {
            "task_id": task_id,
            "task_description": task.description,
            "task_progress": task.progress,
            # Retrieved context from workspace (distributed by assistant)
            "workspace_context": context,
            # Direct workspace access mirrors retriever context and avoids duplicate reads.
            "workspace_files": context.get("files", []),
            "workspace_memory": context.get("memory", "")[:1000],  # First 1000 chars
            # Pipeline assets from previous agent executions
            "assets": assets,
        }
        
        return packaged_data
    
    def execute_agent(
        self,
        agent_id: str,
        task_id: str,
        inputs: Dict[str, Any],
        agent_instance=None
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
        
        if agent_instance is None:
            agent_instance = self._get_agent_or_raise(agent_id)
        
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
            
            # Execute the agent
            results = agent_instance.execute(inputs)
            
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
            operation_type='write',
            resource_type='execution',
            resource_id=execution.id,
            agent_id=execution.agent_id,
            task_id=execution.task_id,
            details={
                "status": execution.status.value,
                "error": execution.error,
                "has_results": execution.results is not None
            }
        )

    def _store_file_result(self, workspace: Workspace, execution: AgentExecution, key: str, value: Dict[str, Any]) -> None:
        workspace.store_file(
            file_content=value['file_content'],
            filename=value.get('filename', f'{key}.bin'),
            description=value.get('description', f'File from execution {execution.id}'),
            created_by=execution.agent_id,
            tags=[execution.agent_id, execution.task_id],
            metadata={'execution_id': execution.id}
        )

    def _store_execution_files(self, execution: AgentExecution, workspace: Workspace) -> None:
        if not execution.results or not isinstance(execution.results, dict):
            return

        # Store inline file-shaped outputs.
        for key, value in execution.results.items():
            if isinstance(value, dict) and 'file_content' in value:
                self._store_file_result(workspace, execution, key, value)

        # Store batched media outputs.
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
        
        # Return processed results
        return {
            "execution_id": execution.id,
            "status": execution.status.value,
            "results": execution.results,
            "error": execution.error,
            "workspace_id": workspace.id
        }

    def build_execution_inputs(
        self,
        agent_id: str,
        task_id: str,
        workspace: Workspace,
        additional_inputs: Optional[Dict[str, Any]] = None,
        agent_instance=None,
    ) -> Dict[str, Any]:
        """Boundary 1: build final execution inputs for a sub-agent."""
        packaged_data = self.package_data(
            agent_id=agent_id,
            task_id=task_id,
            workspace=workspace,
            agent_instance=agent_instance,
        )
        if additional_inputs:
            packaged_data.update(additional_inputs)
        return packaged_data

    def run_agent(
        self,
        agent_id: str,
        task_id: str,
        inputs: Dict[str, Any],
        agent_instance=None,
    ) -> AgentExecution:
        """Boundary 2: execute one sub-agent run."""
        return self.execute_agent(
            agent_id=agent_id,
            task_id=task_id,
            inputs=inputs,
            agent_instance=agent_instance,
        )

    def persist_execution_results(
        self,
        execution: AgentExecution,
        workspace: Workspace,
    ) -> Dict[str, Any]:
        """Boundary 3: persist/log execution outputs and return API payload."""
        return self.process_results(execution, workspace)
    
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
        # Resolve once and reuse in all downstream steps.
        agent_instance = self._get_agent_or_raise(agent_id)
        
        # Prepare environment
        workspace = self.prepare_environment(task_id)
        
        # 1) Build inputs
        inputs = self.build_execution_inputs(
            agent_id=agent_id,
            task_id=task_id,
            workspace=workspace,
            additional_inputs=additional_inputs,
            agent_instance=agent_instance,
        )
        
        # 2) Run agent
        execution = self.run_agent(
            agent_id=agent_id,
            task_id=task_id,
            inputs=inputs,
            agent_instance=agent_instance
        )
        
        # 3) Persist results
        return self.persist_execution_results(execution, workspace)
