# FrameWorkers

FrameWorkers 是一个强大的任务管理和 Agent 编排框架，提供分层级的任务执行系统和统一的 Agent 管理平台。

## 项目概述

FrameWorkers 是一个完整的任务编排和 Agent 管理系统，由以下核心组件组成：

- **Dynamic Task Stack**: 分层级任务管理和执行系统
- **Assistant System**: 统一的 Agent 管理和编排系统
- **Agent Framework**: Agent 自动发现和注册框架
- **Workspace**: 全局共享工作空间（文件、内存、日志）
- **Interface**: Web 前端界面

## 目录结构

```
FrameWorkers/
├── agents/                          # Agents 目录（项目根目录）
│   ├── __init__.py
│   ├── base_agent.py                # BaseAgent 导入辅助模块
│   ├── README.md                    # Agents 详细文档
│   └── example_agent/               # 示例 Agent
│       ├── __init__.py
│       └── agent.py
├── director_agent/                  # Director Agent（任务编排和推理）
│   ├── __init__.py
│   ├── director.py                  # Director 核心逻辑
│   ├── api_client.py                # Backend API 客户端
│   ├── reasoning.py                 # 推理模块
│   ├── config.py                    # 配置
│   ├── main.py                      # 主入口
│   ├── run.py                       # 运行脚本
│   ├── requirements.txt             # 依赖
│   ├── README.md                    # Director Agent 文档
│   └── FLOW_SUMMARY.md              # 流程总结
├── dynamic-task-stack/              # Backend 主目录
│   ├── src/
│   │   ├── app.py                   # Flask 应用入口
│   │   ├── task_stack/              # Task Stack 模块
│   │   │   ├── __init__.py
│   │   │   ├── models.py            # 数据模型
│   │   │   ├── routes.py            # API 路由
│   │   │   └── storage.py           # 数据存储
│   │   └── assistant/               # Assistant 模块
│   │       ├── __init__.py
│   │       ├── models.py            # Assistant 数据模型
│   │       ├── routes.py            # Assistant API 路由
│   │       ├── service.py           # Assistant 核心业务逻辑
│   │       ├── storage.py           # Assistant 数据存储
│   │       ├── retrieval.py         # 检索模块
│   │       └── workspace/           # 工作空间模块
│   │           ├── __init__.py
│   │           ├── workspace.py    # 工作空间核心
│   │           ├── file_manager.py  # 文件管理
│   │           ├── log_manager.py   # 日志管理
│   │           ├── memory_manager.py # 内存管理
│   │           └── models.py        # 工作空间数据模型
│   ├── requirements.txt
│   ├── run.py
│   ├── test_api.py
│   ├── README.md                    # Backend 详细文档
│   └── USAGE_EXAMPLES.md            # 使用示例
├── interface/                       # 前端界面
│   ├── src/
│   │   ├── App.vue                  # 主应用组件
│   │   ├── components/              # Vue 组件
│   │   │   ├── ChatWindow.vue       # 聊天窗口
│   │   │   ├── SystemStatus.vue     # 系统状态
│   │   │   └── TaskStackMonitor.vue # 任务栈监控
│   │   ├── services/                # 服务
│   │   │   ├── api.js               # API 客户端
│   │   │   └── polling.js           # 轮询服务
│   │   └── main.js                  # 入口文件
│   ├── package.json
│   ├── vite.config.js
│   └── README.md                    # 前端文档
├── install_requirements.py           # 统一依赖管理脚本
├── requirements.txt                 # 统一依赖（自动生成）
├── tests/                           # 根目录统一测试入口
│   ├── agents/                      # Agents 核心测试
│   └── assistant/                   # Assistant 单元测试
├── Runtime/                         # 运行时目录（工作空间文件存储）
├── README.md                        # 本文档
└── AGENTS_MIGRATION.md              # Agents 迁移说明
```

## 核心组件

### 1. Dynamic Task Stack

分层级的任务管理和执行系统，支持：

- **分层级任务管理**：多层级任务组织，每层可包含多个任务
- **Hook 机制**：每层支持执行前后的 Pre-hook 和 Post-hook
- **执行指针**：跟踪当前执行位置，支持动态修改未执行的任务
- **原子操作**：任务替换、插入层并添加任务等操作的原子性保证
- **批量操作**：统一的批量操作接口，支持一次性执行多个操作（创建任务、创建层、添加任务到层等）

详细文档：[dynamic-task-stack/README.md](./dynamic-task-stack/README.md)

### 2. Assistant System

统一的 Agent 管理和编排系统，提供：

- **全局单例 Assistant**：只有一个全局 assistant 管理所有 sub-agents
- **自动发现**：自动扫描和注册根目录下的所有 agents
- **共享工作空间**：所有 agents 共享一个全局工作空间（文件系统）
- **信息检索**：Assistant 从工作空间中检索信息，然后分发给各个 agent
- **完整执行流程**：6 步执行流程（查询输入 → 准备环境 → 检索信息 → 打包数据 → 执行 → 处理结果）

详细文档：[dynamic-task-stack/README.md](./dynamic-task-stack/README.md)

### 3. Agent Framework

Agent 自动发现和注册框架：

- **BaseAgent**：Agent 抽象基类，定义标准接口
- **Agent Registry**：自动发现和注册机制
- **Metadata**：Agent 元数据管理（名称、描述、能力、输入输出模式）

详细文档：[agents/README.md](./agents/README.md)

### 4. Director Agent

任务编排和推理系统：

