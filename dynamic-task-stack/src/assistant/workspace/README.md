# Workspace Module

Workspace 模块提供了完整的文件系统、Global Memory 和日志管理功能。

## 模块结构

```
workspace/
├── __init__.py          # 模块导出
├── models.py            # 数据模型（FileMetadata, LogEntry）
├── workspace.py         # 主 Workspace 类
├── file_manager.py      # 文件管理器
├── memory_manager.py    # Global Memory 管理器
└── log_manager.py       # 日志管理器
```

## 核心功能

### 1. 文件管理（FileManager）

管理所有产生的文件资源（图片、视频、文档等）。

**主要功能：**
- ✅ 文件存储：将文件存入 `Runtime/{workspace_id}/` 目录
- ✅ 文件编号：自动为文件分配唯一编号（file_000001.png）
- ✅ 元数据记录：记录文件描述、产生时间、路径等信息
- ✅ 文件查询：支持按类型、标签、创建者等条件查询
- ✅ 文件搜索：根据描述或文件名搜索文件

**文件存储结构：**
```
Runtime/
└── {workspace_id}/
    ├── file_000001.png
    ├── file_000002.mp4
    ├── file_000003.txt
    ├── .file_metadata.json    # 文件元数据索引
    ├── global_memory.md        # Global Memory 文件
    └── logs.jsonl              # 日志文件（JSON Lines 格式）
```

**使用示例：**
```python
# 存储文件
file_meta = workspace.store_file(
    file_content=image_bytes,
    filename="storyboard.png",
    description="Storyboard frame 1",
    created_by="storyboard_agent",
    tags=["storyboard", "frame1"]
)

# 查询文件
files = workspace.list_files(file_type="image", tags=["storyboard"])

# 搜索文件
results = workspace.search_files("storyboard", file_type="image")
```

### 2. Global Memory 管理（MemoryManager）

管理全局共享记忆，以 Markdown 格式存储。

**主要功能：**
- ✅ 读写操作：支持读取和写入 Global Memory
- ✅ 追加模式：支持追加内容到现有记忆
- ✅ 长度校验：自动校验和限制记忆长度（默认 100KB）
- ✅ 智能截断：超出长度时智能截断（在合理位置）
- ✅ 使用统计：提供记忆使用情况统计

**长度限制：**
- 最大长度：100,000 字符（100KB）
- 超出时自动截断并添加提示信息
- 提供使用百分比和容量警告

**使用示例：**
```python
# 写入记忆
result = workspace.write_memory("# Project Notes\n\nImportant information...")

# 追加记忆
result = workspace.append_memory("\n\n## Update\n\nNew information...")

# 读取记忆
memory = workspace.read_memory()

# 获取记忆信息
info = workspace.get_memory_info()
# {
#   "length": 5000,
#   "max_length": 100000,
#   "usage_percent": 5.0,
#   "is_full": False
# }
```

### 3. 日志管理（LogManager）

管理操作日志和记录，以 JSON Lines 格式存储。

**主要功能：**
- ✅ 操作记录：记录所有读写创建删除操作
- ✅ JSON 格式：每条日志为独立的 JSON 对象
- ✅ 查询过滤：支持按操作类型、资源类型、Agent ID、Task ID 过滤
- ✅ 日志搜索：支持在日志详情中搜索
- ✅ 持久化存储：日志持久化到 `logs.jsonl` 文件

**日志格式：**
```json
{
  "id": "log_abc123",
  "timestamp": "2024-01-01T10:00:00",
  "operation_type": "create",
  "resource_type": "file",
  "resource_id": "file_000001",
  "details": {"filename": "image.png"},
  "agent_id": "storyboard_agent",
  "task_id": "task_1"
}
```

**使用示例：**
```python
# 获取日志（自动记录，无需手动调用）
logs = workspace.get_logs(
    operation_type="create",
    resource_type="file",
    agent_id="storyboard_agent",
    limit=10
)

# 搜索日志
results = workspace.log_manager.search_logs("storyboard")
```

## Workspace 主类

`Workspace` 类统一协调所有管理器，提供统一的接口。

**主要方法：**

### 文件操作
- `store_file()` - 存储文件
- `get_file()` - 获取文件元数据
- `get_file_content()` - 获取文件内容
- `list_files()` - 列出文件
- `search_files()` - 搜索文件
- `delete_file()` - 删除文件

### Memory 操作
- `read_memory()` - 读取 Global Memory
- `write_memory()` - 写入 Global Memory
- `append_memory()` - 追加到 Global Memory
- `get_memory_info()` - 获取记忆信息

### 日志操作
- `get_logs()` - 获取日志
- `get_recent_logs()` - 获取最近日志

### 综合操作
- `search_all()` - 综合搜索（文件、记忆、日志）
- `get_summary()` - 获取工作空间摘要

## API 端点

### Workspace 信息

#### 获取工作空间摘要

**GET** `/api/assistant/workspace`

获取工作空间的基本摘要信息。

**响应：**

```json
{
    "workspace_id": "workspace_global_abc123",
    "created_at": "2024-01-01T10:00:00",
    "updated_at": "2024-01-01T10:05:00",
    "file_count": 10,
    "memory_length": 5000,
    "log_count": 50
}
```

