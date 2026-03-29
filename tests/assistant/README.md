# Assistant HTTP E2E Tests

This directory contains end-to-end HTTP tests for the backend assistant APIs.

## Test variants

- `test_assistant_e2e_http_flow_covers_core_endpoints`:
  uses a dummy registry + dummy pipeline agent to validate backend orchestration
  without external model/network dependencies.
- `test_director_http_message_flow_supports_poll_and_read_ack`:
  simulates Director-side polling with `/api/messages/*` endpoints and verifies
  read-status acknowledgment flow over HTTP.
- `test_assistant_pipeline_http_flow_reuses_previous_agent_asset`:
  validates two-step pipeline chaining (`ProducerAgent` -> `ConsumerAgent`) via
  `/api/assistant/execute`, ensuring downstream agent receives upstream asset.
- `test_assistant_and_taskstack_http_contract_validation_errors`:
  checks API contract accuracy for common bad requests (missing fields/query,
  invalid enum values, invalid `top_k`) and expected status/error payload shape.
- `test_assistant_execute_returns_404_for_unknown_sub_agent`:
  ensures `/api/assistant/execute` returns `404` when `agent_id` is not in registry.
- `test_assistant_e2e_http_flow_with_real_agents`:
  runs the same `/api/tasks/create` -> `/api/assistant/execute` flow against
  multiple real agents from production `AGENT_REGISTRY` (currently
  `StoryAgent` + `ExamplePipelineAgent`) to validate status transitions and
  payload handling against a real model provider.
- `test_full_pipeline_live_http_flow_generates_about_one_minute_video`:
  runs a full live pipeline over HTTP (`StoryAgent` -> `ScreenplayAgent` ->
  `StoryboardAgent` -> `KeyFrameAgent` -> `VideoAgent` -> `AudioAgent`) from
  a draft idea and validates final duration is near one minute. To reduce media
  cost/latency while keeping end-to-end flow real, the test can trim generated
  screenplay/storyboard before media agents.

## Running live LLM test

The live test is opt-in and skipped by default.

Required environment variables:

- `FW_ENABLE_LIVE_LLM_TESTS=1`
- `OPENAI_API_KEY=<your key>`

Example:

```bash
FW_ENABLE_LIVE_LLM_TESTS=1 OPENAI_API_KEY=... pytest tests/assistant/test_assistant_http_e2e.py -k real_agents
```

Run full pipeline live e2e (opt-in, slow):

```bash
FW_ENABLE_LIVE_LLM_TESTS=1 FW_ENABLE_FULL_PIPELINE_E2E=1 pytest tests/assistant/test_full_pipeline_live_e2e.py -q -s
```

Run one-shot fal.ai smoke script (image + video + voice + mux):

```bash
FAL_API_KEY=... python tests/assistant/fal_one_shot_smoke.py
```

Optional flags:

- `--output-dir /absolute/path`
- `--workspace-dir /absolute/path/to/saved_workspace`
- `--shot-id sh_001`
- `--narration "custom narration text"` (optional override; defaults to linked screenplay blocks)

Replay saved simplified workspace (KeyFrame -> Video -> Audio):

```bash
conda activate frameworkers && python tests/assistant/replay_simplified_workspace_smoke.py
```

This script snapshots:
- `Runtime/live_e2e_outputs/workspace_global_20260320_105714_349207`

into:
- `Runtime/saved_workspaces/workspace_simplified_20260320_105714`

then runs media agents and writes replay summary under:
- `Runtime/saved_workspace_replay_outputs/debug/`

Default artifact location for this test:

- `Runtime/live_e2e_outputs/workspace_global_<id>/` (project root)

Persisted **binary media** from Assistant follow `artifacts/media/<sub_agent_id>/<video|audio|image|other>/…`; JSON snapshots remain under `artifacts/<asset_key>/…` (see `dynamic-task-stack/src/assistant/README.md`).

Optional override:

- `FW_LIVE_E2E_RUNTIME_DIR=/absolute/path/to/output_dir`

Optional duration bounds (seconds):

- `FW_PIPELINE_TARGET_SECONDS` (default `10`)
- `FW_PIPELINE_MIN_SECONDS` (default `8`)
- `FW_PIPELINE_MAX_SECONDS` (default `20`)

Optional media-stage trim knobs (applied after Storyboard, before KeyFrame):

- `FW_MEDIA_TRIM_SCENES` (default `0`; `<=0` means no scene trim)
- `FW_MEDIA_TRIM_SHOTS_PER_SCENE` (default `0`; `<=0` means no shot trim)
- `FW_MEDIA_TRIM_PREFER_CHARACTER_SHOTS` (default `1`, prioritize scenes/shots
  that include characters so KeyFrame output still covers character anchors)

This keeps Story/Screenplay/Storyboard fully real, then optionally narrows media
workload for `KeyFrameAgent` / `VideoAgent` / `AudioAgent` via the trim env vars
above (see `test_full_pipeline_live_e2e.py`; pipeline inputs are assembled by
Assistant — `execute_fields` + global_memory / LLM role selection — not passed as raw HTTP `assets`).

JSON response note:

- Media-heavy agent responses expose `_media_files` as a JSON-safe `dict` summary.
- Raw binary payloads are not returned directly in HTTP JSON; binary fields are
  normalized as metadata stubs (type + size) for traceability.

## Materializer temp artifacts

Temporary materializer files are cleaned automatically after execution.
