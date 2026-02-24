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
from threading import Lock
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
            agents_dir = str(Path(__file__).resolve().parent)

        self.agents_dir = Path(agents_dir)
        self._agents: Dict[str, BaseAgent] = {}
        self._agent_classes: Dict[str, Type[BaseAgent]] = {}
        self._sync_factories: Dict[str, Type[BaseAgent]] = {}
        self._descriptors: Dict[str, Any] = {}
        self._pipeline_llm_client: Optional[Any] = None
        self._pipeline_init_lock = Lock()
        self._sync_init_lock = Lock()
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
                            # Lazy-load sync agent: register factory only.
                            self._sync_factories[agent_name] = obj
                            self._agent_classes[agent_name] = obj
                            return
                except ImportError as e:
                    logger.debug("Import attempt %s failed: %s", module_name, e)
                    continue

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        agent = self._agents.get(agent_id)
        if agent is not None:
            return agent

        # Lazy-init sync agents when requested.
        sync_cls = self._sync_factories.get(agent_id)
        if sync_cls is not None:
            with self._sync_init_lock:
                agent = self._agents.get(agent_id)
                if agent is not None:
                    return agent
                instance = sync_cls()
                resolved_id = instance.metadata.id
                self._agents[resolved_id] = instance
                self._agent_classes[resolved_id] = sync_cls
                if resolved_id != agent_id:
                    # Keep alias compatibility when directory name != metadata.id.
                    self._agents[agent_id] = instance
                    self._agent_classes[agent_id] = sync_cls
                return instance

        # Fallback: if caller requested metadata.id (not directory key),
        # resolve by progressively materializing remaining sync factories.
        if self._sync_factories:
            with self._sync_init_lock:
                agent = self._agents.get(agent_id)
                if agent is not None:
                    return agent
                for candidate_key, candidate_cls in list(self._sync_factories.items()):
                    if candidate_key in self._agents:
                        continue
                    instance = candidate_cls()
                    resolved_id = instance.metadata.id
                    self._agents[resolved_id] = instance
                    self._agent_classes[resolved_id] = candidate_cls
                    if resolved_id != candidate_key:
                        self._agents[candidate_key] = instance
                        self._agent_classes[candidate_key] = candidate_cls
                    if resolved_id == agent_id:
                        return instance

        descriptor = self._descriptors.get(agent_id)
        if descriptor is None:
            return None

        # Lazy-init pipeline adapters only when actually requested.
        with self._pipeline_init_lock:
            agent = self._agents.get(agent_id)
            if agent is not None:
                return agent
            adapter = PipelineAgentAdapter(descriptor, self._pipeline_llm_client)
            self._agents[agent_id] = adapter
            return adapter

    def get_agent_class(self, agent_id: str) -> Optional[Type[BaseAgent]]:
        return self._agent_classes.get(agent_id)

    def list_agents(self) -> List[str]:
        return sorted(
            set(self._agents.keys()) | set(self._descriptors.keys()) | set(self._sync_factories.keys())
        )

    def get_all_agents_info(self) -> List[Dict[str, Any]]:
        infos: List[Dict[str, Any]] = [agent.get_info() for agent in self._agents.values()]

        for agent_id in self._sync_factories.keys():
            if agent_id in self._agents:
                continue
            infos.append({
                "id": agent_id,
                "name": agent_id,
                "description": "Sync agent (lazy-loaded)",
                "version": "1.0.0",
                "author": None,
                "capabilities": [],
                "input_schema": {},
                "output_schema": {},
                "created_at": "",
                "updated_at": "",
            })

        for agent_id, descriptor in self._descriptors.items():
            if agent_id in self._agents:
                # Already instantiated; info is included above.
                continue
            infos.append({
                "id": agent_id,
                "name": agent_id,
                "description": (descriptor.catalog_entry or "")[:200],
                "version": "1.0.0",
                "author": None,
                "capabilities": ["pipeline_agent", descriptor.asset_key],
                "input_schema": {},
                "output_schema": {},
                "created_at": "",
                "updated_at": "",
            })

        return infos

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
                         created adapters can execute; otherwise they are
                         discovery-only (visible in listings, but
                         ``execute()`` raises). Adapters are lazily
                         instantiated on first ``get_agent()``.
        """
        self._pipeline_llm_client = llm_client
        for name, desc in descriptors.items():
            if name in self._descriptors or name in self._agents:
                logger.debug("Pipeline agent %s already registered, skipping", name)
                continue
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
        self._sync_factories.clear()
        self._descriptors.clear()
        self._pipeline_llm_client = None
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
