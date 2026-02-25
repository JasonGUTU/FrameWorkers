# Assistant Module

Assistant 模块是“执行入口 + 执行编排器”，负责把 Task Stack 的任务落地为具体 sub-agent 执行，并把结果写入 Workspace。

它是后端中的被动 API：  
前端和 `director_agent` 通过 HTTP 调它；Assistant 不直接与前端建立连接。

## 1. 文件职责

- `routes.py`：HTTP 路由，做请求校验、参数解析、错误返回
- `service.py`：核心执行流程（准备输入、执行 agent、处理结果、写入 workspace）
- `storage.py`：assistant/execution/workspace 全局实例管理
- `retrieval.py`：从 workspace 拉上下文，组装执行前输入
- `serializers.py`：Assistant 与 Workspace 的响应序列化
- `workspace/`：文件、记忆、日志三类数据管理

设计取向：保持 `service.py` 单文件内聚，不为拆分而拆分。

## 2. 与其他模块关系

- 上游：`director_agent`
  - 调 `POST /api/assistant/execute` 触发执行
  - 调执行查询接口获取结果状态
- 旁路：`task_stack`
  - Assistant 不直接驱动任务编排
  - Director 负责“何时执行哪个任务”，Assistant 只负责“执行这个任务”
- 下游：`agents/`
  - 通过 `AgentRegistry` 发现 descriptor
  - 按 descriptor 构造输入并执行 pipeline agent
- 推理能力来源：`inference/`
  - LLM 客户端来自 `inference/runtime/base_client.py`
  - media 服务（image/video/audio）由 `inference/generation/image_generators/service.py`、`inference/generation/video_generators/service.py`、`inference/generation/audio_generators/service.py` 提供
- 数据落盘：`workspace/`
  - 保存执行产生的文件
  - 记录运行日志和全局记忆

## 3. 执行模型（当前统一模型）

当前只保留一种执行模型：descriptor-driven pipeline agent。

核心链路：

1) `get_agent_registry().get_descriptor(agent_id)` 获取 descriptor  
2) `descriptor.build_input(...)` 构造标准输入  
3) `descriptor.build_equipped_agent(...).run(...)` 执行  
4) `service.process_results(...)` 归一化结果并写入 workspace  
5) 返回 execution 记录（含 `execution_id`、状态、结果、错误）

说明：

- 不再维护 sync/pipeline 双路径
- `routes.py` 只做编排，不写 agent 细节逻辑

## 4. 核心 API

### 4.1 模块信息

- `GET /api/assistant`

用于检查 assistant 运行状态、基础信息。

### 4.2 Sub-agent 发现与输入能力

- `GET /api/assistant/sub-agents`
- `GET /api/assistant/sub-agents/<agent_id>`
- `GET /api/assistant/agents/<agent_id>/inputs`

约束：

- 列表和单项详情复用同一套聚合结构（字段形状一致）
- 返回中包含 `asset_key` / `asset_type`，便于调用方做资产路由

### 4.3 执行与执行记录

- `POST /api/assistant/execute`
- `GET /api/assistant/executions/<execution_id>`
- `GET /api/assistant/executions/task/<task_id>`

执行请求：

```json
{
  "agent_id": "StoryAgent",
  "task_id": "task_xxx",
  "additional_inputs": {}
}
```

执行响应（示意）：

```json
{
  "execution_id": "exec_xxx",
  "status": "COMPLETED",
  "results": {},
  "error": null,
  "workspace_id": "workspace_global_xxx"
}
```

调试说明（materializer 路径）：

- 默认会清理 materializer 临时目录。
- 设置 `FW_KEEP_ASSISTANT_TEMP=1` 后，临时目录不会被清理，且执行结果会包含
  `results._materialize_temp_dir`，可用于手动检查中间产物。

### 4.4 Workspace 透传接口（由 assistant 暴露）

- `GET /api/assistant/workspace`
- `GET /api/assistant/workspace/summary`
- `GET /api/assistant/workspace/files`
- `GET /api/assistant/workspace/files/<file_id>`
- `GET /api/assistant/workspace/files/search`
- `GET /api/assistant/workspace/memory`
- `POST /api/assistant/workspace/memory`
- `GET /api/assistant/workspace/logs`
- `GET /api/assistant/workspace/search`

注意：Workspace 不直接对前端/director 暴露独立服务端口，统一经 Assistant 路由访问。

## 5. 常见开发入口（读代码顺序）

建议按下面顺序走读：

1) `routes.py` 的 `execute` 入口  
2) `service.py` 中执行主流程  
3) `retrieval.py` 看上下文如何拼装  
4) `workspace/workspace.py` 看文件/记忆/日志如何落盘  
5) `serializers.py` 看返回给 API 的字段形状

## 6. 常见排查点

- 执行 400：先查 `agent_id`、`task_id`、JSON body 是否有效
- 找不到 agent：检查 `AgentRegistry` 是否加载到 descriptor
- 执行成功但结果为空：检查 `process_results` 的归一化规则和 workspace 写入路径
- Director 侧字段不匹配：优先核对 `director_agent/api_client.py` 与此处请求体约定

## 7. 与 `inference/` 的职责边界（迁移约束）

为支持后续把部分 sub-agent 执行能力下沉到 `inference/`，Assistant 侧约束如下：

- **Assistant 保留**：任务读取、workspace 检索/落盘、execution 状态机、HTTP 语义。
- **Assistant 可下沉**：纯执行原语（如 descriptor 执行、media 文件归一化、推理配置适配）。
- **边界原则**：`inference` 不感知 task/layer/execution 业务模型，不直接读写 workspace。
- **兼容要求**：`/api/assistant/execute` 请求与响应结构保持不变，确保 Director/前端无感迁移。
