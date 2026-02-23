# Sync Adapter — bridges async pipeline agents into service.py's synchronous world.
#
# Contains:
#   AgentMetadata        — agent identity / capabilities / schemas
#   BaseAgent            — sync ABC; agents implement execute(Dict) -> Dict
#   PipelineAgentAdapter — wraps a SubAgentDescriptor-based async agent
#                          so service.py can call execute(inputs)

from __future__ import annotations

import asyncio
import logging
import os
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .descriptor import SubAgentDescriptor
    from .llm_client import LLMClient

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Agent metadata
# ---------------------------------------------------------------------------

@dataclass
class AgentMetadata:
    """Metadata describing an agent's identity, capabilities, and schemas."""

    id: str
    name: str
    description: str
    version: str = "1.0.0"
    author: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


# ---------------------------------------------------------------------------
# Base agent
# ---------------------------------------------------------------------------

class BaseAgent(ABC):
    """Abstract base class for all agents in dynamic-task-stack.

    Agents implement ``get_metadata()`` and ``execute()``.
    ``service.py`` calls ``execute(inputs)`` to run the agent.
    """

    def __init__(self):
        self.metadata = self.get_metadata()

    # ------------------------------------------------------------------
    # Abstract interface
    # ------------------------------------------------------------------

    @abstractmethod
    def get_metadata(self) -> AgentMetadata:
        """Return agent metadata."""
        ...

    @abstractmethod
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent with given inputs and return results dict."""
        ...

    # ------------------------------------------------------------------
    # Convenience methods (called by service.py / routes.py)
    # ------------------------------------------------------------------

    def get_input_schema(self) -> Dict[str, Any]:
        return self.metadata.input_schema

    def get_output_schema(self) -> Dict[str, Any]:
        return self.metadata.output_schema

    def get_capabilities(self) -> List[str]:
        return self.metadata.capabilities

    def get_info(self) -> Dict[str, Any]:
        return {
            "id": self.metadata.id,
            "name": self.metadata.name,
            "description": self.metadata.description,
            "version": self.metadata.version,
            "author": self.metadata.author,
            "capabilities": self.metadata.capabilities,
            "input_schema": self.metadata.input_schema,
            "output_schema": self.metadata.output_schema,
            "created_at": self.metadata.created_at.isoformat(),
            "updated_at": self.metadata.updated_at.isoformat(),
        }


# ---------------------------------------------------------------------------
# Pipeline agent adapter — wraps async SubAgentDescriptor agents for service.py
# ---------------------------------------------------------------------------

class _AttrDict:
    """Dict wrapper with attribute access and pipeline config defaults.

    ``service.py`` passes ``config`` as a plain dict (or ``None``), but
    pipeline agents' ``build_input()`` may access ``config.language`` or
    ``config.target_total_duration_sec`` via attribute syntax.  This
    wrapper provides safe attribute access with sensible defaults.
    """

    _DEFAULTS: Dict[str, Any] = {
        "target_total_duration_sec": 60,
        "language": "en",
    }

    def __init__(self, data: Dict[str, Any] | None = None):
        self._data = {**self._DEFAULTS, **(data or {})}

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(name)
        try:
            return self._data[name]
        except KeyError:
            raise AttributeError(name) from None


class PipelineAgentAdapter(BaseAgent):
    """Sync wrapper that exposes an async pipeline agent via the BaseAgent API.

    ``service.py`` calls ``execute(inputs)`` on every agent uniformly.
    This adapter bridges that contract to the async
    ``SubAgentDescriptor.build_equipped_agent(llm).run(typed_input)``
    pipeline.

    ``_map_inputs()`` translates both service.py keys (``task_id``,
    ``task_description``, ``workspace_context``) and pipeline-native keys
    (``project_id``, ``draft_id``, ``assets``, ``config``).

    Construction requires an ``LLMClient``; if none is provided the
    adapter is **discovery-only** (shows up in listings but ``execute()``
    raises).
    """

    def __init__(
        self,
        descriptor: SubAgentDescriptor,
        llm_client: LLMClient | None = None,
    ):
        self._descriptor = descriptor
        self._llm_client = llm_client
        super().__init__()

    def get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            id=self._descriptor.agent_name,
            name=self._descriptor.agent_name,
            description=self._descriptor.catalog_entry[:200] if self._descriptor.catalog_entry else "",
            capabilities=["pipeline_agent", self._descriptor.asset_key],
        )

    # -- Input mapping (service.py dict → pipeline agent keys) ---------------

    def _map_inputs(self, inputs: Dict[str, Any]) -> tuple:
        """Map service.py's ``package_data()`` keys to pipeline agent keys.

        Handles both formats:
          - Pipeline format: ``project_id``, ``draft_id``, ``assets``, ``config``
          - service.py format: ``task_id``, ``task_description``,
            ``workspace_context``, ``workspace_files``, ``workspace_memory``

        Returns:
            ``(project_id, draft_id, assets, config)`` tuple ready for
            ``descriptor.build_input()``.
        """
        project_id = inputs.get("project_id") or inputs.get("task_id", "")
        draft_id = inputs.get("draft_id") or inputs.get("task_id", "")

        if "assets" in inputs:
            assets = inputs["assets"]
        else:
            assets: Dict[str, Any] = {}
            task_desc = inputs.get("task_description", "")
            if task_desc:
                assets["draft_idea"] = task_desc
                assets["source_text"] = task_desc
            ctx = inputs.get("workspace_context")
            if isinstance(ctx, dict):
                assets.update(ctx)

        raw_config = inputs.get("config")
        if raw_config is None or isinstance(raw_config, dict):
            config = _AttrDict(raw_config)
        else:
            config = raw_config

        return project_id, draft_id, assets, config

    # -- Sync execute -------------------------------------------------------

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Run the pipeline agent synchronously and return its output dict.

        Accepts both pipeline-native keys (``project_id``, ``assets``) and
        service.py keys (``task_id``, ``task_description``).

        For media agents (keyframe / video / audio) a ``MaterializeContext``
        is built automatically so binary assets are generated and saved to a
        temp directory.  The returned dict uses ``asset_dict`` (with URIs
        written in-place) when materialization occurred.
        """
        if self._llm_client is None:
            raise RuntimeError(
                f"PipelineAgentAdapter({self._descriptor.agent_name}) has no "
                f"LLMClient — cannot execute.  Provide one at construction."
            )

        agent = self._descriptor.build_equipped_agent(self._llm_client)
        project_id, draft_id, assets, config = self._map_inputs(inputs)
        typed_input = self._descriptor.build_input(
            project_id, draft_id, assets, config,
        )

        upstream = self._descriptor.build_upstream(assets)

        materialize_ctx = None
        if agent.materializer is not None:
            from .base_agent import MaterializeContext

            output_dir = tempfile.mkdtemp(prefix="fw_media_")

            def _persist(media_asset):
                path = os.path.join(
                    output_dir,
                    f"{media_asset.sys_id}.{media_asset.extension}",
                )
                with open(path, "wb") as fh:
                    fh.write(media_asset.data)
                return path

            materialize_ctx = MaterializeContext(
                project_id=project_id,
                assets=assets,
                persist_binary=_persist,
            )

        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(
                agent.run(
                    typed_input,
                    upstream=upstream,
                    materialize_ctx=materialize_ctx,
                )
            )
        finally:
            loop.close()

        if result.asset_dict is not None:
            output = result.asset_dict
        elif result.output is not None:
            output = result.output.model_dump() if hasattr(result.output, "model_dump") else dict(result.output)
        else:
            output = {}

        if result.media_assets:
            output["_media_files"] = self._collect_media_files(result.media_assets)

        if materialize_ctx is not None:
            import shutil
            shutil.rmtree(output_dir, ignore_errors=True)

        return output

    # -- Media file collection for service.py process_results() -------------

    @staticmethod
    def _collect_media_files(media_assets: list) -> Dict[str, Any]:
        """Read materialized temp files into ``file_content`` dicts.

        ``service.py``'s ``process_results()`` scans top-level result keys
        for ``{'file_content': bytes, ...}`` values and stores them in the
        workspace.  This method packages each ``MediaAsset``'s temp file
        into that format.

        Returns a dict keyed by ``sys_id`` so ``process_results()`` can
        iterate and store each one.
        """
        files: Dict[str, Any] = {}
        for asset in media_assets:
            uri = asset.uri_holder.get("uri", "")
            if not uri or not os.path.isfile(uri):
                continue
            with open(uri, "rb") as fh:
                data = fh.read()
            files[asset.sys_id] = {
                "file_content": data,
                "filename": f"{asset.sys_id}.{asset.extension}",
                "description": f"Media asset {asset.sys_id}",
            }
        return files
