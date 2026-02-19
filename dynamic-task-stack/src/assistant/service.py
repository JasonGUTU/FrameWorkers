# Assistant Service - Core business logic for agent orchestration

from typing import Dict, Any, Optional, List
from datetime import datetime

from .models import (
    Assistant, Agent, AgentExecution, Workspace,
    ExecutionStatus
)
from ..task_stack.storage import storage as task_storage  # Read-only access to task storage
from .agents import get_agent_registry


class AssistantService:
    """Service class for managing assistant operations"""
    
    def __init__(self, assistant_storage):
        """
        Initialize assistant service
        
        Args:
            assistant_storage: Storage instance for assistant data
        """
        self.storage = assistant_storage
        self.agent_registry = get_agent_registry()
    
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
        # Try to get from registry first (preferred)
        agent_instance = self.agent_registry.get_agent(agent_id)
        if agent_instance:
            return {
                "agent_id": agent_id,
                "agent_name": agent_instance.metadata.name,
                "input_schema": agent_instance.get_input_schema(),
                "output_schema": agent_instance.get_output_schema(),
                "capabilities": agent_instance.get_capabilities(),
                "description": agent_instance.metadata.description
            }
        
        # Fallback to storage (for backward compatibility)
        agent = self.storage.get_agent(agent_id)
        if agent is None:
            raise ValueError(f"Agent {agent_id} not found")
        
        return {
            "agent_id": agent_id,
            "agent_name": agent.name,
            "input_schema": agent.input_schema,
            "capabilities": agent.capabilities
        }
    
    def prepare_environment(self, assistant_id: str, task_id: str) -> Workspace:
        """
        Prepare workspace environment for agent execution
        
        Args:
            assistant_id: ID of the assistant
            task_id: ID of the task being executed
            
        Returns:
            Workspace instance (conceptual for now)
            
        Raises:
            ValueError: If assistant not found
        """
        assistant = self.storage.get_assistant(assistant_id)
        if assistant is None:
            raise ValueError(f"Assistant {assistant_id} not found")
        
        # Get or create workspace for this assistant
        workspace = self.storage.get_workspace_by_assistant(assistant_id)
        if workspace is None:
            workspace = self.storage.create_workspace(assistant_id)
        
        # For now, workspace is conceptual - actual implementation deferred
        # In future, this would:
        # - Load shared files
        # - Initialize shared memory
        # - Set up logging context
        # - Prepare asset directories
        
        return workspace
    
    def package_data(
        self,
        agent_id: str,
        task_id: str,
        workspace: Workspace
    ) -> Dict[str, Any]:
        """
        Package relevant resources for agent execution
        
        Args:
            agent_id: ID of the agent to execute
            task_id: ID of the task
            workspace: Workspace instance
            
        Returns:
            Dictionary containing packaged data for agent
            
        Raises:
            ValueError: If agent or task not found
        """
        agent = self.storage.get_agent(agent_id)
        if agent is None:
            raise ValueError(f"Agent {agent_id} not found")
        
        # Get task from task storage (read-only)
        task = task_storage.get_task(task_id)
        if task is None:
            raise ValueError(f"Task {task_id} not found")
        
        # Package data based on agent's input schema
        packaged_data = {
            "task_id": task_id,
            "task_description": task.description,
            "task_progress": task.progress,
            "workspace_files": workspace.shared_files,
            "workspace_memory": workspace.shared_memory,
            # Additional data can be added based on agent requirements
        }
        
        return packaged_data
    
    def execute_agent(
        self,
        assistant_id: str,
        agent_id: str,
        task_id: str,
        inputs: Dict[str, Any]
    ) -> AgentExecution:
        """
        Execute an agent and retrieve results
        
        Args:
            assistant_id: ID of the assistant
            agent_id: ID of the agent to execute
            task_id: ID of the task
            inputs: Input data for the agent
            
        Returns:
            AgentExecution instance with results
            
        Raises:
            ValueError: If agent, assistant, or task not found
        """
        # Validate agent exists and belongs to assistant
        assistant = self.storage.get_assistant(assistant_id)
        if assistant is None:
            raise ValueError(f"Assistant {assistant_id} not found")
        
        if agent_id not in assistant.agent_ids:
            raise ValueError(f"Agent {agent_id} is not managed by assistant {assistant_id}")
        
        agent = self.storage.get_agent(agent_id)
        if agent is None:
            raise ValueError(f"Agent {agent_id} not found")
        
        # Create execution record
        execution = self.storage.create_execution(
            assistant_id=assistant_id,
            agent_id=agent_id,
            task_id=task_id,
            inputs=inputs
        )
        
        try:
            # Get agent instance from registry
            agent_instance = self.agent_registry.get_agent(agent_id)
            
            if agent_instance is None:
                # Fallback: try to get from storage (for backward compatibility)
                # But prefer registry-based agents
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
        # Store results in workspace
        if execution.results:
            workspace.assets[f"execution_{execution.id}"] = execution.results
            workspace.updated_at = datetime.now()
            self.storage.update_workspace(workspace)
        
        # Log execution
        log_entry = {
            "execution_id": execution.id,
            "agent_id": execution.agent_id,
            "task_id": execution.task_id,
            "status": execution.status.value,
            "timestamp": datetime.now().isoformat(),
            "error": execution.error
        }
        workspace.logs.append(log_entry)
        self.storage.update_workspace(workspace)
        
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
        assistant_id: str,
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
            assistant_id: ID of the assistant
            agent_id: ID of the agent to execute
            task_id: ID of the task
            additional_inputs: Optional additional inputs to merge
            
        Returns:
            Dictionary containing execution results
        """
        # Step 1: Query agent inputs (for validation)
        input_info = self.query_agent_inputs(agent_id)
        
        # Step 2: Prepare environment
        workspace = self.prepare_environment(assistant_id, task_id)
        
        # Step 3: Package data
        packaged_data = self.package_data(agent_id, task_id, workspace)
        
        # Merge additional inputs if provided
        inputs = packaged_data.copy()
        if additional_inputs:
            inputs.update(additional_inputs)
        
        # Step 4: Execute agent
        execution = self.execute_agent(
            assistant_id=assistant_id,
            agent_id=agent_id,
            task_id=task_id,
            inputs=inputs
        )
        
        # Step 5: Process results
        results = self.process_results(execution, workspace)
        
        return results
