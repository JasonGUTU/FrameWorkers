#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# One-command regression for core backend/director/agent paths.
python3 -m pytest \
  tests/assistant/test_assistant_*.py \
  tests/director/test_director_plan.py \
  tests/director/test_director_backend_integration.py \
  tests/dynamic_task_stack/test_app_factory_unit.py \
  tests/dynamic_task_stack/test_plan_stack_http_integration.py \
  tests/agents/test_agent_core.py \
  tests/agents/test_phase2_guards.py \
  -v
