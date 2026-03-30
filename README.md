# FrameWorkers

FrameWorkers 是一个强大的任务管理和 Agent 编排框架，提供分层级的任务执行系统和统一的 Agent 管理平台。

## 项目概述

FrameWorkers 是一个完整的任务编排和 Agent 管理系统，由以下核心组件组成：

- **Dynamic Task Stack**: 分层级任务管理与 Flask `/api/` 编排
- **Assistant System**: 基于 `SubAgentDescriptor` 的流水线执行与 Workspace 落盘
- **Agent Framework**（`agents/`）: 注册表、评估器与媒体 materializer
- **Director Agent**: 轮询后端、推理与任务栈更新
- **Director (no stack)**（`director_nostack/`）: 仅用聊天消息 + Assistant，**不**使用 Task Stack；**`merge_session_goal`** 会合并「新一行 + 更早用户原文（messages list）+ memory + execution」再选下一 sub-agent（见该目录 `README.md`）
- **Inference**: LLM 客户端与 image/video/audio 生成服务（独立库）
- **Workspace**: 全局共享工作空间（文件、**global_memory**、日志、资产索引）
- **Interface**: Web 前端（Vue 3 + Vite）

## 目录结构

与架构约定以仓库根目录 [`.cursorrules`](./.cursorrules) 为准；以下为与代码树同步的摘要。

```
FrameWorkers/
├── .cursorrules                     # AI / 贡献者架构单源说明（与实现同步维护）
├── agents/                          # Agent 框架与流水线实现（根目录，运行时注册）
│   ├── __init__.py                  # AGENT_REGISTRY、LLMClient（来自 inference）等导出
│   ├── base_agent.py                # 流水线 BaseAgent（LLMBaseAgent）
│   ├── base_evaluator.py
│   ├── descriptor.py                # SubAgentDescriptor
│   ├── common_schema.py
│   ├── agent_registry.py
│   ├── README.md
│   ├── story/ … example_agent/     # 各子目录：agent / schema / evaluator / descriptor；媒体类含 materializer
│   └── …                            # 完整列表见 agents/README.md
├── director_agent/
│   ├── director.py
│   ├── api_client.py                # 仅封装 Director 主循环与仓库内测试实际调用的 HTTP 端点
│   ├── reasoning.py
│   ├── config.py
│   ├── main.py
│   ├── run.py
│   ├── requirements.txt
│   └── README.md
├── director_nostack/                # 可选：无任务栈编排（聊天 → Assistant）
│   ├── director.py                  # DirectorNoStack + run_nostack_pipeline
│   ├── router.py                    # LlmSubAgentPlanner（调用 + 解析）
│   ├── prompts.py                   # system 文案与 user 拼装
│   ├── api_client.py
│   ├── config.py
│   ├── main.py
│   ├── run.py
│   └── README.md
├── dynamic-task-stack/
│   ├── src/
│   │   ├── app.py
│   │   ├── common_http.py           # Task Stack + Assistant 共用：JSON body、bad_request、query 等
│   │   ├── task_stack/
│   │   │   ├── models.py
│   │   │   ├── routes.py            # 使用 common_http + api_serialize
│   │   │   ├── api_serialize.py     # serialize_for_api（dataclass/enum JSON）
│   │   │   ├── state_store.py
│   │   │   ├── execution_flow.py
│   │   │   ├── batch_mutator.py
│   │   │   └── storage.py           # 门面 + 全局 storage 单例
│   │   └── assistant/
│   │       ├── models.py
│   │       ├── routes.py            # 与 task_stack 共用 common_http
│   │       ├── response_serializers.py
│   │       ├── service.py           # AssistantService（descriptor 流水线执行）
│   │       ├── state_store.py
│   │       └── workspace/
│   │           ├── workspace.py
│   │           ├── file_manager.py
│   │           ├── memory_manager.py
│   │           ├── log_manager.py
│   │           ├── asset_manager.py
│   │           └── models.py
│   ├── run.py
│   ├── requirements.txt
│   ├── README.md
│   └── USAGE_EXAMPLES.md
├── inference/
│   ├── clients/                     # base + implementations（LLMClient 等）
│   ├── input_processing/            # ImageUtils、MessageUtils / MultimodalUtils 别名
│   ├── generation/                  # image / video / audio 注册表与服务；fal_helpers（fal 订阅与下载）
│   ├── config/
│   ├── README.md
│   └── MODELS.md
├── interface/
│   └── src/ …                       # Vue 3 + Vite，api.js / polling.js
├── tests/                           # agents、assistant、director 等（含 HTTP e2e）
├── Runtime/                         # Workspace 运行时文件
├── install_requirements.py
├── requirements.txt
├── README.md
└── AGENTS_MIGRATION.md
```

