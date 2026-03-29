# Assistant Module

Assistant 模块是“执行入口 + 执行编排器”，负责把 Task Stack 的任务落地为具体 sub-agent 执行，并把结果写入 Workspace。

它是后端中的被动 API：  
前端和 `director_agent` 通过 HTTP 调它；Assistant 不直接与前端建立连接。

**四条数据边界（Director ↔ Assistant ↔ Sub-agent）的完整格式说明见下文 §4.3「四条数据边界」小节**（与 §3.5 叙述一致；该小节按表格 + 可复制 JSON 排版，便于速查）。

## 1. 文件职责

- `routes.py`：HTTP 路由，做请求校验、参数解析、错误返回（与 Task Stack 共用 `src/common_http.py` 的 `bad_request` / `json_body_or_error` / `required_query_or_error`）
- `service.py`：核心执行流程（准备输入、执行 agent、处理结果、写入 workspace）
- `state_store.py`：assistant runtime state（assistant/execution/workspace）全局实例管理
- `response_serializers.py`：Assistant 与 Workspace 的响应序列化
- `workspace/`：文件、记忆、日志、资产四类数据管理（`asset_manager.py` 负责 asset 持久化与索引）

维护说明（2026-03）：
- 执行期不按 descriptor 静态白名单过滤 pipeline 输入；上游 role 由 **输入打包 LLM** 从 `CATALOG_ENTRY` + `artifact_locations` 推断。生成与评估统一读取 **`InputBundleV2`**（`artifacts[]` + **`context`（含 `resolved_inputs`）** + `hints`），并以只读 `FrozenInputBundleV2` 传入 `build_input` / `run`。**global_memory** 仅存在于执行输入对象的**顶层**（供编排与审计），不直接合并进 bundle。
- 清理了未被调用的冗余方法：`MemoryManager.clear_memory`、`LogManager.get_all_logs`、`FileManager.store_file_from_path`、`FileManager.update_file_metadata`、`FileManager.get_all_files`。
- `workspace/file_manager.py`、`workspace/log_manager.py`、`workspace/memory_manager.py` 的告警输出统一改为 `logging`（替代 `print`）。
- `assistant/__init__.py` 移除了包级 `sys.path` 注入，改为惰性导出 `create_assistant_blueprint`；项目根路径注入前移到 `src/app.py` 启动边界。
- **执行契约**：`POST /api/assistant/execute` 的 JSON 根级为 **`agent_id`**、**`task_id`**、**`execute_fields`**（对象）。`execute_fields` 内常用键：`text`、`image`/`video`/`audio`。执行侧组装 `input_bundle_v2`，并在执行前转换为 `InputBundleV2`。

设计取向：保持 `service.py` 单文件内聚，不为拆分而拆分。

## 2. 与其他模块关系

- 上游：`director_agent`
  - 调 `POST /api/assistant/execute` 触发执行
  - 调执行查询接口获取结果状态
- 旁路：`task_stack`
  - Assistant **不读** Task Stack 存储；任务快照由调用方放在 **`execute_fields.text`**（Director 或 HTTP 客户端）。
  - Director 负责“何时执行哪个任务”，Assistant 只负责“在给定快照下执行这个 agent”
- 下游：`agents/`
  - 通过 `AgentRegistry` 发现 descriptor
  - 按 descriptor 构造输入并执行 pipeline agent
- 推理能力来源：`inference/`
  - LLM 客户端来自 `inference/clients/base/base_client.py`（推荐业务代码直接从 `inference/clients/__init__.py` 导入）
  - media 服务（image/video/audio）由 `inference/generation/image_generators/service.py`、`inference/generation/video_generators/service.py`、`inference/generation/audio_generators/service.py` 提供
