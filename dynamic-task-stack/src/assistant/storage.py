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
    
    There is only one global workspace shared by all agents.
    """
    
    def __init__(self):
        self.assistants: Dict[str, Assistant] = {}
        self.agents: Dict[str, Agent] = {}
        self.executions: Dict[str, AgentExecution] = {}
        self.global_workspace: Optional[Workspace] = None  # Single global workspace
        self.assistant_counter = 0
        self.agent_counter = 0
        self.execution_counter = 0
        self.lock = Lock()
    
    # Assistant operations
    def create_assistant(
        self,
        name: str,
        description: str,
        agent_ids: Optional[List[str]] = None
    ) -> Assistant:
        """Create a new assistant"""
        with self.lock:
            self.assistant_counter += 1
            assistant_id = f"assistant_{self.assistant_counter}_{uuid.uuid4().hex[:8]}"
            
            assistant = Assistant(
                id=assistant_id,
                name=name,
                description=description,
                agent_ids=agent_ids or [],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            self.assistants[assistant_id] = assistant
            return assistant
    
    def get_assistant(self, assistant_id: str) -> Optional[Assistant]:
        """Get an assistant by ID"""
        with self.lock:
            return self.assistants.get(assistant_id)
    
    def get_all_assistants(self) -> List[Assistant]:
        """Get all assistants"""
        with self.lock:
            return list(self.assistants.values())
    
    def update_assistant(
        self,
        assistant_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        agent_ids: Optional[List[str]] = None
    ) -> Optional[Assistant]:
        """Update an assistant"""
        with self.lock:
            assistant = self.assistants.get(assistant_id)
            if assistant is None:
                return None
            
            updated_assistant = Assistant(
                id=assistant.id,
                name=name if name is not None else assistant.name,
                description=description if description is not None else assistant.description,
                agent_ids=agent_ids if agent_ids is not None else assistant.agent_ids,
                created_at=assistant.created_at,
                updated_at=datetime.now()
            )
            self.assistants[assistant_id] = updated_assistant
            return updated_assistant
    
    def add_agent_to_assistant(self, assistant_id: str, agent_id: str) -> bool:
        """Add an agent to an assistant"""
        with self.lock:
            assistant = self.assistants.get(assistant_id)
            if assistant is None:
                return False
            
            if agent_id not in assistant.agent_ids:
                assistant.agent_ids.append(agent_id)
                assistant.updated_at = datetime.now()
                self.assistants[assistant_id] = assistant
            
            return True
    
    # Agent operations
    def create_agent(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        capabilities: List[str]
    ) -> Agent:
        """Create a new agent"""
        with self.lock:
            self.agent_counter += 1
            agent_id = f"agent_{self.agent_counter}_{uuid.uuid4().hex[:8]}"
            
            agent = Agent(
                id=agent_id,
                name=name,
                description=description,
                input_schema=input_schema,
                capabilities=capabilities,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            self.agents[agent_id] = agent
            return agent
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get an agent by ID"""
        with self.lock:
            return self.agents.get(agent_id)
    
    def get_all_agents(self) -> List[Agent]:
        """Get all agents"""
        with self.lock:
            return list(self.agents.values())
    
    def update_agent(
        self,
        agent_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        input_schema: Optional[Dict[str, Any]] = None,
        capabilities: Optional[List[str]] = None
    ) -> Optional[Agent]:
        """Update an agent"""
        with self.lock:
            agent = self.agents.get(agent_id)
            if agent is None:
                return None
            
            updated_agent = Agent(
                id=agent.id,
                name=name if name is not None else agent.name,
                description=description if description is not None else agent.description,
                input_schema=input_schema if input_schema is not None else agent.input_schema,
                capabilities=capabilities if capabilities is not None else agent.capabilities,
                created_at=agent.created_at,
                updated_at=datetime.now()
            )
            self.agents[agent_id] = updated_agent
            return updated_agent
    
    # Execution operations
    def create_execution(
        self,
        assistant_id: str,
        agent_id: str,
        task_id: str,
        inputs: Dict[str, Any]
    ) -> AgentExecution:
        """Create a new execution record"""
        with self.lock:
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
    
    # Legacy methods for backward compatibility (deprecated)
    def create_workspace(self, assistant_id: str) -> Workspace:
        """
        Legacy method - creates/returns global workspace
        
        Deprecated: Use create_global_workspace() instead
        """
        return self.create_global_workspace()
    
    def get_workspace_by_assistant(self, assistant_id: str) -> Optional[Workspace]:
        """
        Legacy method - returns global workspace
        
        Deprecated: Use get_global_workspace() instead
        """
        return self.get_global_workspace()


# Global storage instance
assistant_storage = AssistantStorage()
