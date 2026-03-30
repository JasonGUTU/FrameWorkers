# Workspace Module

Workspace 是 Assistant 的共享运行空间，负责四类数据：

- 文件（agents 产生的产物与元数据）
- 全局记忆 **global_memory**（**按 workspace 单文件**落盘 **`global_memory.md`**，与 `.file_metadata.json`、`logs.jsonl` 并列；内嵌 **Entries** JSON 数组，每条含 **`content` / `task_id` / `agent_id` / `created_at` / `execution_result`**（执行摘要对象，可为 `{}`）/ 可选 **`artifact_locations`**（落盘路径列表）；另含 **File tree** 快照块仅供**人读**，编排以 **`artifact_locations`** + 运行时 **`Workspace.get_workspace_root_file_tree_text()`** 为准）
- 运行日志（可检索的操作记录）
- 资产索引（由 `asset_manager.py` 维护）

Workspace 不是独立对外服务；它通过 `assistant/routes.py` 对外暴露 HTTP 接口。

## 1. 文件职责

- `workspace.py`
  - 对上提供统一 facade（汇总 file/memory/log 三类能力）
  - 输出 summary（文件数量、memory 条目数量、日志数量）
  - Assistant 侧输入装配已由 **global_memory 的 `artifact_locations` + LLM `selected_roles`** 驱动；Workspace 仍提供 **`hydrate_indexed_assets`**，将 bundle 中带 `json_uri` 的轻量索引展开为完整 JSON（供执行路径与历史兼容）
- `file_manager.py`
  - 文件落盘、读取、列表、筛选、搜索
  - 管理 `.file_metadata.json`
- `memory_manager.py`
  - 管理 **`Runtime/{workspace_id}/global_memory.md`**（写入**必须**带 `task_id`，并存入 entry 字段）；人类可读说明 + **File tree**（快照，非权威）+ **Entries** JSON 数组（`content`、`task_id`、`agent_id`、`created_at`、`execution_result`、可选 `artifact_locations`）。**输入打包 LLM（#1）** 与 **持久化路径 LLM（#2）** 均注入 **`Workspace.get_workspace_root_file_tree_text()`**（workspace 根下完整树，含 **`artifacts/`**）；已移除按 task 子目录单独列树的 API。
  - **`get_memory_brief`**：返回 **`{"global_memory": [...]}`**，条目**无** `content`，`created_at` 降序，当前查询范围内**全部**行（**Director**、**`GET .../memory/brief`**）。可按 `task_id`、`agent_id` 过滤。**`build_execution_inputs`** 使用 **`list_memory_entries`**（含 `content`）。也可用 **`GET .../memory/entries`** 浏览完整字段。
- `log_manager.py`
  - 记录 `logs.jsonl`
  - 支持按条件过滤和搜索
- `asset_manager.py`
  - 执行资产持久化、JSON snapshot 索引、indexed asset hydration
  - 资产落盘统一走 `store_file_at_relative_path`（无 `store_file` fallback）
- `models.py`
  - `FileMetadata`、`LogEntry` 等结构定义

精简说明（2026-03）：移除了未被引用的 `Workspace.get_file_content`、`FileManager.get_file_content`、`Workspace.get_recent_logs`、`LogManager.get_recent_logs`，统一通过现有 `get_file` / `read_binary_from_uri` / `get_logs(limit=...)` 路径使用，减少重复 API 面。

精简说明（2026-03 续）：移除仅单测使用的 `AssetManager.build_pipeline_asset_value` 与 `Workspace` 上对应的转发方法，以及从未被调用的 `Workspace.is_asset_index_entry` 门面（索引判断保留在 `AssetManager` 内部供 hydration 使用）。

## 2. 运行目录结构

```text
Runtime/{workspace_id}/
├── .file_metadata.json
├── global_memory.md
└── logs.jsonl
```

补充：

- `workspace_id` 通常为全局实例（例如 `workspace_global_20260320_083015_123456`）
- Runtime 目录由系统自动创建并维护

## 3. 对外 API（由 Assistant 暴露）

- `GET /api/assistant/workspace/files`
- `GET /api/assistant/workspace/files/<file_id>`
- `GET /api/assistant/workspace/memory/entries`
- `POST /api/assistant/workspace/memory/entries`
- `GET /api/assistant/workspace/memory/brief`
- `GET /api/assistant/workspace/logs`

说明：前端和 Director 都通过 Assistant 调 Workspace，不直接操作 Runtime 文件。

## 4. 关键返回结构

### 4.1 结构化 Memory Entry（仅 global memory）

