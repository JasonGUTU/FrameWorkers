# Dynamic Task Stack Backend

Dynamic Task Stack 是一个强大的任务管理和 Agent 编排系统，提供分层级的任务执行框架和统一的 Agent 管理平台。

## 目录

- [系统概述](#系统概述)
- [架构设计](#架构设计)
- [子模块设计](#子模块设计)
- [数据结构](#数据结构)
- [API 路由](#api-路由)
- [快速开始](#快速开始)
- [使用示例](#使用示例)
- [开发指南](#开发指南)

---

## 系统概述

Dynamic Task Stack 由两个核心系统组成：

### 1. Task Stack（任务栈系统）
- **分层级任务管理**：支持多层级任务组织，每层可包含多个任务
- **Hook 机制**：每层支持执行前后的 Pre-hook 和 Post-hook
- **执行指针**：跟踪当前执行位置，支持动态修改未执行的任务
- **原子操作**：确保任务替换、批量操作等操作的原子性
- **批量操作**：支持一次性执行多个操作，提高效率

### 2. Assistant（助手系统）
- **统一管理**：只有一个全局 assistant 来管理所有的 sub-agent
- **自动发现**：自动扫描和注册根目录下的所有 agents
- **共享工作空间**：所有 agents 共享一个全局工作空间（文件系统）
- **信息检索**：Assistant 从工作空间中检索信息，然后分发给各个 agent
- **执行流程**：完整的 6 步执行流程（查询输入 → 准备环境 → 检索信息 → 打包数据 → 执行 → 处理结果）

---

## 架构设计

### 目录结构

```
dynamic-task-stack/
├── src/
│   ├── app.py                   # Flask 应用入口
│   ├── task_stack/              # Task Stack 模块
│   │   ├── __init__.py
│   │   ├── models.py            # 数据模型
│   │   ├── routes.py            # API 路由
│   │   └── storage.py           # 数据存储
│   └── assistant/               # Assistant 模块
│       ├── __init__.py
│       ├── models.py            # Assistant 数据模型
│       ├── routes.py            # Assistant API 路由
│       ├── service.py           # Assistant 核心业务逻辑
│       ├── storage.py           # Assistant 数据存储
│       ├── retrieval.py         # 检索模块（PLACEHOLDER）
│       ├── agent_core/           # Agent 核心框架（基础设施）
│       │   ├── __init__.py
│       │   ├── base_agent.py     # BaseAgent 抽象基类
│       │   └── agent_registry.py # Agent 发现和注册机制
│       └── workspace/           # 工作空间模块
│           ├── __init__.py
│           ├── workspace.py     # 工作空间核心
│           ├── file_manager.py  # 文件管理
│           ├── log_manager.py   # 日志管理
│           ├── memory_manager.py # 内存管理
│           └── models.py        # 工作空间数据模型
├── requirements.txt
├── run.py
├── test_api.py
├── README.md                    # 本文档
└── USAGE_EXAMPLES.md            # 使用示例
```

### 设计原则

1. **代码隔离**：Task Stack 和 Assistant 系统完全分离，互不干扰
2. **统一管理**：Assistant 统一管理所有 sub-agents
3. **自动发现**：Agents 自动注册，无需手动配置
4. **易于扩展**：添加新 Agent 只需创建文件夹和实现类
5. **向后兼容**：支持旧的 agents 目录结构
6. **线程安全**：所有存储操作都是线程安全的

---

## 子模块设计

### Task Stack 模块

#### 1. models.py - 数据模型

定义了所有 Task Stack 相关的数据模型：

- **枚举类型**：
  - `TaskStatus`: 任务状态（PENDING, IN_PROGRESS, COMPLETED, FAILED, CANCELLED）
  - `ReadingStatus`: 消息读取状态（UNREAD, READ）
  - `BatchOperationType`: 批量操作类型

- **核心数据类**：
  - `UserMessage`: 用户消息
  - `Task`: 任务
  - `TaskStackEntry`: 任务栈条目
  - `TaskLayer`: 任务层
  - `ExecutionPointer`: 执行指针

- **批量操作模型**：
  - `BatchOperation`: 单个批量操作
  - `BatchOperationsRequest`: 批量操作请求

#### 2. storage.py - 数据存储

`TaskStackStorage` 类提供线程安全的内存存储：

**用户消息操作**：
- `create_user_message()`: 创建用户消息（支持 sender_type 参数：worker, director, subagent, user）
- `get_user_message()`: 获取消息
- `get_all_user_messages()`: 获取所有消息
- `update_message_read_status()`: 更新消息读取状态（使用 director_read_status 替代 worker_read_status）

**任务操作**：
- `create_task()`: 创建任务
- `get_task()`: 获取任务
- `get_all_tasks()`: 获取所有任务
- `update_task()`: 更新任务
- `delete_task()`: 删除任务

**层操作**：
- `create_layer()`: 创建层
- `get_layer()`: 获取层
- `get_all_layers()`: 获取所有层
- `add_task_to_layer()`: 添加任务到层
- `remove_task_from_layer()`: 从层中移除任务
- `replace_task_in_layer()`: 原子替换任务
- `update_layer_hooks()`: 更新层的 hooks
- `modify_task_stack()`: 修改任务栈（插入层并添加任务）

**执行指针操作**：
- `get_execution_pointer()`: 获取执行指针
- `set_execution_pointer()`: 设置执行指针
- `advance_execution_pointer()`: 推进执行指针
- `get_next_task()`: 获取下一个要执行的任务

**批量操作**：
- `batch_operations()`: 执行批量操作（原子性）

**内部辅助方法**（用于批量操作，避免死锁）：
- `_create_task_internal()`
- `_create_layer_internal()`
- `_add_task_to_layer_internal()`
- `_remove_task_from_layer_internal()`
- `_replace_task_in_layer_internal()`
- `_update_layer_hooks_internal()`

#### 3. routes.py - API 路由

提供完整的 RESTful API：

**用户消息路由**：
- `POST /api/messages/create` - 创建用户消息
- `GET /api/messages/<msg_id>` - 获取消息
- `GET /api/messages/list` - 获取所有消息
- `PUT /api/messages/<msg_id>/read-status` - 更新消息读取状态
- `GET /api/messages/<msg_id>/check` - 检查消息

**任务路由**：
- `POST /api/tasks/create` - 创建任务
- `GET /api/tasks/<task_id>` - 获取任务
- `GET /api/tasks/list` - 获取所有任务
- `PUT /api/tasks/<task_id>` - 更新任务
- `DELETE /api/tasks/<task_id>` - 删除任务
- `PUT /api/tasks/<task_id>/status` - 更新任务状态
- `POST /api/tasks/<task_id>/messages` - 推送消息到任务

**层路由**：
- `POST /api/layers/create` - 创建层
- `GET /api/layers/list` - 获取所有层
- `GET /api/layers/<layer_index>` - 获取特定层
- `PUT /api/layers/<layer_index>/hooks` - 更新层的 hooks
- `POST /api/layers/<layer_index>/tasks` - 添加任务到层
- `DELETE /api/layers/<layer_index>/tasks/<task_id>` - 从层中删除任务
- `POST /api/layers/<layer_index>/tasks/replace` - 原子替换任务

**执行指针路由**：
- `GET /api/execution-pointer/get` - 获取执行指针
- `PUT /api/execution-pointer/set` - 设置执行指针
- `POST /api/execution-pointer/advance` - 推进执行指针

**任务栈路由**：
- `GET /api/task-stack/next` - 获取下一个要执行的任务
- `GET /api/task-stack` - 获取所有层
- `POST /api/task-stack/modify` - 修改任务栈（插入层并添加任务）

**批量操作路由**：
- `POST /api/batch-operations` - 执行批量操作

**健康检查**：
- `GET /health` - 健康检查

### Assistant 模块

#### 1. models.py - 数据模型

定义了所有 Assistant 相关的数据模型：

- **枚举类型**：
  - `AgentStatus`: Agent 状态（IDLE, EXECUTING, COMPLETED, FAILED）
  - `ExecutionStatus`: 执行状态（PENDING, IN_PROGRESS, COMPLETED, FAILED）

- **核心数据类**：
  - `Agent`: Agent 信息
  - `Assistant`: Assistant 实例（全局单例）
  - `AgentExecution`: Agent 执行记录

#### 2. storage.py - 数据存储

`AssistantStorage` 类提供线程安全的内存存储：

**全局 Assistant 操作**：
- `get_global_assistant()`: 获取或创建全局 assistant
- `update_global_assistant()`: 更新全局 assistant
- `add_agent_to_global_assistant()`: 添加 agent 到全局 assistant

**Agent 操作**：
- `create_agent()`: 创建 agent
- `get_agent()`: 获取 agent
- `get_all_agents()`: 获取所有 agents

**执行操作**：
- `create_execution()`: 创建执行记录
- `get_execution()`: 获取执行记录
- `get_executions_by_task()`: 获取任务的所有执行记录
- `update_execution()`: 更新执行记录

**工作空间操作**：
- `create_global_workspace()`: 创建全局工作空间
- `get_global_workspace()`: 获取全局工作空间
- `update_workspace()`: 更新工作空间

#### 3. service.py - 核心业务逻辑

`AssistantService` 类提供完整的执行流程：

- `query_agent_inputs()`: 查询 agent 所需输入
- `prepare_environment()`: 准备执行环境
- `package_data()`: 打包数据
- `execute_agent()`: 执行 agent
- `process_results()`: 处理结果
- `execute_agent_for_task()`: 完整的执行流程

#### 4. routes.py - API 路由

提供完整的 RESTful API：

**Assistant 管理**：
- `GET /api/assistant` - 获取全局 assistant
- `PUT /api/assistant` - 更新全局 assistant
- `POST /api/assistant/agents` - 添加 agent 到 assistant

**Agent 管理**：
- `POST /api/assistant/agents/create` - 创建 agent
- `GET /api/assistant/agents/list` - 列出所有 agents
- `GET /api/assistant/agents/<agent_id>` - 获取 agent
- `GET /api/assistant/agents/<agent_id>/inputs` - 获取 agent 输入要求

**Sub-Agent 查询**（自动发现的 agents）：
- `GET /api/assistant/sub-agents` - 获取所有已安装的 sub-agents
- `GET /api/assistant/sub-agents/<agent_id>` - 获取特定 sub-agent 信息

**Agent 执行**：
- `POST /api/assistant/execute` - 执行 agent
- `GET /api/assistant/executions/<execution_id>` - 获取执行记录
- `GET /api/assistant/executions/task/<task_id>` - 获取任务的所有执行记录

**工作空间**：
- `GET /api/assistant/workspace` - 获取全局工作空间
- `GET /api/assistant/workspace/summary` - 获取工作空间摘要
- `GET /api/assistant/workspace/files` - 列出工作空间文件
- `GET /api/assistant/workspace/files/<file_id>` - 获取文件元数据
- `GET /api/assistant/workspace/files/search` - 搜索文件
- `GET /api/assistant/workspace/memory` - 获取全局内存
- `POST /api/assistant/workspace/memory` - 写入全局内存
- `GET /api/assistant/workspace/logs` - 获取日志
- `GET /api/assistant/workspace/search` - 综合搜索

#### 5. agent_core/ - Agent 核心框架

**base_agent.py**：
- `BaseAgent`: Agent 抽象基类
- `AgentMetadata`: Agent 元数据

**agent_registry.py**：
- `AgentRegistry`: Agent 注册表
- `get_agent_registry()`: 获取全局注册表实例
- 自动发现和注册 agents

#### 6. workspace/ - 工作空间模块

**workspace.py**：
- `Workspace`: 工作空间核心类
- 文件、内存、日志的统一管理

**file_manager.py**：
- 文件管理功能

**log_manager.py**：
- 日志管理功能

**memory_manager.py**：
- 内存管理功能

---

## 数据结构

### Task Stack 数据结构

#### TaskStatus（枚举）
```python
PENDING = "PENDING"           # 等待处理
IN_PROGRESS = "IN_PROGRESS"   # 正在处理
COMPLETED = "COMPLETED"        # 已完成
FAILED = "FAILED"              # 失败
CANCELLED = "CANCELLED"        # 已取消
```

#### ReadingStatus（枚举）
```python
UNREAD = "UNREAD"              # 未读
READ = "READ"                  # 已读
```

#### MessageSenderType（枚举）
```python
WORKER = "worker"              # Worker（向后兼容）
DIRECTOR = "director"          # Director
SUBAGENT = "subagent"          # Subagent
USER = "user"                  # User
```

#### UserMessage
```python
@dataclass
class UserMessage:
    id: str                     # 消息 ID
    content: str                # 消息内容
    timestamp: datetime         # 时间戳
    user_id: str               # 用户 ID
    sender_type: MessageSenderType  # 发送者类型：worker, director, subagent, user
    director_read_status: ReadingStatus  # Director 读取状态（原 worker_read_status）
    user_read_status: ReadingStatus   # 用户读取状态
    task_id: Optional[str]     # 关联的任务 ID
```

#### Task
```python
@dataclass
class Task:
    id: str                     # 任务 ID
    description: Dict[str, Any] # 任务描述（包含 overall_description, input, requirements, additional_notes）
    status: TaskStatus          # 任务状态
    progress: Dict[str, Any]    # 进度信息（消息集合）
    results: Optional[Dict[str, Any]]  # 任务结果
    created_at: datetime        # 创建时间
    updated_at: datetime        # 更新时间
```

#### TaskStackEntry
```python
@dataclass
class TaskStackEntry:
    task_id: str                # 任务 ID
    created_at: datetime        # 创建时间
```

#### TaskLayer
```python
@dataclass
class TaskLayer:
    layer_index: int            # 层索引（0-based）
    tasks: List[TaskStackEntry] # 该层的任务列表
    pre_hook: Optional[Dict[str, Any]]  # 执行前的 hook
    post_hook: Optional[Dict[str, Any]]  # 执行后的 hook
    created_at: datetime        # 创建时间
```

#### ExecutionPointer
```python
@dataclass
class ExecutionPointer:
    current_layer_index: int    # 当前执行的层索引
    current_task_index: int    # 当前执行的任务索引
    is_executing_pre_hook: bool # 是否正在执行 pre-hook
    is_executing_post_hook: bool # 是否正在执行 post-hook
```

#### BatchOperationType（枚举）
```python
CREATE_TASKS = "create_tasks"                           # 批量创建任务
CREATE_LAYERS = "create_layers"                       # 批量创建层
ADD_TASKS_TO_LAYERS = "add_tasks_to_layers"           # 批量添加任务到层
REMOVE_TASKS_FROM_LAYERS = "remove_tasks_from_layers" # 批量从层中移除任务
REPLACE_TASKS_IN_LAYERS = "replace_tasks_in_layers"   # 批量替换任务
UPDATE_LAYER_HOOKS = "update_layer_hooks"             # 批量更新层 hooks
```

#### BatchOperation
```python
@dataclass
class BatchOperation:
    type: BatchOperationType    # 操作类型
    params: Dict[str, Any]      # 操作参数
```

### Assistant 数据结构

#### AgentStatus（枚举）
```python
IDLE = "IDLE"                  # 空闲
EXECUTING = "EXECUTING"         # 执行中
COMPLETED = "COMPLETED"        # 已完成
FAILED = "FAILED"              # 失败
```

#### ExecutionStatus（枚举）
```python
PENDING = "PENDING"            # 等待中
IN_PROGRESS = "IN_PROGRESS"    # 进行中
COMPLETED = "COMPLETED"        # 已完成
FAILED = "FAILED"              # 失败
```

#### Agent
```python
@dataclass
class Agent:
    id: str                     # Agent ID
    name: str                   # Agent 名称
    description: str            # Agent 描述
    input_schema: Dict[str, Any] # 输入模式
    capabilities: List[str]     # 能力列表
    created_at: datetime        # 创建时间
    updated_at: datetime        # 更新时间
```

#### Assistant
```python
@dataclass
class Assistant:
    id: str                     # Assistant ID（全局单例，固定为 "assistant_global"）
    name: str                   # Assistant 名称
    description: str            # Assistant 描述
    agent_ids: List[str]       # 管理的 Agent ID 列表
    created_at: datetime        # 创建时间
    updated_at: datetime        # 更新时间
```

#### AgentExecution
```python
@dataclass
class AgentExecution:
    id: str                     # 执行 ID
    assistant_id: str          # Assistant ID
    agent_id: str              # Agent ID
    task_id: str               # 任务 ID
    status: ExecutionStatus    # 执行状态
    inputs: Dict[str, Any]    # 输入数据
    results: Optional[Dict[str, Any]]  # 执行结果
    error: Optional[str]       # 错误信息
    started_at: Optional[datetime]     # 开始时间
    completed_at: Optional[datetime]   # 完成时间
    created_at: datetime        # 创建时间
```

---

## API 路由

### Task Stack API

#### 用户消息
- `POST /api/messages/create` - 创建用户消息（支持 sender_type 参数：worker, director, subagent, user）
- `GET /api/messages/<msg_id>` - 获取消息
- `GET /api/messages/list` - 获取所有消息（可选 user_id 过滤）
- `PUT /api/messages/<msg_id>/read-status` - 更新消息读取状态（使用 director_read_status 替代 worker_read_status）
- `GET /api/messages/<msg_id>/check` - 检查消息（数据结构、读取状态、是否新任务）

#### 任务管理
- `POST /api/tasks/create` - 创建任务
- `GET /api/tasks/<task_id>` - 获取任务
- `GET /api/tasks/list` - 获取所有任务
- `PUT /api/tasks/<task_id>` - 更新任务
- `DELETE /api/tasks/<task_id>` - 删除任务
- `PUT /api/tasks/<task_id>/status` - 更新任务状态
- `POST /api/tasks/<task_id>/messages` - 推送消息到任务

#### 层管理
- `POST /api/layers/create` - 创建层（可选 layer_index, pre_hook, post_hook）
- `GET /api/layers/list` - 获取所有层
- `GET /api/layers/<layer_index>` - 获取特定层
- `PUT /api/layers/<layer_index>/hooks` - 更新层的 hooks
- `POST /api/layers/<layer_index>/tasks` - 添加任务到层（可选 insert_index）
- `DELETE /api/layers/<layer_index>/tasks/<task_id>` - 从层中删除任务
- `POST /api/layers/<layer_index>/tasks/replace` - 原子替换任务

#### 执行指针
- `GET /api/execution-pointer/get` - 获取执行指针
- `PUT /api/execution-pointer/set` - 设置执行指针
- `POST /api/execution-pointer/advance` - 推进执行指针

#### 任务栈
- `GET /api/task-stack/next` - 获取下一个要执行的任务
- `GET /api/task-stack` - 获取所有层
- `POST /api/task-stack/modify` - 修改任务栈（在指定位置插入层并添加任务）

#### 批量操作
- `POST /api/batch-operations` - 执行批量操作

#### 健康检查
- `GET /health` - 健康检查

### Assistant API

#### Assistant 管理
- `GET /api/assistant` - 获取全局 assistant
- `PUT /api/assistant` - 更新全局 assistant
- `POST /api/assistant/agents` - 添加 agent 到 assistant

#### Agent 管理
- `POST /api/assistant/agents/create` - 创建 agent（存储）
- `GET /api/assistant/agents/list` - 列出所有 agents（存储）
- `GET /api/assistant/agents/<agent_id>` - 获取 agent（存储）
- `GET /api/assistant/agents/<agent_id>/inputs` - 获取 agent 输入要求

#### Sub-Agent 查询（自动发现的 agents）
- `GET /api/assistant/sub-agents` - 获取所有已安装的 sub-agents（聚合信息）
- `GET /api/assistant/sub-agents/<agent_id>` - 获取特定 sub-agent 信息

#### Agent 执行
- `POST /api/assistant/execute` - 执行 agent
- `GET /api/assistant/executions/<execution_id>` - 获取执行记录
- `GET /api/assistant/executions/task/<task_id>` - 获取任务的所有执行记录

#### 工作空间
- `GET /api/assistant/workspace` - 获取全局工作空间
- `GET /api/assistant/workspace/summary` - 获取工作空间摘要
- `GET /api/assistant/workspace/files` - 列出工作空间文件（可选过滤）
- `GET /api/assistant/workspace/files/<file_id>` - 获取文件元数据
- `GET /api/assistant/workspace/files/search` - 搜索文件
- `GET /api/assistant/workspace/memory` - 获取全局内存
- `POST /api/assistant/workspace/memory` - 写入全局内存
- `GET /api/assistant/workspace/logs` - 获取日志（可选过滤）
- `GET /api/assistant/workspace/search` - 综合搜索

---

## 快速开始

### 1. 安装依赖

```bash
cd dynamic-task-stack
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python run.py
```

服务将在 `http://localhost:5000` 启动。

### 3. 健康检查

```bash
curl http://localhost:5000/health
```

响应：
```json
{
  "status": "ok",
  "service": "Frameworks Backend"
}
```

---

## 使用示例

### Task Stack 基本使用

#### 创建任务栈

```bash
# 1. 创建层
POST /api/layers/create
{
  "pre_hook": {"type": "middleware", "action": "prepare"},
  "post_hook": {"type": "hook", "action": "cleanup"}
}

# 2. 创建任务
POST /api/tasks/create
{
  "description": {
    "overall_description": "处理用户输入",
    "input": {"data": "example"},
    "requirements": ["validate", "transform"]
  }
}

# 3. 添加任务到层
POST /api/layers/0/tasks
{
  "task_id": "task_1_abc123"
}
```

#### 执行任务栈

```bash
# 设置执行指针
PUT /api/execution-pointer/set
{
  "layer_index": 0,
  "task_index": 0
}

# 获取下一个任务
GET /api/task-stack/next

# 推进指针
POST /api/execution-pointer/advance
```

#### 修改任务栈（插入层）

```bash
POST /api/task-stack/modify
{
  "insert_layer_index": 3,
  "task_ids": ["task_1_xxx", "task_2_xxx"],
  "pre_hook": {"type": "middleware", "action": "prepare"},
  "post_hook": {"type": "hook", "action": "cleanup"}
}
```

#### 批量操作

```bash
POST /api/batch-operations
{
  "operations": [
    {
      "type": "create_tasks",
      "params": {
        "tasks": [
          {"description": {"overall_description": "任务1"}},
          {"description": {"overall_description": "任务2"}}
        ]
      }
    },
    {
      "type": "create_layers",
      "params": {
        "layers": [
          {"pre_hook": {"type": "middleware"}, "post_hook": {"type": "hook"}}
        ]
      }
    },
    {
      "type": "add_tasks_to_layers",
      "params": {
        "additions": [
          {"layer_index": 0, "task_id": "task_1_xxx"},
          {"layer_index": 0, "task_id": "task_2_xxx"}
        ]
      }
    }
  ]
}
```

### Assistant 基本使用

#### 查询 Sub-Agents

```bash
# 获取所有已安装的 sub-agents
GET /api/assistant/sub-agents

# 获取特定 sub-agent 信息
GET /api/assistant/sub-agents/<agent_id>
```

#### 执行 Agent

```bash
POST /api/assistant/execute
{
  "agent_id": "my_agent",
  "task_id": "task_1",
  "additional_inputs": {
    "input": "test data"
  }
}
```

#### 工作空间操作

```bash
# 获取工作空间
GET /api/assistant/workspace

# 列出文件
GET /api/assistant/workspace/files

# 搜索文件
GET /api/assistant/workspace/files/search?query=test

# 读取内存
GET /api/assistant/workspace/memory

# 写入内存
POST /api/assistant/workspace/memory
{
  "content": "memory content",
  "append": false
}
```

更多详细示例请参考 [USAGE_EXAMPLES.md](./USAGE_EXAMPLES.md)。

---

## 开发指南

### 创建新的 Agent

详细步骤请参考 [agents/README.md](../agents/README.md)。

### 代码规范

1. **命名规范**
   - Agent 文件夹名：使用下划线命名（snake_case）
   - Agent ID：与文件夹名保持一致
   - Agent 类名：使用驼峰命名（PascalCase）

2. **错误处理**
   - 使用 `validate_inputs()` 验证输入
   - 抛出有意义的异常信息
   - 在 `execute()` 中处理所有可能的错误

3. **文档**
   - 为 Agent 类添加详细的 docstring
   - 为输入输出字段添加描述
   - 说明 Agent 的能力和用途

### 测试

```bash
# 运行 API 测试
python test_api.py
```

---

## 注意事项

1. **任务修改限制**：只能修改未执行的任务，已执行的任务不能被修改
2. **执行顺序**：严格按照层级顺序执行（Layer 0 → Layer 1 → Layer 2 → ...）
3. **任务状态**：任务状态只能向前推进
4. **原子操作**：`replace_task_in_layer` 和 `modify_task_stack` 是原子操作，确保数据一致性
5. **批量操作**：所有批量操作在单个锁内执行，保证原子性
6. **线程安全**：所有操作都是线程安全的，支持并发访问
7. **Agent ID 唯一性**：Agent ID 必须唯一
8. **自动发现**：Agent 会在应用启动时自动被发现和注册

---

## 相关文档

- [agents/README.md](../agents/README.md) - Agents 详细开发指南
- [USAGE_EXAMPLES.md](./USAGE_EXAMPLES.md) - 使用示例
- [AGENTS_MIGRATION.md](../AGENTS_MIGRATION.md) - Agents 迁移说明

---

## 许可证

[添加许可证信息]

---

## 贡献

欢迎贡献代码和提出建议！
