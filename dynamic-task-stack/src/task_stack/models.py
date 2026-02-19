# Data models for Frameworks Backend

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid


class TaskStatus(Enum):
    """Task status enumeration"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ReadingStatus(Enum):
    """Reading status for messages"""
    UNREAD = "UNREAD"
    READ = "READ"


@dataclass
class UserMessage:
    """User Message structure"""
    id: str
    content: str
    timestamp: datetime
    user_id: str
    worker_read_status: ReadingStatus
    user_read_status: ReadingStatus
    task_id: Optional[str] = None  # Associated task ID if any


@dataclass
class Task:
    """Task structure"""
    id: str
    description: Dict[str, Any]  # Contains: overall_description, input, requirements, additional_notes
    status: TaskStatus
    progress: Dict[str, Any]  # Collection of messages
    results: Optional[Dict[str, Any]] = None  # Task results
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class TaskStackEntry:
    """Task Stack entry - represents a task in a layer"""
    task_id: str
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class TaskLayer:
    """Task Layer - contains multiple tasks and hooks"""
    layer_index: int  # Layer number (0-based)
    tasks: List[TaskStackEntry]  # Tasks in this layer
    pre_hook: Optional[Dict[str, Any]] = None  # Hook before layer execution
    post_hook: Optional[Dict[str, Any]] = None  # Hook after layer execution
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ExecutionPointer:
    """Execution pointer - tracks current execution position"""
    current_layer_index: int  # Current layer being executed
    current_task_index: int  # Current task index within the layer
    is_executing_pre_hook: bool = False  # Whether currently executing pre-hook
    is_executing_post_hook: bool = False  # Whether currently executing post-hook


# Request/Response DTOs
@dataclass
class CreateUserMessageRequest:
    content: str
    user_id: str


@dataclass
class CreateTaskRequest:
    description: Dict[str, Any]


@dataclass
class UpdateTaskRequest:
    description: Optional[Dict[str, Any]] = None
    status: Optional[TaskStatus] = None
    progress: Optional[Dict[str, Any]] = None
    results: Optional[Dict[str, Any]] = None


@dataclass
class UpdateMessageReadStatusRequest:
    worker_read_status: Optional[ReadingStatus] = None
    user_read_status: Optional[ReadingStatus] = None


# Batch operation models
class BatchOperationType(Enum):
    """Batch operation types"""
    CREATE_TASKS = "create_tasks"
    CREATE_LAYERS = "create_layers"
    ADD_TASKS_TO_LAYERS = "add_tasks_to_layers"
    REMOVE_TASKS_FROM_LAYERS = "remove_tasks_from_layers"
    REPLACE_TASKS_IN_LAYERS = "replace_tasks_in_layers"
    UPDATE_LAYER_HOOKS = "update_layer_hooks"


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


@dataclass
class BatchOperationsRequest:
    """
    Request for batch operations
    
    Contains a list of operations to execute atomically.
    All operations are executed within a single lock, ensuring atomicity.
    """
    operations: List[BatchOperation]
