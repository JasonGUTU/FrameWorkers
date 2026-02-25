# Assistant API 文档

Assistant 模块提供了统一的 Agent 管理和编排系统，支持全局单例 Assistant、Sub-agent 自动发现、Agent 执行和工作空间管理。

## 目录

- [数据结构](#数据结构)
- [Assistant 管理 API](#assistant-管理-api)
- [Sub-Agent 查询 API](#sub-agent-查询-api)
- [Agent 执行 API](#agent-执行-api)
- [执行记录 API](#执行记录-api)
- [Workspace API](#workspace-api)

---

## 数据结构

### ExecutionStatus

执行状态枚举：

- `PENDING` - 待执行
- `IN_PROGRESS` - 执行中
- `COMPLETED` - 已完成
- `FAILED` - 失败

### Assistant

全局 Assistant 数据结构：

```python
{
    "id": str,              # Assistant ID（固定为 "assistant_global"）
    "name": str,            # Assistant 名称
    "description": str,      # Assistant 描述
    "agent_ids": List[str], # 管理的 Agent ID 列表
    "created_at": datetime, # 创建时间
    "updated_at": datetime  # 更新时间
}
```

### AgentExecution

Agent 执行记录数据结构：

```python
{
    "id": str,                      # 执行 ID
    "assistant_id": str,            # Assistant ID
    "agent_id": str,                # Agent ID
    "task_id": str,                 # 任务 ID
    "status": ExecutionStatus,      # 执行状态
    "inputs": Dict[str, Any],       # 输入数据
    "results": Optional[Dict[str, Any]],  # 执行结果
    "error": Optional[str],         # 错误信息
    "started_at": Optional[datetime],  # 开始时间
    "completed_at": Optional[datetime], # 完成时间
    "created_at": datetime          # 创建时间
}
```

---

## Assistant 管理 API

### 获取全局 Assistant

**GET** `/api/assistant`

获取全局 Assistant 实例（单例，预先定义）。

**说明：**
- Assistant 是全局单例，ID 固定为 `"assistant_global"`
- Assistant 是预先定义好的，不需要更新
- 所有 Sub-agents 都是预先定义好的，通过 Agent Registry 自动发现，不需要手动添加

**响应：**

```json
{
    "id": "assistant_global",
    "name": "Global Assistant",
    "description": "Global assistant instance that manages all sub-agents and workspace interactions",
    "agent_ids": [],  // 信息性字段，所有 sub-agents 通过 registry 自动发现
    "created_at": "2024-01-01T10:00:00",
    "updated_at": "2024-01-01T10:00:00"
}
```

**状态码：**
- `200` - 成功

---

## Sub-Agent 查询 API

### Agent 类型

注册表统一使用 descriptor-driven pipeline agent 模型。

| 类型 | 示例 | 接口 | 需要 LLM |
|------|------|------|----------|
| **Pipeline Agent** | `StoryAgent`, `VideoAgent` 等 | `SubAgentDescriptor` + async `run()` | 是（`OPENAI_API_KEY`） |

所有 agent 通过 `GET /api/assistant/sub-agents` 统一返回。Pipeline agents 的 `capabilities` 包含 `"pipeline_agent"` 标记。

### 获取所有 Sub-Agents

**GET** `/api/assistant/sub-agents`

获取所有已安装的 Sub-agents（descriptor 注册的 pipeline agents）。

**响应：**

```json
{
    "total_agents": 7,
    "agents": [
        {
            "id": "StoryAgent",
            "name": "StoryAgent",
            "description": "Generates a story blueprint from a draft idea...",
            "capabilities": ["pipeline_agent", "story_blueprint"],
            ...
        }
    ],
    "all_capabilities": ["pipeline_agent", "story_blueprint", ...],
    "agent_ids": ["StoryAgent", "ScreenplayAgent", ...]
}
```

**状态码：**
- `200` - 成功

---

### 获取单个 Sub-Agent 信息

**GET** `/api/assistant/sub-agents/<agent_id>`

获取特定 Sub-agent 的详细信息。

**响应：**

```json
{
    "id": "StoryAgent",
    "name": "StoryAgent",
    "description": "Generates a story blueprint from a draft idea...",
    "version": "1.0.0",
    "author": null,
    "capabilities": ["pipeline_agent", "story_blueprint"],
    "input_schema": {},
    "output_schema": {},
    "created_at": "",
    "updated_at": "",
    "asset_key": "story_blueprint",
    "asset_type": "story_blueprint"
}
```

**状态码：**
- `200` - 成功
- `404` - Sub-agent 不存在

---

### 获取 Agent 输入要求

**GET** `/api/assistant/agents/<agent_id>/inputs`

查询 Agent 的输入要求和模式。

**响应：**

```json
{
    "agent_id": "StoryAgent",
    "agent_name": "StoryAgent",
    "input_schema": {},
    "output_schema": {},
    "capabilities": ["pipeline_agent", "story_blueprint"],
    "description": "Generates a story blueprint from a draft idea..."
}
```

**状态码：**
- `200` - 成功
- `404` - Agent 不存在

---

## Agent 执行 API

### 执行 Agent

**POST** `/api/assistant/execute`

执行 Agent 的完整流程，包括：
1. 查询 Agent 输入要求
2. 准备执行环境
3. 检索相关信息
4. 打包数据
5. 执行 Agent
6. 处理结果

**请求体：**

```json
{
    "agent_id": "example_agent",
    "task_id": "task_1_abc123",
    "additional_inputs": {  // 可选：额外的输入数据
        "custom_param": "value"
    }
}
```

**响应：**

```json
{
    "execution_id": "exec_1_abc123",
    "agent_id": "example_agent",
    "task_id": "task_1_abc123",
    "status": "COMPLETED",
    "inputs": {
        "input": "processed input data",
        "custom_param": "value"
    },
    "results": {
        "result": "execution result"
    },
    "started_at": "2024-01-01T10:00:00",
    "completed_at": "2024-01-01T10:05:00"
}
```

**状态码：**
- `200` - 执行成功
- `400` - 请求体无效或缺少必需字段
- `404` - Agent 或任务不存在
- `500` - 执行失败

---

## 执行记录 API

### 获取执行记录

**GET** `/api/assistant/executions/<execution_id>`

根据执行 ID 获取执行记录。

**响应：**

```json
{
    "id": "exec_1_abc123",
    "assistant_id": "assistant_global",
    "agent_id": "example_agent",
    "task_id": "task_1_abc123",
    "status": "COMPLETED",
    "inputs": {...},
    "results": {...},
    "error": null,
    "started_at": "2024-01-01T10:00:00",
    "completed_at": "2024-01-01T10:05:00",
    "created_at": "2024-01-01T10:00:00"
}
```

**状态码：**
- `200` - 成功
- `404` - 执行记录不存在

---

### 获取任务的所有执行记录

**GET** `/api/assistant/executions/task/<task_id>`

获取指定任务的所有执行记录。

**响应：**

```json
[
    {
        "id": "exec_1_abc123",
        "agent_id": "example_agent",
        "status": "COMPLETED",
        ...
    },
    {
        "id": "exec_2_def456",
        "agent_id": "another_agent",
        "status": "FAILED",
        "error": "Execution error message",
        ...
    },
    ...
]
```

**状态码：**
- `200` - 成功

---

## Workspace API

Workspace API 提供了文件管理、Global Memory 和日志管理功能。详细文档请参考 [Workspace README](./workspace/README.md)。

### Workspace 信息

- `GET /api/assistant/workspace` - 获取工作空间摘要
- `GET /api/assistant/workspace/summary` - 获取详细摘要

### 文件管理

- `GET /api/assistant/workspace/files` - 列出文件
- `GET /api/assistant/workspace/files/<file_id>` - 获取文件元数据
- `GET /api/assistant/workspace/files/search` - 搜索文件

### Global Memory

- `GET /api/assistant/workspace/memory` - 读取记忆
- `POST /api/assistant/workspace/memory` - 写入记忆

### 日志

- `GET /api/assistant/workspace/logs` - 获取日志

### 综合搜索

- `GET /api/assistant/workspace/search` - 综合搜索（文件、记忆、日志）

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
- `404` - 资源不存在（Agent、任务、执行记录等）
- `500` - 服务器内部错误（执行失败等）

---

## 注意事项

1. **全局单例**：系统只有一个全局 Assistant 实例，ID 固定为 `"assistant_global"`。Assistant 是预先定义好的，不需要更新。

2. **Agent 注册表**：注册表统一管理 descriptor-driven pipeline agents：
   - 从 `AGENT_REGISTRY`（`SubAgentDescriptor` dict）自动注册（如 `StoryAgent`）
   - Assistant 执行阶段基于 descriptor 直接构建输入并调用 async `run()`

3. **质量门**：pipeline agents 使用内置三层评估（L1 结构 → L2 LLM 创意 → L3 资产）+ 自动重试

4. **LLM 配置**：Pipeline agents 需要 `OPENAI_API_KEY` 环境变量。`LLMClient` 在 `get_agent_registry()` 首次调用时创建并注入，采用 lazy-init：
   - 构造时不读 API key（不会阻止启动）
   - 真正发 LLM 请求时才从环境变量读取

5. **执行流程**：`execute_agent` API 执行完整的 5 步流程：
   - 查询 Agent 输入要求
   - 准备执行环境
   - 打包数据（从 workspace 检索上下文）
   - 执行 Agent（含质量门 + 重试）
   - 处理结果（写回 workspace）

6. **工作空间共享**：所有 Agents 共享一个全局工作空间，可以访问相同的文件、记忆和日志。

7. **执行记录**：每次 Agent 执行都会创建执行记录，结果中包含 `_eval_result`、`_passed`、`_attempts` 元数据。

8. **Service 边界（单文件实现）**：`service.py` 当前保持单文件实现，不强制拆分模块；通过内部方法分区维持职责边界：
   - Pipeline 执行辅助（`_map_pipeline_inputs`、`_execute_pipeline_descriptor`）
   - 输入打包与上下文检索（`build_execution_inputs`、`package_data`）
   - 结果落盘与日志（`process_results`、`_store_execution_files`）
