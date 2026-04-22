# Data models for the Plan Stack backend.
#
# One ``PlanStep`` corresponds to one planned agent execution (one-to-one with
# ``AgentExecution``).

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List


class PlanStepStatus(Enum):
    """Plan-step status enumeration (one step == one planned agent execution)."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ReadingStatus(Enum):
    """Reading status for messages"""
    UNREAD = "UNREAD"
    READ = "READ"


class MessageSenderType(Enum):
    """Message sender type"""
    DIRECTOR = "director"
    SUBAGENT = "subagent"
    USER = "user"


@dataclass
class UserMessage:
    """User Message structure"""
    id: str
    content: str
    timestamp: datetime
    sender_type: MessageSenderType  # Type of sender: director, subagent, user
    director_read_status: ReadingStatus
    user_read_status: ReadingStatus
    step_id: Optional[str] = None  # Associated plan-step id if any


@dataclass
class PlanStep:
    """
    A planned agent execution.

    One PlanStep <-> one AgentExecution. ``description`` captures the intent
    (what the agent should do); ``results`` is populated after execution.
    """
    id: str
    description: Dict[str, Any]
    status: PlanStepStatus
    progress: Dict[str, Any]  # Collection of messages
    results: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class PlanStepEntry:
    """Stack entry - a slot in a layer that points to one PlanStep by id."""
    step_id: str
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PlanLayer:
    """Plan layer - holds an ordered list of plan-step slots."""
    layer_index: int
    steps: List[PlanStepEntry]
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ExecutionPointer:
    """Execution pointer - tracks current execution position"""
    current_layer_index: int
    current_step_index: int


# Batch operation models
class BatchOperationType(Enum):
    """Batch operation types (HTTP API contract for ``POST /api/plan-stack/modify``)."""
    CREATE_STEPS = "create_steps"
    CREATE_LAYERS = "create_layers"
    ADD_STEPS_TO_LAYERS = "add_steps_to_layers"
    REMOVE_STEPS_FROM_LAYERS = "remove_steps_from_layers"


@dataclass
class BatchOperation:
    """
    Single operation in a batch transaction

    Each operation has:
    - type: Operation type (BatchOperationType)
    - params: Operation-specific parameters (Dict[str, Any])
    """
    type: BatchOperationType
    params: Dict[str, Any]
