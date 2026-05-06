"""Base class and helpers for all evaluators (structural + creative).

Evaluators are the **unified quality hub** for each agent. They own two
evaluation layers, both invoked pre-materialization on the typed output:

  - **Layer 1 — ``check_structure()``:** Rule-based structural checks
    (ID refs, order continuity, required fields, format/range invariants
    Pydantic doesn't already enforce). Free, deterministic, instant.
  - **Layer 2 — ``evaluate_creative()``:** LLM-based creative assessment
    with agent-specific dimensions. Only runs if Layer 1 passes.

Both are invoked via ``evaluate()`` before materialization.

Note: a previous ``Layer 3 — evaluate_asset()`` post-materialization hook
was removed (Phase 4 of the materializer-raise refactor). Failure
detection for binary assets now lives in each materializer itself: the
materializer runs a partial-resume retry loop up to
``DEFAULT_ASSET_RETRIES`` and then raises, so the outer
``LLMBaseAgent.run`` loop catches the exception and feeds it back to
the LLM as ``rework_notes`` for the next attempt. Artifact-content
quality (e.g. "is the generated image good?") is a separate evaluation
concern handled outside the agent run loop.

**Output-only**: every evaluator method receives ONLY the agent's own
output. Evaluators do NOT cross-validate against upstream artifacts —
that violates sub-agent decoupling. The ``resolved_artifacts`` dict is
intentionally absent from every method signature in this base class.

Each evaluation method returns (or contributes to) the standard result::

    {
        "dimensions": {"<name>": {"score": float, "notes": [str]}},
        "overall_pass": bool,
        "summary": str
    }
"""

from __future__ import annotations

import json
import logging
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from inference.clients import LLMClient

logger = logging.getLogger(__name__)

OutputT = TypeVar("OutputT", bound=BaseModel)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def check_uri(uri: str) -> str:
    """Classify an asset URI as 'success', 'error', or 'missing'.

    Returns one of: ``"success"``, ``"error"``, ``"missing"``.

    Classification rules:
      - empty or ``"placeholder"`` → ``"missing"`` (not yet generated)
      - starts with ``"error:"``   → ``"error"``   (generation failed)
      - anything else              → ``"success"``  (real file path)

    Retained as a generic utility after the L3 layer was removed — still
    used by unregistered univa_* evaluators and available for any future
    code that needs URI classification.
    """
    if not uri or uri == "placeholder":
        return "missing"
    if uri.startswith("error:"):
        return "error"
    return "success"


# ---------------------------------------------------------------------------
# Abstract base
# ---------------------------------------------------------------------------

