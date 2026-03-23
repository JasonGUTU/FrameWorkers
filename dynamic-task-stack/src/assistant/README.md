# Assistant Module

Assistant 模块是“执行入口 + 执行编排器”，负责把 Task Stack 的任务落地为具体 sub-agent 执行，并把结果写入 Workspace。

它是后端中的被动 API：  
前端和 `director_agent` 通过 HTTP 调它；Assistant 不直接与前端建立连接。

## 1. 文件职责

- `routes.py`：HTTP 路由，做请求校验、参数解析、错误返回
- `service.py`：核心执行流程（准备输入、执行 agent、处理结果、写入 workspace）
- `state_store.py`：assistant runtime state（assistant/execution/workspace）全局实例管理
- `workspace_context.py`：从 workspace 拉上下文，组装执行前输入
- `response_serializers.py`：Assistant 与 Workspace 的响应序列化
- `workspace/`：文件、记忆、日志、资产四类数据管理（`asset_manager.py` 负责 asset 持久化与索引）

维护说明（2026-03）：
- 执行期不再按 descriptor 白名单过滤 pipeline `assets`（全量工作集经 hydrate 后传入 sub-agent）；`upstream_keys` 等仍用于文档/Director，键使用契约由 `tests/agents/test_descriptor_asset_contract.py` 在测试阶段校验。
- 清理了未被调用的冗余方法：`WorkspaceContextBuilder.retrieve_assets`、`MemoryManager.clear_memory`、`LogManager.get_all_logs`、`FileManager.store_file_from_path`、`FileManager.update_file_metadata`、`FileManager.get_all_files`。
- `workspace/file_manager.py`、`workspace/log_manager.py`、`workspace/memory_manager.py` 的告警输出统一改为 `logging`（替代 `print`）。
- `assistant/__init__.py` 移除了包级 `sys.path` 注入，改为惰性导出 `create_assistant_blueprint`；项目根路径注入前移到 `src/app.py` 启动边界。
- 对外 API 与执行流程无变化，行为保持一致。

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
  - LLM 客户端来自 `inference/clients/base/base_client.py`（推荐业务代码直接从 `inference/clients/__init__.py` 导入）
  - media 服务（image/video/audio）由 `inference/generation/image_generators/service.py`、`inference/generation/video_generators/service.py`、`inference/generation/audio_generators/service.py` 提供
- 数据落盘：`workspace/`
  - 保存执行产生的文件
  - 记录运行日志和短期结构化记忆（STM；LTM 已关闭）

## 3. 执行模型（当前统一模型）

当前只保留一种执行模型：descriptor-driven pipeline agent。

核心链路：

1) `get_agent_registry().get_descriptor(agent_id)` 获取 descriptor  
2) `descriptor.build_input(project_id, draft_id, assets, config)` 构造标准输入（`project_id`/`draft_id` 由 Assistant 从 `task_id` 等推导；不需要的 agent 可在实现里忽略前两参且不放入 Input 模型）  
3) `descriptor.build_equipped_agent(...).run(...)` 执行  
4) `service.process_results(...)` 触发 workspace 资产持久化并写入执行索引  
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

- 列表项与 `GET .../sub-agents/<agent_id>` 单项均来自同一套 descriptor 元数据（字段形状一致）
- 返回包含 `asset_key` / `asset_type`、`capabilities`、`description`；**不再**返回占位的 `schemas` / `input_schema` / `output_schema` / `contract` / `version` / `author` / `created_at` / `updated_at`
- `GET .../agents/<agent_id>/inputs` 与列表项对齐：`agent_id`、`agent_name`、`asset_key`、`asset_type`、`capabilities`、`description`（无 JSON Schema 占位字段）

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

覆盖写入控制（用于 Director 触发局部重跑）：

```json
{
  "agent_id": "VideoAgent",
  "task_id": "task_xxx",
  "additional_inputs": {
    "_assistant_control": {
      "overwrite_assets": true
    }
  }
}
```

说明：
- `_assistant_control` 是 Assistant 内部控制区，不会透传给 sub-agent 的 `build_input`
- `overwrite_assets=true` 时，当前 execution 产出的同 `task_id + producer_agent_id + asset_key` 旧文件会先清理，再写入新文件
- 覆盖范围包含文件资产（image/video/audio/binary）和结构化 JSON snapshot

执行响应（示意）：

```json
{
  "execution_id": "exec_xxx",
  "status": "COMPLETED",
  "results": {
    "_execution_debug": {
      "attempts": 1,
      "overall_pass": true,
      "eval_summary": "L1/L2/L3 passed"
    }
  },
  "error": null,
  "workspace_id": "workspace_global_20260320_083015_123456"
}
```

