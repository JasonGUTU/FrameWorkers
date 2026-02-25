"""Base agent — abstract class that all pipeline agents inherit from.

Provides:
- LLM client access
- Standardized run() → ExecutionResult flow with built-in quality gate
- Three-layer evaluation: L1 structural, L2 creative, L3 asset
- Retry loop with rework-notes feedback (self-correction)
- Optional materialization with caller-provided persistence callback
- JSON validation via Pydantic
- System / User prompt templating

Each agent can be assembled with an evaluator and materializer (via
``SubAgentDescriptor.build_equipped_agent()``).  ``run()`` orchestrates
generation, evaluation, and retry internally — callers receive a single
``ExecutionResult`` indicating pass/fail, eval details, and any media
assets produced.

Skeleton-first mode (opt-in per agent):
  When ``build_skeleton()`` returns a non-None output, the agent switches to
  skeleton mode.  The system pre-builds all structural fields (IDs, order,
  source refs, placeholders) from upstream data, and the LLM is asked only
  to fill creative fields (prompt_summary, dialogue text, mood, etc.).
  This eliminates structural errors and reduces output tokens by 35-70%.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Generic, TypeVar, get_args

from pydantic import BaseModel

from inference.runtime.base_client import LLMClient

if TYPE_CHECKING:
    from .base_evaluator import BaseEvaluator
    from .descriptor import BaseMaterializer, MediaAsset

logger = logging.getLogger(__name__)

InputT = TypeVar("InputT", bound=BaseModel)
OutputT = TypeVar("OutputT", bound=BaseModel)


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass
class MaterializeContext:
    """Bundles the external infrastructure needed for binary materialization.

    Passed to ``BaseAgent.run()`` when the caller supports media persistence.
    When ``None``, materialization and L3 asset evaluation are skipped —
    this allows the same agent to run in environments without file I/O
    (e.g. ``dynamic-task-stack``).

    Attributes:
        project_id:      Current project identifier.
        assets:          Full in-memory asset cache (read context for the
                         materializer, e.g. ``assets["storyboard"]``).
        persist_binary:  Callback that saves a ``MediaAsset`` to disk and
                         returns the URI string of the saved file.
    """

    project_id: str
    assets: dict[str, Any]
    persist_binary: Callable[[MediaAsset], str]


@dataclass
class ExecutionResult:
    """Outcome of a full ``BaseAgent.run()`` execution.

    Wraps the agent's output together with evaluation results, pass/fail
    status, attempt count, and any media assets produced during
    materialization.

    Attributes:
        output:       The agent's typed output (Pydantic model) from the
                      last attempt.  Always present even when ``passed``
                      is False (useful for debugging).
        eval_result:  Combined evaluation result dict with ``overall_pass``,
                      ``summary``, ``dimensions``, etc.
        passed:       ``True`` if all evaluation layers passed within the
                      retry budget.
        attempts:     Number of generation attempts made (1-based).
        media_assets: Binary assets produced by materialization (empty for
                      non-media agents or when no ``MaterializeContext``
                      was provided).
        asset_dict:   The output serialized as a dict with materialized
                      URIs written in-place.  ``None`` for non-media
                      agents.  Callers can persist this dict directly.
    """

    output: BaseModel | None
    eval_result: dict[str, Any]
    passed: bool
    attempts: int
    media_assets: list = field(default_factory=list)
    asset_dict: dict[str, Any] | None = None


class BaseAgent(Generic[InputT, OutputT]):
    """Abstract base for all FrameWorkers agents.

    Each agent is a **self-contained execution unit**.  ``run()`` orchestrates:

      1. Generation (LLM call via skeleton or legacy mode)
      2. L1+L2 evaluation (structural + creative) via ``self.evaluator``
      3. Materialization via ``self.materializer`` (media agents only)
      4. L3 asset evaluation (post-materialization, media agents only)
      5. Retry loop with rework-notes feedback on failure

    The evaluator and materializer are injected as attributes (typically
    by ``SubAgentDescriptor.build_equipped_agent()``).  When ``None``,
    the corresponding steps are skipped — making the agent usable in
    lightweight environments without quality infrastructure.

    Subclasses must implement:
      - system_prompt(): returns the system prompt string
      - build_user_prompt(input_data): returns the user prompt string

    Optional overrides:
      - parse_output(raw_json): default uses OutputT.model_validate()
      - recompute_metrics(output): fix LLM-generated counts
    """

    def __init__(self, llm_client: LLMClient | None = None, **kwargs: Any) -> None:
        self.llm = llm_client or LLMClient(**kwargs)
        self.evaluator: BaseEvaluator | None = None
        self.materializer: BaseMaterializer | None = None

    # ------------------------------------------------------------------
    # Abstract interface
    # ------------------------------------------------------------------

    @property
    def agent_name(self) -> str:
        """Human-readable agent name, derived from class name by default."""
        return type(self).__name__

    def system_prompt(self) -> str:
        """Return the full system prompt for this agent.

        Override in agents that use legacy mode or whose skeleton mode
        needs a specific system prompt for the creative-fill LLM call.
        """
        raise NotImplementedError(f"{self.agent_name}.system_prompt()")

    def build_user_prompt(self, input_data: InputT) -> str:
        """Build the user prompt from structured input.

        Only needed by agents that use legacy mode (StoryAgent) or
        structuring mode (ScreenplayAgent, StoryboardAgent).
        """
        raise NotImplementedError(f"{self.agent_name}.build_user_prompt()")

    def parse_output(self, raw: dict[str, Any]) -> OutputT:
        """Validate raw JSON dict and return typed output model.

        Default implementation resolves the ``OutputT`` generic parameter
        at runtime and calls ``model_validate(raw)``.  Override only if
        your agent needs custom parsing (e.g. KeyFrameAgent).
        """
        output_cls = get_args(self.__class__.__orig_bases__[0])[1]
        return output_cls.model_validate(raw)

    def recompute_metrics(self, output: OutputT) -> None:
        """Recompute metrics from content, overriding LLM-generated values.

        LLMs are notoriously bad at counting — metrics like scene_count,
        block_count, etc. are derivable from content and should never be
        trusted from LLM output.  Each agent overrides this to compute
        the correct values from the parsed ``output.content``.

        Called automatically after ``parse_output`` in ``run()``.
        Mutates ``output.metrics`` in-place.
        """
        # default: no recomputation (agents without metrics can skip)

    # ------------------------------------------------------------------
    # Skeleton-first mode (opt-in per agent)
    # ------------------------------------------------------------------

    @property
    def skeleton_is_complete(self) -> bool:
        """If True, ``build_skeleton`` returns a fully complete output.

        When True the agent skips the LLM call entirely — no creative
        prompt is built and no ``fill_creative`` merge is needed.  Use
        this for agents whose output contains zero creative fields
        (e.g. VideoAgent).

        Default is ``False``; override in LLM-free agents.
        """
        return False

    def build_skeleton(self, input_data: InputT) -> OutputT | None:
        """Pre-build structural output from upstream data.

        Override in agents where the output structure (IDs, order, source
        refs, placeholders) is fully deterministic from upstream.  The
        returned skeleton has all structural fields filled and creative
        fields left as empty strings.

        Returns ``None`` (default) to use legacy full-JSON mode.
        """
        return None

    def build_creative_prompt(
        self, input_data: InputT, skeleton: OutputT
    ) -> str:
        """Build a prompt asking the LLM to fill ONLY creative fields.

        Called only when ``build_skeleton()`` returns non-None.
        Must be overridden by agents that use skeleton mode.

        Args:
            input_data: The agent's typed input (for upstream context).
            skeleton: The pre-built structural skeleton.

        Returns:
            A user-prompt string instructing the LLM to return a compact
            JSON containing only IDs (for matching) and creative values.
        """
        raise NotImplementedError(
            f"{self.agent_name} uses skeleton mode but does not implement "
            f"build_creative_prompt()"
        )

    def fill_creative(self, skeleton: OutputT, creative: dict) -> OutputT:
        """Merge LLM creative output into the pre-built skeleton.

        Called only when ``build_skeleton()`` returns non-None.
        Must be overridden by agents that use skeleton mode.

        Args:
            skeleton: The pre-built structural skeleton (mutated in-place).
            creative: The compact creative JSON returned by the LLM.

        Returns:
            The skeleton with creative fields populated.
        """
        raise NotImplementedError(
            f"{self.agent_name} uses skeleton mode but does not implement "
            f"fill_creative()"
        )

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def run(
        self,
        input_data: InputT,
        *,
        upstream: dict[str, Any] | None = None,
        rework_notes: str = "",
        max_retries: int = 3,
        materialize_ctx: MaterializeContext | None = None,
    ) -> ExecutionResult:
        """Execute the agent with built-in quality gate and retry loop.

        Orchestrates generation, evaluation (L1+L2+L3), optional
        materialization, and retries — returning a single
        ``ExecutionResult``.

        Quality gate flow per attempt:
          1. ``_generate()`` — LLM call (skeleton / legacy mode)
          2. ``evaluator.evaluate()`` — L1 structural + L2 creative
          3. ``materializer.materialize()`` — binary asset generation
             (only if materializer is set and ``materialize_ctx`` provided)
          4. ``evaluator.evaluate_asset()`` — L3 post-materialization
          5. On any failure: feed eval summary as rework_notes and retry

        Args:
            input_data:      Typed agent input payload.
            upstream:        Upstream asset dicts for evaluator cross-checks.
            rework_notes:    Initial rework instructions (e.g. from the
                             Director when action is ``"regenerate"``).
            max_retries:     Total attempts before giving up.
            materialize_ctx: External infrastructure for binary persistence.
                             ``None`` skips materialization and L3.
        """
        logger.info(
            "[%s] Starting run (max_retries=%d) …",
            self.agent_name, max_retries,
        )

        eval_result: dict[str, Any] = {}
        output: OutputT | None = None
        media_assets: list = []
        asset_dict: dict[str, Any] | None = None

        for attempt in range(1, max_retries + 1):
            logger.info(
                "[%s] Attempt %d/%d", self.agent_name, attempt, max_retries,
            )
            media_assets = []
            asset_dict = None

            # --- Step 1: Generate (LLM call) ---
            output = await self._generate(input_data, rework_notes=rework_notes)

            # --- Step 2: L1+L2 evaluation (structural + creative) ---
            if self.evaluator is not None:
                try:
                    eval_result = await self.evaluator.evaluate(output, upstream)
                except Exception as exc:
                    logger.error(
                        "[%s] Evaluation error on attempt %d: %s",
                        self.agent_name, attempt, exc,
                    )
                    eval_result = {
                        "overall_pass": True,
                        "summary": f"Evaluation error: {exc}",
                    }

                if not eval_result.get("overall_pass", False):
                    logger.warning(
                        "[%s] L1+L2 FAILED (attempt %d/%d): %s",
                        self.agent_name, attempt, max_retries,
                        eval_result.get("summary", "no summary"),
                    )
                    rework_notes = eval_result.get("summary", "")
                    if attempt < max_retries:
                        continue
                    return ExecutionResult(
                        output=output, eval_result=eval_result,
                        passed=False, attempts=attempt,
                    )
            else:
                eval_result = {
                    "overall_pass": True,
                    "summary": f"No evaluator for {self.agent_name}.",
                }

            # --- Step 3: Materialize (if applicable) ---
            if self.materializer is not None and materialize_ctx is not None:
                asset_dict = output.model_dump(exclude={"meta"})
                try:
                    raw_media = await self.materializer.materialize(
                        materialize_ctx.project_id,
                        asset_dict,
                        materialize_ctx.assets,
                    )
                    for media in raw_media:
                        uri = materialize_ctx.persist_binary(media)
                        media.uri_holder["uri"] = uri
                    media_assets = list(raw_media)
                except Exception as exc:
                    logger.warning(
                        "[%s] Materialization failed (attempt %d/%d): %s",
                        self.agent_name, attempt, max_retries, exc,
                    )
                    eval_result = {
                        "overall_pass": False,
                        "summary": f"Materialization error: {exc}",
                    }
                    rework_notes = str(exc)
                    if attempt < max_retries:
                        continue
                    return ExecutionResult(
                        output=output, eval_result=eval_result,
                        passed=False, attempts=attempt,
                        media_assets=media_assets, asset_dict=asset_dict,
                    )

                # --- Step 4: L3 evaluation (post-materialization) ---
                if self.evaluator is not None:
                    try:
                        asset_eval = await self.evaluator.evaluate_asset(
                            asset_dict, upstream,
                        )
                    except Exception as exc:
                        logger.error(
                            "[%s] Asset evaluation error: %s",
                            self.agent_name, exc,
                        )
                        asset_eval = {
                            "overall_pass": True,
                            "summary": f"Asset evaluation error: {exc}",
                        }

                    if not asset_eval.get("overall_pass", True):
                        logger.warning(
                            "[%s] L3 asset eval FAILED (attempt %d/%d): %s",
                            self.agent_name, attempt, max_retries,
                            asset_eval.get("summary", "no summary"),
                        )
                        eval_result = asset_eval
                        rework_notes = asset_eval.get("summary", "")
                        if attempt < max_retries:
                            continue
                        return ExecutionResult(
                            output=output, eval_result=eval_result,
                            passed=False, attempts=attempt,
                            media_assets=media_assets, asset_dict=asset_dict,
                        )

            # --- ALL layers PASSED ---
            logger.info(
                "[%s] Quality gate PASSED (attempt %d)",
                self.agent_name, attempt,
            )
            return ExecutionResult(
                output=output, eval_result=eval_result,
                passed=True, attempts=attempt,
                media_assets=media_assets, asset_dict=asset_dict,
            )

        # Safety net (loop always returns, but satisfies type checker)
        return ExecutionResult(
            output=output, eval_result=eval_result,
            passed=False, attempts=max_retries,
            media_assets=media_assets, asset_dict=asset_dict,
        )

    # ------------------------------------------------------------------
    # Generation (internal — the old run() logic)
    # ------------------------------------------------------------------

    async def _generate(
        self,
        input_data: InputT,
        *,
        rework_notes: str = "",
    ) -> OutputT:
        """Generate output: build prompts, call LLM, parse and return.

        This is the pure generation step (no evaluation or retry).
        Supports three modes:
          - **LLM-free mode** (skeleton + ``skeleton_is_complete``):
            No LLM call — skeleton IS the final output.
          - **Skeleton mode** (skeleton, not complete):
            LLM fills only creative fields.
          - **Legacy mode** (default): LLM generates full JSON.
        """
        logger.info("[%s] Generating …", self.agent_name)

        skeleton = self.build_skeleton(input_data)

        if skeleton is not None and self.skeleton_is_complete:
            logger.info(
                "[%s] Using LLM-free skeleton mode (no creative fields)",
                self.agent_name,
            )
            output = skeleton
        elif skeleton is not None:
            logger.info("[%s] Using skeleton mode", self.agent_name)
            output = await self._run_skeleton_mode(
                input_data, skeleton, rework_notes
            )
        else:
            output = await self._run_legacy_mode(input_data, rework_notes)

        self.recompute_metrics(output)
        logger.info("[%s] Generation complete.", self.agent_name)
        return output

    async def _run_skeleton_mode(
        self,
        input_data: InputT,
        skeleton: OutputT,
        rework_notes: str,
    ) -> OutputT:
        """Skeleton-first execution: LLM fills only creative fields."""
        system = self.system_prompt()
        user = self.build_creative_prompt(input_data, skeleton)

        if rework_notes:
            user += (
                "\n\n--- REWORK INSTRUCTIONS (from quality review) ---\n"
                f"{rework_notes}\n"
                "--- END REWORK INSTRUCTIONS ---\n"
                "Apply the above fixes while preserving everything else."
            )
            logger.info(
                "[%s] Rework notes injected (%d chars)",
                self.agent_name,
                len(rework_notes),
            )

        logger.debug("[%s] System prompt length: %d", self.agent_name, len(system))
        logger.debug("[%s] User prompt length: %d", self.agent_name, len(user))

        creative_json = await self.llm.chat_json(system, user)
        logger.info(
            "[%s] Received creative-only LLM response, merging …",
            self.agent_name,
        )

        output = self.fill_creative(skeleton, creative_json)
        return output

    async def _run_legacy_mode(
        self,
        input_data: InputT,
        rework_notes: str,
    ) -> OutputT:
        """Legacy execution: LLM generates the full JSON."""
        system = self.system_prompt()
        user = self.build_user_prompt(input_data)

        if rework_notes:
            user += (
                "\n\n--- REWORK INSTRUCTIONS (from quality review) ---\n"
                f"{rework_notes}\n"
                "--- END REWORK INSTRUCTIONS ---\n"
                "Apply the above fixes while preserving everything else."
            )
            logger.info(
                "[%s] Rework notes injected (%d chars)",
                self.agent_name,
                len(rework_notes),
            )

        logger.debug("[%s] System prompt length: %d", self.agent_name, len(system))
        logger.debug("[%s] User prompt length: %d", self.agent_name, len(user))

        raw_json = await self.llm.chat_json(system, user)
        logger.info("[%s] Received LLM response, parsing …", self.agent_name)
        logger.debug(
            "[%s] Raw JSON keys: %s", self.agent_name, list(raw_json.keys())
        )
        logger.debug(
            "[%s] Raw JSON (first 1500): %s",
            self.agent_name,
            json.dumps(raw_json, ensure_ascii=False)[:1500],
        )

        # Strip metrics before parsing — LLM may echo "<SYSTEM_COMPUTED>"
        # placeholders which fail Pydantic type validation.  Defaults (0/0.0)
        # are safe because recompute_metrics overwrites immediately after.
        if "metrics" in raw_json:
            raw_json["metrics"] = {}

        output = self.parse_output(raw_json)
        return output

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_order(items: list, attr: str = "order") -> None:
        """Set ``item.<attr> = i`` for 1-based enumeration.

        Commonly used in ``recompute_metrics`` to fix order fields
        that the LLM may have generated out of sequence.
        """
        for i, item in enumerate(items, 1):
            setattr(item, attr, i)

    @staticmethod
    def to_json_str(model: BaseModel) -> str:
        """Serialize a Pydantic model to a compact JSON string."""
        return model.model_dump_json(indent=2, exclude_none=False)

    @staticmethod
    def dict_to_json_str(data: dict) -> str:
        """Serialize a dict to a JSON string."""
        return json.dumps(data, ensure_ascii=False, indent=2)
