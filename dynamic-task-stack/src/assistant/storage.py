# Storage for Assistant System

from threading import Lock
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from .models import (
    Assistant, Agent, AgentExecution,
    ExecutionStatus
)
from .workspace import Workspace
from pathlib import Path


class AssistantStorage:
    """
    Thread-safe in-memory storage for assistant system
    
    There is only one global assistant instance and one global workspace shared by all agents.
    """
    
    def __init__(self, runtime_base_path: Optional[Path] = None):
        """
        Initialize assistant storage
        
        Args:
            runtime_base_path: Base path to Runtime directory (project root)
                              If None, tries to find project root automatically
        """
        # Determine runtime base path
        if runtime_base_path is None:
            # Try to find project root: dynamic-task-stack/src/assistant -> FrameWorkers/
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent.parent.parent
            runtime_base_path = project_root / "Runtime"
        
        self.runtime_base_path = Path(runtime_base_path)
        self.runtime_base_path.mkdir(parents=True, exist_ok=True)
        
        # Global assistant instance (singleton)
        self.global_assistant: Optional[Assistant] = None
        
        # Execution records
        self.executions: Dict[str, AgentExecution] = {}
        self.global_workspace: Optional[Workspace] = None  # Single global workspace
        self.execution_counter = 0
        self.lock = Lock()
    
    # Global Assistant operations (singleton)
    def get_global_assistant(self) -> Assistant:
        """
        Get or create the global assistant instance (singleton)
        
        Returns:
            The global assistant instance
        """
        with self.lock:
            if self.global_assistant is None:
                # Create global assistant if it doesn't exist
                self.global_assistant = Assistant(
                    id="assistant_global",
                    name="Global Assistant",
                    description="Global assistant instance that manages all sub-agents and workspace interactions",
                    agent_ids=[],  # Will be populated from registry
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
            return self.global_assistant
    
    def update_global_assistant(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        agent_ids: Optional[List[str]] = None
    ) -> Assistant:
        """
        Update the global assistant instance
        
        Args:
            name: Optional new name
            description: Optional new description
            agent_ids: Optional new list of agent IDs
            
        Returns:
            Updated global assistant instance
        """
        with self.lock:
            assistant = self.get_global_assistant()
            
            updated_assistant = Assistant(
                id=assistant.id,
                name=name if name is not None else assistant.name,
                description=description if description is not None else assistant.description,
                agent_ids=agent_ids if agent_ids is not None else assistant.agent_ids,
                created_at=assistant.created_at,
                updated_at=datetime.now()
            )
            self.global_assistant = updated_assistant
            return updated_assistant
    
    def add_agent_to_global_assistant(self, agent_id: str) -> bool:
        """
        Add an agent to the global assistant
        
        Args:
            agent_id: ID of the agent to add
            
        Returns:
            True if added successfully
        """
        with self.lock:
            assistant = self.get_global_assistant()
            
            if agent_id not in assistant.agent_ids:
                assistant.agent_ids.append(agent_id)
                assistant.updated_at = datetime.now()
                self.global_assistant = assistant
            
            return True
    
    # Execution operations
    def create_execution(
        self,
        agent_id: str,
        task_id: str,
        inputs: Dict[str, Any],
        assistant_id: Optional[str] = None
    ) -> AgentExecution:
        """
        Create a new execution record
        
        Args:
            agent_id: ID of the agent to execute
            task_id: ID of the task
            inputs: Input data for the agent
            assistant_id: Optional assistant ID (uses global assistant if None)
            
        Returns:
            AgentExecution instance
        """
        with self.lock:
            # Use global assistant if assistant_id not provided
            if assistant_id is None:
                assistant = self.get_global_assistant()
                assistant_id = assistant.id
            
            self.execution_counter += 1
            execution_id = f"exec_{self.execution_counter}_{uuid.uuid4().hex[:8]}"
            
            execution = AgentExecution(
                id=execution_id,
                assistant_id=assistant_id,
                agent_id=agent_id,
                task_id=task_id,
                status=ExecutionStatus.PENDING,
                inputs=inputs,
                created_at=datetime.now()
            )
            self.executions[execution_id] = execution
            return execution
    
    def get_execution(self, execution_id: str) -> Optional[AgentExecution]:
        """Get an execution by ID"""
        with self.lock:
            return self.executions.get(execution_id)
    
    def get_executions_by_task(self, task_id: str) -> List[AgentExecution]:
        """Get all executions for a task"""
        with self.lock:
            return [
                exec for exec in self.executions.values()
                if exec.task_id == task_id
            ]
    
    def update_execution(self, execution: AgentExecution) -> bool:
        """Update an execution record"""
        with self.lock:
            if execution.id not in self.executions:
                return False
            self.executions[execution.id] = execution
            return True
    
    # Global Workspace operations
    def create_global_workspace(self) -> Workspace:
        """
        Create the global workspace shared by all agents
        
        Returns:
            The global workspace instance
        """
        with self.lock:
            if self.global_workspace is not None:
                return self.global_workspace
            
            workspace_id = f"workspace_global_{uuid.uuid4().hex[:8]}"
            
            # Create Workspace instance with file system support
            workspace = Workspace(
                workspace_id=workspace_id,
                runtime_base_path=self.runtime_base_path
            )
            self.global_workspace = workspace
            return workspace
    
    def get_global_workspace(self) -> Optional[Workspace]:
        """
        Get the global workspace shared by all agents
        
        Returns:
            The global workspace instance or None if not created
        """
        with self.lock:
            return self.global_workspace
    
    def update_workspace(self, workspace: Workspace) -> bool:
        """
        Update the global workspace reference
        
        Args:
            workspace: Workspace instance to update
        
        Returns:
            True if updated successfully, False otherwise
        """
        with self.lock:
            if self.global_workspace is None or workspace.id != self.global_workspace.id:
                return False
            # Workspace updates itself internally, we just update the reference
            self.global_workspace = workspace
            return True


# Global storage instance
assistant_storage = AssistantStorage()