**状态码：**
- `200` - 成功
- `404` - 工作空间不存在

---

#### 获取详细摘要

**GET** `/api/assistant/workspace/summary`

获取工作空间的详细摘要和统计信息。

**响应：**

```json
{
    "workspace_id": "workspace_global_abc123",
    "created_at": "2024-01-01T10:00:00",
    "updated_at": "2024-01-01T10:05:00",
    "statistics": {
        "file_count": 10,
        "memory_length": 5000,
        "memory_max_length": 100000,
        "memory_usage_percent": 5.0,
        "log_count": 50
    }
}
```

**状态码：**
- `200` - 成功
- `404` - 工作空间不存在

---

### 文件管理

#### 列出文件

**GET** `/api/assistant/workspace/files`

列出工作空间中的文件，支持多种过滤条件。

**查询参数：**

- `file_type` (可选) - 文件类型：`image`, `video`, `document`, `other`
- `tags` (可选) - 标签列表（可多次指定）：`?tags=tag1&tags=tag2`
- `created_by` (可选) - 创建者 ID（Agent ID 或用户 ID）
- `limit` (可选) - 返回数量限制（整数）

**示例：**

```
GET /api/assistant/workspace/files?file_type=image&tags=storyboard&limit=10
```

**响应：**

```json
[
    {
        "id": "file_000001",
        "filename": "storyboard.png",
        "description": "Storyboard frame 1",
        "file_type": "image",
        "file_extension": ".png",
        "file_path": "Runtime/workspace_global_abc123/file_000001.png",
        "size_bytes": 102400,
        "created_at": "2024-01-01T10:00:00",
        "created_by": "storyboard_agent",
        "tags": ["storyboard", "frame1"],
        "metadata": {}
    },
    ...
]
```

**状态码：**
- `200` - 成功
- `404` - 工作空间不存在

---

#### 获取文件元数据

**GET** `/api/assistant/workspace/files/<file_id>`

根据文件 ID 获取文件元数据。

**响应：**

```json
{
    "id": "file_000001",
    "filename": "storyboard.png",
    "description": "Storyboard frame 1",
    "file_type": "image",
    "file_extension": ".png",
    "file_path": "Runtime/workspace_global_abc123/file_000001.png",
    "size_bytes": 102400,
    "created_at": "2024-01-01T10:00:00",
    "created_by": "storyboard_agent",
    "tags": ["storyboard", "frame1"],
    "metadata": {}
}
```

**状态码：**
- `200` - 成功
- `404` - 工作空间或文件不存在

---

#### 搜索文件

**GET** `/api/assistant/workspace/files/search`

根据查询字符串搜索文件。

**查询参数：**

- `query` (必需) - 搜索查询字符串
- `file_type` (可选) - 文件类型过滤
- `limit` (可选) - 返回数量限制（默认：10）

**示例：**

```
GET /api/assistant/workspace/files/search?query=storyboard&file_type=image&limit=5
```

**响应：**

```json
[
    {
        "id": "file_000001",
        "filename": "storyboard.png",
        "description": "Storyboard frame 1",
        "file_type": "image",
        "file_path": "Runtime/workspace_global_abc123/file_000001.png",
        "created_at": "2024-01-01T10:00:00"
    },
    ...
]
```

**状态码：**
- `200` - 成功
- `400` - 缺少查询参数
- `404` - 工作空间不存在

---

### Global Memory

#### 读取记忆

**GET** `/api/assistant/workspace/memory`

读取 Global Memory 的内容和信息。

**响应：**

```json
{
    "content": "# Project Notes\n\nImportant information...",
    "info": {
        "length": 5000,
        "max_length": 100000,
        "usage_percent": 5.0,
        "is_full": false
    }
}
```

**状态码：**
- `200` - 成功
- `404` - 工作空间不存在

---

#### 写入记忆

**POST** `/api/assistant/workspace/memory`

写入或追加内容到 Global Memory。

**请求体：**

```json
{
    "content": "# Project Notes\n\nImportant information...",
    "append": false  // 可选：是否追加（默认：false，覆盖）
}
```

**追加模式示例：**

```json
{
    "content": "\n\n## Update\n\nNew information...",
    "append": true
}
```

**响应：**

```json
{
    "success": true,
    "length": 5000,
    "max_length": 100000,
    "usage_percent": 5.0,
    "is_full": false,
    "truncated": false  // 是否被截断
}
```

如果内容超出最大长度：

```json
{
    "success": true,
    "length": 100000,
    "max_length": 100000,
    "usage_percent": 100.0,
    "is_full": true,
    "truncated": true,
    "message": "Content was truncated to fit within max_length"
}
```

**状态码：**
- `200` - 写入成功
- `400` - 请求体无效或缺少必需字段
- `404` - 工作空间不存在

---

### 日志

#### 获取日志

**GET** `/api/assistant/workspace/logs`

获取工作空间的日志记录，支持多种过滤条件。

**查询参数：**

