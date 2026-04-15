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
  source refs, placeholders) from shared assets, and the LLM is asked only
  to fill creative fields (prompt_summary, dialogue text, mood, etc.).
  This eliminates structural errors and reduces output tokens by 35-70%.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Generic, Optional, TypeVar, get_args

from pydantic import BaseModel

from inference.clients import LLMClient

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
        step_id:           Current task identifier (same scope as Task Stack ``step_id``).
        typed_input:       The same Pydantic typed input that the LLM pipeline
                           received. Materializers read whatever fields they
                           need from it (e.g. ``typed_input.shot_stills``,
                           ``typed_input.final_video_path``). The materializer
                           never reaches back to the resolved-artifacts dict
                           directly — every data dependency must already be
                           expressed as a field on the agent's typed input.
        persist_binary:    Callback that saves a ``MediaAsset`` to disk and
                           returns the URI string of the saved file.
        report_failure:    Optional callback that records a per-call
                           materialize failure to the workspace event log
                           (``logs.jsonl``). Materializers call it from
                           inside their ``except`` blocks so silent
                           swallowed errors become findable in post-hoc
                           analysis. Signature:
                           ``report_failure(*, kind: str, sys_id: str, error: str)``.
                           When ``None``, materializers fall back to
                           Python's ``logger.error`` only.
    """

    step_id: str
    typed_input: BaseModel
    persist_binary: Callable[[MediaAsset], str]
    report_failure: Optional[Callable[..., None]] = None


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

      1. ``generate()`` — agent-owned generation flow (zero, one, or many
         LLM calls; skeleton building; creative merging — entirely up to
         the subclass).
      2. L1+L2 evaluation (structural + creative) via ``self.evaluator``
      3. Materialization via ``self.materializer`` (media agents only)
      4. L3 asset evaluation (post-materialization, media agents only)
      5. Retry loop with rework-notes feedback on failure

    The evaluator and materializer are injected as attributes (typically
    by ``SubAgentDescriptor.build_equipped_agent()``).  When ``None``,
    the corresponding steps are skipped — making the agent usable in
    lightweight environments without quality infrastructure.

    Subclasses must implement:
      - generate(input_data, *, rework_notes=""): produce the typed output.
        Each subclass owns its generation logic — there is NO framework-
        level dispatch between "skeleton mode" and "legacy mode" anymore.
        Subclasses are free to call zero LLM calls (LLM-free deterministic
        skeleton), one LLM call (full generation or creative-only fill),
        or compose helpers in any other way.

    Optional helpers (subclasses may use them from generate()):
      - ``_llm_fill_full(input_data, rework_notes)``: full-output LLM call.
        Requires the subclass to also implement ``build_user_prompt`` and
        ``system_prompt``.
      - ``_llm_fill_creative(input_data, skeleton, rework_notes)``: LLM
        fills only creative fields, merged into a pre-built skeleton.
        Requires the subclass to also implement ``build_creative_prompt``,
        ``fill_creative``, and ``system_prompt``.

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
        """Return the full system prompt for any LLM calls this agent makes.

        Required only when ``generate()`` calls ``_llm_fill_full`` or
        ``_llm_fill_creative``. LLM-free agents (e.g. VideoAgent) don't
        need to override this.
        """
        raise NotImplementedError(f"{self.agent_name}.system_prompt()")

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
    # Generation contract — subclasses MUST implement generate()
    # ------------------------------------------------------------------

    async def generate(
        self,
        input_data: InputT,
        *,
        rework_notes: str = "",
    ) -> OutputT:
        """Produce the agent's typed output.

        Each subclass owns its generation flow. There is no framework-
        level dispatch between "skeleton mode" / "legacy mode" anymore;
        subclasses pick how to generate and may call any of the helpers
        below or do something custom.

        Args:
            input_data: The agent's typed input.
            rework_notes: Optional retry hint from a failed evaluation
                          attempt; subclasses may incorporate it into the
                          LLM prompt to address feedback.

        Returns:
            A fully populated typed output. Subclasses that have metrics
            fields should call ``self.recompute_metrics(output)`` before
            returning so derived counts stay consistent.
        """
        raise NotImplementedError(f"{self.agent_name}.generate()")

    # ------------------------------------------------------------------
    # Optional generation helpers — subclasses may use these from generate()
    # ------------------------------------------------------------------

    async def _llm_fill_full(
        self,
        input_data: InputT,
        rework_notes: str = "",
    ) -> OutputT:
        """Helper: ask the LLM to generate the entire output JSON.

        Subclasses that use this must also implement
        ``system_prompt()`` and ``build_user_prompt(input_data)``.
        Returned output is parsed via ``parse_output()`` but
        ``recompute_metrics`` is NOT called — the caller (``generate()``)
        decides when (and whether) to recompute.
        """
        system = self.system_prompt()
        user = self.build_user_prompt(input_data)
        if rework_notes:
            user += self._rework_section(rework_notes)
            logger.info(
                "[%s] Rework notes injected (%d chars)",
                self.agent_name,
                len(rework_notes),
            )
        logger.debug("[%s] System prompt length: %d", self.agent_name, len(system))
        logger.debug("[%s] User prompt length: %d", self.agent_name, len(user))
        raw_json = await self.llm.chat_json(system, user)
        logger.info("[%s] Received LLM response, parsing …", self.agent_name)
        # Strip metrics before parsing — LLM may echo "<SYSTEM_COMPUTED>"
        # placeholders which fail Pydantic type validation.  Defaults (0/0.0)
        # are safe because subclasses call recompute_metrics afterwards.
        if "metrics" in raw_json:
            raw_json["metrics"] = {}
        return self.parse_output(raw_json)

    async def _llm_fill_creative(
        self,
        input_data: InputT,
        skeleton: OutputT,
        rework_notes: str = "",
    ) -> OutputT:
        """Helper: ask the LLM to fill only creative fields, merge into skeleton.

        Subclasses that use this must also implement ``system_prompt()``,
        ``build_creative_prompt(input_data, skeleton)``, and
        ``fill_creative(skeleton, creative_dict)``.
        """
        system = self.system_prompt()
        user = self.build_creative_prompt(input_data, skeleton)
        if rework_notes:
            user += self._rework_section(rework_notes)
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
        return self.fill_creative(skeleton, creative_json)

    @staticmethod
    def _rework_section(rework_notes: str) -> str:
        return (
            "\n\n--- REWORK INSTRUCTIONS (from quality review) ---\n"
            f"{rework_notes}\n"
            "--- END REWORK INSTRUCTIONS ---\n"
            "Apply the above fixes while preserving everything else."
        )

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def run(
        self,
        input_data: InputT,
        *,
        rework_notes: str = "",
        max_retries: int = 3,
        materialize_ctx: MaterializeContext | None = None,
    ) -> ExecutionResult:
        """Execute the agent with built-in quality gate and retry loop.

        Orchestrates generation, evaluation (L1+L2+L3), optional
        materialization, and retries — returning a single
        ``ExecutionResult``.

        Quality gate flow per attempt:
          1. ``self.generate()`` — subclass-owned generation (any mix
             of LLM calls, deterministic skeleton building, etc.)
          2. ``evaluator.evaluate()`` — L1 structural + L2 creative
          3. ``materializer.materialize()`` — binary asset generation
             (only if materializer is set and ``materialize_ctx`` provided)
          4. ``evaluator.evaluate_asset()`` — L3 post-materialization
          5. On any failure: feed eval summary as rework_notes and retry

        Args:
            input_data:      Typed agent input payload — the SINGLE source
                             of input for the agent. There is no second
                             "wide bundle" channel; everything the LLM
                             pipeline and the materializer need must be
                             expressed as fields on ``input_data``.
            rework_notes:    Initial rework instructions (e.g. from the
                             Director when action is ``"regenerate"``).
            max_retries:     Total attempts before giving up.
            materialize_ctx: External infrastructure for binary persistence.
                             ``None`` skips materialization and L3. The
                             materializer reads ``ctx.typed_input`` to get
                             the same input the LLM pipeline received.
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

            # --- Step 1: Generate (subclass-owned flow) ---
            output = await self.generate(input_data, rework_notes=rework_notes)

            # --- Step 2: L1+L2 evaluation (structural + creative) ---
            if self.evaluator is not None:
                try:
                    eval_result = await self.evaluator.evaluate(output)
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
                        materialize_ctx,
                        asset_dict,
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
                        asset_eval = await self.evaluator.evaluate_asset(asset_dict)
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

