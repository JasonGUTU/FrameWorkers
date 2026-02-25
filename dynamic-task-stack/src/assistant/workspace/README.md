# Workspace Module

Workspace 是 Assistant 的共享运行空间，负责三类数据：

- 文件（agents 产生的产物与元数据）
- 全局记忆（跨任务可复用文本上下文）
- 运行日志（可检索的操作记录）

Workspace 不是独立对外服务；它通过 `assistant/routes.py` 对外暴露 HTTP 接口。

## 1. 文件职责

- `workspace.py`
  - 对上提供统一 facade（汇总 file/memory/log 三类能力）
  - 输出 summary（文件数量、memory 使用率、日志数量）
- `file_manager.py`
  - 文件落盘、读取、列表、筛选、搜索
  - 管理 `.file_metadata.json`
- `memory_manager.py`
  - 管理 `global_memory.md` 的写入/读取/长度控制
- `log_manager.py`
  - 记录 `logs.jsonl`
  - 支持按条件过滤和搜索
- `models.py`
  - `FileMetadata`、`LogEntry` 等结构定义

## 2. 运行目录结构

```text
Runtime/{workspace_id}/
├── .file_metadata.json
├── global_memory.md
└── logs.jsonl
```

补充：

- `workspace_id` 通常为全局实例（例如 `workspace_global_xxx`）
- Runtime 目录由系统自动创建并维护

## 3. 对外 API（由 Assistant 暴露）

- `GET /api/assistant/workspace`
- `GET /api/assistant/workspace/summary`
- `GET /api/assistant/workspace/files`
- `GET /api/assistant/workspace/files/<file_id>`
- `GET /api/assistant/workspace/files/search`
- `GET /api/assistant/workspace/memory`
- `POST /api/assistant/workspace/memory`
- `GET /api/assistant/workspace/logs`
- `GET /api/assistant/workspace/search`

说明：前端和 Director 都通过 Assistant 调 Workspace，不直接操作 Runtime 文件。

## 4. 关键返回结构

### 4.1 Summary

`/api/assistant/workspace` 与 `/summary` 返回 `workspace.get_summary()`：

```json
{
  "workspace_id": "workspace_global_xxx",
  "created_at": "2026-01-01T00:00:00",
  "updated_at": "2026-01-01T00:00:00",
  "file_count": 3,
  "memory_info": {
    "length": 128,
    "max_length": 100000,
    "usage_percent": 0.128,
    "is_full": false,
    "file_path": "Runtime/workspace_global_xxx/global_memory.md"
  },
  "log_count": 12,
  "runtime_path": "Runtime/workspace_global_xxx"
}
```

注意字段：`usage_percent`（不是 `usage_percentage`）。

### 4.2 写入 Memory

`POST /api/assistant/workspace/memory` 返回 `memory_manager.write_memory()` 结果：

```json
{
  "success": true,
  "was_truncated": false,
  "original_length": 64,
  "final_length": 64,
  "message": "Memory written successfully"
}
```

## 5. 常见流程

### 流程 A：Agent 产物写入文件

1) Assistant 收到执行结果  
2) `service.py` 调 workspace 保存文件  
3) `file_manager.py` 写文件并更新元数据  
4) `log_manager.py` 追加一条操作日志  
5) API 返回可查询的 `file_id`

### 流程 B：Director 同步记忆摘要

1) Director 在任务完成后调用 `POST /api/assistant/workspace/memory`  
2) `memory_manager.py` 写入到 `global_memory.md`  
3) 若超过 `MAX_MEMORY_LENGTH` 则截断并在返回体标记 `was_truncated=true`

## 6. 约束与边界

- `MAX_MEMORY_LENGTH = 100000`
- Workspace 由 assistant storage 持有全局实例
- Workspace 层只做领域能力，不处理 HTTP 协议细节
- 对外字段序列化由 `assistant/serializers.py` 负责

## 7. 常见排查点

- 文件列表为空：先查 `.file_metadata.json` 是否存在且可读
- Memory 写入成功但内容不对：检查是否触发截断（`was_truncated`）
- 日志搜索无结果：确认 `resource_type`/`operation_type` 条件是否匹配
