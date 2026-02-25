# Workspace Module

Workspace 是 Assistant 的共享运行空间，负责文件、全局记忆和日志。

## 目录

- `workspace.py`：统一 facade，协调 file/memory/log manager
- `file_manager.py`：文件存储与元数据查询
- `memory_manager.py`：`global_memory.md` 读写与长度控制
- `log_manager.py`：`logs.jsonl` 日志记录与检索
- `models.py`：`FileMetadata`、`LogEntry`

## 存储结构

```
Runtime/{workspace_id}/
├── .file_metadata.json
├── global_memory.md
└── logs.jsonl
```

## API（由 assistant routes 暴露）

- `GET /api/assistant/workspace`
- `GET /api/assistant/workspace/summary`
- `GET /api/assistant/workspace/files`
- `GET /api/assistant/workspace/files/<file_id>`
- `GET /api/assistant/workspace/files/search`
- `GET /api/assistant/workspace/memory`
- `POST /api/assistant/workspace/memory`
- `GET /api/assistant/workspace/logs`
- `GET /api/assistant/workspace/search`

## 返回结构（关键字段）

### Summary

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

### Write Memory

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

## 注意事项

- `MAX_MEMORY_LENGTH = 100000`，超过会截断并附带提示
- workspace 为全局共享实例，由 assistant storage 创建/持有
- 路由层负责 HTTP 形态，workspace 层负责领域操作与日志落盘
