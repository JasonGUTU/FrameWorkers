# Agents 开发指南

本文档详细说明如何创建、开发和部署 Agent 到 Frameworks Backend。

**目录结构说明：**
- `agents/`（根目录）：Agent 核心框架和所有 Agent 实现
  - 核心框架文件：`base_agent.py`, `base_evaluator.py`, `sync_adapter.py`, `descriptor.py`, `llm_client.py`, `common_schema.py`, `agent_registry.py`
  - Pipeline Agent 子包：`story/`, `screenplay/`, `storyboard/`, `keyframe/`, `video/`, `audio/`
  - 示例 Agent：`example_agent/`

## 目录

- [概述](#概述)
- [目录结构](#目录结构)
- [创建新 Agent - 详细步骤](#创建新-agent---详细步骤)
- [Agent 实现规范](#agent-实现规范)
- [输入输出模式定义](#输入输出模式定义)
- [Agent 自动发现机制](#agent-自动发现机制)
- [测试和调试](#测试和调试)
- [最佳实践](#最佳实践)
- [常见问题](#常见问题)

---

## 概述

Agent 是 Frameworks Backend 中的核心功能单元，每个 Agent 负责实现特定的功能。Agent 系统具有以下特点：

- ✅ **自动发现**：Agent 会在应用启动时自动被发现和注册
- ✅ **易于开发**：只需继承 `BaseAgent` 并实现两个方法
- ✅ **统一管理**：通过 Assistant 系统统一管理和执行
- ✅ **独立部署**：Agent 位于项目根目录，易于访问和修改

---

## 目录结构

```
agents/
├── __init__.py                  # 包入口：re-export 所有核心类和注册表
├── README.md                    # 本文档
│
│  # ── 核心框架 ─────────────────────────────────────
├── sync_adapter.py              # Sync BaseAgent / AgentMetadata / PipelineAgentAdapter
├── base_agent.py                # Async LLM BaseAgent（pipeline agents 基类）
├── base_evaluator.py            # BaseEvaluator（L1+L2+L3 质量评估）
├── llm_client.py                # LLMClient（OpenAI wrapper）
├── descriptor.py                # SubAgentDescriptor / BaseMaterializer / MediaAsset
├── common_schema.py             # 共享 Pydantic 模型（Meta, ImageAsset 等）
├── agent_registry.py            # AgentRegistry（自动发现 + 管线注册）
│
│  # ── Pipeline Agents ──────────────────────────────
├── story/                       # StoryAgent
├── screenplay/                  # ScreenplayAgent
├── storyboard/                  # StoryboardAgent
├── keyframe/                    # KeyFrameAgent（含 materializer）
├── video/                       # VideoAgent（含 materializer）
├── audio/                       # AudioAgent（含 materializer）
│
│  # ── 示例 ─────────────────────────────────────────
└── example_agent/               # ExamplePipelineAgent（参考实现）
    ├── __init__.py              # 导出 Agent / Evaluator / Descriptor
    ├── agent.py                 # Agent 实现（继承 BaseAgent[InputT, OutputT]）
    ├── schema.py                # Pydantic 输入/输出模型定义
    ├── evaluator.py             # 质量评估器（L1 结构化 + L2 创意评估）
    └── descriptor.py            # SubAgentDescriptor 注册清单
```

---

## 创建新 Agent - 详细步骤

### 步骤 1: 创建 Agent 目录

在项目根目录的 `agents/` 文件夹下创建新目录：

```bash
mkdir agents/your_agent
```

**注意事项：**
- 目录名使用下划线命名（snake_case），如 `storyboard_agent`、`transcript_agent`
- 目录名应该清晰描述 Agent 的功能
- 避免使用特殊字符和空格

### 步骤 2: 实现 Agent

参考 `example_agent/` 目录中的 Pipeline Agent 示例实现。

每个 Pipeline Agent 需要以下文件：

**agent.py** — Agent 主体：

```python
from __future__ import annotations
from ..base_agent import BaseAgent
from .schema import YourInput, YourOutput

class YourAgent(BaseAgent[YourInput, YourOutput]):
    def system_prompt(self) -> str:
        return "You are ..."

    def build_user_prompt(self, input_data: YourInput) -> str:
        return f"Process: {input_data.source_text}"
```

**schema.py** — 输入/输出模型：

```python
from pydantic import BaseModel, Field
from ..common_schema import Meta

class YourInput(BaseModel):
    project_id: str = ""
    draft_id: str = ""
    source_text: str = ""

class YourOutput(BaseModel):
    meta: Meta = Field(default_factory=Meta)
    content: YourContent = Field(default_factory=YourContent)
```

**evaluator.py** — 质量评估器：

```python
from ..base_evaluator import BaseEvaluator
from .schema import YourOutput

class YourEvaluator(BaseEvaluator[YourOutput]):
    creative_dimensions = [
        ("accuracy", "Does the output match the input?"),
    ]

    def check_structure(self, output, upstream=None):
        errors = []
        # L1 structural checks
        return errors
```

**descriptor.py** — 注册清单：

```python
from ..descriptor import SubAgentDescriptor
from .agent import YourAgent
from .schema import YourInput
from .evaluator import YourEvaluator

DESCRIPTOR = SubAgentDescriptor(
    agent_name="YourAgent",
    asset_key="your_output",
    asset_type="your_type",
    agent_factory=lambda llm: YourAgent(llm_client=llm),
    evaluator_factory=YourEvaluator,
    build_input=lambda pid, did, assets, cfg: YourInput(...),
)
```

**__init__.py** — 导出：

```python
from .agent import YourAgent
from .schema import YourInput, YourOutput
from .evaluator import YourEvaluator
from .descriptor import DESCRIPTOR
```

### 步骤 3: 注册 Agent

在 `agents/__init__.py` 中添加你的 Agent 到 `AGENT_REGISTRY`。

### 步骤 4: 验证 Agent

重启 Backend 服务，Agent 会自动被发现和注册：

```bash
cd dynamic-task-stack
python run.py
```

```bash
# 查询所有已安装的 agents
curl http://localhost:5002/api/assistant/sub-agents
```

---

## Agent 自动发现机制

### 工作原理

1. **启动时扫描**：Backend 启动时，`AgentRegistry` 会自动扫描 `agents/` 目录
2. **加载 Agent**：对于每个子目录，尝试导入并实例化 Agent 类
3. **注册 Agent**：将成功加载的 Agent 注册到全局 registry
4. **Pipeline 注册**：Pipeline agents 通过 `AGENT_REGISTRY` 字典单独注册
5. **错误处理**：如果某个 Agent 加载失败，会记录警告但不会影响其他 Agent

---

## 最佳实践

### 1. 命名规范

- **目录名**：使用下划线命名（snake_case），如 `storyboard_agent`
- **Agent ID**：与目录名保持一致
- **类名**：使用驼峰命名（PascalCase），如 `StoryboardAgent`

### 2. 导入规范

始终使用相对导入：

```python
from ..base_agent import BaseAgent      # LLM pipeline 基类
from ..base_evaluator import BaseEvaluator
from ..descriptor import SubAgentDescriptor
from ..common_schema import Meta
```

### 3. 错误处理

```python
def execute(self, inputs):
    try:
        result = self._process(inputs)
        return result
    except ValueError as e:
        raise ValueError(f"Invalid input: {e}")
    except Exception as e:
        raise RuntimeError(f"Execution failed: {e}")
```

---

## 参考示例

```bash
# 查看示例 Pipeline Agent
agents/example_agent/agent.py       # Agent 主体
agents/example_agent/schema.py      # Pydantic 输入/输出模型
agents/example_agent/evaluator.py   # 质量评估器
agents/example_agent/descriptor.py  # SubAgentDescriptor 注册清单
agents/example_agent/__init__.py    # 导出
```