`POST /api/assistant/workspace/memory/entries` 请求示例：

```json
{
  "content": "Last run failed on vocals; lower music bed next time.",
  "task_id": "task_xxx",
  "agent_id": "AudioAgent",
  "execution_result": {
    "status": "FAILED",
    "execution_id": "exec_001",
    "error": "timeout"
  }
}
```

**响应体**含：`content`、`agent_id`、`created_at`（UTC ISO8601）、`execution_result`（对象，缺省为 `{}`）。**`task_id` 必填**（否则 400）。

`GET /api/assistant/workspace/memory/brief?task_id=task_xxx`：查询参数为 `task_id`、`agent_id`（可选）。响应 **`{"global_memory": [...]}`**，每条**无** `content`，`created_at` 降序，**全部**匹配条目。

若带 `task_id`，读取该任务文件；**不按** `agent_id` 过滤。若未带 `task_id` 但带 `agent_id`，则按 `agent_id` 过滤聚合结果；两者皆无时为全表聚合。

响应示例：

```json
{
  "global_memory": []
}
```

单条示例（**无** `content` 键）：

```json
{
  "global_memory": [
    {
      "agent_id": "VideoAgent",
      "created_at": "2026-01-01T00:00:00+00:00",
      "execution_result": {
        "status": "FAILED",
        "execution_id": "exec_001",
        "error": "timeout"
      }
    }
  ]
}
```

## 5. 常见流程

### 流程 A：Agent 产物写入文件

1) Assistant 收到执行结果  
2) `service.py` 调 workspace 保存文件  
3) `file_manager.py` 写文件并更新元数据  
4) `log_manager.py` 追加一条操作日志  
5) API 返回可查询的 `file_id`

重跑覆盖模式（Assistant 自动检测到同任务同 agent 同 asset_key 历史资产）下，流程 A 会先执行“同任务同 agent 同 asset_key 旧文件清理”，再写入新文件。  
覆盖范围包含：
- 二进制资产（image/audio/video/other）
- JSON snapshot（`<agent_id>_<asset_key>_<execution_id>.json`）

文件落盘命名补充：

- Runtime 真实文件名会保留语义名称（来自原始 `filename`）；若同目录重名，仅追加短随机后缀避免覆盖（不再附加全局顺序号）。

### 流程 B：Assistant 写入 global_memory，Director 只读

1) 每次子 agent 执行完成后，**Assistant**（`service.py` → `process_results`）追加一条 `global_memory` 条目（LLM `content` + **`artifact_locations`** + `task_id` + `agent_id` + `created_at` + `execution_result`），落盘 **`Runtime/{workspace_id}/global_memory.md`**  
2) 规划前 Director 调 `GET /memory/brief`，取 **`global_memory`** 极薄行（仅 `task_id` / `agent_id` / `created_at` / **`execution_result`**；**无** `content`、**无** **`artifact_locations`**；路径由 Assistant 侧 **`list_memory_entries` / 文件树** 使用，不在 brief 暴露）  
3) Reasoning：若**最新**一条 **`execution_result.status` 为 `FAILED`**，优先用该条 **`agent_id`** 作为重试；否则可将 **最新**条目的 `agent_id` 作为续跑提示（brief 按 `created_at` 降序）

### 流程 C：`global_memory.md` 中的 File tree（人读 vs 事实）

- **人读**：每次追加记忆条目会重写 `global_memory.md`，并嵌入当前 workspace 下的 **File tree** 文本快照（可能截断），便于打开文件时扫一眼目录。  
- **事实**：Assistant 编排侧 LLM 以 **`artifact_locations`** 与 **`get_workspace_root_file_tree_text()`** 为准，**不解析** md 里的 File tree。  
- 仅增删 workspace 文件、未追加记忆时，可调用 `refresh_file_tree()` 更新快照（与 `Workspace.store_file` / `delete_file` 联动）。

## 6. 约束与边界

- Workspace 由 assistant state store 持有全局实例
- Workspace 层只做领域能力，不处理 HTTP 协议细节
- 对外字段序列化由 `assistant/response_serializers.py` 负责
- 覆盖写入依赖文件 metadata 中的 `task_id` / `producer_agent_id` / `asset_key`（及 `asset_variant`）进行精确匹配

## 7. 常见排查点

- 文件列表为空：先查 `.file_metadata.json` 是否存在且可读
- Memory 条目缺失：检查 `task_id` 是否对应目录下 `global_memory.md` 与 **Entries** JSON 块
- 日志搜索无结果：确认 `resource_type`/`operation_type` 条件是否匹配