- `operation_type` (可选) - 操作类型：`create`, `read`, `update`, `delete`
- `resource_type` (可选) - 资源类型：`file`, `memory`, `workspace`
- `agent_id` (可选) - Agent ID
- `task_id` (可选) - 任务 ID
- `limit` (可选) - 返回数量限制（整数）

**示例：**

```
GET /api/assistant/workspace/logs?operation_type=create&resource_type=file&agent_id=storyboard_agent&limit=10
```

**响应：**

```json
[
    {
        "id": "log_abc123",
        "timestamp": "2024-01-01T10:00:00",
        "operation_type": "create",
        "resource_type": "file",
        "resource_id": "file_000001",
        "details": {
            "filename": "storyboard.png",
            "description": "Storyboard frame 1",
            "file_type": "image",
            "size_bytes": 102400
        },
        "agent_id": "storyboard_agent",
        "task_id": "task_1_abc123"
    },
    ...
]
```

**状态码：**
- `200` - 成功
- `404` - 工作空间不存在

---

### 综合搜索

#### 综合搜索

**GET** `/api/assistant/workspace/search`

在工作空间中执行综合搜索，可同时搜索文件、记忆和日志。

**查询参数：**

- `query` (必需) - 搜索查询字符串
- `types` (可选) - 搜索类型列表（可多次指定）：`?types=files&types=memory&types=logs`（默认：全部）

**示例：**

```
GET /api/assistant/workspace/search?query=storyboard&types=files&types=memory
```

**响应：**

```json
{
    "query": "storyboard",
    "results": {
        "files": [
            {
                "id": "file_000001",
                "filename": "storyboard.png",
                "description": "Storyboard frame 1",
                "file_path": "Runtime/workspace_global_abc123/file_000001.png",
                "created_at": "2024-01-01T10:00:00"
            },
            ...
        ],
        "memory": {
            "matches": [
                {
                    "snippet": "...storyboard generation...",
                    "context": "..."
                },
                ...
            ]
        },
        "logs": [
            {
                "id": "log_abc123",
                "timestamp": "2024-01-01T10:00:00",
                "operation_type": "create",
                "resource_type": "file",
                "details": {
                    "filename": "storyboard.png"
                }
            },
            ...
        ]
    },
    "summary": {
        "files_count": 5,
        "memory_matches": 2,
        "logs_count": 10
    }
}
```

**状态码：**
- `200` - 成功
- `400` - 缺少查询参数
- `404` - 工作空间不存在

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
- `404` - 资源不存在（工作空间、文件等）

---

## 注意事项

1. **文件编号**：文件自动编号，格式为 `file_000001.{ext}`，存储在 `Runtime/{workspace_id}/` 目录。

2. **Memory 长度限制**：
   - 最大长度：100,000 字符（100KB）
   - 超出时自动截断并添加提示信息
   - 提供使用百分比和容量警告

3. **日志格式**：使用 JSON Lines 格式（`.jsonl`），每行一个 JSON 对象。

4. **线程安全**：Workspace 操作不是线程安全的，应在单线程环境使用或添加锁。

5. **路径管理**：Runtime 路径自动检测，指向项目根目录的 `Runtime/` 文件夹。

6. **全局共享**：所有 Agents 共享一个全局工作空间，可以访问相同的文件、记忆和日志。

## 使用示例

### 存储 Agent 产生的文件

```python
# Agent 执行后产生文件
image_bytes = generate_storyboard_image()

# 存储到 workspace
file_meta = workspace.store_file(
    file_content=image_bytes,
    filename="storyboard_frame_1.png",
    description="First frame of the storyboard",
    created_by="storyboard_agent",
    tags=["storyboard", "frame1", "task_123"]
)

# 文件会自动编号：file_000001.png
# 存储在：Runtime/{workspace_id}/file_000001.png
```

### 更新 Global Memory

```python
# Agent 执行后更新记忆
workspace.append_memory(
    f"\n\n## Storyboard Generation\n\n"
    f"Generated storyboard frame 1 at {datetime.now()}\n"
    f"File ID: {file_meta.id}"
)
```

### 查询和检索

```python
# 搜索相关文件
storyboard_files = workspace.search_files("storyboard", file_type="image")

# 读取记忆
memory = workspace.read_memory()

# 综合搜索
results = workspace.search_all(
    query="storyboard",
    search_files=True,
    search_memory=True,
    search_logs=True
)
```

## 数据持久化

所有数据都持久化到文件系统：

1. **文件**：存储在 `Runtime/{workspace_id}/` 目录
2. **文件元数据**：存储在 `.file_metadata.json`
3. **Global Memory**：存储在 `global_memory.md`
4. **日志**：存储在 `logs.jsonl`（JSON Lines 格式）

## 注意事项

1. **文件编号**：文件自动编号，格式为 `file_000001.{ext}`
2. **Memory 长度**：超过 100KB 会自动截断
3. **日志格式**：使用 JSON Lines 格式，每行一个 JSON 对象
4. **线程安全**：Workspace 操作不是线程安全的，应在单线程环境使用或添加锁
5. **路径管理**：Runtime 路径自动检测，指向项目根目录的 `runtime/` 文件夹