## 核心组件

### 1. Dynamic Task Stack

分层级的任务管理和执行系统，支持：

- **分层级任务管理**：多层级任务组织，每层可包含多个任务
- **Hook 机制**：每层支持执行前后的 Pre-hook 和 Post-hook
- **执行指针**：跟踪当前执行位置，支持动态修改未执行的任务（`execution_flow` + `storage`）
- **原子写路径**：`batch_mutator` 承载批量/多步修改；`state_store` 为纯状态容器
- **批量操作**：`POST /api/task-stack/modify` 等统一原子接口
- **HTTP 层**：`routes.py` 复用 `src/common_http.py` 与 `api_serialize.serialize_for_api`，减少与 Assistant 蓝图重复的校验代码

详细文档：[dynamic-task-stack/README.md](./dynamic-task-stack/README.md)

### 2. Assistant System

统一的 Agent 管理与执行入口，提供：

- **全局单例 Assistant**：一个全局 assistant 管理所有 sub-agents（`state_store`）
- **自动发现**：通过 `agents.AgentRegistry` / `AGENT_REGISTRY` 与 `SubAgentDescriptor` 驱动 **descriptor 流水线**（无单独 sync adapter 路径）
- **共享工作空间**：文件、**global_memory**、日志、执行资产索引（`asset_manager`）
- **执行流程**：查询输入 → 准备环境 → `build_execution_inputs`（global_memory + LLM `selected_roles` → `input_bundle_v2` / `resolved_inputs`）→ 执行 pipeline agent → 处理结果并落盘

详细文档：[dynamic-task-stack/README.md](./dynamic-task-stack/README.md)（含 `src/assistant/README.md`）

### 3. Agent Framework

流水线 Agent 框架（与 Assistant 对齐）：

- **LLMBaseAgent**（`base_agent.BaseAgent`）：异步 pipeline 执行体
- **SubAgentDescriptor**：`build_input` / `build_equipped_agent` / `run` 契约；在 `agents/__init__.py` 的 `AGENT_REGISTRY` 中登记
- **AgentRegistry**：文件系统扫描 + 注册表聚合
- **BaseEvaluator**：结构 / 创意 / 资产 三层评估与重试预算
- **LLMClient**：类型由 `inference.clients` 提供，在 `agents/__init__.py` 中再导出

详细文档：[agents/README.md](./agents/README.md)

### 4. Director Agent

任务编排和推理系统：

- **任务编排**：根据用户消息和任务栈状态进行推理和规划
- **任务委托**：将任务委托给 Assistant Agent 执行
- **执行总结**：接收执行结果并进行反思（部分分支仍为占位实现，见 `director.py` 注释）
- **任务栈更新**：根据执行结果更新任务栈
- **HTTP 客户端**：`api_client.BackendAPIClient` **仅包装** Director 主循环与仓库内单测实际调用的后端路由；其余 REST 仍可由脚本或临时扩展 client 直调 Flask

详细文档：[director_agent/README.md](./director_agent/README.md)

### 5. Inference Module

统一提供 LLM 运行时与多模态生成能力：

- **公共抽象层**：`inference/clients/base/base_client.py`（`BaseLLMClient`、`Message`、`ModelConfig`）
- **具体客户端层**：`inference/clients/implementations/`（`default_client`、`gpt5_client`、`custom_model`）
- **输入处理**：`inference/input_processing/`（图像与消息工具；兼容 `MultimodalUtils` 等别名）
- **生成能力层**：`inference/generation/` — image / video / **audio** 注册表与 `ImageService` / `VideoService` / `AudioService` 等；fal.ai 后端共享 `generation/fal_helpers.py`（`fal_client.subscribe` 与环境键、HTTP 下载）

