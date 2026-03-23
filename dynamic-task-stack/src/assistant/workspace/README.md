# Workspace Module

Workspace 是 Assistant 的共享运行空间，负责四类数据：

- 文件（agents 产生的产物与元数据）
- 记忆（结构化 **短期** STM 条目；LTM 已关闭）
- 运行日志（可检索的操作记录）
- 资产索引（由 `asset_manager.py` 维护）

Workspace 不是独立对外服务；它通过 `assistant/routes.py` 对外暴露 HTTP 接口。

## 1. 文件职责

- `workspace.py`
  - 对上提供统一 facade（汇总 file/memory/log 三类能力）
  - 输出 summary（文件数量、memory 条目数量、日志数量）
- `file_manager.py`
  - 文件落盘、读取、列表、筛选、搜索
  - 管理 `.file_metadata.json`
- `memory_manager.py`
  - 管理 `memory_entries_short_term.json`（仅 STM）
  - 生成 `memory_brief`（仅 STM Top-K；`long_term` 恒为 `[]`）
- `log_manager.py`
  - 记录 `logs.jsonl`
  - 支持按条件过滤和搜索
- `asset_manager.py`
  - 执行资产持久化、JSON snapshot 索引、indexed asset hydration
- `models.py`
  - `FileMetadata`、`LogEntry` 等结构定义

## 2. 运行目录结构

```text
Runtime/{workspace_id}/
├── .file_metadata.json
├── memory_entries_short_term.json
└── logs.jsonl
```

补充：

- `workspace_id` 通常为全局实例（例如 `workspace_global_20260320_083015_123456`）
- Runtime 目录由系统自动创建并维护

## 3. 对外 API（由 Assistant 暴露）

- `GET /api/assistant/workspace`
- `GET /api/assistant/workspace/summary`
- `GET /api/assistant/workspace/files`
- `GET /api/assistant/workspace/files/<file_id>`
- `GET /api/assistant/workspace/files/search`
- `GET /api/assistant/workspace/memory/entries`
- `POST /api/assistant/workspace/memory/entries`
- `GET /api/assistant/workspace/memory/brief`
- `GET /api/assistant/workspace/logs`
- `GET /api/assistant/workspace/search`

说明：前端和 Director 都通过 Assistant 调 Workspace，不直接操作 Runtime 文件。

## 4. 关键返回结构

### 4.1 Summary

`/api/assistant/workspace` 与 `/summary` 返回 `workspace.get_summary()`：

```json
{
  "workspace_id": "workspace_global_20260320_083015_123456",
  "created_at": "2026-01-01T00:00:00",
  "updated_at": "2026-01-01T00:00:00",
  "file_count": 3,
  "memory_info": {
    "entries_count": 8,
    "short_term_entries_count": 8,
    "long_term_entries_count": 0,
    "short_term_entries_file_path": "Runtime/workspace_global_xxx/memory_entries_short_term.json",
    "long_term_entries_file_path": null,
    "legacy_entries_file_path": "Runtime/workspace_global_xxx/memory_entries.json"
  },
  "log_count": 12,
  "runtime_path": "Runtime/workspace_global_xxx"
}
```

### 4.2 结构化 Memory Entry（仅 STM）

`POST /api/assistant/workspace/memory/entries` 请求示例：

```json
{
  "content": "Last run failed on vocals; lower music bed next time.",
  "tier": "short_term",
  "kind": "failure_pattern",
  "priority": 4,
  "confidence": 0.6,
  "task_id": "task_xxx"
}
```

`tier: "long_term"` 会被拒绝（400）。

`GET /api/assistant/workspace/memory/brief?task_id=task_xxx&short_term_limit=6`：查询参数为 `task_id`、`agent_id`（可选）、`short_term_limit`（默认 6）；**不再接受** `long_term_limit`（LTM 未实现）。

响应示例：

```json
{
  "short_term": [],
  "long_term": []
}
```

## 5. 常见流程

### 流程 A：Agent 产物写入文件

1) Assistant 收到执行结果  
2) `service.py` 调 workspace 保存文件  
3) `file_manager.py` 写文件并更新元数据  
4) `log_manager.py` 追加一条操作日志  
5) API 返回可查询的 `file_id`

重跑覆盖模式（`_assistant_control.overwrite_assets=true`）下，流程 A 会先执行“同任务同 agent 同 asset_key 旧文件清理”，再写入新文件。  
覆盖范围包含：
- 二进制资产（image/audio/video/other）
- JSON snapshot（`<agent_id>_<asset_key>_<execution_id>.json`）

文件落盘命名补充：

- Runtime 真实文件名会保留语义前缀（来自原始 `filename`，并附加顺序号），例如：
  `storyagent_story_blueprint_exec_xxx_file_000001.json`

### 流程 B：Director 维护 STM

1) 每次子 agent 执行完成后，Director 使用 LLM 归纳执行结论并写 `short_term` 条目（`execution_summary`）  
2) 下次规划前 Director 调 `GET /memory/brief` 获取短期计划上下文（`long_term` 为空）  
3) 短期条目用于 rerun / 下游 agent 选择建议（如 `metadata.suggested_next_agent`）

LTM（用户消息提取偏好、instruction LLM 改写）已移除。

## 6. 约束与边界

- Workspace 由 assistant state store 持有全局实例
- Workspace 层只做领域能力，不处理 HTTP 协议细节
- 对外字段序列化由 `assistant/response_serializers.py` 负责
- 覆盖写入依赖文件 metadata 中的 `task_id` / `producer_agent_id` / `asset_key`（及 `asset_variant`）进行精确匹配

## 7. 常见排查点

- 文件列表为空：先查 `.file_metadata.json` 是否存在且可读
- Memory 条目缺失：检查 tier/kind 过滤条件与 `memory_entries_*` 文件内容
- 日志搜索无结果：确认 `resource_type`/`operation_type` 条件是否匹配