说明：

- `results._execution_debug.attempts` 表示该 sub-agent 在自评估质量门下的实际尝试次数（含重试）。
- `results._execution_debug.eval_summary` 提供最终评估摘要，便于快速定位重试原因。
- 若结果中包含二进制字段（如 materializer 临时结构中的 `bytes`），`routes.py`
  会通过 `response_serializers.py` 统一转换为 JSON 友好结构（`{"_type":"binary","size_bytes":N}`），避免
  `Object of type bytes is not JSON serializable`。

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
- `GET /api/assistant/workspace/memory/entries`
- `POST /api/assistant/workspace/memory/entries`
- `GET /api/assistant/workspace/memory/brief`
- `GET /api/assistant/workspace/logs`
- `GET /api/assistant/workspace/logs/insights`
- `GET /api/assistant/workspace/search`

注意：Workspace 不直接对前端/director 暴露独立服务端口，统一经 Assistant 路由访问。

`/api/assistant/workspace/logs/insights` 用于策略级日志分析（失败趋势、跨任务活跃度、事件类型分布）。
支持参数：

- `window_hours`：仅统计最近 N 小时日志
- `top_k`：各榜单返回条目数（默认 5）

`/api/assistant/workspace/memory/entries` 用于结构化写入/读取**短期**记忆条目：

- `tier`: 仅支持 `short_term`（`long_term` 会返回 400）
- `kind`: `constraint/decision/strategy/failure_pattern/next_action/user_preference/execution_summary/note`
- 可选关联：`task_id`、`agent_id`、`source_asset_refs`、`priority`、`confidence`

`/api/assistant/workspace/memory/brief` 用于执行前 STM 简报（Top-K 聚合）：

- 输入：`task_id`、`agent_id`、`short_term_limit`（响应仍含 `long_term: []`，LTM 未启用）
- 输出：`short_term[]` + `long_term[]`（后者恒为 `[]`）
- 典型用途：Director 规划/执行时读取近期执行摘要；用户偏好型 LTM 不再写入或注入

## 5. 常见开发入口（读代码顺序）

建议按下面顺序走读：

1) `routes.py` 的 `execute` 入口  
2) `service.py` 中执行主流程  
3) `workspace_context.py` 看上下文如何拼装  
4) `workspace/workspace.py` 看文件/记忆/日志如何落盘  
5) `response_serializers.py` 看返回给 API 的字段形状

补充：asset 文件落盘、JSON snapshot 索引、indexed asset hydration 统一由 `workspace/asset_manager.py` 负责，`service.py` 只保留执行编排。
同时，pipeline `assets` 中每个 agent 结果条目的轻量索引拼装（`_asset_index` 识别与 fallback）也已收敛到 `AssetManager`。
执行状态日志（`execution_started` / `execution_completed` / `execution_failed`）也通过 `workspace/workspace.py` 的 façade 方法写入，`service.py` 不再直接操作 `log_manager`。
并且 `AssetManager` 通过 `Workspace` 注入的回调完成文件持久化与日志写入，不再直接依赖 `FileManager`/`LogManager`，边界更清晰。
当前 `json_uri` 与 media `uri` 的读取也统一走 `FileManager.read_binary_from_uri`（由 `Workspace` 注入到 `AssetManager`），`service.py` 不再直接按路径读取文件。
新增：`service.py` 会先拆分 `additional_inputs` 中的 `_assistant_control`，执行期输入与持久化策略解耦；覆盖策略仅影响持久化阶段。

## 6. Asset / Memory / Log 边界约定

Assistant 内部统一采用以下三层语义边界：

- **Asset（事实产物层）**
  - 可执行、可复用的输入/输出产物（JSON 结构、媒体文件引用等）
  - 执行输入中的 `assets` 是事实产物的临时工作集
  - 例如 `VideoAgent` 读取 `assets["keyframes"]` 中每个 shot 的 keyframe `image_asset.uri` 作为生成条件
  - `AudioAgent` 在生成 `final_audio_asset` 后，会与上游 `video.final_video_asset` 做 mux，产出 `final_delivery_asset`
  - 文件类产物落盘时会写入统一 metadata（`execution_id`、`task_id`、`producer_agent_id`、`asset_key`）
