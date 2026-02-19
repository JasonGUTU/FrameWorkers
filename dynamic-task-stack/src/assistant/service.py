# Assistant Service - Core business logic for agent orchestration

from typing import Dict, Any, Optional, List
from datetime import datetime

from .models import (
    Assistant, Agent, AgentExecution,
    ExecutionStatus
)
from .workspace import Workspace
from ..task_stack.storage import storage as task_storage  # Read-only access to task storage
from .agent_core import get_agent_registry
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
        # Get agent from registry
        agent_instance = self.agent_registry.get_agent(agent_id)
        if agent_instance is None:
            raise ValueError(f"Agent {agent_id} not found in registry")
        
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
    
    def package_data(
        self,
        agent_id: str,
        task_id: str,
        workspace: Workspace
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
        # Get agent instance to understand its requirements
        agent_instance = self.agent_registry.get_agent(agent_id)
        if agent_instance is None:
            raise ValueError(f"Agent {agent_id} not found in registry")
        
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
        
        # Get recent files and memory for context
        recent_files = workspace.list_files(limit=10)
        memory_content = workspace.read_memory()
        
        # Package data: combine task data with retrieved workspace context
        packaged_data = {
            "task_id": task_id,
            "task_description": task.description,
            "task_progress": task.progress,
            # Retrieved context from workspace (distributed by assistant)
            "workspace_context": context,
            # Direct workspace access
            "workspace_files": [
                {
                    "id": f.id,
                    "filename": f.filename,
                    "description": f.description,
                    "file_type": f.file_type,
                    "file_path": f.file_path
                }
                for f in recent_files
            ],
            "workspace_memory": memory_content[:1000] if memory_content else "",  # First 1000 chars
            # Additional data can be added based on agent requirements
        }
        
        return packaged_data
    
    def execute_agent(
        self,
        agent_id: str,
        task_id: str,
        inputs: Dict[str, Any]
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
        # Get global assistant
        assistant = self.storage.get_global_assistant()
        
        # Validate agent exists in registry
        agent_instance = self.agent_registry.get_agent(agent_id)
        if agent_instance is None:
            raise ValueError(f"Agent {agent_id} not found in registry")
        
        # Create execution record
        execution = self.storage.create_execution(
            agent_id=agent_id,
            task_id=task_id,
            inputs=inputs
        )
        
        try:
            # Get agent instance from registry
            agent_instance = self.agent_registry.get_agent(agent_id)
            
            if agent_instance is None:
                raise ValueError(f"Agent {agent_id} not found in registry")
            
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
        # Log execution using workspace log manager
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
        
        # If results contain files, store them in workspace
        if execution.results:
            # Check if results contain file data to store
            if isinstance(execution.results, dict):
                # Look for file-like data in results
                for key, value in execution.results.items():
                    if isinstance(value, dict) and 'file_content' in value:
                        # Store file
                        workspace.store_file(
                            file_content=value['file_content'],
                            filename=value.get('filename', f'{key}.bin'),
                            description=value.get('description', f'File from execution {execution.id}'),
                            created_by=execution.agent_id,
                            tags=[execution.agent_id, execution.task_id],
                            metadata={'execution_id': execution.id}
                        )
        
        # Return processed results
        return {
            "execution_id": execution.id,
            "status": execution.status.value,
            "results": execution.results,
            "error": execution.error,
            "workspace_id": workspace.id
        }
    
    def execute_agent_for_task(
        self,
        agent_id: str,
        task_id: str,
        additional_inputs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete workflow: Execute an agent for a task
        
        This method orchestrates the full execution flow:
        1. Query agent inputs
        2. Prepare environment
        3. Package data
        4. Execute agent
        5. Process results
        
        Args:
            agent_id: ID of the agent to execute
            task_id: ID of the task
            additional_inputs: Optional additional inputs to merge
            
        Returns:
            Dictionary containing execution results
        """
        # Step 1: Query agent inputs (for validation)
        input_info = self.query_agent_inputs(agent_id)
        
        # Step 2: Prepare environment
        workspace = self.prepare_environment(task_id)
        
        # Step 3: Package data
        packaged_data = self.package_data(agent_id, task_id, workspace)
        
        # Merge additional inputs if provided
        inputs = packaged_data.copy()
        if additional_inputs:
            inputs.update(additional_inputs)
        
        # Step 4: Execute agent
        execution = self.execute_agent(
            agent_id=agent_id,
            task_id=task_id,
            inputs=inputs
        )
        
        # Step 5: Process results
        results = self.process_results(execution, workspace)
        
        return results
