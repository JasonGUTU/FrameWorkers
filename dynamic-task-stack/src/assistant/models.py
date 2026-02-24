"""Data models for Assistant system boundaries.

This module defines only Assistant-domain state objects. It should not contain
retrieval/orchestration logic.
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List


class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "IDLE"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ExecutionStatus(Enum):
    """Execution status for agent execution"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class Agent:
    """Sub-agent that can be executed by assistant"""
    id: str
    name: str
    description: str
    input_schema: Dict[str, Any]  # Schema defining required inputs
    capabilities: List[str]  # List of capabilities this agent provides
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Assistant:
    """
    Global Assistant instance that manages all sub-agents
    
    There should be only one assistant instance that manages all sub-agents.
    All agents share a single workspace (file system).
    """
    id: str
    name: str
    description: str
    agent_ids: List[str]  # List of agent IDs managed by this assistant
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class AgentExecution:
    """Tracks an agent execution instance"""
    id: str
    assistant_id: str
    agent_id: str
    task_id: str
    status: ExecutionStatus
    inputs: Dict[str, Any]  # Inputs provided to the agent
    results: Optional[Dict[str, Any]] = None  # Results from agent execution
    error: Optional[str] = None  # Error message if execution failed
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)

