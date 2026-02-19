# Agent Registry - Discovers and manages all installed agents

import os
import importlib
import inspect
from typing import Dict, List, Optional, Type, Any
from pathlib import Path

from .base_agent import BaseAgent, AgentMetadata


class AgentRegistry:
    """
    Registry for discovering and managing all installed agents
    
    Automatically scans the root-level agents/ directory and registers all agents
    that inherit from BaseAgent.
    """
    
    def __init__(self, agents_dir: Optional[str] = None):
        """
        Initialize the agent registry
        
        Args:
            agents_dir: Directory containing agent subdirectories.
                       If None, tries to find agents directory at project root
        """
        if agents_dir is None:
            # Try to find agents directory at project root
            current_file = Path(__file__)
            # Go up to project root: dynamic-task-stack/src/assistant/agent_core -> FrameWorkers/
            project_root = current_file.parent.parent.parent.parent.parent
            root_agents_dir = project_root / "agents"
            
            if root_agents_dir.exists() and root_agents_dir.is_dir():
                agents_dir = str(root_agents_dir)
            else:
                raise ValueError("agents/ directory not found at project root")
        
        self.agents_dir = Path(agents_dir)
        self._agents: Dict[str, BaseAgent] = {}
        self._agent_classes: Dict[str, Type[BaseAgent]] = {}
        self._discover_agents()
    
    def _discover_agents(self):
        """Discover all agents in the agents directory"""
        if not self.agents_dir.exists():
            return
        
        # Iterate through subdirectories
        for item in self.agents_dir.iterdir():
            if not item.is_dir():
                continue
            
            # Skip __pycache__ and hidden directories
            if item.name.startswith('_') or item.name.startswith('.'):
                continue
            
            # Try to import the agent
            try:
                self._load_agent_from_directory(item)
            except Exception as e:
                # Log error but continue discovering other agents
                print(f"Warning: Failed to load agent from {item.name}: {e}")
                continue
    
    def _load_agent_from_directory(self, agent_dir: Path):
        """
        Load an agent from a directory
        
        Args:
            agent_dir: Path to the agent directory
        """
        agent_name = agent_dir.name
        
        # Try to import the agent module
        # Expected structure: agent_dir/agent.py or agent_dir/__init__.py
        module_paths = [
            (agent_dir / "agent.py", "agent"),
            (agent_dir / "__init__.py", "__init__")
        ]
        
        for module_path, module_file in module_paths:
            if not module_path.exists():
                continue
            
            try:
                # Add agent directory to sys.path for imports
                import sys
                agent_parent = str(agent_dir.parent)
                if agent_parent not in sys.path:
                    sys.path.insert(0, agent_parent)
                
                # Import strategies for root-level agents directory
                import_strategies = [
                    f"agents.{agent_name}.{module_file}",
                    f"agents.{agent_name}",
                ]
                
                for module_name in import_strategies:
                    try:
                        # Add project root to path for root-level agents
                        import sys
                        project_root = str(self.agents_dir.parent)
                        if project_root not in sys.path:
                            sys.path.insert(0, project_root)
                        
                        module = importlib.import_module(module_name)
                        
                        # Find all classes that inherit from BaseAgent
                        for name, obj in inspect.getmembers(module, inspect.isclass):
                            if (issubclass(obj, BaseAgent) and 
                                obj != BaseAgent and 
                                obj.__module__ == module.__name__):
                                
                                # Instantiate the agent
                                agent_instance = obj()
                                agent_id = agent_instance.metadata.id
                                
                                # Register the agent
                                self._agents[agent_id] = agent_instance
                                self._agent_classes[agent_id] = obj
                                return  # Successfully loaded, exit
                    except ImportError as e:
                        # Debug: print import error for troubleshooting
                        print(f"Debug: Failed to import {module_name}: {e}")
                        continue
                
            except Exception as e:
                print(f"Warning: Failed to load agent from {agent_name}: {e}")
                import traceback
                traceback.print_exc()
                continue
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """
        Get an agent instance by ID
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            BaseAgent instance or None if not found
        """
        return self._agents.get(agent_id)
    
    def get_agent_class(self, agent_id: str) -> Optional[Type[BaseAgent]]:
        """
        Get an agent class by ID
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Agent class or None if not found
        """
        return self._agent_classes.get(agent_id)
    
    def list_agents(self) -> List[str]:
        """
        List all registered agent IDs
        
        Returns:
            List of agent IDs
        """
        return list(self._agents.keys())
    
    def get_all_agents_info(self) -> List[Dict[str, Any]]:
        """
        Get information about all registered agents
        
        Returns:
            List of agent information dictionaries
        """
        return [agent.get_info() for agent in self._agents.values()]
    
    def gather_agents_info(self) -> Dict[str, Any]:
        """
        Gather and aggregate information about all agents
        
        Returns:
            Dictionary containing aggregated agent information
        """
        agents_info = self.get_all_agents_info()
        
        # Aggregate capabilities
        all_capabilities = set()
        for agent_info in agents_info:
            all_capabilities.update(agent_info.get("capabilities", []))
        
        return {
            "total_agents": len(agents_info),
            "agents": agents_info,
            "all_capabilities": sorted(list(all_capabilities)),
            "agent_ids": [info["id"] for info in agents_info]
        }
    
    def register_agent(self, agent: BaseAgent):
        """
        Manually register an agent
        
        Args:
            agent: Agent instance to register
        """
        agent_id = agent.metadata.id
        self._agents[agent_id] = agent
        self._agent_classes[agent_id] = type(agent)
    
    def reload(self):
        """Reload all agents from the directory"""
        self._agents.clear()
        self._agent_classes.clear()
        self._discover_agents()


# Global registry instance
_registry: Optional[AgentRegistry] = None


def get_agent_registry() -> AgentRegistry:
    """
    Get the global agent registry instance
    
    Returns:
        AgentRegistry: Global registry instance
    """
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
    return _registry
