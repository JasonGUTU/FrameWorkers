# Agent Core Framework Module
# This module provides the core infrastructure for agents:
# - BaseAgent: Abstract base class for all agents
# - AgentRegistry: Discovers and manages agents from the root-level agents/ directory

from .base_agent import BaseAgent
from .agent_registry import AgentRegistry, get_agent_registry

__all__ = ['BaseAgent', 'AgentRegistry', 'get_agent_registry']