- **任务编排**：根据用户消息和任务栈状态进行推理和规划
- **任务委托**：将任务委托给 Assistant Agent 执行
- **执行总结**：接收执行结果并进行反思
- **任务栈更新**：根据执行结果更新任务栈

详细文档：[director_agent/README.md](./director_agent/README.md)

### 5. Workspace

全局共享工作空间：

- **文件管理**：文件创建、查询、搜索、标签管理
- **内存管理**：全局内存读写
- **日志管理**：操作日志记录和查询
- **综合搜索**：跨文件、内存、日志的搜索

详细文档：[dynamic-task-stack/src/assistant/workspace/README.md](./dynamic-task-stack/src/assistant/workspace/README.md)

### 6. Interface

Web 前端界面：

- **聊天窗口**：用户消息交互
- **系统状态**：系统运行状态监控
- **任务栈监控**：任务栈状态可视化

详细文档：[interface/README.md](./interface/README.md)

## 快速开始

### 1. 安装依赖

```bash
# 创建 conda 环境 (frameworkers, python 3.11) 并安装所有依赖
python install_requirements.py
conda activate frameworkers

# 前端依赖
cd interface && npm install
```

### 2. 启动服务

```bash
# 启动 Backend
cd dynamic-task-stack
python run.py

# 启动 Director Agent（新终端）
cd director_agent
python run.py

# 启动 Frontend（新终端）
cd interface
npm run dev
```

### 3. 访问服务

- Backend API: `http://localhost:5002`
- Frontend: `http://localhost:3000`

### 4. 运行测试

```bash
# agents 核心测试
python -m pytest tests/agents/test_agent_core.py -v

# assistant 单元测试
python -m pytest tests/assistant/test_assistant_*.py -v
```

## 系统架构

### 整体流程

```
用户消息
  ↓
Director Agent（推理和规划）
  ↓
Task Stack（任务编排）
  ↓
Assistant System（Agent 执行）
  ↓
Workspace（结果存储）
  ↓
Director Agent（反思和更新）
```

### 组件交互

1. **Director Agent** 监听用户消息和任务栈状态
2. **Director Agent** 进行推理和规划，创建/更新任务栈
3. **Task Stack** 管理任务执行顺序
4. **Assistant System** 执行具体的 Agent
5. **Workspace** 存储执行结果和中间数据
6. **Director Agent** 接收执行结果，进行反思和任务栈更新

## 核心概念

### Task Stack

- **Layer（层）**：任务栈的基本组织单位，按顺序执行
- **Task（任务）**：具体的执行单元，包含描述、状态、进度、结果
- **Execution Pointer（执行指针）**：跟踪当前执行位置
- **Hook**：层执行前后的钩子函数

### Assistant System

- **Assistant（助手）**：全局单例，管理所有 sub-agents
- **Agent（代理）**：具体的功能实现单元
- **Workspace（工作空间）**：全局共享的文件、内存、日志存储
- **Execution（执行）**：Agent 执行记录

### Agent Framework

- **BaseAgent**：所有 Agent 的基类
- **AgentMetadata**：Agent 元数据（名称、描述、能力、输入输出模式）
- **Agent Registry**：自动发现和注册机制

## 开发指南

### 创建新的 Agent

1. 在 `agents/` 目录下创建新的文件夹
2. 实现 `agent.py`，继承 `BaseAgent`
3. 实现 `get_metadata()` 和 `execute()` 方法
4. Agent 会自动被发现和注册

详细步骤：[agents/README.md](./agents/README.md)

### API 使用

#### Task Stack API

```bash
# 创建任务
POST /api/tasks/create
{
  "description": {
    "overall_description": "任务描述",
    "input": {},
    "requirements": []
  }
}

# 创建层
POST /api/layers/create
{
  "pre_hook": {"type": "middleware"},
  "post_hook": {"type": "hook"}
}

# 添加任务到层
POST /api/layers/0/tasks
{
  "task_id": "task_1_xxx"
}

# 插入层并添加任务（原子操作）
POST /api/task-stack/insert-layer
{
  "insert_layer_index": 3,
  "task_ids": ["task_1_xxx", "task_2_xxx"],
  "pre_hook": {"type": "middleware"},
  "post_hook": {"type": "hook"}
}

# 批量操作（修改任务栈）
POST /api/task-stack/modify
{
  "operations": [
    {
      "type": "create_tasks",
      "params": {
        "tasks": [
          {"description": {"overall_description": "任务1"}}
        ]
      }
    },
    {
      "type": "create_layers",
      "params": {
        "layers": [
          {"layer_index": 0, "pre_hook": {}, "post_hook": {}}
        ]
      }
    }
  ]
}
```

#### Assistant API

```bash
# 查询所有 sub-agents
GET /api/assistant/sub-agents

# 执行 agent
POST /api/assistant/execute
{
  "agent_id": "my_agent",
  "task_id": "task_1",
  "additional_inputs": {}
}
```

详细 API 文档：[dynamic-task-stack/README.md](./dynamic-task-stack/README.md)

## 相关文档

- [dynamic-task-stack/README.md](./dynamic-task-stack/README.md) - Backend 详细文档
- [agents/README.md](./agents/README.md) - Agents 开发指南
- [director_agent/README.md](./director_agent/README.md) - Director Agent 文档
- [interface/README.md](./interface/README.md) - 前端文档
- [AGENTS_MIGRATION.md](./AGENTS_MIGRATION.md) - Agents 迁移说明

## 许可证

[添加许可证信息]

## 贡献

欢迎贡献代码和提出建议！
