# Task Stack Module

Task Stack 模块负责消息、任务、层、执行指针和批量修改。

## 职责边界

- `models.py`：Task/Layer/ExecutionPointer 等数据模型
- `storage.py`：线程安全内存存储与原子操作
- `routes.py`：REST API（参数校验 + 调 storage）

## 关键 API

### 消息

- `POST /api/messages/create`
- `GET /api/messages/<msg_id>`
- `GET /api/messages/list`
- `GET /api/messages/unread`
- `PUT /api/messages/<msg_id>/read-status`
- `GET /api/messages/<msg_id>/check`

`POST /api/messages/create` 请求体：

```json
{
  "content": "hello",
  "sender_type": "user"
}
```

> 单用户系统：`user_id` 固定由后端管理，不需要客户端传入。
> `GET /api/messages/<msg_id>/check` 返回 `message` 与 `is_new_task` 两个字段，不再返回重复的 `data_structure`。

### 任务

- `POST /api/tasks/create`
- `GET /api/tasks/<task_id>`
- `GET /api/tasks/list`
- `PUT /api/tasks/<task_id>`
- `DELETE /api/tasks/<task_id>`
- `PUT /api/tasks/<task_id>/status`
- `POST /api/tasks/<task_id>/messages`

`POST /api/tasks/<task_id>/messages` 请求体：

```json
{
  "content": "delegated to agent",
  "sender_type": "director"
}
```

### 层

- `POST /api/layers/create`
- `GET /api/layers/list`
- `GET /api/layers/<layer_index>`
- `PUT /api/layers/<layer_index>/hooks`
- `POST /api/layers/<layer_index>/tasks`
- `DELETE /api/layers/<layer_index>/tasks/<task_id>`
- `POST /api/layers/<layer_index>/tasks/replace`

### 执行指针

- `GET /api/execution-pointer/get`
- `PUT /api/execution-pointer/set`
- `POST /api/execution-pointer/advance`

### 任务栈与批量修改

- `GET /api/task-stack`
- `GET /api/task-stack/next`
- `POST /api/task-stack/insert-layer`
- `POST /api/task-stack/modify`

## 设计说明

- 路由层已统一使用通用 helper（JSON body / enum 解析）减少重复逻辑
- `sender_type` 与布尔 query 参数解析已复用统一 helper，避免多处手写解析分叉
- 响应序列化在各模块内聚实现（`task_stack/routes.py` 与 `assistant/serializers.py`）
- `modify_task_stack` 在单锁内执行，保证批量操作原子性