- 数据落盘：`workspace/`
  - 保存执行产生的文件
  - 记录运行日志；**global_memory** 由 `process_results` 在每次执行结束（成功或失败）后用 **LLM #1** 写摘要，并与 Workspace 已落盘的 **确定性路径**（`_asset_index`、二进制持久化路径）合并为 **`artifact_locations`**，一并写入 `global_memory.md`
  - **`build_execution_inputs`**：先装配请求期 hints（`source_text` / 可选媒体），再加载 **global_memory**。随后由 **LLM #2** 基于 descriptor + `global_memory.artifact_locations` + file tree 输出 **`selected_roles`**；Assistant 按 role 读取 JSON 并补齐输入（无 deterministic 索引回退）。对多输入 agent（如 `VideoAgent` 需 `storyboard + keyframes`）会执行 required-roles 强校验，缺失即失败。
  - **输出持久化**：`process_results` 先构建确定性 persist plan，再由必选 **LLM #3** 结合 **workspace 根目录文件树**（`workspace_file_tree`，含 `artifacts/`）与 **task 子目录树**（`task_runtime_file_tree`）编排最终 `relative_path`；并带上 **`_naming_specs`** 与 `persist_naming_policy.json`，然后 `persist_execution_from_plan` 写盘并回写 `persist_plan_meta`。若 LLM 调用失败或返回非法 JSON，执行失败（无 fallback）。
  - JSON 快照命名采用短格式：`artifacts/<asset_key>/<asset_key>_exec_<n>.json`（例如 `artifacts/screenplay/screenplay_exec_2.json`）。**二进制媒体**（顶层结果里的 `file_content` 与 `_media_files`）默认落在 **`artifacts/media/<sub_agent_id>/<video|audio|image|other>/文件名`**：先按 **sub-agent**（`execution.agent_id`，如 `KeyFrameAgent`），再按扩展名分子目录；`keyframes_manifest.json` 仍随 keyframes 语义写在 `artifacts/keyframes/`。
  - **Keyframe**：`KeyFrameAgent` 成功后计划内包含 **`keyframes_manifest.json`**（有序 `items[]`），并在 memory 的 **`artifact_locations`** 中增加 **`role: keyframes_manifest`**

## 3. 执行模型（当前统一模型）

当前只保留一种执行模型：descriptor-driven pipeline agent。

核心链路：

1) `get_agent_registry().get_descriptor(agent_id)` 获取 descriptor  
2) `descriptor.build_input(task_id, input_bundle_v2, config)` 构造标准输入  
3) `descriptor.build_equipped_agent(...).run(..., input_bundle_v2=...)` 执行  
4) `service.process_results(...)` 触发 workspace 资产持久化、写入执行索引，并 **追加 global_memory 条目**（LLM 摘要 + 合并后的 **`artifact_locations`** + `execution_result` 快照 → `add_memory_entry`）  
5) 返回 execution 摘要（`task_id`、`execution_id`、`status`、`results`、`error`、`workspace_id`）

说明：

- 不再维护 sync/pipeline 双路径
- `routes.py` 只做编排，不写 agent 细节逻辑

## 3.5 数据边界：Director ↔ Assistant ↔ Sub-agent

以下四条为**当前代码中的真实契约**（Director 仅通过 HTTP 调 Assistant；Assistant 与 Sub-agent 在同一进程内调用 `agents` 包）。

### 3.5.1 Director → Assistant（HTTP 输入）

- **方法与路径**：`POST /api/assistant/execute`
- **JSON 体形状**：根级 **`agent_id`**、**`task_id`**、**`execute_fields`**（对象，可 `{}`）。若省略 `execute_fields` 则服务层按空对象处理。若 `execute_fields` 存在且不是 JSON object → **400**。
- **`agent_id`**：与 `AGENT_REGISTRY` 键一致（如 `"StoryAgent"`）。
- **`task_id`**：Task Stack 任务 ID；执行作用域**仅**使用此 ID。
- **`execute_fields`（嵌套对象）**：
  - **`text`**：**必须是字符串**（语义上替代旧版根级 **`task_description`**）→ `input_bundle_v2["source_text"]`（`_text_for_source_text()` 仅 `strip`；非 `str` → **400**）。Task Stack 当前仍常存 **dict** 描述时，由 **Director** 在调用 Assistant 前用 `_task_stack_description_to_assistant_text()` 收成字符串，**不在** Assistant 内解析结构化字段。**可省略** `text` 键。
  - **`image` / `video` / `audio`**：替代旧版 **`task_attachments`** 列表；按类型分键，各为一个字符串引用（data URI / URL 等），复制到 bundle 同名键。
