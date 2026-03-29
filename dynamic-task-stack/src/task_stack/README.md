# Task Stack Module

Task Stack provides layered task orchestration for the backend. It owns:

- user/director/subagent messages
- task lifecycle and status
- ordered task layers with hooks
- execution pointer progression
- atomic batch mutation

## Module Boundaries

- `models.py`
  - Dataclasses/enums for message/task/layer/pointer and batch operations
- `state_store.py`
  - Thread-safe in-memory runtime state container (data only)
- `execution_flow.py`
  - Execution pointer transition logic (`get/set/next/advance`)
- `batch_mutator.py`
  - Atomic batch write helpers and `modify_task_stack` orchestration
- `storage.py`
  - `TaskStackService` facade used by routes and callers
- `api_serialize.py`
  - JSON-safe serialization for dataclass/enum payloads returned by Task Stack routes
- `routes.py`
  - HTTP API layer with request parsing/validation; uses `../common_http.py` for JSON body / enum parsing / `bad_request`（400）与 `api_serialize.serialize_for_api` 做响应序列化

## Public Entry Points

- Package API (`task_stack/__init__.py`)
  - `create_blueprint`
  - `storage` (canonical global singleton)
  - `TaskStackService`

## API Surface (routes)

- Messages
  - `POST /api/messages/create`
  - `GET /api/messages/<msg_id>`
  - `GET /api/messages/list`
  - `GET /api/messages/unread`
  - `PUT /api/messages/<msg_id>/read-status`
  - `GET /api/messages/<msg_id>/check`

- Tasks
  - `POST /api/tasks/create`
  - `GET /api/tasks/<task_id>`
  - `GET /api/tasks/list`
  - `PUT /api/tasks/<task_id>`
  - `DELETE /api/tasks/<task_id>`
  - `PUT /api/tasks/<task_id>/status`
  - `POST /api/tasks/<task_id>/messages`

- Layers
  - `POST /api/layers/create`
  - `GET /api/layers/list`
  - `GET /api/layers/<layer_index>`
  - `PUT /api/layers/<layer_index>/hooks`
  - `POST /api/layers/<layer_index>/tasks`
  - `DELETE /api/layers/<layer_index>/tasks/<task_id>`
  - `POST /api/layers/<layer_index>/tasks/replace`

- Pointer / Stack
  - `GET /api/execution-pointer/get`
  - `PUT /api/execution-pointer/set`
  - `POST /api/execution-pointer/advance`
  - `GET /api/task-stack`
  - `GET /api/task-stack/next`
  - `POST /api/task-stack/insert-layer`
  - `POST /api/task-stack/modify`

## Recent Cleanup Notes (2026-03)

- Removed unused `TaskStackService.get_unread_user_messages()`
- Removed unused internal proxy methods in `TaskStackService`
- Standardized singleton naming: `storage` is canonical (deprecated module-level aliases removed).
- Narrowed package exports to route/service-facing API only
