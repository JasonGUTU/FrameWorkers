# Task Stack API 文档

Task Stack 模块提供了完整的任务管理和执行系统，支持分层级任务组织、消息管理、执行指针跟踪等功能。

## 目录

- [数据结构](#数据结构)
- [用户消息 API](#用户消息-api)
- [任务 API](#任务-api)
- [任务层 API](#任务层-api)
- [执行指针 API](#执行指针-api)
- [任务栈 API](#任务栈-api)
- [批量操作 API](#批量操作-api)
- [健康检查](#健康检查)

---

## 数据结构

### TaskStatus

任务状态枚举：

- `PENDING` - 待执行
- `IN_PROGRESS` - 执行中
- `COMPLETED` - 已完成
- `FAILED` - 失败
- `CANCELLED` - 已取消

### ReadingStatus

读取状态枚举：

- `UNREAD` - 未读
- `READ` - 已读

### MessageSenderType

消息发送者类型枚举：

- `DIRECTOR` - Director Agent
- `SUBAGENT` - Sub-agent
- `USER` - 用户

### UserMessage

用户消息数据结构：

```python
{
    "id": str,                    # 消息 ID
    "content": str,               # 消息内容
    "timestamp": datetime,        # 时间戳
    "user_id": str,              # 用户 ID（固定为 "user"）
    "sender_type": MessageSenderType,  # 发送者类型
    "director_read_status": ReadingStatus,  # Director 读取状态
    "user_read_status": ReadingStatus,      # 用户读取状态
    "task_id": Optional[str]      # 关联的任务 ID
}
```

### Task

任务数据结构：

```python
{
    "id": str,                    # 任务 ID
    "description": Dict[str, Any], # 任务描述（包含 overall_description, input, requirements, additional_notes）
    "status": TaskStatus,         # 任务状态
    "progress": Dict[str, Any],   # 进度信息（消息集合）
    "results": Optional[Dict[str, Any]],  # 任务结果
    "created_at": datetime,       # 创建时间
    "updated_at": datetime        # 更新时间
}
```

### TaskLayer

任务层数据结构：

```python
{
    "layer_index": int,           # 层索引（0-based）
    "tasks": List[TaskStackEntry], # 任务列表
    "pre_hook": Optional[Dict[str, Any]],  # Pre-hook
    "post_hook": Optional[Dict[str, Any]],  # Post-hook
    "created_at": datetime        # 创建时间
}
```

### ExecutionPointer

执行指针数据结构：

```python
{
    "current_layer_index": int,   # 当前层索引
    "current_task_index": int,    # 当前任务索引
    "is_executing_pre_hook": bool,  # 是否正在执行 pre-hook
    "is_executing_post_hook": bool # 是否正在执行 post-hook
}
```

---

## 用户消息 API

### 创建用户消息

**POST** `/api/messages/create`

创建一条新的用户消息。

**请求体：**

```json
{
    "content": "消息内容",
    "sender_type": "user",  // 可选：director, subagent, user（默认：user）
    "task_id": "task_1"     // 可选：关联的任务 ID
}
```

**响应：**

```json
{
    "id": "msg_1_abc123",
    "content": "消息内容",
    "timestamp": "2024-01-01T10:00:00",
    "user_id": "user",
    "sender_type": "user",
    "director_read_status": "UNREAD",
    "user_read_status": "UNREAD",
    "task_id": "task_1"
}
```

**状态码：**
- `201` - 创建成功
- `400` - 请求体无效或缺少必需字段

---

### 获取单个消息

**GET** `/api/messages/<msg_id>`

根据消息 ID 获取单个消息。

**响应：**

```json
{
    "id": "msg_1_abc123",
    "content": "消息内容",
    "timestamp": "2024-01-01T10:00:00",
    "user_id": "user",
    "sender_type": "user",
    "director_read_status": "UNREAD",
    "user_read_status": "UNREAD",
    "task_id": null
}
```

**状态码：**
- `200` - 成功
- `404` - 消息不存在

---

### 获取所有消息

**GET** `/api/messages/list`

获取所有用户消息。

**响应：**

```json
[
    {
        "id": "msg_1_abc123",
        "content": "消息内容",
        ...
    },
    ...
]
```

**状态码：**
- `200` - 成功

---

### 获取未读消息

**GET** `/api/messages/unread`

获取未读消息，支持多种过滤条件。

**查询参数：**

- `sender_type` (可选) - 过滤发送者类型：`director`, `subagent`, `user`
- `check_director_read` (可选) - 布尔值，是否检查 director_read_status（默认：如果未指定任何检查，则为 true）
- `check_user_read` (可选) - 布尔值，是否检查 user_read_status（默认：false）

**示例：**

```
GET /api/messages/unread?sender_type=user&check_director_read=true
GET /api/messages/unread?check_user_read=true
```

**响应：**

```json
[
    {
        "id": "msg_1_abc123",
        "content": "消息内容",
        "director_read_status": "UNREAD",
        ...
    },
    ...
]
```

**状态码：**
- `200` - 成功
- `400` - 无效的查询参数

---

### 更新消息读取状态

**PUT** `/api/messages/<msg_id>/read-status`

更新消息的读取状态。

**请求体：**

```json
{
    "director_read_status": "READ",  // 可选
    "user_read_status": "READ"        // 可选
}
```

**响应：**

```json
{
    "id": "msg_1_abc123",
    "director_read_status": "READ",
    "user_read_status": "READ",
    ...
}
```

**状态码：**
- `200` - 更新成功
- `400` - 请求体无效或状态值无效
- `404` - 消息不存在

---

### 检查消息

**GET** `/api/messages/<msg_id>/check`

检查消息的详细信息，包括数据结构、读取状态和是否为新任务。

**响应：**

```json
{
    "message": {
        "id": "msg_1_abc123",
        ...
    },
    "is_new_task": false,
    "data_structure": {
        "id": "msg_1_abc123",
        "content": "消息内容",
        "timestamp": "2024-01-01T10:00:00",
        "user_id": "user",
        "sender_type": "user",
        "director_read_status": "UNREAD",
        "user_read_status": "UNREAD",
        "task_id": null
    }
}
```

**状态码：**
- `200` - 成功
- `404` - 消息不存在

---

## 任务 API

### 创建任务

**POST** `/api/tasks/create`

创建一个新任务（不会自动添加到任务栈）。

**请求体：**

```json
{
    "description": {
        "overall_description": "任务描述",
        "input": {},
        "requirements": [],
        "additional_notes": ""
    }
}
```

**响应：**

```json
{
    "id": "task_1_abc123",
    "description": {
        "overall_description": "任务描述",
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

**状态码：**
- `201` - 创建成功
- `400` - 请求体无效或缺少必需字段

---

### 获取单个任务

**GET** `/api/tasks/<task_id>`

根据任务 ID 获取单个任务。

**响应：**

```json
{
    "id": "task_1_abc123",
    "description": {...},
    "status": "PENDING",
    ...
}
```

**状态码：**
- `200` - 成功
- `404` - 任务不存在

---

### 获取所有任务

**GET** `/api/tasks/list`

获取所有任务。

**响应：**

```json
[
    {
        "id": "task_1_abc123",
        ...
    },
    ...
]
```

**状态码：**
- `200` - 成功

---

### 更新任务

**PUT** `/api/tasks/<task_id>`

更新任务信息。

**请求体：**

```json
{
    "description": {...},      // 可选
    "status": "IN_PROGRESS",   // 可选
    "progress": {...},         // 可选
    "results": {...}           // 可选
}
```

**响应：**

```json
{
    "id": "task_1_abc123",
    "description": {...},
    "status": "IN_PROGRESS",
    "progress": {...},
    "results": {...},
    "updated_at": "2024-01-01T10:05:00"
}
```

**状态码：**
- `200` - 更新成功
- `400` - 请求体无效或状态值无效
- `404` - 任务不存在

---

### 更新任务状态

**PUT** `/api/tasks/<task_id>/status`

快速更新任务状态。

**请求体：**

```json
{
    "status": "COMPLETED"
}
```

**响应：**

```json
{
    "id": "task_1_abc123",
    "status": "COMPLETED",
    ...
}
```

**状态码：**
- `200` - 更新成功
- `400` - 请求体无效或状态值无效
- `404` - 任务不存在

---

### 删除任务

**DELETE** `/api/tasks/<task_id>`

删除一个任务。

**响应：**

```json
{
    "message": "Task deleted successfully"
}
```

**状态码：**
- `200` - 删除成功
- `404` - 任务不存在

---

### 推送消息到任务

**POST** `/api/tasks/<task_id>/messages`

为任务创建一条关联消息。

**请求体：**

```json
{
    "content": "消息内容",
    "sender_type": "user"  // 可选：director, subagent, user（默认：user）
}
```

**响应：**

```json
{
    "id": "msg_1_abc123",
    "content": "消息内容",
    "task_id": "task_1_abc123",
    ...
}
```

**状态码：**
- `201` - 创建成功
- `400` - 请求体无效或缺少必需字段
- `404` - 任务不存在

---

## 任务层 API

### 创建层

**POST** `/api/layers/create`

创建一个新的任务层。

**请求体：**

```json
{
    "layer_index": 0,        // 可选：指定层索引（默认追加到末尾）
    "pre_hook": {...},       // 可选：Pre-hook
    "post_hook": {...}       // 可选：Post-hook
}
```

**响应：**

```json
{
    "layer_index": 0,
    "tasks": [],
    "pre_hook": {...},
    "post_hook": {...},
    "created_at": "2024-01-01T10:00:00"
}
```

**状态码：**
- `201` - 创建成功
- `400` - 请求体无效

---

### 获取所有层

**GET** `/api/layers/list`

获取所有任务层。

**响应：**

```json
[
    {
        "layer_index": 0,
        "tasks": [...],
        ...
    },
    ...
]
```

**状态码：**
- `200` - 成功

---

### 获取单个层

**GET** `/api/layers/<layer_index>`

根据层索引获取单个层。

**响应：**

```json
{
    "layer_index": 0,
    "tasks": [...],
    "pre_hook": {...},
    "post_hook": {...},
    "created_at": "2024-01-01T10:00:00"
}
```

**状态码：**
- `200` - 成功
- `404` - 层不存在

---

### 更新层 Hooks

**PUT** `/api/layers/<layer_index>/hooks`

更新层的 Pre-hook 和 Post-hook。

**请求体：**

```json
{
    "pre_hook": {...},   // 可选
    "post_hook": {...}   // 可选
}
```

**响应：**

```json
{
    "layer_index": 0,
    "pre_hook": {...},
    "post_hook": {...},
    ...
}
```

**状态码：**
- `200` - 更新成功
- `400` - 请求体无效
- `404` - 层不存在或层已执行

---

### 添加任务到层

**POST** `/api/layers/<layer_index>/tasks`

将任务添加到指定层。

**请求体：**

```json
{
    "task_id": "task_1_abc123",
    "insert_index": 0  // 可选：指定插入位置（默认追加到末尾）
}
```

**响应：**

```json
{
    "layer_index": 0,
    "tasks": [
        {
            "task_id": "task_1_abc123",
            "created_at": "2024-01-01T10:00:00"
        },
        ...
    ],
    ...
}
```

**状态码：**
- `200` - 添加成功
- `400` - 请求体无效或缺少必需字段
- `404` - 层不存在、任务不存在、任务已在层中或层已执行

---

### 从层中移除任务

**DELETE** `/api/layers/<layer_index>/tasks/<task_id>`

从层中移除任务（仅当任务未执行时）。

**响应：**

```json
{
    "message": "Task removed from layer successfully"
}
```

**状态码：**
- `200` - 移除成功
- `404` - 层不存在、任务不存在或任务已执行

---

### 替换层中的任务

**POST** `/api/layers/<layer_index>/tasks/replace`

原子性地替换层中的任务（取消旧任务，添加新任务）。

**请求体：**

```json
{
    "old_task_id": "task_1_abc123",
    "new_task_id": "task_2_def456"
}
```

**响应：**

```json
{
    "layer_index": 0,
    "tasks": [
        {
            "task_id": "task_2_def456",
            "created_at": "2024-01-01T10:00:00"
        },
        ...
    ],
    ...
}
```

**状态码：**
- `200` - 替换成功
- `400` - 请求体无效或缺少必需字段
- `404` - 层不存在、任务不存在或任务已执行

---

## 执行指针 API

### 获取执行指针

**GET** `/api/execution-pointer/get`

获取当前执行指针。

**响应：**

```json
{
    "current_layer_index": 0,
    "current_task_index": 0,
    "is_executing_pre_hook": false,
    "is_executing_post_hook": false
}
```

或者：

```json
{
    "message": "No execution pointer set"
}
```

**状态码：**
- `200` - 成功

---

### 设置执行指针

**PUT** `/api/execution-pointer/set`

设置执行指针位置。

**请求体：**

```json
{
    "layer_index": 0,
    "task_index": 0,
    "is_executing_pre_hook": false,  // 可选，默认：false
    "is_executing_post_hook": false  // 可选，默认：false
}
```

**响应：**

```json
{
    "current_layer_index": 0,
    "current_task_index": 0,
    "is_executing_pre_hook": false,
    "is_executing_post_hook": false
}
```

**状态码：**
- `200` - 设置成功
- `400` - 请求体无效或索引无效

---

### 推进执行指针

**POST** `/api/execution-pointer/advance`

将执行指针推进到下一个任务。

**响应：**

```json
{
    "current_layer_index": 0,
    "current_task_index": 1,
    "is_executing_pre_hook": false,
    "is_executing_post_hook": false
}
```

**状态码：**
- `200` - 推进成功
- `400` - 无法推进指针（已到达末尾）

---

## 任务栈 API

### 获取下一个任务

**GET** `/api/task-stack/next`

根据执行指针获取下一个要执行的任务。

**响应：**

```json
{
    "layer_index": 0,
    "task_index": 0,
    "task_id": "task_1_abc123",
    "task": {
        "id": "task_1_abc123",
        "description": {...},
        "status": "PENDING",
        ...
    },
    "layer": {
        "layer_index": 0,
        "tasks": [...],
        "pre_hook": {...},
        "post_hook": {...}
    },
    "is_pre_hook": false
}
```

或者：

```json
{
    "message": "No tasks in stack"
}
```

**状态码：**
- `200` - 成功

---

### 获取所有层

**GET** `/api/task-stack`

获取任务栈中的所有层。

**响应：**

```json
[
    {
        "layer_index": 0,
        "tasks": [...],
        ...
    },
    ...
]
```

**状态码：**
- `200` - 成功

---

### 插入层并添加任务

**POST** `/api/task-stack/insert-layer`

原子性地在指定位置插入一个新层，并可选择性地添加任务。

**请求体：**

```json
{
    "insert_layer_index": 3,
    "task_ids": ["task_1_abc123", "task_2_def456"],  // 可选：任务 ID 列表（可省略以插入空层）
    "pre_hook": {...},   // 可选
    "post_hook": {...}   // 可选
}
```

**示例：插入空层**

```json
{
    "insert_layer_index": 3,
    "pre_hook": {"type": "middleware", "action": "prepare"},
    "post_hook": {"type": "hook", "action": "cleanup"}
}
```

**响应：**

```json
{
    "layer_index": 3,
    "tasks": [
        {
            "task_id": "task_1_abc123",
            "created_at": "2024-01-01T10:00:00"
        },
        ...
    ],
    "pre_hook": {...},
    "post_hook": {...},
    "created_at": "2024-01-01T10:00:00"
}
```

**状态码：**
- `201` - 插入成功
- `400` - 请求体无效、索引无效、任务不存在或无法在已执行层之前插入

---

## 批量操作 API

### 修改任务栈（批量操作）

**POST** `/api/task-stack/modify`

统一的批量操作接口，支持一次性执行多个操作，所有操作在单个事务中原子执行。

**请求体：**

```json
{
    "operations": [
        {
            "type": "create_tasks",
            "params": {
                "tasks": [
                    {
                        "description": {
                            "overall_description": "任务1",
                            "input": {},
                            "requirements": [],
                            "additional_notes": ""
                        }
                    },
                    ...
                ]
            }
        },
        {
            "type": "create_layers",
            "params": {
                "layers": [
                    {
                        "layer_index": 0,  // 可选
                        "pre_hook": {...},  // 可选
                        "post_hook": {...}  // 可选
                    },
                    ...
                ]
            }
        },
        {
            "type": "add_tasks_to_layers",
            "params": {
                "additions": [
                    {
                        "layer_index": 0,
                        "task_id": "task_1_abc123",
                        "insert_index": 0  // 可选
                    },
                    ...
                ]
            }
        },
        {
            "type": "remove_tasks_from_layers",
            "params": {
                "removals": [
                    {
                        "layer_index": 0,
                        "task_id": "task_1_abc123"
                    },
                    ...
                ]
            }
        },
        {
            "type": "replace_tasks_in_layers",
            "params": {
                "replacements": [
                    {
                        "layer_index": 0,
                        "old_task_id": "task_1_abc123",
                        "new_task_id": "task_2_def456"
                    },
                    ...
                ]
            }
        },
        {
            "type": "update_layer_hooks",
            "params": {
                "updates": [
                    {
                        "layer_index": 0,
                        "pre_hook": {...},  // 可选
                        "post_hook": {...}  // 可选
                    },
                    ...
                ]
            }
        }
    ]
}
```

**支持的操作类型：**

1. **create_tasks** - 创建任务
2. **create_layers** - 创建层
3. **add_tasks_to_layers** - 添加任务到层
4. **remove_tasks_from_layers** - 从层中移除任务
5. **replace_tasks_in_layers** - 替换层中的任务
6. **update_layer_hooks** - 更新层的 Hooks

**响应：**

```json
{
    "success": true,
    "results": [
        {
            "operation_index": 0,
            "type": "create_tasks",
            "success": true,
            "data": {
                "created_task_ids": ["task_1_abc123", "task_2_def456"]
            }
        },
        {
            "operation_index": 1,
            "type": "create_layers",
            "success": true,
            "data": {
                "created_layer_indices": [0, 1]
            }
        },
        ...
    ],
    "errors": [],
    "created_task_ids": ["task_1_abc123", "task_2_def456"],
    "created_layer_indices": [0, 1]
}
```

如果操作失败：

```json
{
    "success": false,
    "results": [
        {
            "operation_index": 0,
            "type": "create_tasks",
            "success": true,
            "data": {...}
        },
        {
            "operation_index": 1,
            "type": "add_tasks_to_layers",
            "success": false,
            "error": "Task not found"
        }
    ],
    "errors": [
        {
            "operation_index": 1,
            "type": "add_tasks_to_layers",
            "error": "Task not found",
            "params": {...}
        }
    ],
    "created_task_ids": ["task_1_abc123"],
    "created_layer_indices": []
}
```

**状态码：**
- `200` - 执行完成（可能部分成功）
- `400` - 请求体无效或操作列表为空

---

## 健康检查

### 健康检查

**GET** `/health`

检查服务健康状态。

**响应：**

```json
{
    "status": "ok",
    "service": "Frameworks Backend"
}
```

**状态码：**
- `200` - 服务正常

---

## 错误处理

所有 API 在出错时返回标准错误响应：

```json
{
    "error": "错误描述信息"
}
```

常见错误状态码：

- `400` - 请求错误（无效的请求体、缺少必需字段等）
- `404` - 资源不存在
- `500` - 服务器内部错误

---

## 注意事项

1. **单用户系统**：系统设计为单用户系统，`user_id` 固定为 `"user"`，所有消息 API 不需要传递 `user_id` 参数。

2. **原子操作**：
   - `replace_task_in_layer` - 任务替换是原子操作
   - `insert_layer_with_tasks` - 插入层并添加任务是原子操作
   - `modify_task_stack` - 批量操作中的所有操作在单个事务中原子执行

3. **执行指针**：
   - 执行指针跟踪当前执行位置
   - 不能修改已执行的层和任务
   - 插入层时不能插入到已执行层之前

4. **任务状态**：
   - 任务创建时默认为 `PENDING` 状态
   - 只有未执行的任务可以被修改或删除

5. **消息读取状态**：
   - 消息创建时默认为 `UNREAD`
   - 支持分别跟踪 Director 和用户的读取状态
