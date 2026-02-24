"""Assistant — execution engine for the DirectorAgent-driven pipeline.

Assistant is the **execution engine** — it does not decide *what* to run
or *in what order*.  That responsibility belongs to DirectorAgent, which
calls ``execute_step()`` one step at a time based on LLM-driven planning and
review.

What Assistant owns:
  1. **Agent invocation** — dispatches to the correct sub-agent via
     ``AGENT_REGISTRY`` descriptors.
  2. **Per-agent quality gate (three layers, unified retry):**
     - Layer 1 — ``check_structure()``: rule-based structural checks (fast,
       deterministic, free).
     - Layer 2 — ``evaluate_creative()``: LLM-based creative assessment.
     - Layer 3 — ``evaluate_asset()``: post-materialization media quality
       checks (image/video/audio success rates, format compliance, etc.).
     All three layers share a unified retry budget (up to
     ``max_per_agent_retries``).  If any layer fails, the entire step is
     retried from scratch (new LLM call, new materialization).  Retries
     exhausted raises ``AgentQualityError``.
  3. **Persist-per-step** — every asset is saved to disk immediately after
     the agent produces it (crash-safe).
  4. **Media materialization** — after Layers 1+2 pass, delegates to the
     agent's co-located ``BaseMaterializer`` (if any).  The materializer
     returns ``list[MediaAsset]`` (pure data); Assistant saves each
     binary via ``AssetManager.save_binary()`` and writes URIs back.

Design principles:
  - Assistant discovers agents from ``AGENT_REGISTRY`` — zero hardcoded
    agent-specific logic.  Adding a new agent requires no edits here.
  - Assistant decides **when** and **what** to persist.
  - AssetManager decides **how** to persist (file I/O, versioning).
  - Sub-agents are pure generators: input -> LLM -> output.
  - Evaluators handle all quality checks (structural + creative + asset).
  - Agents NEVER access AssetManager directly.
  - All inputs flow through the ``assets`` dict — no input type is
    special-cased.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Callable, Coroutine

from pydantic import BaseModel

from src.sub_agent import AGENT_REGISTRY, AGENT_NAME_TO_ASSET_KEY
from src.sub_agent.base_evaluator import BaseEvaluator
from src.sub_agent.descriptor import MediaAsset
from src.direction.director_agent import DirectorAgent
from src.direction.director_schema import (
    PipelineConfig,
    RoutingStep,
    StepResult,
)
from src.utils.llm_client import LLMClient
from src.utils.asset_manager import AssetManager

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class AgentQualityError(Exception):
    """Raised when an agent exhausts all per-agent retries and still fails.

    This is a **hard failure** — the pipeline aborts immediately because
    downstream agents should never run on a known-bad upstream asset.

    Attributes:
        agent_name: Name of the agent that failed (e.g. ``"StoryboardAgent"``).
        attempts:   Number of attempts made before giving up.
        last_eval:  The evaluation result dict from the last attempt.
    """

    def __init__(
        self,
        agent_name: str,
        attempts: int,
        last_eval: dict[str, Any] | None = None,
    ) -> None:
        self.agent_name = agent_name
        self.attempts = attempts
        self.last_eval = last_eval or {}
        summary = self.last_eval.get("summary", "no summary")
        super().__init__(
            f"{agent_name} failed quality gate after {attempts} attempt(s): "
            f"{summary}"
        )


class Assistant:
    """Step executor for the DirectorAgent-driven pipeline.

    Assistant does not decide *what* to run or *in what order*.
    DirectorAgent calls ``execute_step()`` one step at a time.

    All agent-specific logic is encapsulated in ``AGENT_REGISTRY``
    descriptors.  Assistant operates generically via the descriptor
    interface: ``build_input()``, ``build_upstream()``, and
    ``materializer.materialize()``.

    **On-demand creation:** ``__init__`` stores only shared infrastructure
    (LLMClient, AssetManager, services_override).  Agents, evaluators,
    materializers, and services are created on-demand inside
    ``execute_step()`` from the descriptor — no pre-creation, no caching.
    All components are lightweight (attribute assignment only), so
    creating them per-step has negligible cost.

    Asset flow (persist-per-step):
        Agent output (content + metrics) -> _persist_step (injects _build_meta)
        -> in-memory cache + disk.  Next agent reads from in-memory cache (fast path)
        Resume       <- reads from disk via load_project_assets (recovery path)

    Unified three-layer quality gate (per-agent, single retry budget):
        for attempt in 1..max_per_agent_retries:
            Agent -> evaluator.evaluate() (L1+L2)
                |-- FAIL -> retry
                +-- PASS -> materialize (if media agent)
                            |-- ERROR -> retry
                            +-- OK -> evaluator.evaluate_asset() (L3)
                                      |-- FAIL -> retry
                                      +-- PASS -> done
        All retries exhausted -> AgentQualityError
    """

    def __init__(
        self,
        llm_client: LLMClient | None = None,
        asset_manager: AssetManager | None = None,
        services_override: dict[str, Any] | None = None,
    ) -> None:
        self.llm = llm_client or LLMClient()
        self.asset_mgr = asset_manager or AssetManager()
        self._services_override = services_override or {}
        self._svc_ctx: dict[str, Any] = {"llm_client": self.llm}
        self.director = DirectorAgent(llm_client=self.llm)

    # ------------------------------------------------------------------
    # On-demand component creation from descriptors
    # ------------------------------------------------------------------

    def _build_services(self, desc: Any) -> dict[str, Any]:
        """Build the services dict needed by a descriptor's materializer.

        For each service key declared in ``desc.service_factories``:
          - Use the override if one was provided at construction time.
          - Otherwise create via the descriptor's factory.

        Returns a dict suitable for passing to ``materializer_factory``.
        """
        services: dict[str, Any] = {}
        for svc_key, svc_factory in desc.service_factories.items():
            if svc_key in self._services_override:
                services[svc_key] = self._services_override[svc_key]
            else:
                services[svc_key] = svc_factory(self._svc_ctx)
        return services

    # ------------------------------------------------------------------
    # Meta building — system-authoritative asset metadata
    # ------------------------------------------------------------------

    def _build_meta(
        self,
        *,
        project_id: str,
        draft_id: str,
        asset_type: str,
        agent_name: str,
        iteration: int,
    ) -> tuple[str, dict[str, str]]:
        """Build a system-generated meta dict (LLM never produces this).

        Returns ``(asset_id, meta_dict)``.
        """
        version = self.asset_mgr.next_version(project_id, asset_type, iteration)
        asset_id = AssetManager.generate_asset_id(
            asset_type=asset_type,
            iteration=iteration,
            version=version,
        )
        meta = {
            "project_id": project_id,
            "draft_id": draft_id,
            "asset_id": asset_id,
            "asset_type": asset_type,
            "schema_version": "0.3",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_by_agent": agent_name,
            "language": "en",
        }
        return asset_id, meta

    # ------------------------------------------------------------------
    # Persist-per-step — save immediately after each agent
    # ------------------------------------------------------------------

    def _persist_step(
        self,
        assets: dict[str, Any],
        asset_key: str,
        output: BaseModel,
        *,
        project_id: str,
        draft_id: str,
        asset_type: str,
        agent_name: str,
        iteration: int,
    ) -> str:
        """Build meta, persist to disk, update in-memory cache, return asset_id.

        Meta is injected by the system — LLM output never contains it.

        This is called after every agent step to ensure:
          1. The asset is on disk immediately (crash-safe).
          2. The in-memory ``assets`` dict stays current (fast path for next agent).
        """
        aid, meta = self._build_meta(
            project_id=project_id,
            draft_id=draft_id,
            asset_type=asset_type,
            agent_name=agent_name,
            iteration=iteration,
        )

        asset_dict = output.model_dump(exclude={"meta"})
        asset_dict["meta"] = meta

        self.asset_mgr.save_asset(project_id, aid, asset_dict)
        logger.info("[%s] Persisted %s -> disk", agent_name, aid)

        assets[asset_key] = asset_dict

        return aid

    # ------------------------------------------------------------------
    # Quality gate — per-agent retry loop
    # ------------------------------------------------------------------

    async def _run_step_with_quality_gate(
        self,
        *,
        step_name: str,
        run_fn: Callable[[], Coroutine[Any, Any, BaseModel]],
        evaluator: BaseEvaluator | None,
        upstream_fn: Callable[[], dict[str, Any] | None],
        assets: dict[str, Any],
        asset_key: str,
        project_id: str,
        draft_id: str,
        asset_type: str,
        agent_name: str,
        iteration: int,
        max_retries: int,
        materialize_fn: Callable[[], Coroutine[Any, Any, None]] | None = None,
    ) -> dict[str, Any] | None:
        """Run an agent step with unified quality gate retries (L1+L2+L3).

        All three evaluation layers share a single retry budget:
          - Layer 1+2: ``evaluator.evaluate()`` (structural + creative)
          - Layer 3: ``evaluator.evaluate_asset()`` (post-materialization)

        If any layer fails, the entire step is retried from scratch
        (new LLM call → new output → new materialization).  This ensures
        that materialization failures caused by problematic prompts can
        be recovered by regenerating the prompts.

        Args:
            materialize_fn: Optional async callable that materializes
                binary assets, saves them via AssetManager, and writes
                URIs back into ``assets[asset_key]``.  ``None`` for
                non-media agents.

        Returns the evaluation result dict, or ``None`` if the step was
        skipped (asset already exists).

        Raises:
            AgentQualityError: If all retries are exhausted.
        """
        if asset_key in assets:
            logger.info("Skipping %s — asset already exists", step_name)
            return None

        eval_result: dict[str, Any] | None = None
        for attempt in range(1, max_retries + 1):
            logger.info(
                "[%s] Attempt %d/%d", step_name, attempt, max_retries
            )

            # 1. Run the agent (LLM generates JSON)
            output = await run_fn()

            # 2. Persist JSON immediately (URIs empty for media agents)
            self._persist_step(
                assets,
                asset_key,
                output,
                project_id=project_id,
                draft_id=draft_id,
                asset_type=asset_type,
                agent_name=agent_name,
                iteration=iteration,
            )

            # 3. Evaluate L1+L2 (structural + creative)
            if evaluator is None:
                eval_result = {
                    "overall_pass": True,
                    "summary": f"No evaluator registered for {step_name}.",
                }
            else:
                try:
                    upstream = upstream_fn()
                    eval_result = await evaluator.evaluate(output, upstream)
                except Exception as exc:
                    logger.error(
                        "[%s] Evaluation error on attempt %d: %s",
                        step_name, attempt, exc,
                    )
                    eval_result = {
                        "overall_pass": True,
                        "summary": f"Evaluation error: {exc}",
                    }

            if not eval_result.get("overall_pass", False):
                logger.warning(
                    "[%s] L1+L2 FAILED (attempt %d/%d): %s",
                    step_name,
                    attempt,
                    max_retries,
                    eval_result.get("summary", "no summary"),
                )
                if attempt < max_retries:
                    assets.pop(asset_key, None)
                continue

            # 4. Materialize media (if applicable)
            if materialize_fn is not None:
                try:
                    await materialize_fn()
                except Exception as exc:
                    logger.warning(
                        "[%s] Materialization failed (attempt %d/%d): %s",
                        step_name, attempt, max_retries, exc,
                    )
                    eval_result = {
                        "overall_pass": False,
                        "summary": f"Materialization error: {exc}",
                    }
                    if attempt < max_retries:
                        assets.pop(asset_key, None)
                    continue

                # 5. Evaluate L3 (post-materialization asset checks)
                if evaluator is not None:
                    try:
                        upstream = upstream_fn()
                        asset_eval = await evaluator.evaluate_asset(
                            assets[asset_key], upstream,
                        )
                    except Exception as exc:
                        logger.error(
                            "[%s] Asset evaluation error: %s",
                            step_name, exc,
                        )
                        asset_eval = {
                            "overall_pass": True,
                            "summary": f"Asset evaluation error: {exc}",
                        }

                    if not asset_eval.get("overall_pass", True):
                        logger.warning(
                            "[%s] L3 asset eval FAILED (attempt %d/%d): %s",
                            step_name,
                            attempt,
                            max_retries,
                            asset_eval.get("summary", "no summary"),
                        )
                        eval_result = asset_eval
                        if attempt < max_retries:
                            assets.pop(asset_key, None)
                        continue

            # ALL layers PASSED
            logger.info(
                "[%s] Quality gate PASSED (attempt %d)", step_name, attempt
            )
            return eval_result

        # All retries exhausted — HARD FAILURE.
        logger.error(
            "[%s] Max retries (%d) exhausted — aborting pipeline",
            step_name,
            max_retries,
        )
        raise AgentQualityError(
            agent_name=step_name,
            attempts=max_retries,
            last_eval=eval_result,
        )

    # ------------------------------------------------------------------
    # Load / Resume — read existing assets from disk
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Generic step executor (used by DirectorAgent.direct)
    # ------------------------------------------------------------------

    @staticmethod
    def agent_name_to_asset_key(agent_name: str) -> str:
        """Map an agent name to its asset cache key."""
        return AGENT_NAME_TO_ASSET_KEY.get(agent_name, "")

    async def execute_step(
        self,
        step: RoutingStep,
        assets: dict[str, Any],
        project_id: str,
        draft_id: str,
        iteration: int,
        config: PipelineConfig,
    ) -> StepResult:
        """Execute a single pipeline step as directed by DirectorAgent.

        Dispatches to the correct agent via ``AGENT_REGISTRY``, runs
        the unified quality gate (L1+L2+L3 with shared retry budget),
        and returns a ``StepResult``.

        Args:
            step: The routing step describing which agent to run.
            assets: In-memory asset cache (read + written).
            project_id: Current project ID.
            draft_id: Current draft ID.
            iteration: Global iteration counter.
            config: Pipeline configuration.

        Returns:
            ``StepResult`` with agent output, evaluation, and pass/fail.
        """
        agent_name = step.agent_name
        desc = AGENT_REGISTRY.get(agent_name)
        if desc is None:
            logger.error("Unknown agent name in step: %s", agent_name)
            return StepResult(
                agent_name=agent_name,
                passed=False,
                eval_result={"error": f"Unknown agent: {agent_name}"},
            )

        asset_key = desc.asset_key
        rework_notes = step.reason if step.action == "regenerate" else ""

        agent = desc.agent_factory(self.llm)
        evaluator = desc.evaluator_factory()

        async def run_fn(_rn: str = rework_notes) -> BaseModel:
            input_data = desc.build_input(project_id, draft_id, assets, config)
            return await agent.run(input_data, rework_notes=_rn)

        def upstream_fn() -> dict[str, Any] | None:
            return desc.build_upstream(assets)

        _materialize_fn = None
        if desc.materializer_factory is not None:
            async def _do_materialize() -> None:
                services = self._build_services(desc)
                materializer = desc.materializer_factory(services)
                media_results: list[MediaAsset] = await materializer.materialize(
                    project_id, assets[asset_key], assets,
                )
                for media in media_results:
                    path = self.asset_mgr.save_binary(
                        project_id, media.sys_id, media.data, media.extension,
                    )
                    media.uri_holder["uri"] = str(path)
                aid = assets[asset_key]["meta"]["asset_id"]
                self.asset_mgr.save_asset(project_id, aid, assets[asset_key])

            _materialize_fn = _do_materialize

        try:
            eval_result = await self._run_step_with_quality_gate(
                step_name=agent_name,
                run_fn=run_fn,
                evaluator=evaluator,
                upstream_fn=upstream_fn,
                assets=assets,
                asset_key=asset_key,
                project_id=project_id,
                draft_id=draft_id,
                asset_type=desc.asset_type,
                agent_name=agent_name,
                iteration=iteration,
                max_retries=config.max_per_agent_retries,
                materialize_fn=_materialize_fn,
            )
        except AgentQualityError as exc:
            logger.error("execute_step: %s failed quality gate: %s", agent_name, exc)
            return StepResult(
                agent_name=agent_name,
                asset_key=asset_key,
                eval_result=exc.last_eval,
                passed=False,
            )

        return StepResult(
            agent_name=agent_name,
            asset_key=asset_key,
            asset_data=assets.get(asset_key, {}),
            eval_result=eval_result or {},
            passed=True,
        )
