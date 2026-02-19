# Dynamic Task Stack API Documentation

## Base URL
```
http://localhost:5000
```

## API Routes

### Health Check

#### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "service": "Dynamic Task Stack"
}
```

---

## User Messages API

### POST /api/messages/create
Create a new user message.

**Request Body:**
```json
{
  "content": "string (required)",
  "user_id": "string (required)"
}
```

**Response (201 Created):**
```json
{
  "id": "msg_1_abc123",
  "content": "message content",
  "timestamp": "2024-01-01T10:00:00",
  "user_id": "user123",
  "worker_read_status": "UNREAD",
  "user_read_status": "UNREAD",
  "task_id": null
}
```

**Error Responses:**
- `400 Bad Request`: Invalid JSON body or missing required fields
- `500 Internal Server Error`: Server error

---

### GET /api/messages/list
Get all user messages, optionally filtered by user_id.

**Query Parameters:**
- `user_id` (optional): Filter messages by user ID

**Example:**
```
GET /api/messages/list
GET /api/messages/list?user_id=user123
```

**Response (200 OK):**
```json
[
  {
    "id": "msg_1_abc123",
    "content": "message content",
    "timestamp": "2024-01-01T10:00:00",
    "user_id": "user123",
    "worker_read_status": "UNREAD",
    "user_read_status": "UNREAD",
    "task_id": null
  }
]
```

---

### GET /api/messages/<msg_id>
Get a specific user message by ID.

**Path Parameters:**
- `msg_id` (string, required): Message ID

**Response (200 OK):**
```json
{
  "id": "msg_1_abc123",
  "content": "message content",
  "timestamp": "2024-01-01T10:00:00",
  "user_id": "user123",
  "worker_read_status": "UNREAD",
  "user_read_status": "UNREAD",
  "task_id": null
}
```

**Error Responses:**
- `404 Not Found`: Message not found

---

### PUT /api/messages/<msg_id>/read-status
Update read status of a message.

**Path Parameters:**
- `msg_id` (string, required): Message ID

**Request Body:**
```json
{
  "worker_read_status": "UNREAD" | "READ" (optional),
  "user_read_status": "UNREAD" | "READ" (optional)
}
```

**Response (200 OK):**
```json
{
  "id": "msg_1_abc123",
  "content": "message content",
  "timestamp": "2024-01-01T10:00:00",
  "user_id": "user123",
  "worker_read_status": "READ",
  "user_read_status": "READ",
  "task_id": null
}
```

**Error Responses:**
- `400 Bad Request`: Invalid JSON body or invalid status value
- `404 Not Found`: Message not found

---

### GET /api/messages/<msg_id>/check
Check user message (data structure, read status, is new task).

**Path Parameters:**
- `msg_id` (string, required): Message ID

**Response (200 OK):**
```json
{
  "message": {
    "id": "msg_1_abc123",
    "content": "message content",
    "timestamp": "2024-01-01T10:00:00",
    "user_id": "user123",
    "worker_read_status": "UNREAD",
    "user_read_status": "UNREAD",
    "task_id": "task_1_xyz789"
  },
  "is_new_task": true,
  "data_structure": {
    "id": "msg_1_abc123",
    "content": "message content",
    "timestamp": "2024-01-01T10:00:00",
    "user_id": "user123",
    "worker_read_status": "UNREAD",
    "user_read_status": "UNREAD",
    "task_id": "task_1_xyz789"
  }
}
```

**Error Responses:**
- `404 Not Found`: Message not found

---

## Tasks API

### POST /api/tasks/create
Create a new task (does not add to stack automatically).

**Request Body:**
```json
{
  "description": {
    "overall_description": "string (required)",
    "input": "object (optional)",
    "requirements": "array (optional)",
    "additional_notes": "string (optional)"
  }
}
```

**Response (201 Created):**
```json
{
  "id": "task_1_abc123",
  "description": {
    "overall_description": "Process user data",
    "input": {},
    "requirements": [],
    "additional_notes": ""
  },
  "status": "PENDING",
  "progress": {},
  "results": null,
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:00:00"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid JSON body or description is not a dictionary

---

### GET /api/tasks/list
Get all tasks.

**Response (200 OK):**
```json
[
  {
    "id": "task_1_abc123",
    "description": {...},
    "status": "PENDING",
    "progress": {},
    "results": null,
    "created_at": "2024-01-01T10:00:00",
    "updated_at": "2024-01-01T10:00:00"
  }
]
```

---

### GET /api/tasks/<task_id>
Get a specific task by ID.

**Path Parameters:**
- `task_id` (string, required): Task ID

**Response (200 OK):**
```json
{
  "id": "task_1_abc123",
  "description": {...},
  "status": "COMPLETED",
  "progress": {
    "step1": "done",
    "step2": "done"
  },
  "results": {
    "output": "processed_data"
  },
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:05:00"
}
```

**Error Responses:**
- `404 Not Found`: Task not found

---

### PUT /api/tasks/<task_id>
Update a task.

**Path Parameters:**
- `task_id` (string, required): Task ID

**Request Body:**
```json
{
  "description": {
    "overall_description": "string (optional)",
    "input": "object (optional)",
    "requirements": "array (optional)",
    "additional_notes": "string (optional)"
  },
  "status": "PENDING" | "IN_PROGRESS" | "COMPLETED" | "FAILED" | "CANCELLED" (optional),
  "progress": {
    "key": "value"
  } (optional),
  "results": {
    "key": "value"
  } (optional)
}
```

**Response (200 OK):**
```json
{
  "id": "task_1_abc123",
  "description": {...},
  "status": "COMPLETED",
  "progress": {...},
  "results": {...},
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:05:00"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid JSON body, invalid status, or description/progress not dictionaries
- `404 Not Found`: Task not found

---

### DELETE /api/tasks/<task_id>
Delete a task and remove it from all layers.

**Path Parameters:**
- `task_id` (string, required): Task ID

**Response (200 OK):**
```json
{
  "message": "Task deleted successfully"
}
```

**Error Responses:**
- `404 Not Found`: Task not found

---

### PUT /api/tasks/<task_id>/status
Update task status only.

**Path Parameters:**
- `task_id` (string, required): Task ID

**Request Body:**
```json
{
  "status": "PENDING" | "IN_PROGRESS" | "COMPLETED" | "FAILED" | "CANCELLED" (required)
}
```

**Response (200 OK):**
```json
{
  "id": "task_1_abc123",
  "description": {...},
  "status": "COMPLETED",
  "progress": {...},
  "results": {...},
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:05:00"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid JSON body or invalid status
- `404 Not Found`: Task not found

---

### POST /api/tasks/<task_id>/messages
Push a user message to a task.

**Path Parameters:**
- `task_id` (string, required): Task ID

**Request Body:**
```json
{
  "content": "string (required)",
  "user_id": "string (required)"
}
```

**Response (201 Created):**
```json
{
  "id": "msg_2_def456",
  "content": "message content",
  "timestamp": "2024-01-01T10:01:00",
  "user_id": "user123",
  "worker_read_status": "UNREAD",
  "user_read_status": "UNREAD",
  "task_id": "task_1_abc123"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid JSON body or missing required fields
- `404 Not Found`: Task not found

---

## Task Layers API

### POST /api/layers/create
Create a new task layer.

**Request Body:**
```json
{
  "layer_index": 0 (optional, default: append to end),
  "pre_hook": {
    "type": "string",
    "action": "string",
    "config": {}
  } (optional),
  "post_hook": {
    "type": "string",
    "action": "string",
    "config": {}
  } (optional)
}
```

**Response (201 Created):**
```json
{
  "layer_index": 0,
  "tasks": [],
  "pre_hook": {...},
  "post_hook": {...},
  "created_at": "2024-01-01T10:00:00"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid JSON body or invalid layer_index

---

### GET /api/layers/list
Get all task layers.

**Response (200 OK):**
```json
[
  {
    "layer_index": 0,
    "tasks": [
      {
        "task_id": "task_1_abc123",
        "created_at": "2024-01-01T10:00:00"
      }
    ],
    "pre_hook": {...},
    "post_hook": {...},
    "created_at": "2024-01-01T10:00:00"
  }
]
```

---

### GET /api/layers/<layer_index>
Get a specific layer by index.

**Path Parameters:**
- `layer_index` (integer, required): Layer index (0-based)

**Response (200 OK):**
```json
{
  "layer_index": 0,
  "tasks": [
    {
      "task_id": "task_1_abc123",
      "created_at": "2024-01-01T10:00:00"
    }
  ],
  "pre_hook": {...},
  "post_hook": {...},
  "created_at": "2024-01-01T10:00:00"
}
```

**Error Responses:**
- `404 Not Found`: Layer not found

---

### PUT /api/layers/<layer_index>/hooks
Update hooks for a layer (only if layer not executed).

**Path Parameters:**
- `layer_index` (integer, required): Layer index (0-based)

**Request Body:**
```json
{
  "pre_hook": {
    "type": "string",
    "action": "string",
    "config": {}
  } (optional),
  "post_hook": {
    "type": "string",
    "action": "string",
    "config": {}
  } (optional)
}
```

**Response (200 OK):**
```json
{
  "layer_index": 0,
  "tasks": [...],
  "pre_hook": {...},
  "post_hook": {...},
  "created_at": "2024-01-01T10:00:00"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid JSON body
- `404 Not Found`: Layer not found or layer has already been executed

---

### POST /api/layers/<layer_index>/tasks
Add a task to a layer (only if layer not executed).

**Path Parameters:**
- `layer_index` (integer, required): Layer index (0-based)

**Request Body:**
```json
{
  "task_id": "string (required)",
  "insert_index": 0 (optional, default: append to end)
}
```

**Response (200 OK):**
```json
{
  "layer_index": 0,
  "tasks": [
    {
      "task_id": "task_1_abc123",
      "created_at": "2024-01-01T10:00:00"
    }
  ],
  "pre_hook": {...},
  "post_hook": {...},
  "created_at": "2024-01-01T10:00:00"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid JSON body or missing required fields
- `404 Not Found`: Layer not found, task not found, task already in layer, or cannot add to executed layer

---

### DELETE /api/layers/<layer_index>/tasks/<task_id>
Remove a task from a layer (only if not executed).

**Path Parameters:**
- `layer_index` (integer, required): Layer index (0-based)
- `task_id` (string, required): Task ID

**Response (200 OK):**
```json
{
  "message": "Task removed from layer successfully"
}
```

**Error Responses:**
- `404 Not Found`: Layer or task not found, or task has already been executed

---

### POST /api/layers/<layer_index>/tasks/replace
Atomically replace a task in a layer (cancel old, add new).

**Path Parameters:**
- `layer_index` (integer, required): Layer index (0-based)

**Request Body:**
```json
{
  "old_task_id": "string (required)",
  "new_task_id": "string (required)"
}
```

**Response (200 OK):**
```json
{
  "layer_index": 0,
  "tasks": [
    {
      "task_id": "task_new_xyz789",
      "created_at": "2024-01-01T10:05:00"
    }
  ],
  "pre_hook": {...},
  "post_hook": {...},
  "created_at": "2024-01-01T10:00:00"
}
```

**Note:** This operation will automatically set the old task status to `CANCELLED`.

**Error Responses:**
- `400 Bad Request`: Invalid JSON body or missing required fields
- `404 Not Found`: Layer not found, task not found, or task has already been executed

---

## Execution Pointer API

### GET /api/execution-pointer/get
Get current execution pointer.

**Response (200 OK):**
```json
{
  "current_layer_index": 0,
  "current_task_index": 0,
  "is_executing_pre_hook": false,
  "is_executing_post_hook": false
}
```

**Response (200 OK - No pointer set):**
```json
{
  "message": "No execution pointer set"
}
```

---

### PUT /api/execution-pointer/set
Set execution pointer.

**Request Body:**
```json
{
  "layer_index": 0 (required),
  "task_index": 0 (required),
  "is_executing_pre_hook": false (optional, default: false),
  "is_executing_post_hook": false (optional, default: false)
}
```

**Response (200 OK):**
```json
{
  "current_layer_index": 0,
  "current_task_index": 0,
  "is_executing_pre_hook": false,
  "is_executing_post_hook": false
}
```

**Error Responses:**
- `400 Bad Request`: Invalid JSON body, missing required fields, or invalid layer_index/task_index

---

### POST /api/execution-pointer/advance
Advance execution pointer to next task.

**Response (200 OK):**
```json
{
  "current_layer_index": 0,
  "current_task_index": 1,
  "is_executing_pre_hook": false,
  "is_executing_post_hook": false
}
```

**Error Responses:**
- `400 Bad Request`: Cannot advance pointer (no more tasks)

---

## Task Stack API (Convenience Routes)

### GET /api/task-stack/next
Get the next task to execute based on execution pointer.

**Response (200 OK):**
```json
{
  "layer_index": 0,
  "task_index": 0,
  "task_id": "task_1_abc123",
  "task": {
    "id": "task_1_abc123",
    "description": {...},
    "status": "PENDING",
    "progress": {},
    "results": null,
    "created_at": "2024-01-01T10:00:00",
    "updated_at": "2024-01-01T10:00:00"
  },
  "layer": {
    "layer_index": 0,
    "tasks": [...],
    "pre_hook": {...},
    "post_hook": {...},
    "created_at": "2024-01-01T10:00:00"
  },
  "is_pre_hook": false
}
```

**Response (200 OK - No tasks):**
```json
{
  "message": "No tasks in stack"
}
```

---

### GET /api/task-stack
Get all layers in the task stack.

**Response (200 OK):**
```json
[
  {
    "layer_index": 0,
    "tasks": [...],
    "pre_hook": {...},
    "post_hook": {...},
    "created_at": "2024-01-01T10:00:00"
  }
]
```

---

## Status Enums

### TaskStatus
- `PENDING`: Task is waiting to be processed
- `IN_PROGRESS`: Task is currently being processed
- `COMPLETED`: Task has been completed
- `FAILED`: Task has failed
- `CANCELLED`: Task has been cancelled

### ReadingStatus
- `UNREAD`: Message has not been read
- `READ`: Message has been read