- **流水线 `input_bundle_v2` / `config`**：仅服务内组装，**不是** HTTP 字段。
- **HTTP 客户端**：`director_agent/api_client.py` 的 `execute_agent()` 发送 `{ agent_id, task_id, execute_fields }`。

### 3.5.2 Assistant → Director（HTTP 输出）

- **成功（200）**：`process_results()` 返回并经 `serialize_response_value` 序列化的 **object**，核心字段：
  - `task_id`：与请求根级 `task_id` 一致（Assistant 回显）。
  - `execution_id`：本次 `AgentExecution.id`（与 `GET /api/assistant/executions/task/{task_id}` 返回列表中对应条目的 `id` 一致）。
  - `status`：`COMPLETED` / `FAILED`（枚举字符串值）。
  - `results`：Sub-agent 产出经 `service._execute_pipeline_descriptor()` 归一化后的 **object**（见 §3.5.4）；持久化后可能含 `_asset_index` 等。
  - `error`：失败时的错误信息；成功时多为 `null`。
  - `workspace_id`：全局 workspace ID。
- **Director 侧**：可直接使用响应中的 `task_id`；可再 `GET /api/assistant/executions/task/{task_id}` 取最新执行详情挂到 `execution_result["execution"]`。
- **错误**：校验失败 **400** `{ "error": "..." }`（如 `execute_fields.text` 非字符串）；未知 agent **404**；**global_memory 摘要 LLM** 失败或返回非法 JSON 时 **500**（`AssistantGlobalMemorySyncError` 消息，无静默回退）；其它执行抛错 **500** `{ "error": "Execution failed: ..." }`（无上述成功体）。

### 3.5.3 Assistant → Sub-agent（进程内输入）

边界在 `AssistantService.build_execution_inputs()` → `package_data()` → `_merge_execution_inputs()`，得到 **`inputs: dict`**，再传入 `_execute_pipeline_descriptor()`。

- **`inputs` 典型内容**：
  - `task_id`。
  - **`input_bundle_v2`**：初始只含请求期 hints（`execute_fields.text` → `source_text`；`image`/`video`/`audio` 注入同名键）；随后按 LLM 选择的 **`selected_roles`** 从 `global_memory.artifact_locations` 读取 JSON 并写入同名键。
  - **global_memory**（执行输入顶层）：来自 `get_memory_brief(task_id=...)`（无 `content`），用于 role 选择与路径定位；**不**传入 `descriptor.build_input` 的只读 bundle。
  - `execute_fields`：与 HTTP 传入一致；已废弃键 **`_memory_brief`** 会被静默忽略。
- **映射**（`service._map_pipeline_inputs`）：
  - 字符串 `task_id`、**`InputBundleV2`**、`config`（**不含** `global_memory`）。
  - bundle 的数据经 `workspace.hydrate_indexed_assets` 再装回 bundle；`FrozenInputBundleV2` 只读传入 `build_input` / `run`，`MaterializeContext` 携带同一 v2 输入视图供 materializer 使用。
- **调用 Sub-agent**（每个 `SubAgentDescriptor`）：
  - `typed_input = descriptor.build_input(task_id, readonly_input_bundle_v2, config)` → 各 agent 的 **Pydantic Input 模型**（只读 **`FrozenInputBundleV2`**；业务侧优先读 **`context["resolved_inputs"]`**；**不含** 顶层 `global_memory`）。
  - 若 descriptor 带 materializer：`MaterializeContext(task_id, input_bundle_v2, persist_binary)`，否则为 `null`。
  - `await agent.run(typed_input, input_bundle_v2=readonly_input_bundle_v2, materialize_ctx=...)`

