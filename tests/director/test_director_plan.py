"""Unit tests for the Upfront-plan Director (no live LLM, no live backend)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock

import pytest

_repo_root = Path(__file__).resolve().parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from director_agent import config as director_config
from director_agent.director import (
    DirectorAgent,
    _project_plan_stack_as_memory,
    _persist_plan,
    run_plan_pipeline,
)
from director_agent.router import (
    LlmSubAgentPlanner,
    PlanStepSpec,
    ReplanDecision,
    _agents_catalog_for_prompt,
    _allowed_ids,
    _parse_plan,
)


_CATALOG = [
    {"id": "StoryAgent", "description": "story"},
    {"id": "ScreenplayAgent", "description": "screenplay"},
    {"id": "KeyFrameAgent", "description": "keyframe"},
]


# ---------------------------------------------------------------------------
# Fake LLM + planner factory
# ---------------------------------------------------------------------------


class _FakeLLM:
    """Scripted async ``chat_json`` replacement for :class:`inference.clients.LLMClient`."""

    def __init__(self, payload):
        self.payload = payload
        self.calls: list[dict] = []

    async def chat_json(self, **kwargs):
        self.calls.append(kwargs)
        if isinstance(self.payload, Exception):
            raise self.payload
        return self.payload


def _planner(payload) -> LlmSubAgentPlanner:
    return LlmSubAgentPlanner(llm_client=_FakeLLM(payload))


# ---------------------------------------------------------------------------
# 1. _parse_plan helper
# ---------------------------------------------------------------------------


class TestParsePlan:
    def test_valid_plan(self):
        data = {
            "plan": [
                {"agent_id": "StoryAgent", "intent": "story"},
                {"agent_id": "ScreenplayAgent", "intent": "screenplay"},
            ]
        }
        out = _parse_plan(data, _allowed_ids(_CATALOG), max_steps=20)
        assert [s.agent_id for s in out] == ["StoryAgent", "ScreenplayAgent"]
        assert out[0].intent == "story"

    def test_filters_unknown_agent_ids(self):
        data = {
            "plan": [
                {"agent_id": "Unknown"},
                {"agent_id": "StoryAgent"},
            ]
        }
        out = _parse_plan(data, _allowed_ids(_CATALOG), max_steps=20)
        assert [s.agent_id for s in out] == ["StoryAgent"]

    def test_missing_plan_key(self):
        assert _parse_plan({}, _allowed_ids(_CATALOG), max_steps=20) == []

    def test_empty_plan_list(self):
        assert _parse_plan({"plan": []}, _allowed_ids(_CATALOG), max_steps=20) == []

    def test_respects_max_steps(self):
        data = {"plan": [{"agent_id": "StoryAgent"} for _ in range(5)]}
        out = _parse_plan(data, _allowed_ids(_CATALOG), max_steps=2)
        assert len(out) == 2


# ---------------------------------------------------------------------------
# 2. plan_pipeline_upfront
# ---------------------------------------------------------------------------


class TestPlanPipelineUpfront:
    def test_happy_path(self):
        p = _planner({
            "plan": [
                {"agent_id": "StoryAgent", "intent": "story"},
                {"agent_id": "ScreenplayAgent", "intent": "screenplay"},
            ],
            "rationale": "template",
        })
        plan = p.plan_pipeline_upfront(
            user_goal="make a film",
            available_agents=_CATALOG,
            stack_memory=[],
        )
        assert [s.agent_id for s in plan] == ["StoryAgent", "ScreenplayAgent"]

    def test_empty_catalog_short_circuits(self):
        p = _planner({"plan": [{"agent_id": "StoryAgent"}]})
        plan = p.plan_pipeline_upfront(
            user_goal="x",
            available_agents=[],
        )
        assert plan == []
        assert p._llm.calls == []

    def test_llm_exception_returns_empty_plan(self):
        p = _planner(RuntimeError("boom"))
        plan = p.plan_pipeline_upfront(
            user_goal="x",
            available_agents=_CATALOG,
        )
        assert plan == []

    def test_llm_non_dict_rejected(self):
        p = _planner("oops")
        plan = p.plan_pipeline_upfront(
            user_goal="x",
            available_agents=_CATALOG,
        )
        assert plan == []


# ---------------------------------------------------------------------------
# 3. merge_session_goal short-circuits (unchanged semantics from Markov era)
# ---------------------------------------------------------------------------


class TestMergeSessionGoal:
    def test_no_prior_no_memory_skips_llm(self):
        llm = _FakeLLM({"merged_goal": "SHOULD NOT BE USED"})
        p = LlmSubAgentPlanner(llm_client=llm)
        assert p.merge_session_goal(
            latest_user_message="  fresh brief  ",
            stack_memory=[],
        ) == "fresh brief"
        assert llm.calls == []

    def test_blank_latest_returns_empty(self):
        p = _planner({"merged_goal": "x"})
        assert p.merge_session_goal(
            latest_user_message="   ",
            stack_memory=[{"agent_id": "StoryAgent"}],
        ) == ""

    def test_memory_triggers_llm(self):
        llm = _FakeLLM({"merged_goal": "merged brief"})
        p = LlmSubAgentPlanner(llm_client=llm)
        out = p.merge_session_goal(
            latest_user_message="make shorter",
            stack_memory=[{"agent_id": "StoryAgent", "status": "COMPLETED"}],
        )
        assert out == "merged brief"
        assert len(llm.calls) == 1

    def test_llm_failure_falls_back_to_latest(self):
        p = _planner(RuntimeError("llm down"))
        assert p.merge_session_goal(
            latest_user_message="latest line",
            stack_memory=[{"agent_id": "StoryAgent"}],
        ) == "latest line"


# ---------------------------------------------------------------------------
# 4. replan_on_failure
# ---------------------------------------------------------------------------


class TestReplanOnFailure:
    def test_valid_plan(self):
        p = _planner({
            "plan": [{"agent_id": "ScreenplayAgent", "intent": "retry"}],
            "rationale": "new plan",
        })
        d = p.replan_on_failure(
            user_goal="g",
            available_agents=_CATALOG,
            failed_step={"step_id": "s1", "agent_id": "StoryAgent"},
            pending_tail=[],
            completed_tail=[],
        )
        assert [s.agent_id for s in d.new_tail] == ["ScreenplayAgent"]
        assert d.rationale == "new plan"

    def test_empty_plan_returns_empty_tail(self):
        p = _planner({"plan": []})
        d = p.replan_on_failure(
            user_goal="g",
            available_agents=_CATALOG,
            failed_step={"step_id": "s1", "agent_id": "StoryAgent"},
            pending_tail=[],
            completed_tail=[],
        )
        assert d.new_tail == []

    def test_no_plan_field_returns_empty_tail(self):
        p = _planner({"rationale": "nothing to do"})
        d = p.replan_on_failure(
            user_goal="g",
            available_agents=_CATALOG,
            failed_step={"step_id": "s1", "agent_id": "StoryAgent"},
            pending_tail=[],
            completed_tail=[],
        )
        assert d.new_tail == []

    def test_llm_exception_returns_empty_tail(self):
        p = _planner(RuntimeError("boom"))
        d = p.replan_on_failure(
            user_goal="g",
            available_agents=_CATALOG,
            failed_step={"step_id": "s1", "agent_id": "StoryAgent"},
            pending_tail=[],
            completed_tail=[],
        )
        assert d.new_tail == []


# ---------------------------------------------------------------------------
# 5. Fake Backend for full pipeline test
# ---------------------------------------------------------------------------


class _FakeBackend:
    """Minimal in-memory stand-in for the Flask backend.

    Supports enough surface area to drive ``run_plan_pipeline`` + the
    per-step execution loop without a real HTTP server.
    """

    def __init__(self, *, exec_status_chain: List[str] = None) -> None:
        self.exec_status_chain = list(exec_status_chain or ["COMPLETED"])
        self.messages: List[str] = []
        self._counter = 0
        self._steps: Dict[str, Dict[str, Any]] = {}
        self._layers: List[Dict[str, Any]] = []
        self._pointer: Optional[Dict[str, Any]] = None
        self.execute_calls: List[tuple[str, str]] = []
        self.updated_statuses: List[tuple[str, str]] = []

    # ---- Messages ----
    def list_messages(self):
        return []

    def create_message(self, content, sender_type="director"):
        self.messages.append(content)
        return {"id": f"msg_{len(self.messages)}"}

    # ---- Plan stack reads ----
    def get_plan_stack(self):
        return list(self._layers)

    def get_step(self, step_id):
        return self._steps.get(step_id)

    def get_execution_pointer(self):
        return self._pointer

    def get_next_step(self):
        if self._pointer is None:
            if not self._layers:
                return None
            self._pointer = {"current_layer_index": 0, "current_step_index": 0}
        li = self._pointer["current_layer_index"]
        si = self._pointer["current_step_index"]
        if li >= len(self._layers):
            return None
        layer = self._layers[li]
        steps = layer["steps"]
        if si >= len(steps):
            return None
        entry = steps[si]
        step_payload = self._steps.get(entry["step_id"])
        return {
            "layer_index": li,
            "step_index": si,
            "step_id": entry["step_id"],
            "step": step_payload,
            "layer": layer,
        }

    # ---- Plan stack writes ----
    def modify_plan_stack(self, operations):
        created_step_ids: List[str] = []
        created_layer_indices: List[int] = []
        errors = []
        for op in operations:
            op_type = op.get("type")
            params = op.get("params", {})
            if op_type == "create_steps":
                for step_desc in params.get("steps", []):
                    self._counter += 1
                    sid = f"step_{self._counter}_abc"
                    self._steps[sid] = {
                        "id": sid,
                        "description": step_desc.get("description", {}),
                        "status": "PENDING",
                        "progress": {},
                        "results": None,
                    }
                    created_step_ids.append(sid)
            elif op_type == "create_layers":
                for layer_cfg in params.get("layers", []):
                    li = layer_cfg.get("layer_index")
                    if li is None:
                        li = len(self._layers)
                    layer = {
                        "layer_index": li,
                        "steps": [],
                        "pre_hook": None,
                        "post_hook": None,
                    }
                    self._layers.append(layer)
                    created_layer_indices.append(li)
            elif op_type == "add_steps_to_layers":
                for add in params.get("additions", []):
                    li = add["layer_index"]
                    sid = add["step_id"]
                    self._layers[li]["steps"].append({"step_id": sid})
            elif op_type == "remove_steps_from_layers":
                for rem in params.get("removals", []):
                    li = rem["layer_index"]
                    sid = rem["step_id"]
                    self._layers[li]["steps"] = [
                        e for e in self._layers[li]["steps"] if e["step_id"] != sid
                    ]
            else:
                errors.append({"op": op_type, "error": "unsupported in fake"})
        return {
            "success": not errors,
            "errors": errors,
            "created_step_ids": created_step_ids,
            "created_layer_indices": created_layer_indices,
            "results": [],
        }

    def set_execution_pointer(self, *, layer_index, step_index, **kwargs):
        self._pointer = {
            "current_layer_index": layer_index,
            "current_step_index": step_index,
        }
        return dict(self._pointer)

    def advance_execution_pointer(self):
        if self._pointer is None:
            return {}
        li = self._pointer["current_layer_index"]
        si = self._pointer["current_step_index"]
        if li < len(self._layers):
            if si + 1 < len(self._layers[li]["steps"]):
                self._pointer["current_step_index"] = si + 1
                return dict(self._pointer)
        # move to next layer
        if li + 1 < len(self._layers):
            self._pointer = {"current_layer_index": li + 1, "current_step_index": 0}
            return dict(self._pointer)
        # exhausted
        self._pointer["current_step_index"] = si + 1  # off-end; get_next_step returns None
        return dict(self._pointer)

    def update_step_status(self, step_id, status):
        self.updated_statuses.append((step_id, status))
        if step_id in self._steps:
            self._steps[step_id]["status"] = status
        return self._steps.get(step_id)

    def execute_agent(self, agent_id, step_id):
        self.execute_calls.append((agent_id, step_id))
        status = self.exec_status_chain.pop(0) if self.exec_status_chain else "COMPLETED"
        return {
            "id": f"exec_{len(self.execute_calls)}",
            "agent_id": agent_id,
            "step_id": step_id,
            "status": status,
            "error": "bad" if status == "FAILED" else None,
        }


# ---------------------------------------------------------------------------
# 6. run_plan_pipeline end-to-end
# ---------------------------------------------------------------------------


class TestRunPlanPipeline:
    def test_happy_path_plans_persists_and_executes(self):
        backend = _FakeBackend(exec_status_chain=["COMPLETED", "COMPLETED"])
        planner = MagicMock()
        planner.merge_session_goal.return_value = "merged"
        planner.plan_pipeline_upfront.return_value = [
            PlanStepSpec("StoryAgent", "intake text"),
            PlanStepSpec("StoryAgent", "write story"),
        ]

        run_plan_pipeline(
            backend,
            planner,
            agents=_CATALOG,
            user_goal="make me a film",
            current_user_message_id="m1",
        )

        assert backend.execute_calls == [
            ("StoryAgent", backend.execute_calls[0][1]),
            ("StoryAgent", backend.execute_calls[1][1]),
        ]
        # Both step ids should be distinct and each marked COMPLETED at the end.
        completed = [s for (s, st) in backend.updated_statuses if st == "COMPLETED"]
        assert len(completed) == 2
        # And the Plan Stack now has one layer with two steps.
        assert len(backend._layers) == 1
        assert len(backend._layers[0]["steps"]) == 2

    def test_empty_plan_aborts_before_modify(self):
        backend = _FakeBackend()
        planner = MagicMock()
        planner.merge_session_goal.return_value = "merged"
        planner.plan_pipeline_upfront.return_value = []

        run_plan_pipeline(
            backend,
            planner,
            agents=_CATALOG,
            user_goal="x",
            current_user_message_id="m1",
        )

        assert backend.execute_calls == []
        assert backend._layers == []
        assert any("no plan" in m.lower() for m in backend.messages)

    def test_blank_goal_returns_early(self):
        backend = _FakeBackend()
        planner = MagicMock()
        run_plan_pipeline(
            backend,
            planner,
            agents=_CATALOG,
            user_goal="   ",
            current_user_message_id="m1",
        )
        planner.merge_session_goal.assert_not_called()
        planner.plan_pipeline_upfront.assert_not_called()
        assert backend.execute_calls == []

    def test_failed_status_halts_when_replanner_disabled(self, monkeypatch):
        # MAX_REPLAN_ROUNDS=0 disables the replanner. With no recovery
        # mechanism available the executor must halt on the first FAILED
        # step rather than silently advancing past it.
        monkeypatch.setattr(director_config, "MAX_REPLAN_ROUNDS", 0)
        backend = _FakeBackend(exec_status_chain=["FAILED", "COMPLETED"])
        planner = MagicMock()
        planner.merge_session_goal.return_value = "merged"
        planner.plan_pipeline_upfront.return_value = [
            PlanStepSpec("StoryAgent", "intake"),
            PlanStepSpec("StoryAgent", "story"),
        ]

        run_plan_pipeline(
            backend,
            planner,
            agents=_CATALOG,
            user_goal="x",
            current_user_message_id="m1",
        )

        statuses = [st for (_sid, st) in backend.updated_statuses]
        assert "FAILED" in statuses
        assert "COMPLETED" not in statuses
        assert len(backend.execute_calls) == 1
        assert any("halted" in m.lower() for m in backend.messages)

    def test_failed_status_halts_when_replanner_returns_empty(self, monkeypatch):
        # Replanner enabled (budget > 0) but produces no actionable tail —
        # the executor must still halt, not advance.
        monkeypatch.setattr(director_config, "MAX_REPLAN_ROUNDS", 2)
        backend = _FakeBackend(exec_status_chain=["FAILED", "COMPLETED"])
        planner = MagicMock()
        planner.merge_session_goal.return_value = "merged"
        planner.plan_pipeline_upfront.return_value = [
            PlanStepSpec("StoryAgent", "intake"),
            PlanStepSpec("StoryAgent", "story"),
        ]
        planner.replan_on_failure.return_value = ReplanDecision(
            new_tail=[], rationale="cannot recover"
        )

        run_plan_pipeline(
            backend,
            planner,
            agents=_CATALOG,
            user_goal="x",
            current_user_message_id="m1",
        )

        assert len(backend.execute_calls) == 1
        assert any("halted" in m.lower() for m in backend.messages)
        planner.replan_on_failure.assert_called_once()


# ---------------------------------------------------------------------------
# 7. _project_plan_stack_as_memory
# ---------------------------------------------------------------------------


class TestProjectStackMemory:
    def test_empty_stack_yields_empty(self):
        backend = _FakeBackend()
        assert _project_plan_stack_as_memory(backend, window=20) == []

    def test_projects_each_step(self):
        backend = _FakeBackend()
        resp = backend.modify_plan_stack([
            {"type": "create_steps", "params": {"steps": [
                {"description": {"agent_id": "StoryAgent", "intent": "intake"}},
                {"description": {"agent_id": "StoryAgent", "intent": "story"}},
            ]}},
            {"type": "create_layers", "params": {"layers": [{"layer_index": 0}]}},
        ])
        created = resp["created_step_ids"]
        backend.modify_plan_stack([
            {"type": "add_steps_to_layers", "params": {"additions": [
                {"layer_index": 0, "step_id": created[0]},
                {"layer_index": 0, "step_id": created[1]},
            ]}},
        ])
        out = _project_plan_stack_as_memory(backend, window=20)
        assert len(out) == 2
        assert out[0]["agent_id"] == "StoryAgent"
        assert out[1]["agent_id"] == "StoryAgent"


# ---------------------------------------------------------------------------
# 8. DirectorAgent._cycle guards
# ---------------------------------------------------------------------------


class TestCycleGuards:
    def test_no_unread_does_not_plan(self):
        client = MagicMock()
        client.get_unread_messages.return_value = []
        planner = MagicMock()
        DirectorAgent(client=client, planner=planner)._cycle()
        planner.merge_session_goal.assert_not_called()
        planner.plan_pipeline_upfront.assert_not_called()
        client.execute_agent.assert_not_called()

    def test_empty_agents_catalog_short_circuits(self):
        client = MagicMock()
        client.get_unread_messages.return_value = [{"id": "m1", "content": "hi"}]
        client.get_all_agents.return_value = []
        planner = MagicMock()
        DirectorAgent(client=client, planner=planner)._cycle()
        client.update_message_read_status.assert_called_once()
        planner.plan_pipeline_upfront.assert_not_called()
        client.execute_agent.assert_not_called()

    def test_blank_message_content_does_not_plan(self):
        client = MagicMock()
        client.get_unread_messages.return_value = [{"id": "m1", "content": "   "}]
        planner = MagicMock()
        DirectorAgent(client=client, planner=planner)._cycle()
        client.update_message_read_status.assert_called_once()
        planner.plan_pipeline_upfront.assert_not_called()
        client.execute_agent.assert_not_called()


# ---------------------------------------------------------------------------
# 9. Catalog normalization
# ---------------------------------------------------------------------------


class TestCatalogNormalization:
    def test_filters_non_dict_entries(self):
        out = _agents_catalog_for_prompt([
            {"id": "A"},
            "not a dict",
            None,
        ])
        assert [x["id"] for x in out] == ["A"]

    def test_filters_blank_ids(self):
        out = _agents_catalog_for_prompt([
            {"id": "A"},
            {"id": ""},
            {"id": "   "},
        ])
        assert [x["id"] for x in out] == ["A"]

    def test_allowed_ids_matches_catalog_order(self):
        assert _allowed_ids([
            {"id": "A"},
            {"id": "B"},
            "junk",
        ]) == ["A", "B"]
