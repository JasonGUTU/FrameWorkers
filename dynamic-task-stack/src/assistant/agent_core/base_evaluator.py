"""Base class and helpers for all evaluators (structural + creative + asset).

Evaluators are the **unified quality hub** for each agent.  They own all
three evaluation layers:

  - **Layer 1 — ``check_structure()``:** Rule-based structural checks
    (ID refs, metrics, order).  Free, deterministic, instant.
  - **Layer 2 — ``evaluate_creative()``:** LLM-based creative assessment
    with agent-specific dimensions.  Only runs if Layer 1 passes.
  - **Layer 3 — ``evaluate_asset()``:** Post-materialization binary asset
    checks (success rates, format, assembly).  Only runs after media
    services generate files.

Layers 1+2 are invoked via ``evaluate()`` before materialization.
Layer 3 is invoked via ``evaluate_asset()`` after materialization.

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

from .llm_client import LLMClient

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

    Each agent has a corresponding evaluator that handles all quality
    checks.  Subclasses override the layer methods they need:

      - ``check_structure()``    — Layer 1 (rule-based structural checks)
      - ``evaluate_creative()`` — Layer 2 (LLM creative assessment)
      - ``evaluate_asset()``    — Layer 3 (post-materialization binary checks)

    ``evaluate()`` is the combined L1+L2 entry point called by
    Assistant before materialization.  ``evaluate_asset()`` is called
    separately after materialization completes.

    Assistant looks up the correct evaluator via
    ``AGENT_NAME_TO_EVALUATOR`` (defined in ``src.sub_agent.__init__``).
    """

    CREATIVE_PASS_THRESHOLD: float = 0.65
    ASSET_PASS_THRESHOLD: float = 0.8

    def __init__(self, llm_client: LLMClient | None = None, **kwargs: Any) -> None:
        self.llm = llm_client or LLMClient(**kwargs)

    @property
    def evaluator_name(self) -> str:
        """Human-readable evaluator name, derived from class name by default."""
        return type(self).__name__

    # ------------------------------------------------------------------
    # Layer 1 — Rule-based structural checks
    # ------------------------------------------------------------------

    def check_structure(
        self,
        output: OutputT,
        upstream: dict[str, Any] | None = None,
    ) -> list[str]:
        """Rule-based structural checks.  Override per evaluator.

        Checks deterministic properties: ID referential integrity,
        metrics consistency, required fields, cross-asset alignment.

        Args:
            output: The parsed agent output (Pydantic model).
            upstream: Optional dict of upstream asset dicts for cross-check.

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

    def _build_creative_context(
        self,
        output: OutputT,
        upstream: dict[str, Any] | None,
    ) -> str:
        """Return upstream context string for the creative evaluation prompt.

        Override in evaluators that have creative dimensions.  The returned
        string is inserted into the user prompt above the creative content.

        Default returns empty string.
        """
        return ""

    async def evaluate_creative(
        self,
        output: OutputT,
        upstream: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """LLM-based creative quality evaluation (template method).

        If ``creative_dimensions`` is empty, returns an auto-pass.
        Otherwise builds a system+user prompt from the declared dimensions
        and ``_build_creative_context()``, calls the LLM, and normalizes
        the pass threshold.

        Subclasses should NOT override this method.  Instead, declare
        ``creative_dimensions`` and override ``_build_creative_context()``.
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
        context = self._build_creative_context(output, upstream)
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
        result = await self.llm.chat_json(system, user)
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

    async def evaluate(
        self,
        output: OutputT,
        upstream: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Full evaluation: structural rules first, then LLM creative.

        This is the method that Assistant calls before materialization.
        It combines Layers 1 and 2 into a single result dict.

        Returns:
            Dict with ``structural_errors``, ``dimensions``,
            ``overall_pass``, and ``summary``.
        """
        # Layer 1: rule-based (fast, free, deterministic)
        structural_errors = self.check_structure(output, upstream)
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
        creative_result = await self.evaluate_creative(output, upstream)
        creative_result["structural_errors"] = []
        return creative_result

    # ------------------------------------------------------------------
    # Layer 3 — Post-materialization asset evaluation (optional)
    # ------------------------------------------------------------------

    async def evaluate_asset(
        self,
        asset_data: dict[str, Any],
        upstream: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Evaluate materialized binary assets.  Override for media agents.

        Called by Assistant after media services produce files.
        Only agents with binary outputs (keyframes, video, audio) need
        to override this.

        Args:
            asset_data: The complete asset dict with materialized URIs.
            upstream: Optional upstream asset dicts for context.

        Returns:
            Evaluation result dict with ``dimensions``, ``overall_pass``,
            and ``summary``.
        """
        return {
            "dimensions": {},
            "overall_pass": True,
            "summary": f"No asset evaluation defined for {self.evaluator_name}.",
        }

    # ------------------------------------------------------------------
    # Structural-check helpers (for use inside check_structure())
    # ------------------------------------------------------------------

    @staticmethod
    def _check_metric(
        errors: list[str],
        field_name: str,
        expected: int | float,
        actual: int | float,
    ) -> None:
        """Append an error if ``expected != actual`` for a metrics field."""
        if expected != actual:
            errors.append(
                f"metrics.{field_name} ({expected}) != actual ({actual})"
            )

    @staticmethod
    def _check_order_continuous(
        errors: list[str],
        name: str,
        orders: list[int],
    ) -> None:
        """Append an error if ``orders`` is not [1, 2, ..., N]."""
        if orders and orders != list(range(1, len(orders) + 1)):
            errors.append(f"{name} order not continuous from 1: {orders}")

    @staticmethod
    def _check_id_coverage(
        errors: list[str],
        label: str,
        expected_ids: set[str],
        actual_ids: set[str],
    ) -> None:
        """Append errors for missing / extra IDs between two sets."""
        missing = expected_ids - actual_ids
        extra = actual_ids - expected_ids
        if missing:
            errors.append(f"{label} missing: {sorted(missing)}")
        if extra:
            errors.append(f"{label} extra: {sorted(extra)}")

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