### 3.5.4 Sub-agent → Assistant（进程内输出）

- **运行时类型**：`BaseAgent.run()` 返回 **`ExecutionResult`**（`output`、`eval_result`、`passed`、`attempts`、`media_assets`、`asset_dict`）。
- **写入 `execution.results` 的 dict**（`service._execute_pipeline_descriptor`）：
  - 优先使用 **`asset_dict`**（含 materializer 写入的 `uri` 等）；否则用 **`output`** 的 `model_dump()` 或 `dict(...)`。
  - 若有 **`media_assets`**：增加 **`_media_files`**（workspace 收集的持久化信息）。
  - 调试：**`_execution_debug`**（`attempts`、`overall_pass`、`eval_summary` 等）。
- **`process_results` 之后**：可能对 `results` 写入 **`_asset_index`**（JSON 快照索引）；业务字段由各 agent 输出 schema 决定，系统字段多以 `_` 前缀标识。

---

**与 §4.3 的关系**：§3.5 为分条叙述；**§4.3「四条数据边界」小节**用表格 + JSON 示例写同一套契约，便于复制对照。

## 4. 核心 API

### 4.1 模块信息

- `GET /api/assistant`

用于检查 assistant 运行状态、基础信息。

### 4.2 Sub-agent 发现

- `GET /api/assistant/sub-agents`
- `GET /api/assistant/sub-agents/<agent_id>`

约束：

- 列表项与 `GET .../sub-agents/<agent_id>` 单项均来自同一套 descriptor 元数据（字段形状一致）
- 返回包含 `asset_key`、`capabilities`、`description`；**不再**返回占位的 `schemas` / `input_schema` / `output_schema` / `contract` / `version` / `author` / `created_at` / `updated_at`

### 4.3 执行与执行记录

- `POST /api/assistant/execute`
- `GET /api/assistant/executions/task/<task_id>`

#### 四条数据边界（输入 / 输出格式）

以下四条与 **§3.5** 描述同一套契约；本节用**表格 + JSON 示例**写清楚，便于对照实现（`routes.py` → `AssistantService` → `agents`）。

---

**（1）Director → Assistant：HTTP 输入**

| 项目 | 说明 |
|------|------|
| 方法 / 路径 | `POST /api/assistant/execute` |
| 体结构 | 根级 **`agent_id`**、**`task_id`**、**`execute_fields`**（JSON 对象）。流水线 **`input_bundle_v2` 装配** / **`config`** 非 HTTP 字段（由 Assistant 内部组装）。 |
| 必填（根级） | `agent_id`、`task_id` |
| **`execute_fields` 内常用键** | `text`（任务快照，常与 Task `description` 一致）、`image`/`video`/`audio`（可选） |
| 客户端 | `director_agent/api_client.py` 的 `execute_agent()` 发送 `{ agent_id, task_id, execute_fields }` |

示例（最小 + 常见可选）：

```json
{
  "agent_id": "StoryAgent",
  "task_id": "task_xxx",
  "execute_fields": {
    "text": "生成一支短片"
  }
}
```

---

**（2）Assistant → Director：HTTP 输出**

| 项目 | 说明 |
|------|------|
| 成功 **200** | JSON object，由 `process_results()` + `serialize_response_value()` 序列化 |
| 字段 | `task_id`、`execution_id`、`status`（`COMPLETED` \| `FAILED`）、`results`（见下（4）落在 HTTP 里的形态）、`error`（失败信息，成功多为 `null`）、`workspace_id` |
| Director 侧 | 使用响应内 `task_id`；可 `GET /api/assistant/executions/task/{task_id}` 取最新执行详情并挂到 `execution_result["execution"]` |
| 失败 | **400** / **404** / **500**：`{ "error": "..." }`，**无**上述成功体的完整字段 |

