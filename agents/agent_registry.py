"""Agent registry for descriptor-driven pipeline agents."""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Descriptor-first registry (single model: pipeline agents)."""

    def __init__(self):
        self._descriptors: Dict[str, Any] = {}
        self._pipeline_llm_client: Optional[Any] = None
    
    def get_agent(self, agent_id: str) -> Optional[Any]:
        """Compatibility helper.
        
        Returns an equipped async pipeline agent if an LLM client is available.
        New code should prefer ``get_descriptor()``.
        """
        descriptor = self._descriptors.get(agent_id)
        if descriptor is None:
            return None
        if self._pipeline_llm_client is None:
            return None
        return descriptor.build_equipped_agent(self._pipeline_llm_client)

    def list_agents(self) -> List[str]:
        return sorted(self._descriptors.keys())

    def get_all_agents_info(self) -> List[Dict[str, Any]]:
        infos: List[Dict[str, Any]] = []
        for agent_id, descriptor in self._descriptors.items():
            infos.append({
                "id": agent_id,
                "name": agent_id,
                "description": (descriptor.catalog_entry or "")[:200],
                "version": "1.0.0",
                "author": None,
                "agent_type": "pipeline",
                "capabilities": ["pipeline_agent", descriptor.asset_key],
                "asset_key": descriptor.asset_key,
                "asset_type": getattr(descriptor, "asset_type", ""),
                "schemas": {
                    "input": {},
                    "output": {},
                },
                "input_schema": {},
                "output_schema": {},
                "contract": {
                    "version": "2",
                    "deprecated_fields": ["input_schema", "output_schema"],
                },
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

    def register_pipeline_agents(
        self,
        descriptors: Dict[str, Any],
        llm_client: Optional[Any] = None,
    ):
        """Register descriptors from AGENT_REGISTRY."""
        self._pipeline_llm_client = llm_client
        for name, desc in descriptors.items():
            if name in self._descriptors:
                logger.debug("Pipeline agent %s already registered, skipping", name)
                continue
            self._descriptors[name] = desc
            logger.info("Registered pipeline agent: %s", name)

    def get_descriptor(self, agent_id: str) -> Optional[Any]:
        """Return the ``SubAgentDescriptor`` for a pipeline agent, or None."""
        return self._descriptors.get(agent_id)

    def is_pipeline_agent(self, agent_id: str) -> bool:
        """Check whether an agent is an async pipeline agent."""
        return agent_id in self._descriptors

    def reload(self):
        self._descriptors.clear()
        self._pipeline_llm_client = None


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
            from inference.runtime.base_client import LLMClient
            _registry.register_pipeline_agents(AGENT_REGISTRY, llm_client=LLMClient())
        except ImportError:
            logger.debug("AGENT_REGISTRY not available; pipeline agents skipped")
    return _registry