class BaseEvaluator(Generic[OutputT]):
    """Abstract base for all FrameWorkers evaluators.

    Each agent has a corresponding evaluator that handles its quality
    checks. Subclasses override the layer methods they need:

      - ``check_structure()``   — Layer 1 (rule-based structural checks)
      - ``evaluate_creative()`` — Layer 2 (LLM creative assessment)

    ``evaluate()`` is the combined L1+L2 entry point called by Assistant
    before materialization.

    The equipped pipeline agent holds its evaluator from the descriptor’s
    ``evaluator_factory`` (see ``SubAgentDescriptor`` / ``build_equipped_agent``).
    """

    CREATIVE_PASS_THRESHOLD: float = 0.6

    def __init__(self, llm_client: LLMClient | None = None, **kwargs: Any) -> None:
        self.llm = llm_client or LLMClient(**kwargs)

    @property
    def evaluator_name(self) -> str:
        """Human-readable evaluator name, derived from class name by default."""
        return type(self).__name__

    # ------------------------------------------------------------------
    # Layer 1 — Rule-based structural checks
    # ------------------------------------------------------------------

    def check_structure(self, output: OutputT) -> list[str]:
        """Rule-based structural checks.  Override per evaluator.

        Checks deterministic properties of the agent's own output:
        ID referential integrity within the output, metrics consistency,
        required fields.  Does NOT compare against any upstream artifact.

        Args:
            output: The parsed agent output (Pydantic model).

        Returns:
            List of error strings.  Empty list means all checks passed.
        """
        return []  # default: no extra structural rules

    # ------------------------------------------------------------------
    # Layer 2 — LLM-based creative evaluation (template method)
    # ------------------------------------------------------------------

    creative_dimensions: list[tuple[str, str]] = []
    """Declare creative dimensions as ``[(name, description), ...]``.

    Example::

        creative_dimensions = [
            ("alignment", "Does the blueprint faithfully expand the draft idea?"),
            ("dramatic", "Clear conflict, stakes, turning points, satisfying arc?"),
        ]

    Leave empty (default) to skip creative evaluation entirely.
    """

    def _build_creative_context(self, output: OutputT) -> str:
        """Return additional context string for the creative evaluation prompt.

        Default returns empty string. Subclasses MAY override to inject
        additional summarization derived from the agent's own output.
        Subclasses MUST NOT read upstream artifacts here.
        """
        return ""

    async def evaluate_creative(self, output: OutputT) -> dict[str, Any]:
        """LLM-based creative quality evaluation (template method).

        If ``creative_dimensions`` is empty, returns an auto-pass.
        Otherwise builds a system+user prompt from the declared dimensions
        and ``_build_creative_context()``, calls the LLM, and normalizes
        the pass threshold.

        Subclasses should NOT override this method.  Instead, declare
        ``creative_dimensions`` and (optionally) override
        ``_build_creative_context()``.
        """
        if not self.creative_dimensions:
            return {
                "dimensions": {},
                "overall_pass": True,
                "summary": f"No creative evaluation defined for {self.evaluator_name}.",
            }

        # --- Build system prompt from declared dimensions ---
        dim_lines = "\n".join(
            f"{i}. **{name}** -- {desc}"
            for i, (name, desc) in enumerate(self.creative_dimensions, 1)
        )
        dim_json_parts = ", ".join(
            f'"{name}": {{"score": float, "notes": [str]}}'
            for name, _ in self.creative_dimensions
        )
        system = (
            f"You are a quality evaluator for a film production pipeline.\n"
            f"Evaluate the output on these dimensions:\n"
            f"{dim_lines}\n\n"
            f"Score each dimension 0.0-1.0.  Overall pass: all >= {self.CREATIVE_PASS_THRESHOLD}.\n"
            f"Provide actionable notes for any score < 0.75.\n\n"
            f"Return JSON only:\n"
            f'{{"dimensions": {{{dim_json_parts}}}, '
            f'"overall_pass": bool, "summary": str}}'
        )

        # --- Build user prompt ---
        context = self._build_creative_context(output)
        creative_content = self.extract_creative_fields(output.content)
        content_json = json.dumps(creative_content, ensure_ascii=False, indent=2)
        user = (
            f"{context}\n\n"
            f"Creative content:\n{content_json}\n\n"
            f"Evaluate and return JSON only."
        ) if context else (
            f"Creative content:\n{content_json}\n\n"
            f"Evaluate and return JSON only."
        )

        # --- Call LLM and normalize ---
        result = await self.llm.chat_json(system, user, max_tokens=8192)
        dims = result.get("dimensions", {})
        all_pass = all(
            d.get("score", 0) >= self.CREATIVE_PASS_THRESHOLD
            for d in dims.values()
        )
        result["overall_pass"] = all_pass and result.get("overall_pass", True)
        return result

    # ------------------------------------------------------------------
    # Combined L1+L2 entry point
    # ------------------------------------------------------------------

    async def evaluate(self, output: OutputT) -> dict[str, Any]:
        """Full evaluation: structural rules first, then LLM creative.

        This is the method that Assistant calls before materialization.
        It combines Layers 1 and 2 into a single result dict.

        Returns:
            Dict with ``structural_errors``, ``dimensions``,
            ``overall_pass``, and ``summary``.
        """
        # Layer 1: rule-based (fast, free, deterministic)
        structural_errors = self.check_structure(output)
        if structural_errors:
            logger.warning(
                "[%s] Structural validation failed: %s",
                self.evaluator_name,
                structural_errors,
            )
            return {
                "structural_errors": structural_errors,
                "dimensions": {},
                "overall_pass": False,
                "summary": (
                    f"Structural validation failed with "
                    f"{len(structural_errors)} error(s): "
                    + "; ".join(structural_errors[:3])
                ),
            }

        # Layer 2: LLM creative evaluation
        creative_result = await self.evaluate_creative(output)
        creative_result["structural_errors"] = []
        return creative_result

    # ------------------------------------------------------------------
    # Structural-check helpers (for use inside check_structure())
    # ------------------------------------------------------------------

    @staticmethod
    def _check_order_continuous(
        errors: list[str],
        name: str,
        orders: list[int],
    ) -> None:
        """Append an error if ``orders`` is not [1, 2, ..., N]."""
        if orders and orders != list(range(1, len(orders) + 1)):
            errors.append(f"{name} order not continuous from 1: {orders}")

    # ------------------------------------------------------------------
    # Other helpers
    # ------------------------------------------------------------------

    @staticmethod
    def extract_creative_fields(model: BaseModel) -> dict:
        """Recursively extract only fields marked ``creative=True``.

        Walks a Pydantic model tree and returns a dict containing only the
        leaf fields whose ``json_schema_extra`` includes ``{"creative": True}``.
        Container fields (nested ``BaseModel`` or ``list[BaseModel]``) are
        recursed into automatically; if a container yields any creative
        content, it is included under the same key name.

        Returns:
            A (possibly nested) dict with only creative field values.
            Empty dict if no creative fields are found.
        """
        result: dict = {}
        for name, field_info in type(model).model_fields.items():
            value = getattr(model, name)
            extra = field_info.json_schema_extra or {}
            if extra.get("creative"):
                if isinstance(value, BaseModel):
                    result[name] = value.model_dump()
                else:
                    result[name] = value
            elif isinstance(value, BaseModel):
                sub = BaseEvaluator.extract_creative_fields(value)
                if sub:
                    result[name] = sub
            elif isinstance(value, list) and value and isinstance(value[0], BaseModel):
                items = [BaseEvaluator.extract_creative_fields(item) for item in value]
                items = [i for i in items if i]
                if items:
                    result[name] = items
        return result
