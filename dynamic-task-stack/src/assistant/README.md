# Assistant Module

Assistant 模块负责统一编排 sub-agent 执行，并管理共享 workspace。

## 职责边界

- 路由层：`routes.py`，仅做参数校验和 HTTP 编排
- 服务层：`service.py`，执行主流程（组装输入 -> 执行 -> 结果处理）
- 存储层：`storage.py`，全局 assistant/execution/workspace 单例管理
- 检索层：`retrieval.py`，从 workspace 取上下文数据
- 工作空间：`workspace/`，文件/记忆/日志管理

## Agent 执行模型

- 统一使用 descriptor-driven pipeline agent
- 通过 `agents.get_agent_registry().get_descriptor(agent_id)` 取 descriptor
- 执行链路：`build_input(...)` -> `build_equipped_agent(...).run(...)`

## 关键 API

### Assistant 信息

- `GET /api/assistant`

### Sub-agent 查询

- `GET /api/assistant/sub-agents`
- `GET /api/assistant/sub-agents/<agent_id>`
- `GET /api/assistant/agents/<agent_id>/inputs`

说明：列表与单项都复用同一份注册表聚合数据（同字段形状），并包含 `asset_key` / `asset_type`，便于调用方按资产类型路由。

### 执行与记录

- `POST /api/assistant/execute`
- `GET /api/assistant/executions/<execution_id>`
- `GET /api/assistant/executions/task/<task_id>`

`POST /api/assistant/execute` 请求体：

```json
{
  "agent_id": "StoryAgent",
  "task_id": "task_xxx",
  "additional_inputs": {}
}
```

执行响应（来自 `process_results`）：

```json
{
  "execution_id": "exec_xxx",
  "status": "COMPLETED",
  "results": {},
  "error": null,
  "workspace_id": "workspace_global_xxx"
}
```

### Workspace 访问

- `GET /api/assistant/workspace`
- `GET /api/assistant/workspace/summary`
- `GET /api/assistant/workspace/files`
- `GET /api/assistant/workspace/files/<file_id>`
- `GET /api/assistant/workspace/files/search`
- `GET /api/assistant/workspace/memory`
- `POST /api/assistant/workspace/memory`
- `GET /api/assistant/workspace/logs`
- `GET /api/assistant/workspace/search`

## 说明

- 当前模块保持 `service.py` 单文件实现，以执行链路聚合为主
- 不再支持 sync adapter 双模型路径，统一 descriptor pipeline 路径
