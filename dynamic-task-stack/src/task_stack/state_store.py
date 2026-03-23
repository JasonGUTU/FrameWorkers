"""In-memory runtime state container for Task Stack."""

from threading import Lock
from typing import Dict, List, Optional

from .models import UserMessage, Task, TaskLayer, ExecutionPointer


class TaskStackStateStore:
    """Thread-safe state container (no business rules)."""

    def __init__(self) -> None:
        self.user_messages: Dict[str, UserMessage] = {}
        self.tasks: Dict[str, Task] = {}
        self.task_layers: List[TaskLayer] = []
        self.execution_pointer: Optional[ExecutionPointer] = None
        self.user_message_counter: int = 0
        self.task_counter: int = 0
        self.lock = Lock()
