"""SubAgentDescriptor — self-describing manifest for pluggable sub-agents.

Each sub-agent package exports a ``DESCRIPTOR`` instance so the orchestration
layer can discover and invoke agents **generically**, without hardcoding any
agent-specific logic.  Think of it as an LLM tool definition: name,
description, input builder, dependencies, and execution hooks.

Adding a new agent = create a sub-package with a ``DESCRIPTOR`` and register
it in ``agents/__init__.py`` (``AGENT_REGISTRY``).  Zero edits to orchestration code.

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
    from .base_agent import BaseAgent, MaterializeContext
    from .base_evaluator import BaseEvaluator
    from inference.clients import LLMClient

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# MediaAsset — output of materialize(), persisted by Assistant
# ---------------------------------------------------------------------------

@dataclass
class MediaAsset:
    """A single binary asset produced by a materializer.

    Assistant iterates the list returned by ``materialize()``, saves
    each one via ``ArtifactWriter`` (in the workspace layer), and writes
    the resulting path into ``uri_holder["uri"]``.

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
    ``ArtifactWriter`` or perform file I/O.  Persistence is Assistant's
    sole responsibility.

    Single-input contract: a materializer receives only the
    ``MaterializeContext`` (which carries ``typed_input``, ``step_id``,
    and the ``persist_binary`` callback) plus the ``asset_dict`` produced
    by the LLM pipeline.  It does NOT receive any second
    ``resolved_artifacts`` channel.  Whatever data the materializer
    needs must already be expressed as a field on the agent's typed
    input.
    """

    @abstractmethod
    async def materialize(
        self,
        ctx: "MaterializeContext",
        asset_dict: dict[str, Any],
    ) -> list[MediaAsset]:
        """Generate binary assets and return them for persistence.

        The materializer sets ``uri_holder["asset_id"] = sys_id`` for each
        produced asset, but leaves ``uri_holder["uri"]`` unset — Assistant
        fills it after saving.

        Args:
            ctx: ``MaterializeContext`` carrying ``step_id``,
                 ``typed_input`` (the same Pydantic input the LLM pipeline
                 received), and the ``persist_binary`` callback.
            asset_dict: The agent's LLM output dict (``asset_id`` fields are
                 written in-place; ``uri`` fields are left for Assistant).

        Returns:
            List of ``MediaAsset`` objects to be persisted by Assistant.
        """
        ...


# ---------------------------------------------------------------------------
# AgentSpec — single-source-of-truth for catalog_entry + input_needs_description
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class InputLabelSpec:
    """Declarative spec for one input slot.

    One per ``[label] (single|collection)`` block the agent exposes. Holds
    the single description string that the framework renders into BOTH:
      * ``catalog_entry``'s Input section (read by Director's planner LLM)
      * ``input_needs_description``'s ``[label]`` block (read by InputResolver LLM)

    Writing the description once here prevents the two LLM-facing views
    from drifting apart (the bug pattern where CATALOG claims "accepts X
    or Y" but input_needs_description only describes X, causing the
    planner to route Y → this agent while the resolver fails to match).
    """

    name: str
    cardinality: str  # "single" or "collection"
    description: str
    optional: bool = False


@dataclass(frozen=True)
class AgentSpec:
    """Single-source manifest. Renders catalog_entry + input_needs_description.

    Pass to ``SubAgentDescriptor.from_spec`` instead of hand-writing the
    two strings separately.
    """

    agent_id: str
    inputs: list[InputLabelSpec] = field(default_factory=list)
    output_description: str = ""
    purpose_and_routing: str = ""
    input_preamble: str = ""
    promotes_consumed_inputs_to_global: bool = False


def render_catalog_entry(spec: AgentSpec) -> str:
    """Planner-facing string. Lists each [label] with its description."""
    lines: list[str] = [spec.agent_id]
    lines.append("  - Inputs:")
    for inp in spec.inputs:
        req = "optional" if inp.optional else "required"
        lines.append(
            f"      [{inp.name}] ({inp.cardinality}, {req}): {inp.description}"
        )
    lines.append(f"  - Output: {spec.output_description}")
    lines.append(f"  - Purpose / routing: {spec.purpose_and_routing}")
    return "\n".join(lines)


def render_input_needs_description(spec: AgentSpec) -> str:
    """InputResolver-facing string. [label] blocks in the parseable format."""
    parts: list[str] = []
    if spec.input_preamble.strip():
        parts.append(spec.input_preamble.strip())
        parts.append("")
    for inp in spec.inputs:
        parts.append(f"[{inp.name}] ({inp.cardinality})")
        parts.append(inp.description)
        parts.append("")
    return "\n".join(parts).rstrip()


# ---------------------------------------------------------------------------
# SubAgentDescriptor — the pluggable manifest
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SubAgentDescriptor:
    """Self-describing manifest for a sub-agent package.

    Assistant and DirectorAgent read these descriptors from the
    ``AGENT_REGISTRY`` to discover agents dynamically.

    Attributes:
        agent_id:
            Unique agent identifier, e.g. ``"AudioAgent"``.  Used as the
            lookup key in the registry, in ``RoutingStep.agent_id``, and as
            the slug for the JSON snapshot file written under
            ``artifacts/<agent_id>/<agent_id>_exec_<n>.json``.
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
            ``(step_id, resolved_artifacts) -> BaseModel`` —
            constructs the agent's typed input from the dict of artifacts
            selected by InputResolver, keyed by the consumer agent's
            ``[label]`` headers. Assistant always passes the Task Stack
            ``step_id``; agents that do not need it may name the parameter
            ``_step_id`` and omit it from the returned Pydantic model.
            Duration, language, and other creative intent must be
            **inferred by the sub-agent LLM** from the resolved artifacts
            (e.g. prior JSON snapshots, source text uploads) — not from a
            separate orchestrator ``config`` object or deterministic
            keyword parsing in Python.
        build_captions:
            ``(agent_id, output_dict) -> {sys_id: {"caption": str, "scope": str}}``
            — generates captions for all artifacts produced by this
            execution.  ``agent_id`` is used as the key for the JSON
            snapshot caption.  Media artifacts use their ``sys_id``
            (e.g. ``"img_char_001_global"``, ``"clip_sh_001"``).
            ArtifactWriter calls this once per execution to populate
            global_memory.
        service_factories:
            Mapping of ``service_key -> factory(ctx) -> service_instance``.
            ``ctx`` is a dict with at least ``{"llm_client": LLMClient}``.
            Services with the same key across descriptors are created once
            and shared (first descriptor to declare a key wins).
            Non-media agents leave this as an empty dict.
        materializer_factory:
            Optional ``(services_dict) -> BaseMaterializer``.
            ``None`` for agents with no binary output.
    """

    agent_id: str
    catalog_entry: str = ""

    agent_factory: Callable[..., Any] = field(repr=False, default=lambda llm: None)
    evaluator_factory: Callable[..., Any] = field(repr=False, default=lambda: None)

    build_input: Callable[..., BaseModel] = field(
        repr=False,
        default=lambda step_id, resolved_artifacts: None,
    )
    service_factories: dict[str, Callable[..., Any]] = field(
        repr=False, default_factory=dict,
    )
    materializer_factory: Callable[..., BaseMaterializer] | None = field(
        repr=False, default=None,
    )
    input_needs_description: str = (
        "Needs any relevant prior artifacts from the workspace as context."
    )
    build_captions: Callable[..., dict[str, dict[str, str]]] = field(
        repr=False,
        default=lambda agent_id, output_dict: {},
    )
    promotes_consumed_inputs_to_global: bool = False

    # ------------------------------------------------------------------
    # Spec-based constructor (preferred for new agents)
    # ------------------------------------------------------------------

    @classmethod
    def from_spec(
        cls,
        spec: "AgentSpec",
        *,
        agent_factory: Callable[..., Any],
        evaluator_factory: Callable[..., Any],
        build_input: Callable[..., BaseModel],
        build_captions: Callable[..., dict[str, dict[str, str]]] | None = None,
        service_factories: dict[str, Callable[..., Any]] | None = None,
        materializer_factory: Callable[..., BaseMaterializer] | None = None,
    ) -> "SubAgentDescriptor":
        """Build a descriptor from a single AgentSpec.

        ``catalog_entry`` and ``input_needs_description`` are derived from
        the spec's structured inputs so the two LLM-facing views stay in
        sync. Non-spec fields (factories, build_input, etc.) are passed
        through as kwargs.
        """
        kwargs: dict[str, Any] = {
            "agent_id": spec.agent_id,
            "catalog_entry": render_catalog_entry(spec),
            "input_needs_description": render_input_needs_description(spec),
            "agent_factory": agent_factory,
            "evaluator_factory": evaluator_factory,
            "build_input": build_input,
            "promotes_consumed_inputs_to_global": spec.promotes_consumed_inputs_to_global,
        }
        if build_captions is not None:
            kwargs["build_captions"] = build_captions
        if service_factories is not None:
            kwargs["service_factories"] = service_factories
        if materializer_factory is not None:
            kwargs["materializer_factory"] = materializer_factory
        return cls(**kwargs)

    # ------------------------------------------------------------------
    # Fully-equipped agent factory
    # ------------------------------------------------------------------

    def build_equipped_agent(self, llm: LLMClient) -> BaseAgent:
        """Create an agent with its evaluator and materializer wired in.

        This is the single entry point for constructing a ready-to-run
        agent.  The returned agent's ``run()`` method will use the
        injected evaluator for quality gate checks and the materializer
        for binary asset generation.

        The descriptor's ``service_factories`` are the single source of
        truth for which media backend an agent uses; mock-vs-real
        selection lives inside those factories (see
        ``inference.generation.select_*_service``), not here.

        Args:
            llm: Shared LLM client instance.

        Returns:
            A ``BaseAgent`` subclass instance with ``evaluator`` and
            ``materializer`` attributes set.
        """
        agent = self.agent_factory(llm)
        agent.evaluator = self.evaluator_factory()

        if self.materializer_factory is not None:
            ctx: dict[str, Any] = {"llm_client": llm}
            services: dict[str, Any] = {
                svc_key: svc_factory(ctx)
                for svc_key, svc_factory in self.service_factories.items()
            }
            agent.materializer = self.materializer_factory(services)

        return agent
