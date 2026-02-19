# Frameworks Backend

Frameworks Backend 是一个强大的任务管理和 Agent 编排系统，提供分层级的任务执行框架和统一的 Agent 管理平台。

## 目录

- [系统概述](#系统概述)
- [架构设计](#架构设计)
- [核心功能](#核心功能)
- [快速开始](#快速开始)
- [Task Stack 系统](#task-stack-系统)
- [Assistant 系统](#assistant-系统)
- [API 文档](#api-文档)
- [使用示例](#使用示例)
- [开发指南](#开发指南)

---

## 系统概述

Frameworks Backend 由两个核心系统组成：

### 1. Task Stack（任务栈系统）
- **分层级任务管理**：支持多层级任务组织，每层可包含多个任务
- **Hook 机制**：每层支持执行前后的 Pre-hook 和 Post-hook
- **执行指针**：跟踪当前执行位置，支持动态修改未执行的任务
- **原子操作**：确保任务替换等操作的原子性

### 2. Assistant（助手系统）
- **Agent 编排**：统一管理和执行多个 sub-agent
- **自动发现**：自动扫描和注册根目录下的所有 agents
- **工作空间**：为每个 assistant 提供独立的工作空间（文件、内存、日志、资产）
- **执行流程**：完整的 6 步执行流程（查询输入 → 准备环境 → 打包数据 → 执行 → 处理结果）

---

## 架构设计

### 目录结构

```
FrameWorkers/
├── agents/                          # Agents 目录（项目根目录）
│   ├── __init__.py
│   ├── base_agent.py                # BaseAgent 导入辅助模块
│   ├── README.md                    # Agents 详细文档
│   └── example_agent/              # 示例 Agent
│       ├── __init__.py
│       └── agent.py
├── dynamic-task-stack/              # Backend 主目录
│   ├── src/
│   │   ├── app.py                   # Flask 应用入口
│   │   ├── task_stack/              # Task Stack 模块
│   │   │   ├── __init__.py
│   │   │   ├── models.py            # 数据模型
│   │   │   ├── routes.py            # API 路由
│   │   │   └── storage.py           # 数据存储
│   │   └── assistant/              # Assistant 模块
│   │       ├── __init__.py
│   │       ├── models.py            # Assistant 数据模型
│   │       ├── routes.py             # Assistant API 路由
│   │       ├── service.py            # Assistant 核心业务逻辑
│   │       ├── storage.py            # Assistant 数据存储
│   │       └── agents/               # Agent 基础设施（向后兼容）
│   │           ├── base_agent.py    # BaseAgent 抽象基类
│   │           └── agent_registry.py # Agent 发现和注册
│   ├── requirements.txt
│   ├── run.py
│   └── README.md                    # 本文档
└── interface/                       # 前端界面
```

### 设计原则

1. **代码隔离**：Task Stack 和 Assistant 系统完全分离，互不干扰
2. **统一管理**：Assistant 统一管理所有 sub-agents
3. **自动发现**：Agents 自动注册，无需手动配置
4. **易于扩展**：添加新 Agent 只需创建文件夹和实现类
5. **向后兼容**：支持旧的 agents 目录结构

---

## 核心功能

### Task Stack 功能

- ✅ 分层级任务管理（Layer-based task management）
- ✅ Pre-hook 和 Post-hook 支持
- ✅ 执行指针跟踪
- ✅ 动态修改未执行任务（原子操作）
- ✅ 任务状态管理（PENDING → IN_PROGRESS → COMPLETED/FAILED）
- ✅ 线程安全的数据存储

### Assistant 功能

- ✅ Agent 自动发现和注册
- ✅ Agent 信息聚合和查询
- ✅ 完整的执行流程编排
- ✅ 工作空间管理（概念模型）
- ✅ 执行历史记录
- ✅ 输入输出模式验证

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

## Task Stack 系统

### 核心概念

#### Layer（层）
- 任务栈的基本组织单位
- 每层包含多个任务
- 支持 Pre-hook 和 Post-hook
- 按顺序执行（Layer 0 → Layer 1 → Layer 2 → ...）

#### Task（任务）
- 具体的执行单元
- 包含描述、状态、进度、结果等信息
- 状态流转：PENDING → IN_PROGRESS → COMPLETED/FAILED

#### Execution Pointer（执行指针）
- 跟踪当前执行位置
- 包含：layer_index, task_index, is_executing_pre_hook, is_executing_post_hook
- 用于确定下一个要执行的任务

### 基本使用流程

#### 步骤 1: 创建任务栈结构

```bash
# 创建第一层
POST /api/layers/create
{
  "pre_hook": {
    "type": "middleware",
    "action": "prepare_environment",
    "config": {}
  },
  "post_hook": {
    "type": "hook",
    "action": "cleanup",
    "config": {}
  }
}

# 创建任务
POST /api/tasks/create
{
  "description": {
    "overall_description": "处理用户输入数据",
    "input": {"data": "example"},
    "requirements": ["validate", "transform"],
    "additional_notes": "需要特殊处理"
  }
}

# 将任务添加到层
POST /api/layers/0/tasks
{
  "task_id": "task_1_abc123"
}
```

#### 步骤 2: 执行任务栈

```bash
# 设置执行指针
PUT /api/execution-pointer/set
{
  "layer_index": 0,
  "task_index": 0,
  "is_executing_pre_hook": false,
  "is_executing_post_hook": false
}

# 获取下一个任务
GET /api/task-stack/next

# 执行任务后，推进指针
POST /api/execution-pointer/advance
```

#### 步骤 3: 动态修改任务栈

**重要：只能修改未执行的任务！**

```bash
# 原子替换任务
POST /api/layers/1/tasks/replace
{
  "old_task_id": "task_2_def456",
  "new_task_id": "task_4_jkl012"
}

# 删除未执行的任务
DELETE /api/layers/1/tasks/task_3_ghi789
```

### 完整示例

参考 [USAGE_EXAMPLES.md](./USAGE_EXAMPLES.md) 获取详细的使用示例。

---

## Assistant 系统

### 核心概念

#### Assistant（助手）
- 管理多个 sub-agent 的容器
- 每个 assistant 拥有独立的工作空间
- 负责编排 agent 的执行流程

#### Agent（代理）
- 具体的功能实现单元
- 必须继承 `BaseAgent` 并实现 `get_metadata()` 和 `execute()` 方法
- 放置在项目根目录的 `agents/` 文件夹中

#### Workspace（工作空间）
- 每个 assistant 的独立工作环境
- 包含：共享文件、共享内存、日志、资产等
- 目前是概念模型，具体实现可后续完善

### Agent 执行流程

```
1. 调用申请
   └─> POST /api/assistant/execute
       {
         "assistant_id": "...",
         "agent_id": "...",
         "task_id": "...",
         "additional_inputs": {...}
       }

2. 输入查询
   └─> query_agent_inputs() - 查询 agent 所需输入参数

3. 环境准备
   └─> prepare_environment() - 准备工作空间环境

4. 数据打包
   └─> package_data() - 打包相关资源供 agent 使用

5. 结果获取
   └─> execute_agent() - 执行 agent 并获取结果

6. 结果处理
   └─> process_results() - 处理结果并存入工作空间
```

### 创建 Agent

详细步骤请参考 [agents/README.md](../agents/README.md)。

快速示例：

```bash
# 1. 创建 agent 目录
mkdir agents/my_agent

# 2. 创建 agent.py
cat > agents/my_agent/agent.py << 'EOF'
from typing import Dict, Any
from datetime import datetime
from ..base_agent import BaseAgent, AgentMetadata

class MyAgent(BaseAgent):
    def get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            id="my_agent",
            name="My Agent",
            description="My custom agent",
            capabilities=["custom_processing"],
            input_schema={
                "input": {"type": "string", "required": True}
            },
            output_schema={
                "result": {"type": "string"}
            }
        )
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        self.validate_inputs(inputs)
        return {"result": f"Processed: {inputs['input']}"}
EOF

# 3. 创建 __init__.py
cat > agents/my_agent/__init__.py << 'EOF'
from .agent import MyAgent
__all__ = ['MyAgent']
EOF

# 4. Agent 会自动被发现和注册！
```

### 查询 Agents

```bash
# 获取所有已安装的 agents（聚合信息）
GET /api/assistant/sub-agents

# 获取特定 agent 信息
GET /api/assistant/sub-agents/{agent_id}
```

### 执行 Agent

```bash
POST /api/assistant/execute
{
  "assistant_id": "assistant_1",
  "agent_id": "my_agent",
  "task_id": "task_1",
  "additional_inputs": {
    "input": "test data"
  }
}
```

---

## API 文档

### Task Stack API

#### 健康检查
- `GET /health` - 健康检查

#### 用户消息
- `POST /api/messages/create` - 创建用户消息
- `GET /api/messages/list` - 获取所有消息
- `GET /api/messages/<msg_id>` - 获取特定消息
- `PUT /api/messages/<msg_id>/read-status` - 更新消息读取状态

#### 任务管理
- `POST /api/tasks/create` - 创建任务
- `GET /api/tasks/list` - 获取所有任务
- `GET /api/tasks/<task_id>` - 获取特定任务
- `PUT /api/tasks/<task_id>` - 更新任务
- `DELETE /api/tasks/<task_id>` - 删除任务
- `PUT /api/tasks/<task_id>/status` - 更新任务状态

#### 层管理
- `POST /api/layers/create` - 创建层
- `GET /api/layers/list` - 获取所有层
- `GET /api/layers/<layer_index>` - 获取特定层
- `PUT /api/layers/<layer_index>/hooks` - 更新层的 Hook
- `POST /api/layers/<layer_index>/tasks` - 添加任务到层
- `DELETE /api/layers/<layer_index>/tasks/<task_id>` - 从层中删除任务
- `POST /api/layers/<layer_index>/tasks/replace` - 原子替换任务

#### 执行指针
- `GET /api/execution-pointer/get` - 获取执行指针
- `PUT /api/execution-pointer/set` - 设置执行指针
- `POST /api/execution-pointer/advance` - 推进执行指针

#### 任务栈
- `GET /api/task-stack/next` - 获取下一个要执行的任务
- `GET /api/task-stack` - 获取所有层

### Assistant API

#### Assistant 管理
- `POST /api/assistant/create` - 创建 assistant
- `GET /api/assistant/<assistant_id>` - 获取 assistant
- `GET /api/assistant/list` - 列出所有 assistant
- `POST /api/assistant/<assistant_id>/agents` - 添加 agent 到 assistant

#### Agent 管理
- `POST /api/assistant/agents/create` - 创建 agent（存储）
- `GET /api/assistant/agents/list` - 列出所有 agent（存储）
- `GET /api/assistant/agents/<agent_id>` - 获取 agent（存储）
- `GET /api/assistant/agents/<agent_id>/inputs` - 获取 agent 输入要求

#### Sub-Agent 查询（自动发现的 agents）
- `GET /api/assistant/sub-agents` - 获取所有已安装的 sub-agent（聚合信息）
- `GET /api/assistant/sub-agents/<agent_id>` - 获取特定 sub-agent 信息

#### Agent 执行
- `POST /api/assistant/execute` - 执行 agent
- `GET /api/assistant/executions/<execution_id>` - 获取执行记录
- `GET /api/assistant/executions/task/<task_id>` - 获取任务的所有执行记录

#### 工作空间
- `GET /api/assistant/<assistant_id>/workspace` - 获取 assistant 的工作空间

详细的 API 文档请参考代码中的注释和 [USAGE_EXAMPLES.md](./USAGE_EXAMPLES.md)。

---

## 使用示例

### Task Stack 完整工作流

```python
# 1. 创建任务栈
layer0 = create_layer(pre_hook={...}, post_hook={...})
task1 = create_task(description={...})
add_task_to_layer(0, task1.id)

layer1 = create_layer(pre_hook={...}, post_hook={...})
task2 = create_task(description={...})
task3 = create_task(description={...})
add_task_to_layer(1, task2.id)
add_task_to_layer(1, task3.id)

# 2. 开始执行
set_execution_pointer(0, 0)

# 3. 执行循环
while True:
    next_task_info = get_next_task()
    if not next_task_info:
        break
    
    # 执行任务
    task = get_task(next_task_info['task_id'])
    result = execute_task(task)
    update_task(task.id, status="COMPLETED", results=result)
    
    # 推进指针
    advance_execution_pointer()
```

### Assistant 执行 Agent

```python
# 1. 创建 assistant
assistant = create_assistant(
    name="Video Production Assistant",
    description="Manages video production sub-agents",
    agent_ids=["storyboard_agent", "transcript_agent"]
)

# 2. 执行 agent
result = execute_agent_for_task(
    assistant_id=assistant.id,
    agent_id="storyboard_agent",
    task_id="task_1",
    additional_inputs={"script": "..."}
)
```

更多示例请参考 [USAGE_EXAMPLES.md](./USAGE_EXAMPLES.md)。

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

## 状态枚举

### TaskStatus
- `PENDING`: 任务等待处理
- `IN_PROGRESS`: 任务正在处理
- `COMPLETED`: 任务已完成
- `FAILED`: 任务失败
- `CANCELLED`: 任务已取消

### ReadingStatus
- `UNREAD`: 消息未读
- `READ`: 消息已读

### ExecutionStatus
- `PENDING`: 执行等待中
- `IN_PROGRESS`: 执行进行中
- `COMPLETED`: 执行完成
- `FAILED`: 执行失败

---

## 注意事项

1. **任务修改限制**：只能修改未执行的任务，已执行的任务不能被修改
2. **执行顺序**：严格按照层级顺序执行（Layer 0 → Layer 1 → Layer 2 → ...）
3. **任务状态**：任务状态只能向前推进
4. **原子操作**：`replace_task_in_layer` 是原子操作，确保数据一致性
5. **线程安全**：所有操作都是线程安全的，支持并发访问
6. **Agent ID 唯一性**：Agent ID 必须唯一
7. **自动发现**：Agent 会在应用启动时自动被发现和注册

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
