# Agent Registry — discovers and manages all installed agents
#
# Supports two agent types:
#   1. Sync agents (agents/ directory) — BaseAgent subclasses with execute()
#   2. Pipeline agents (AGENT_REGISTRY) — async agents wrapped via PipelineAgentAdapter

import os
import sys
import importlib
import inspect
import logging
from typing import Dict, List, Optional, Type, Any
from pathlib import Path

from .sync_adapter import BaseAgent, PipelineAgentAdapter

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Unified registry for sync agents and async pipeline agents.

    Sync agents are discovered from the root-level ``agents/`` directory.
    Pipeline agents are registered via ``register_pipeline_agents()`` from
    ``AGENT_REGISTRY`` (SubAgentDescriptor dict).

    Both types are accessible through the same ``get_agent()`` API —
    pipeline agents are wrapped in ``PipelineAgentAdapter`` so they
    expose the standard ``execute()`` interface.
    """

    def __init__(self, agents_dir: Optional[str] = None):
        if agents_dir is None:
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent.parent.parent
            root_agents_dir = project_root / "agents"

            if root_agents_dir.exists() and root_agents_dir.is_dir():
                agents_dir = str(root_agents_dir)
            else:
                raise ValueError("agents/ directory not found at project root")

        self.agents_dir = Path(agents_dir)
        self._agents: Dict[str, BaseAgent] = {}
        self._agent_classes: Dict[str, Type[BaseAgent]] = {}
        self._descriptors: Dict[str, Any] = {}
        self._discover_agents()

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def _discover_agents(self):
        """Discover all agents in the agents directory."""
        if not self.agents_dir.exists():
            return

        for item in self.agents_dir.iterdir():
            if not item.is_dir():
                continue
            if item.name.startswith("_") or item.name.startswith("."):
                continue
            try:
                self._load_agent_from_directory(item)
            except Exception as e:
                logger.warning("Failed to load agent from %s: %s", item.name, e)

    def _load_agent_from_directory(self, agent_dir: Path):
        agent_name = agent_dir.name

        module_paths = [
            (agent_dir / "agent.py", "agent"),
            (agent_dir / "__init__.py", "__init__"),
        ]

        for module_path, module_file in module_paths:
            if not module_path.exists():
                continue

            agent_parent = str(agent_dir.parent)
            if agent_parent not in sys.path:
                sys.path.insert(0, agent_parent)

            import_strategies = [
                f"agents.{agent_name}.{module_file}",
                f"agents.{agent_name}",
            ]

            for module_name in import_strategies:
                try:
                    project_root = str(self.agents_dir.parent)
                    if project_root not in sys.path:
                        sys.path.insert(0, project_root)

                    module = importlib.import_module(module_name)

                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if (
                            issubclass(obj, BaseAgent)
                            and obj is not BaseAgent
                            and obj.__module__ == module.__name__
                        ):
                            agent_instance = obj()
                            agent_id = agent_instance.metadata.id
                            self._agents[agent_id] = agent_instance
                            self._agent_classes[agent_id] = obj
                            return
                except ImportError as e:
                    logger.debug("Import attempt %s failed: %s", module_name, e)
                    continue

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        return self._agents.get(agent_id)

    def get_agent_class(self, agent_id: str) -> Optional[Type[BaseAgent]]:
        return self._agent_classes.get(agent_id)

    def list_agents(self) -> List[str]:
        return list(self._agents.keys())

    def get_all_agents_info(self) -> List[Dict[str, Any]]:
        return [agent.get_info() for agent in self._agents.values()]

    def gather_agents_info(self) -> Dict[str, Any]:
        agents_info = self.get_all_agents_info()
        all_capabilities: set[str] = set()
        for info in agents_info:
            all_capabilities.update(info.get("capabilities", []))
        return {
            "total_agents": len(agents_info),
            "agents": agents_info,
            "all_capabilities": sorted(all_capabilities),
            "agent_ids": [info["id"] for info in agents_info],
        }

    def register_agent(self, agent: BaseAgent):
        agent_id = agent.metadata.id
        self._agents[agent_id] = agent
        self._agent_classes[agent_id] = type(agent)

    # ------------------------------------------------------------------
    # Pipeline agent registration
    # ------------------------------------------------------------------

    def register_pipeline_agents(
        self,
        descriptors: Dict[str, Any],
        llm_client: Optional[Any] = None,
    ):
        """Register async pipeline agents from AGENT_REGISTRY descriptors.

        Each descriptor is wrapped in a ``PipelineAgentAdapter`` so it can
        be used through the standard ``get_agent()`` / ``execute()``
        interface.

        Args:
            descriptors: ``{agent_name: SubAgentDescriptor}`` dict.
            llm_client:  Optional ``LLMClient`` instance.  If provided,
                         adapters can execute; otherwise they are
                         discovery-only (visible in listings, but
                         ``execute()`` raises).
        """
        for name, desc in descriptors.items():
            if name in self._agents:
                logger.debug("Pipeline agent %s already registered, skipping", name)
                continue
            adapter = PipelineAgentAdapter(desc, llm_client)
            self._agents[name] = adapter
            self._agent_classes[name] = PipelineAgentAdapter
            self._descriptors[name] = desc
            logger.info("Registered pipeline agent: %s", name)

    def get_descriptor(self, agent_id: str) -> Optional[Any]:
        """Return the ``SubAgentDescriptor`` for a pipeline agent, or None."""
        return self._descriptors.get(agent_id)

    def is_pipeline_agent(self, agent_id: str) -> bool:
        """Check whether an agent is an async pipeline agent."""
        return agent_id in self._descriptors

    def reload(self):
        self._agents.clear()
        self._agent_classes.clear()
        self._descriptors.clear()
        self._discover_agents()


# Global registry singleton
_registry: Optional[AgentRegistry] = None


def get_agent_registry() -> AgentRegistry:
    """Return the global agent registry (singleton).

    Auto-registers pipeline agents from ``AGENT_REGISTRY`` on first call.
    """
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
        try:
            from . import AGENT_REGISTRY
            from .llm_client import LLMClient
            _registry.register_pipeline_agents(AGENT_REGISTRY, llm_client=LLMClient())
        except ImportError:
            logger.debug("AGENT_REGISTRY not available; pipeline agents skipped")
    return _registry
