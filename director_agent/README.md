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
├── reasoning.py       # Task create vs execute_task vs wait + ``LlmSubAgentPlanner`` (LLM routing)
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

### Follow-up on an Existing Task (`task_id`)

When a user message is linked to an existing `task_id` (field on the message or JSON body with `"task_id"`), `reason_and_plan` returns `execute_task`. **Sub-agent selection** is done in `director.py` via **`LlmSubAgentPlanner.choose_for_followup`**: it sends the Assistant **sub-agent catalog** (`GET /api/assistant/sub-agents`), **`GET .../memory/brief`** rows for that task, the latest execution summary from `GET .../executions/task/{task_id}`, and the user message to an LLM, which must return JSON `{"agent_id":"<registered id>","rationale":"..."}`. Assistant may reuse/overwrite workspace assets for that `task_id` + `agent_id` as before.

### Sequencing Rule for New User Needs

Director enforces strict sequencing for follow-up requirements:

- if any task is still `IN_PROGRESS`, Director does **not** consume unread user messages this cycle
- Director waits until Assistant finishes and writes execution result
- after completion, Director reads new user message, fetches latest execution summary of target task, and plans next step with both contexts

## Assistant execute contract (Director ↔ Assistant)

Director talks to Assistant **only** via `POST /api/assistant/execute`. The JSON body has **`agent_id`**, **`task_id`**, and nested **`execute_fields`** (object). Pipeline **input assembly** (`input_bundle_v2`, global_memory brief, LLM role selection) and runtime **`config`** are Assistant-internal only — they are **not** HTTP fields. `BackendAPIClient.execute_agent()` sends `execute_fields` as a single nested object.

**Director must send (root-level keys):**

| Key | Required | Meaning |
|-----|----------|---------|
| `agent_id` | yes | Registry id = descriptor `agent_name` (e.g. `StoryAgent`). |
| `task_id` | yes | Task Stack task id (sole execution scope id). |
| `execute_fields` | yes* | JSON object; at minimum usually includes **`text`** = task `description` snapshot (`GET /api/tasks/{id}`). Assistant does **not** read Task Stack. |

\*An empty `{}` is valid; omitting `execute_fields` defaults to `{}` on the server.

**Inside `execute_fields` (optional keys):**

| Key | Meaning |
|-----|---------|
| `text` | **String** passed to Assistant. If Task Stack still stores ``description`` as a **dict** (current API), Director uses ``_task_stack_description_to_assistant_text()`` to turn it into one string (typically the ``goal`` line). When your product stores ``description`` as a **string**, Director passes it through unchanged. |
| `image` / `video` / `audio` | Optional reference strings (e.g. data URI or URL) merged into the Assistant-side input bundle **hints** for multimodal agents. |

**Response (200):** `task_id`（与请求一致）、`execution_id`（本次执行记录 id）、`status`, `results`, `error`, `workspace_id`。`agent_id` 仅在请求根级传入，响应不重复。Director **不再**在进程内补写 `task_id`。随后可再 `GET /api/assistant/executions/task/{task_id}` 取列表并在其中按 `id` 匹配该次执行。Errors: **400** / **404** / **500** with `{ "error": "..." }`.

**Assistant ↔ Sub-agent** (in-process `build_input` / `run` / result dict) is documented in `dynamic-task-stack/src/assistant/README.md` §3.5.

## Configuration

Set environment variables:

- `BACKEND_BASE_URL`: Backend API base URL (default: `http://localhost:5002`)
- `POLLING_INTERVAL`: Polling interval in seconds (default: `2.0`)
- `ASSISTANT_MEMORY_MODEL`: LLM used by **Assistant** to produce the text `content` for each new **global_memory** row (default: `INFERENCE_DEFAULT_MODEL` or `google-ai-studio/gemini-2.5-flash`). `DIRECTOR_MEMORY_MODEL` is a **legacy alias** for the same setting.
- `DIRECTOR_ROUTING_MODEL`: LLM used by **`LlmSubAgentPlanner`** to choose `agent_id` (defaults to `DIRECTOR_MEMORY_MODEL`). Requires `inference` on `PYTHONPATH` (install merged repo `requirements.txt` from the project root).
- `LOG_LEVEL`: Logging level (default: `INFO`)

## Usage

### Run Director Agent

```bash
python -m director_agent.main
```

Or:

```bash
python director_agent/run.py
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

- `POST /api/assistant/execute` - Execute agent (JSON: `agent_id`, `task_id`, `execute_fields`); full request/response shape: **Assistant execute contract** above and `dynamic-task-stack/src/assistant/README.md` §3.5
- `GET /api/assistant/executions/task/{task_id}` - Get executions for task
- `GET /api/assistant/sub-agents` - Get available agents

### Assistant Workspace API

- `GET /api/assistant/workspace/files` - List files with filters
- `GET /api/assistant/workspace/memory/entries` - Read structured memory entries
- `POST /api/assistant/workspace/memory/entries` - Write structured memory entries
- `GET /api/assistant/workspace/memory/brief` - Returns **`global_memory`** rows **without** `content` (all matches, `created_at` desc; Director uses `agent_id` / `created_at` / `execution_result` / optional **`artifact_locations`**).

### Global memory

**Assistant** owns writes: in `process_results` it appends **global_memory** entries (LLM `content`, optional **`artifact_locations`**, `agent_id`, `created_at`, **`execution_result`**) under **`Runtime/{workspace_id}/{task_id}/global_memory.md`**. Director **only reads** `GET /memory/brief` for planning — response rows omit `content`; it does not write rows.

The LLM router may use failed/success rows in `global_memory` implicitly when choosing the next agent; there is no separate keyword-based path.

## Development

### Sub-agent routing (`reasoning.py` — ``LlmSubAgentPlanner``)

Director must send a concrete `agent_id` on `POST /api/assistant/execute`. **`LlmSubAgentPlanner`** (LiteLLM via `inference.clients.LLMClient`) picks **one** id that appears in `GET /api/assistant/sub-agents`:

| Situation | Method | Prompt inputs |
|-----------|--------|----------------|
| Next task from the stack (`get_next_task`) | `choose_for_stack_task` | Task intent string (from task `description`) + agent catalog |
| User message bound to existing `task_id` | `choose_for_followup` | User message + task intent + **memory brief** + latest execution summary + catalog |

If routing fails (LLM error or invalid id), the task is marked `FAILED` in `director.py`.

### Reasoning engine (`reasoning.py`)

Only decides **create_task** vs **execute_task** (when `task_id` is present) vs **wait**. It does **not** choose `agent_id`.

To extend: adjust `reason_and_plan()` for stack mutations; customize routing in `LlmSubAgentPlanner` or inject a mock in tests via `DirectorAgent(sub_agent_planner=...)`.

### Reflection chain（当前为占位，与 LLM 选 agent 独立）

执行路径在 `_delegate_to_assistant` → `_handle_execution_summary` 之后，若 `ReasoningEngine.should_trigger_reflection(...)` 为真（**当前实现恒为 `True`**），会进入一条**本地「反思」流水线**——**不调用**独立 Reflection 服务或新 HTTP 端点，也与 **`LlmSubAgentPlanner`** 无关。

| 步骤 | 代码 | 行为 |
|------|------|------|
| 1 | `should_trigger_reflection` | 是否进入反思；恒 `True` 时每次执行后都会尝试 |
| 2 | `_trigger_reflection` | 用 `get_executions_by_task` 取**最新一条** execution，拼一个 **`reflection_summary` 字典**（`task_id`、`execution_id`、`status`、固定文案 `evaluation`、`recommendations: []`） |
| 3 | `_handle_reflection_summary` | **仅打日志**，不改栈、不写消息 |
| 4 | `reason_and_plan(reflection_summary=...)` | 有 `reflection_summary` 时返回 **`action: update_plan`**，且 **`task_updates` 为空** |
| 5 | `_update_task_stack_from_reflection` | 仅当 `task_updates` 非空时调用 `_create_tasks_from_planning`；当前几乎**不会**建任务 |

因此：**反思链目前是「形状预留」**：主流程的**规划与选 agent** 不依赖它；若要接真反思（LLM 评估、改栈、插入新任务），需要实现 `_trigger_reflection` / `reason_and_plan` 的 `update_plan` 分支或改为调用后端路由，并可考虑将 `should_trigger_reflection` 改为按规则/配置开关，避免每轮空转。

### Adding New Features

1. Add new API methods to `api_client.py` if needed
2. Update `director.py` to use new features
3. Update `reasoning.py` if reasoning logic changes

`api_client.py` scope: it only wraps HTTP endpoints that **Director** (`director.py`) or **unit tests** (`tests/director/test_director_api_client_unit.py`) call. Convenience methods for endpoints unused in-repo (for example full message list, single-message fetch/check, batch `modify_task_stack`, assistant singleton metadata, workspace file-by-id, logs listing) are omitted to avoid dead code; those routes remain on the backend and can be called with plain HTTP when needed.

Recent enhancements in `api_client.py`:
- Normalizes `/api/assistant/sub-agents` response into a flat `List[agent]` for reasoning.
- Workspace: Director only needs **`GET .../memory/brief`** (`get_workspace_memory_brief`); listing files, fetching a single execution by id, and **`POST .../memory/entries`** are not wrapped here—call the Flask routes directly if needed.
- Adds strict response-shape checks and a `BackendAPIError` for invalid/non-JSON backend responses.

## Notes

- Director Agent runs in a continuous loop, polling the backend
- It handles errors gracefully and continues running
- Use SIGINT or SIGTERM for graceful shutdown
- Make sure the backend is running before starting Director Agent
