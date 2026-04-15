"""In-memory runtime state container for Plan Stack (historical alias: "task stack")."""

from threading import Lock
from typing import Dict, List, Optional

from .models import UserMessage, PlanStep, PlanLayer, ExecutionPointer


class PlanStackStateStore:
    """Thread-safe state container (no business rules)."""

    def __init__(self) -> None:
        self.user_messages: Dict[str, UserMessage] = {}
        self.plan_steps: Dict[str, PlanStep] = {}
        self.plan_layers: List[PlanLayer] = []
        self.execution_pointer: Optional[ExecutionPointer] = None
        self.user_message_counter: int = 0
        self.plan_step_counter: int = 0
        self.lock = Lock()