详细文档：[inference/README.md](./inference/README.md)

### 6. Workspace

全局共享工作空间：

- **文件管理**：文件创建、查询、搜索、标签管理
- **结构化记忆**：**global_memory**（见 Assistant / workspace 文档）
- **日志管理**：操作日志记录和查询（含聚合 insights 等 API）
- **资产索引**：`asset_manager` 与执行结果 JSON 快照等持久化
- **综合搜索**：跨文件、记忆、日志（HTTP 层 `Workspace.search_all` 等）

详细文档：[dynamic-task-stack/src/assistant/workspace/README.md](./dynamic-task-stack/src/assistant/workspace/README.md)

### 7. Interface

Web 前端界面：

- **聊天窗口**：用户消息交互
- **系统状态**：系统运行状态监控
- **任务栈监控**：任务栈状态可视化

详细文档：[interface/README.md](./interface/README.md)

## 快速开始

### 1. 安装依赖

```bash
# 推荐：先激活环境再安装（用当前解释器 pip，不依赖 PATH 里必须有 conda）
conda activate frameworkers
python install_requirements.py

# 若尚未创建环境：可在 conda base 下直接执行脚本（需 conda 在 PATH），脚本会创建 frameworkers 后再安装
# python install_requirements.py

# 前端依赖
cd interface && npm install
```

`install_requirements.py` 支持重复执行：若 `frameworkers` 环境已存在会跳过创建，仅更新依赖。已激活 `frameworkers` 时直接用 `python -m pip install`；否则使用 `CONDA_EXE` 或 PATH 中的 `conda` 执行 `conda run`。对不支持 `conda run --no-banner` 的旧版 conda 会自动回退兼容参数。

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
# 一键跑核心回归（assistant + director + task_stack app factory + agents）
bash tests/run_core_tests.sh

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
- **Descriptor 流水线**：每个 sub-agent 对应 `SubAgentDescriptor` + pipeline `BaseAgent`
- **Workspace（工作空间）**：文件、**global_memory**、日志与执行资产
- **Execution（执行）**：`AgentExecution` 记录（状态、结果、错误）

### Agent Framework

- **SubAgentDescriptor**：声明 agent 名称、evaluator、materializer、`build_input` 等
- **LLMBaseAgent**：流水线执行类；由 descriptor `build_equipped_agent` 装配
- **AgentRegistry / AGENT_REGISTRY**：发现与静态登记

## 开发指南

### 创建新的 Agent

1. 在 `agents/` 下新增子目录（如 `my_agent/`）
2. 按流水线约定实现 `agent.py`、`schema.py`、`evaluator.py`、`descriptor.py`（媒体类可加 `materializer.py`）
3. 在 `descriptor.py` 中导出 `DESCRIPTOR`，并在 `agents/__init__.py` 的 `AGENT_REGISTRY` 中注册
4. 运行测试与 Assistant 执行路径验证

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
  "execute_fields": { "text": "…" }
}
# 200 响应体含 task_id、execution_id、status、results、error、workspace_id
```

详细 API 文档：[dynamic-task-stack/README.md](./dynamic-task-stack/README.md)

## 相关文档

- [.cursorrules](./.cursorrules) - 五包架构、目录与维护约定（与代码同步）
- [dynamic-task-stack/README.md](./dynamic-task-stack/README.md) - Backend 详细文档
- [agents/README.md](./agents/README.md) - Agents 开发指南
- [director_agent/README.md](./director_agent/README.md) - Director Agent 文档
- [inference/README.md](./inference/README.md) - 推理与多模态能力文档
- [interface/README.md](./interface/README.md) - 前端文档
- [AGENTS_MIGRATION.md](./AGENTS_MIGRATION.md) - Agents 迁移说明

## 许可证

[添加许可证信息]

## 贡献

欢迎贡献代码和提出建议！
