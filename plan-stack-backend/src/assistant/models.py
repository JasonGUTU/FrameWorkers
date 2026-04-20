"""Data models for Assistant system boundaries.

This module defines only Assistant-domain state objects. It should not contain
retrieval/orchestration logic.
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List


class ExecutionStatus(Enum):
    """Execution status for agent execution"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class AgentExecution:
    """Tracks an agent execution instance"""
    id: str
    agent_id: str
    step_id: str
    status: ExecutionStatus
    inputs: Dict[str, Any]  # Inputs provided to the agent
    results: Optional[Dict[str, Any]] = None  # Results from agent execution
    error: Optional[str] = None  # Error message if execution failed
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    # Absolute workspace paths InputResolver picked for this execution's
    # input labels. Populated by AssistantService.build_execution_inputs
    # so framework-level hooks (e.g. the raw_pending → global scope flip
    # for Intake* agents) can act on the inputs the agent consumed.
    resolved_input_paths: List[str] = field(default_factory=list)

