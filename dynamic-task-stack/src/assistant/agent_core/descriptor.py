"""SubAgentDescriptor — self-describing manifest for pluggable sub-agents.

Each sub-agent package exports a ``DESCRIPTOR`` instance so the orchestration
layer can discover and invoke agents **generically**, without hardcoding any
agent-specific logic.  Think of it as an LLM tool definition: name,
description, input builder, dependencies, and execution hooks.

Adding a new agent = create a sub-package with a ``DESCRIPTOR`` and register
it in ``src.sub_agent.__init__``.  Zero edits to orchestration code.

This module also defines ``BaseMaterializer`` — the abstract base for
post-LLM media generation (images, video, audio).  Media-producing agents
include a ``materializer_factory`` in their descriptor; non-media agents
leave it as ``None``.

Materializers are **pure generators**: they call external services to
produce binary data and return a list of ``MediaAsset`` objects.  They
never perform file I/O — persistence is handled by the caller (Assistant
or ``BaseAgent.run()`` via ``MaterializeContext.persist_binary``).
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from .base_agent import BaseAgent
    from .base_evaluator import BaseEvaluator
    from .llm_client import LLMClient

logger = logging.getLogger(__name__)


def _default_build_upstream(assets: dict[str, Any]) -> dict[str, Any] | None:
    """Sentinel default — replaced by __post_init__ in SubAgentDescriptor."""
    return None


# ---------------------------------------------------------------------------
# MediaAsset — output of materialize(), persisted by Assistant
# ---------------------------------------------------------------------------

@dataclass
class MediaAsset:
    """A single binary asset produced by a materializer.

    Assistant iterates the list returned by ``materialize()``, saves
    each one via ``AssetManager.save_binary()``, and writes the resulting
    path into ``uri_holder["uri"]``.

    Attributes:
        sys_id:     System-generated asset ID, e.g. ``"img_char_001_global"``.
        data:       Raw binary content (image/video/audio bytes).
        extension:  File extension without dot, e.g. ``"png"``, ``"mp4"``.
        uri_holder: Reference to the nested dict in ``asset_dict`` where
                    the URI should be written after saving.
    """

    sys_id: str
    data: bytes
    extension: str
    uri_holder: dict[str, Any]


# ---------------------------------------------------------------------------
# BaseMaterializer — abstract post-LLM media generation
# ---------------------------------------------------------------------------

class BaseMaterializer(ABC):
    """Abstract base for post-LLM binary asset generation.

    Subclasses implement ``materialize()`` which is called by Assistant
    after an agent's LLM output passes the L1+L2 quality gate.

    Materializers are **pure generators** — they call external media
    services and return ``list[MediaAsset]``.  They never hold an
    ``AssetManager`` or perform file I/O.  Persistence is Assistant's
    sole responsibility.
    """

    @abstractmethod
    async def materialize(
        self,
        project_id: str,
        asset_dict: dict[str, Any],
        assets: dict[str, Any],
    ) -> list[MediaAsset]:
        """Generate binary assets and return them for persistence.

        The materializer sets ``uri_holder["asset_id"] = sys_id`` for each
        produced asset, but leaves ``uri_holder["uri"]`` unset — Assistant
        fills it after saving.

        Args:
            project_id: Current project identifier.
            asset_dict: The agent's output dict (``asset_id`` fields are
                written in-place; ``uri`` fields are left for Assistant).
            assets: Full in-memory asset cache (read-only context — e.g.
                ``assets["storyboard"]`` for style info, or
                ``assets["reference_images"]`` for user-provided images).

        Returns:
            List of ``MediaAsset`` objects to be persisted by Assistant.
        """
        ...


# ---------------------------------------------------------------------------
# SubAgentDescriptor — the pluggable manifest
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SubAgentDescriptor:
    """Self-describing manifest for a sub-agent package.

    Assistant and DirectorAgent read these descriptors from the
    ``AGENT_REGISTRY`` to discover agents dynamically.

    Attributes:
        agent_name:
            Unique agent identifier, e.g. ``"AudioAgent"``.  Used as the
            lookup key in the registry and in ``RoutingStep.agent_name``.
        asset_key:
            In-memory asset cache key, e.g. ``"audio"``.  The agent's
            output dict is stored at ``assets[asset_key]``.
        asset_type:
            Versioning key for ``AssetManager``, e.g. ``"audio_package"``.
        upstream_keys:
            List of ``asset_key`` values this agent reads from upstream.
            Used for dependency documentation and auto-generation of
            ``build_upstream``.
        catalog_entry:
            Human-readable text describing this agent's purpose, inputs,
            outputs, and dependencies.  Fed to DirectorAgent's planning
            and review LLM prompts so the LLM knows what tools it has.
            Typically defined as a module-level constant in each agent's
            ``descriptor.py`` for structural separation.
        agent_factory:
            ``(LLMClient) -> BaseAgent`` — creates an agent instance.
        evaluator_factory:
            ``() -> BaseEvaluator`` — creates an evaluator instance.
        build_input:
            ``(project_id, draft_id, assets, config) -> BaseModel`` —
            constructs the agent's typed input from the shared asset cache
            and pipeline config.
        build_upstream:
            ``(assets) -> dict | None`` — extracts the upstream context
            dict needed by the evaluator for cross-asset checks.
        service_factories:
            Mapping of ``service_key -> factory(ctx) -> service_instance``.
            ``ctx`` is a dict with at least ``{"llm_client": LLMClient}``.
            Services with the same key across descriptors are created once
            and shared (first descriptor to declare a key wins).
            Non-media agents leave this as an empty dict.
        materializer_factory:
            Optional ``(services_dict) -> BaseMaterializer``.
            ``None`` for agents with no binary output.
        user_text_key:
            Optional asset key for user-provided text that bypasses
            earlier agents (e.g. ``"user_story_outline"`` for StoryAgent,
            ``"user_screenplay"`` for ScreenplayAgent).  Empty string if
            the agent does not accept user text.
    """

    agent_name: str
    asset_key: str
    asset_type: str
    upstream_keys: list[str] = field(default_factory=list)
    catalog_entry: str = ""

    agent_factory: Callable[..., Any] = field(repr=False, default=lambda llm: None)
    evaluator_factory: Callable[..., Any] = field(repr=False, default=lambda: None)

    build_input: Callable[..., BaseModel] = field(
        repr=False,
        default=lambda project_id, draft_id, assets, config: None,
    )
    build_upstream: Callable[..., dict[str, Any] | None] = field(
        repr=False,
        default=_default_build_upstream,
    )

    service_factories: dict[str, Callable[..., Any]] = field(
        repr=False, default_factory=dict,
    )
    materializer_factory: Callable[..., BaseMaterializer] | None = field(
        repr=False, default=None,
    )
    user_text_key: str = ""

    def __post_init__(self) -> None:
        """Auto-generate ``build_upstream`` from ``upstream_keys`` if not
        explicitly provided.

        The auto-generated version returns
        ``{key: assets.get(key, {}) for key in upstream_keys}``.
        Agents that need a custom mapping (e.g. StoryAgent where
        ``draft_idea`` is a string, not a dict) provide their own
        ``build_upstream`` at construction time.
        """
        if self.build_upstream is _default_build_upstream and self.upstream_keys:
            keys = list(self.upstream_keys)
            object.__setattr__(
                self,
                "build_upstream",
                lambda assets: {k: assets.get(k, {}) for k in keys},
            )

    # ------------------------------------------------------------------
    # Fully-equipped agent factory
    # ------------------------------------------------------------------

    def build_equipped_agent(
        self,
        llm: LLMClient,
        services_override: dict[str, Any] | None = None,
    ) -> BaseAgent:
        """Create an agent with its evaluator and materializer wired in.

        This is the single entry point for constructing a ready-to-run
        agent.  The returned agent's ``run()`` method will use the
        injected evaluator for quality gate checks and the materializer
        for binary asset generation.

        Args:
            llm:               Shared LLM client instance.
            services_override: Optional dict mapping service keys to
                               pre-created service instances (e.g. for
                               testing with mock services).  Keys not
                               present fall back to the descriptor's
                               ``service_factories``.

        Returns:
            A ``BaseAgent`` subclass instance with ``evaluator`` and
            ``materializer`` attributes set.
        """
        agent = self.agent_factory(llm)
        agent.evaluator = self.evaluator_factory()

        if self.materializer_factory is not None:
            ctx: dict[str, Any] = {"llm_client": llm}
            services: dict[str, Any] = {}
            for svc_key, svc_factory in self.service_factories.items():
                if services_override and svc_key in services_override:
                    services[svc_key] = services_override[svc_key]
                else:
                    services[svc_key] = svc_factory(ctx)
            agent.materializer = self.materializer_factory(services)

        return agent
