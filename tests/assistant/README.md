# Assistant HTTP E2E Tests

This directory contains end-to-end HTTP tests for the backend assistant APIs.

## Test variants

- `test_assistant_e2e_http_flow_covers_core_endpoints`:
  uses a dummy registry + dummy pipeline agent to validate backend orchestration
  without external model/network dependencies.
- `test_assistant_e2e_http_flow_with_real_agents`:
  runs the same `/api/tasks/create` -> `/api/assistant/execute` flow against
  multiple real agents from production `AGENT_REGISTRY` (currently
  `StoryAgent` + `ExamplePipelineAgent`) to validate status transitions and
  payload handling against a real model provider.

## Running live LLM test

The live test is opt-in and skipped by default.

Required environment variables:

- `FW_ENABLE_LIVE_LLM_TESTS=1`
- `OPENAI_API_KEY=<your key>`

Example:

```bash
FW_ENABLE_LIVE_LLM_TESTS=1 OPENAI_API_KEY=... pytest tests/assistant/test_assistant_http_e2e.py -k real_agents
```

## Optional temp artifact retention

When testing materializer-based agents, set this to keep temporary media files:

- `FW_KEEP_ASSISTANT_TEMP=1`

If enabled, execution results include `_materialize_temp_dir` for inspection.