示例（成功）：

```json
{
  "task_id": "task_xxx",
  "execution_id": "exec_xxx",
  "status": "COMPLETED",
  "results": {
    "meta": {},
    "content": {},
    "_execution_debug": {
      "attempts": 1,
      "overall_pass": true,
      "eval_summary": "…"
    },
    "_asset_index": {
      "asset_key": "story_blueprint",
      "execution_id": "exec_xxx",
      "file_id": "file_xxx",
      "json_uri": "/path/to/snapshot.json"
    }
  },
  "error": null,
  "workspace_id": "workspace_global_…"
}
```

（`results` 里业务键因 agent 而异；`_asset_index`、`_media_files` 等为系统/调试扩展字段。）

---

**（3）Assistant → Sub-agent：进程内输入（非 HTTP）**

| 项目 | 说明 |
|------|------|
| 形态 | 无独立 HTTP；`AssistantService` 构造 **`inputs: dict`** 后调用 `_execute_pipeline_descriptor()` |
| `inputs` 典型键 | `task_id`、`input_bundle_v2`（请求 hints + 按 LLM `selected_roles` 读取回填的 JSON）、**顶层** `global_memory`（简报行，无 `content`）、`execute_fields`（与 HTTP 一致；已废弃键 `_memory_brief` 会被忽略） |
| 映射 | `_map_pipeline_inputs(inputs)` → 字符串 `task_id`、`InputBundleV2`（经 `hydrate_indexed_assets` 后只读传入）、`config`；**不**把 `global_memory` 合并进 bundle |
| 调用 descriptor | `typed_input = build_input(task_id, readonly_input_bundle_v2, config)`（**Pydantic Input**）；若有 materializer 则 `MaterializeContext(...)`；最后 `await agent.run(typed_input, input_bundle_v2=readonly_input_bundle_v2, materialize_ctx=…)` |

---

**（4）Sub-agent → Assistant：进程内输出（非 HTTP）**

| 项目 | 说明 |
|------|------|
| 运行时 | `BaseAgent.run()` → **`ExecutionResult`**：`output`、`eval_result`、`passed`、`attempts`、`media_assets`、`asset_dict` |
| 写入 `execution.results` | `_execute_pipeline_descriptor`：优先 **`asset_dict`**，否则 **`output.model_dump()`**（或 dict 化） |
| 常见附加键 | `_media_files`（持久化后的媒体索引）、`_execution_debug`（`attempts`、`overall_pass`、`eval_summary`） |
| 持久化后 | `process_results` 可能往 `results` 写入 **`_asset_index`**（JSON 快照索引）；该 dict 即 HTTP **（2）** 中返回的 `results` |

---

执行请求（**常见**：`execute_fields.text` 与 Task Stack 中该任务的 `description` 一致）：

```json
{
  "agent_id": "StoryAgent",
  "task_id": "task_xxx",
  "execute_fields": { "text": "…" }
}
```

说明：
- `routes.py` 将根级 `execute_fields` 交给 `AssistantService`（省略时按 `{}`）。
- 上表「（1）～（4）」与 **§3.5** 为同一契约的不同排版（本节偏速查）。
- `execute_fields` 若存在且非 object → **400**。
- 默认自动覆盖：若 Assistant 检测到同 `task_id + producer_agent_id + asset_key` 的历史资产，则本次写入按覆盖模式执行
- 覆盖策略仅依赖自动检测（`auto_overwrite`）；`execute_fields` 中不再支持 `_assistant_control` 机制
- 覆盖范围包含文件资产（image/video/audio/binary）和结构化 JSON snapshot

执行响应（**最小示意**；完整字段与 `results` 形态见上文 **（2）**）：

