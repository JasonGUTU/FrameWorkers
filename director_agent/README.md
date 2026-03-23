# Director Agent

Director Agent is responsible for reasoning, planning, and task orchestration in the FrameWorkers system.

## Overview

The Director Agent:
1. Monitors user messages and task stack status
2. Performs reasoning and planning
3. Delegates tasks to Assistant Agent
4. Receives execution summaries
5. Triggers reflection phase
6. Updates task stack based on results

## Architecture

```
Director Agent
├── api_client.py      # HTTP client for backend API
├── reasoning.py       # Reasoning and planning engine (placeholder)
├── director.py        # Main orchestration logic
├── config.py          # Configuration
└── main.py            # Entry point
```

## Flow

1. **Check User Messages**: Polls backend for new user messages
2. **Check Task Stack**: Gets current task stack and execution pointer
3. **Reasoning & Planning**: Performs reasoning to decide next actions
4. **Update Task Stack**: Creates/updates tasks based on planning
5. **Get Next Task**: Retrieves next task to execute
6. **Delegate to Assistant**: Sends task to Assistant Agent for execution
7. **Handle Execution Summary**: Processes execution results
8. **Trigger Reflection**: Initiates reflection phase
9. **Handle Reflection Summary**: Processes reflection results
10. **Re-plan**: Updates plan based on reflection

### Re-run Decision for Existing Tasks

When a new user message is linked to an existing `task_id`, Director chooses `execute_task` and reuses normal execution path (no dedicated overwrite branch):

- infer `preferred_agent_id` from user intent (keyword-based, or explicit `preferred_agent_id` / first `rerun_agents` item in JSON message content)
- select one agent and execute it for that task
- before execution, inspect workspace files for `task_id + agent_id`; if existing assets are found, enable overwrite control
- if no existing assets are found, execute as normal write mode

### Sequencing Rule for New User Needs

Director enforces strict sequencing for follow-up requirements:

- if any task is still `IN_PROGRESS`, Director does **not** consume unread user messages this cycle
- Director waits until Assistant finishes and writes execution result
- after completion, Director reads new user message, fetches latest execution summary of target task, and plans next step with both contexts

Assistant overwrite control used by Director:

```json
{
  "_assistant_control": {
    "overwrite_assets": true
  }
}
```

## Configuration

Set environment variables:

- `BACKEND_BASE_URL`: Backend API base URL (default: `http://localhost:5002`)
- `POLLING_INTERVAL`: Polling interval in seconds (default: `2.0`)
- `DIRECTOR_MEMORY_MODEL`: LLM used to summarize executions into **short-term** workspace memory entries (default: `google-ai-studio/gemini-2.5-flash`). Long-term preference extraction is disabled.
- `LOG_LEVEL`: Logging level (default: `INFO`)

## Usage

### Run Director Agent

```bash
python -m director_agent.main
```

Or:

```bash
python director_agent/main.py
```

### With Custom Configuration

```bash
BACKEND_BASE_URL=http://localhost:5002 \
POLLING_INTERVAL=1.0 \
python -m director_agent.main
```

## API Interactions

### Task Stack API

- `GET /api/messages/list` - Get user messages
- `GET /api/task-stack` - Get task stack
- `GET /api/task-stack/next` - Get next task
- `POST /api/tasks/create` - Create task (`description` must be an object)
- `POST /api/tasks/{task_id}/messages` - Push task-linked message (`content`, optional `sender_type`)
- `PUT /api/tasks/{task_id}/status` - Update task status
- `POST /api/execution-pointer/advance` - Advance execution pointer

### Assistant API

- `POST /api/assistant/execute` - Execute agent
- `GET /api/assistant/executions/task/{task_id}` - Get executions for task
- `GET /api/assistant/sub-agents` - Get available agents
- `GET /api/assistant/sub-agents/{agent_id}` - Get single agent metadata
- `GET /api/assistant/agents/{agent_id}/inputs` - Get agent descriptor summary (`asset_key` / `capabilities` / `description`; no JSON Schema placeholders)

### Assistant Workspace API

- `GET /api/assistant/workspace` - Workspace overview/summary
- `GET /api/assistant/workspace/summary` - Workspace counters
- `GET /api/assistant/workspace/files` - List files with filters
- `GET /api/assistant/workspace/files/{file_id}` - Get file metadata
- `GET /api/assistant/workspace/files/search` - Search files
- `GET /api/assistant/workspace/memory/entries` - Read structured memory entries
- `POST /api/assistant/workspace/memory/entries` - Write structured memory entries
- `GET /api/assistant/workspace/memory/brief` - Get STM brief for planning (`long_term` is always empty; backend no longer accepts `long_term_limit` query param)
- `GET /api/assistant/workspace/logs` - Query logs
- `GET /api/assistant/workspace/search` - Cross-source search

### Short-term memory (STM) hooks

Director persists workspace memory in one role:

- **Short-term memory (STM)**: execution summaries and optional `suggested_next_agent` hints, extracted by LLM from each execution result and written as `execution_summary` entries.

**Long-term memory (LTM)** is disabled end-to-end: the backend rejects `tier=long_term` writes, `/memory/brief` always returns `long_term: []`, and Director no longer extracts preferences from user messages or rewrites instructions with LTM.

## Development

### Reasoning Engine

The reasoning engine (`reasoning.py`) currently contains placeholder implementations. To implement actual reasoning:

1. Update `reason_and_plan()` method with your reasoning logic
2. Update `select_agent_for_task()` with agent selection logic
3. Update `should_trigger_reflection()` with reflection trigger logic

Current baseline behavior:
- `reason_and_plan()` returns `execute_task` for user messages that carry a `task_id` (or JSON content with `task_id`)
- `select_agent_for_task()` honors `task.description.preferred_agent_id` when available

### Adding New Features

1. Add new API methods to `api_client.py` if needed
2. Update `director.py` to use new features
3. Update `reasoning.py` if reasoning logic changes

Recent enhancements in `api_client.py`:
- Normalizes `/api/assistant/sub-agents` response into a flat `List[agent]` for reasoning.
- Adds explicit workspace helper methods so Director can inspect files/memory/logs and persist structured STM entries.
- Adds strict response-shape checks and a `BackendAPIError` for invalid/non-JSON backend responses.
- Uses structured memory APIs (`memory/entries`, `memory/brief`) for STM only (`long_term` disabled server-side).

## Notes

- Director Agent runs in a continuous loop, polling the backend
- It handles errors gracefully and continues running
- Use SIGINT or SIGTERM for graceful shutdown
- Make sure the backend is running before starting Director Agent
