"""State store for Assistant runtime singletons and execution records."""

from datetime import datetime
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional
import uuid

from .models import AgentExecution, ExecutionStatus
from .workspace import Workspace


class AssistantStateStore:
    """
    Thread-safe in-memory runtime state for assistant system.

    There is one global workspace shared by all agents and an in-memory
    map of execution records.
    """

    def __init__(self, runtime_base_path: Optional[Path] = None):
        """
        Initialize assistant runtime state store.

        Args:
            runtime_base_path: Base path to Runtime directory (project root).
                If None, tries to find project root automatically.
        """
        if runtime_base_path is None:
            # dynamic-task-stack/src/assistant/state_store.py -> FrameWorkers/
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent.parent
            runtime_base_path = project_root / "_workspaces"

        self.runtime_base_path = Path(runtime_base_path)
        self.runtime_base_path.mkdir(parents=True, exist_ok=True)

        self.executions: Dict[str, AgentExecution] = {}
        self.global_workspace: Optional[Workspace] = None
        self.execution_counter = 0
        self.lock = RLock()

    def create_execution(
        self,
        agent_id: str,
        step_id: str,
        inputs: Dict[str, Any],
    ) -> AgentExecution:
        """Create a new execution record."""
        with self.lock:
            self.execution_counter += 1
            execution_id = f"exec_{self.execution_counter}_{uuid.uuid4().hex[:8]}"

            execution = AgentExecution(
                id=execution_id,
                agent_id=agent_id,
                step_id=step_id,
                status=ExecutionStatus.PENDING,
                inputs=inputs,
                created_at=datetime.now(),
            )
            self.executions[execution_id] = execution
            return execution

    def get_executions_by_step(self, step_id: str) -> List[AgentExecution]:
        """Get all executions for a task."""
        with self.lock:
            return [
                execution
                for execution in self.executions.values()
                if execution.step_id == step_id
            ]

    def get_execution(self, execution_id: str) -> Optional[AgentExecution]:
        """Return a single execution by id, or None."""
        with self.lock:
            return self.executions.get(execution_id)

    def update_execution(self, execution: AgentExecution) -> bool:
        """Update an execution record."""
        with self.lock:
            if execution.id not in self.executions:
                return False
            self.executions[execution.id] = execution
            return True

    def create_global_workspace(self) -> Workspace:
        """Create the global workspace shared by all agents."""
        with self.lock:
            if self.global_workspace is not None:
                return self.global_workspace

            workspace_id = "workspace_global_" + datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )
            workspace = Workspace(
                workspace_id=workspace_id,
                runtime_base_path=self.runtime_base_path,
            )
            self.global_workspace = workspace
            return workspace

    def get_global_workspace(self) -> Optional[Workspace]:
        """Get the global workspace shared by all agents."""
        with self.lock:
            return self.global_workspace


# Preferred singleton name.
assistant_state_store = AssistantStateStore()