- **Memory（结论层）**
  - 任务窗口内的结论、策略、约束、下一步建议（仅 STM）
  - 由 `workspace/memory/entries` 与 `workspace/memory/brief` 维护，不替代事实产物
  - `long_term` 条目类型已关闭；`/memory/brief` 仍返回该字段但恒为空数组以保持响应形状稳定
  - 通过 `/memory/brief` 聚合 STM Top-K，避免把全量历史直接塞给下游 agent
- **Log（过程与审计层）**
  - 记录执行状态流转、读写行为、错误信息
  - 用于可追踪性与排障，不承载长文本业务正文
  - 执行链路会写细化事件类型（如 `execution_started` / `execution_completed` / `execution_failed` / `asset_persisted`），用于后续策略级统计
  - 终态 execution 日志会附带 `details.retry_attempts` 与 `details.eval_summary`

一句话：**Asset 保证正确性，Memory 保证效率，Log 保证可审计性。**

### 6.1 Asset 结构示例

执行期（编排态）`assets` 字典示例（轻量索引）：

```json
{
  "draft_idea": "A retired watchmaker can rewind one minute three times.",
  "story_blueprint": {
    "asset_key": "story_blueprint",
    "json_uri": "Runtime/workspace_xxx/file_000101.json",
    "file_id": "file_000101_abcd1234",
    "execution_id": "exec_10_abcd1234"
  },
  "user_story_outline": "User provided long outline text..."
}
```

文件类产物落盘后的 metadata（文件系统持久态）示例：

```json
{
  "execution_id": "exec_12_abcd1234",
  "task_id": "task_001",
  "producer_agent_id": "VideoAgent",
  "asset_key": "sh_001"
}
```

说明：

- `assets` 是执行时工作集，不是独立数据库表；默认保存轻量索引而非完整大 JSON。
- 文件本体落在 `Runtime/<workspace_id>/`，metadata 作为审计与追踪信息。
- metadata 的存放位置是 **workspace 文件记录**（`FileMetadata.metadata`，由 `workspace/file_manager.py` 持久化到 `.file_metadata.json`）。
- Assistant 在真正调用 sub-agent 前，会按 `json_uri` 自动加载完整 JSON（对 sub-agent 透明）。
- `assets` 内存字典中的每个 key 默认不携带统一 metadata；只有落盘文件条目带该 metadata。
- 对于 media asset（如 `image_asset/video_asset/audio_asset`），Assistant 在 `_media_files` 落盘后会把结构内 `uri` 回填为 workspace 持久路径，避免临时目录清理后失效。

## 7. Pipeline `assets` 与 descriptor 约定

执行前 Assistant **不会**按 descriptor 白名单裁剪 `assets`：任务工作集里已有的键会原样经过 `hydrate_indexed_assets` 后传入 `build_input` / `build_upstream` / materializer（由编排与历史 execution 决定内容是否出现）。

仍保留的约束：

- 传给 descriptor 的 `assets` 视图在执行期内为只读映射（`MappingProxyType` 包装），避免在构造输入阶段误改共享工作集。
- `upstream_keys`、`user_text_key`、`asset_key` 继续用于 **文档与 Director 规划**，并由 `tests/agents/test_descriptor_asset_contract.py` 校验 `build_input` 所读键与声明一致（测试期契约，非运行时拦截）。

`additional_inputs.assets` 会与系统打包的 `assets` 合并，不会整体覆盖。

### 7.1 什么时候需要修改 sub-agent 代码

- 新增了 `build_input` 中 `assets.get("new_key")` 的读取键时，应同步更新 descriptor 的 `upstream_keys` 等声明，便于契约测试与编排文档一致。
- 修改用户直输文本键、上游依赖或 `asset_key` 语义时，同样更新 descriptor 与相关测试。

## 8. 常见排查点

- 执行 400：先查 `agent_id`、`task_id`、JSON body 是否有效
- 找不到 agent：检查 `AgentRegistry` 是否加载到 descriptor
- 执行成功但结果为空：检查 `process_results` 的归一化规则和 workspace 写入路径
- Director 侧字段不匹配：优先核对 `director_agent/api_client.py` 与此处请求体约定

## 9. 与 `inference/` 的职责边界（迁移约束）

为支持后续把部分 sub-agent 执行能力下沉到 `inference/`，Assistant 侧约束如下：

- **Assistant 保留**：任务读取、workspace 检索/落盘、execution 状态机、HTTP 语义。
- **Assistant 可下沉**：纯执行原语（如 descriptor 执行、media 文件归一化、推理配置适配）。
- **边界原则**：`inference` 不感知 task/layer/execution 业务模型，不直接读写 workspace。
- **兼容要求**：`/api/assistant/execute` 请求与响应结构保持不变，确保 Director/前端无感迁移。