```json
{
  "task_id": "task_xxx",
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

- materializer 临时目录在执行后默认清理，不再提供保留开关。

### 4.4 Workspace 透传接口（由 assistant 暴露）

- `GET /api/assistant/workspace/files`
- `GET /api/assistant/workspace/files/<file_id>`
- `GET /api/assistant/workspace/memory/entries`
- `POST /api/assistant/workspace/memory/entries`
- `GET /api/assistant/workspace/memory/brief`
- `GET /api/assistant/workspace/logs`

注意：Workspace 不直接对前端/director 暴露独立服务端口，统一经 Assistant 路由访问。

`/api/assistant/workspace/memory/entries` 用于写入/读取 **global_memory** 条目（落盘 **`{workspace_id}/global_memory.md`**；每条含 **`content`、`task_id`、`agent_id`、`created_at`、`execution_result`**、可选 **`artifact_locations`**；写入时 **`task_id` 必填**；同文件内另有 **File tree** 快照供人读，编排以 **`artifact_locations`** + 运行时 file-tree API 为准）：

- 请求体：`content`（必填）、`task_id`（必填）、`agent_id`（可选）、`execution_result`（可选，JSON 对象，执行摘要）

`/api/assistant/workspace/memory/brief`：**global_memory** 简报（`created_at` 降序，**无** `content` 键，**全部**匹配行）。

- 输入：`task_id`、`agent_id`（可选）
- **sub-agent 注入**与 Director 共用 **`get_memory_brief`** 同一形状；需含 `content` 时用 **`GET .../memory/entries`** 或 `list_memory_entries`

## 5. 常见开发入口（读代码顺序）

建议按下面顺序走读：

1) `routes.py` 的 `execute` 入口  
2) `service.py` 中执行主流程  
4) `workspace/workspace.py` 看文件/记忆/日志如何落盘  
5) `response_serializers.py` 看返回给 API 的字段形状

补充：asset 文件落盘、JSON snapshot 索引、indexed asset hydration 统一由 `workspace/asset_manager.py` 负责，`service.py` 只保留执行编排。
同时，每个 agent 执行结果对应的 JSON 快照轻量索引（`_asset_index` 识别）也已收敛到 `AssetManager`。
执行状态日志（`execution_started` / `execution_completed` / `execution_failed`）也通过 `workspace/workspace.py` 的 façade 方法写入，`service.py` 不再直接操作 `log_manager`。
并且 `AssetManager` 通过 `Workspace` 注入的回调完成文件持久化与日志写入，不再直接依赖 `FileManager`/`LogManager`，边界更清晰。
当前 `json_uri` 与 media `uri` 的读取也统一走 `FileManager.read_binary_from_uri`（由 `Workspace` 注入到 `AssetManager`），`service.py` 不再直接按路径读取文件。
新增：`service.py` 覆盖写入策略统一为自动检测（`auto_overwrite`），不再解析 `_assistant_control`。

## 6. Asset / Memory / Log 边界约定

Assistant 内部统一采用以下三层语义边界：

- **Asset（事实产物层）**
  - 可执行、可复用的输入/输出产物（JSON 结构、媒体文件引用等）
  - 执行前 Assistant 在内存中组装的 **`input_bundle_v2` 映射**（含各 role 的 JSON、经 `hydrate_indexed_assets` 展开后写入 `InputBundleV2.artifacts` / `hints`）是事实产物的临时工作集；**子 agent 业务输入以 `context["resolved_inputs"]` 为准**（由输入打包 LLM 选定 role 并加载）。
  - 例如 `VideoAgent` materializer 从 **`context["resolved_inputs"]`** 读取 `keyframes` / `storyboard` 等，对齐每个 shot 的 keyframe `image_asset.uri` 与 storyboard 元数据
  - `AudioAgent` 在生成 `final_audio_asset` 后，会与上游 `video.final_video_asset` 做 mux，产出 `final_delivery_asset`
  - 文件类产物落盘时会写入统一 metadata（`execution_id`、`task_id`、`producer_agent_id`、`asset_key`）
- **Memory（结论层 / global_memory）**
  - 任务窗口内的结论、策略、约束、下一步建议
  - 由 `workspace/memory/entries` 与 `workspace/memory/brief` 维护，不替代事实产物
  - `/memory/brief` 与 `build_execution_inputs` 均用 `get_memory_brief`（无 `content`、全量匹配行）
- **Log（过程与审计层）**
  - 记录执行状态流转、读写行为、错误信息
  - 用于可追踪性与排障，不承载长文本业务正文
  - 执行链路会写细化事件类型（如 `execution_started` / `execution_completed` / `execution_failed` / `asset_persisted`），用于后续策略级统计
  - 终态 execution 日志会附带 `details.retry_attempts` 与 `details.eval_summary`

一句话：**Asset 保证正确性，Memory 保证效率，Log 保证可审计性。**

### 6.1 装配映射示例（`build_execution_inputs` 阶段的 `input_bundle_v2` dict）

执行期在写入 `InputBundleV2` 之前，装配用 **dict** 可能含轻量索引（hydrate 后变为完整 JSON）。**`descriptor.build_input` 侧推荐只读 `context["resolved_inputs"]`**（若存在）：

```json
{
  "source_text": "A retired watchmaker can rewind one minute three times.",
  "story_blueprint": {
    "asset_key": "story_blueprint",
    "json_uri": "Runtime/workspace_xxx/artifacts/story_blueprint/story_blueprint_exec_10.json",
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

- 上述映射是执行时**内存工作集**（最终映射为 `InputBundleV2`），不是独立数据库表；默认可能保存轻量索引而非完整大 JSON，直至 `hydrate_indexed_assets` 展开。
- 文件本体落在 `Runtime/<workspace_id>/`，metadata 作为审计与追踪信息。
- metadata 的存放位置是 **workspace 文件记录**（`FileMetadata.metadata`，由 `workspace/file_manager.py` 持久化到 `.file_metadata.json`）。
- Assistant 在真正调用 sub-agent 前，会按 `json_uri` 自动加载完整 JSON（对 sub-agent 透明）。
- 装配 dict 中的每个 key 默认不携带统一 metadata；只有落盘文件条目带该 metadata。
- 对于 media asset（如 `image_asset/video_asset/audio_asset`），Assistant 在 `_media_files` 落盘后会把结构内 `uri` 回填为 workspace 持久路径，避免临时目录清理后失效。

## 7. Pipeline 输入与 descriptor 约定

执行前 Assistant **不会**按 descriptor 静态白名单裁剪装配映射：任务工作集里已有的 role 键会经 `hydrate_indexed_assets` 展开，并以只读 **`FrozenInputBundleV2`** 传入 `build_input` / `run` / materializer（具体出现哪些 role 由 **global_memory + 输入打包 LLM** 与历史 execution 决定）。

仍保留的约束：

- 传给 descriptor 的 **`input_bundle_v2` 视图**在执行期内为只读（`FrozenInputBundleV2`），避免在构造输入阶段误改共享工作集。
- `user_text_key`、`asset_key` 保持 descriptor 契约字段；**上游语义依赖以 `context["resolved_inputs"]` 中的 role 为准**，不再在 descriptor 中硬编码 `INPUT_*_ASSET_KEY` 索引全局产物。

HTTP 不提供流水线装配映射 / `config`；它们由本服务对同一 `task_id` 的 **artifact_locations、LLM `selected_roles`、`execute_fields.text`**（及可选媒体键）拼装。

### 7.1 什么时候需要修改 sub-agent 代码

- 在 `build_input` 中新增对某 **role** 的读取（`resolved_inputs.get("role_name")`）时，应同步更新该 agent 的 **`CATALOG_ENTRY`**（供输入打包 LLM 推断 `required_roles`）与 evaluator，避免字符串漂移。
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
- **请求契约**：`POST /api/assistant/execute` 根级为 `agent_id`、`task_id`、`execute_fields`；响应信封保持原有字段形状。
