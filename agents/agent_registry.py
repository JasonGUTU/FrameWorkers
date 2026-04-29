"""Agent registry for descriptor-driven pipeline agents."""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Descriptor-first registry (single model: pipeline agents)."""

    def __init__(self):
        self._descriptors: Dict[str, Any] = {}

    def get_all_agents_info(self) -> List[Dict[str, Any]]:
        """Return per-agent info dicts for the prompt + introspection.

        Schema after 2026-04 cleanup: ``{id, name, description}``. The old
        ``agent_type`` and ``capabilities`` fields were dropped because every
        agent always carried the same constant value (``"pipeline"`` /
        ``["pipeline_agent"]``) so they provided zero routing signal and
        ~600 bytes of dead text per full catalog prompt.
        """
        infos: List[Dict[str, Any]] = []
        for agent_id, descriptor in self._descriptors.items():
            infos.append({
                "id": agent_id,
                "name": agent_id,
                "description": descriptor.catalog_entry or "",
            })

        return infos

    def gather_agents_info(self) -> Dict[str, Any]:
        agents_info = self.get_all_agents_info()
        return {
            "total_agents": len(agents_info),
            "agents": agents_info,
            "agent_ids": [info["id"] for info in agents_info],
        }

    def register_pipeline_agents(self, descriptors: Dict[str, Any]) -> None:
        """Register descriptors from AGENT_REGISTRY."""
        for name, desc in descriptors.items():
            if name in self._descriptors:
                logger.debug("Pipeline agent %s already registered, skipping", name)
                continue
            self._descriptors[name] = desc
            logger.info("Registered pipeline agent: %s", name)

    def get_descriptor(self, agent_id: str) -> Optional[Any]:
        """Return the ``SubAgentDescriptor`` for a pipeline agent, or None."""
        return self._descriptors.get(agent_id)

    def reload(self) -> None:
        self._descriptors.clear()


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

            _registry.register_pipeline_agents(AGENT_REGISTRY)
        except ImportError:
            logger.debug("AGENT_REGISTRY not available; pipeline agents skipped")
    return _registry
