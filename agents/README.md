# Agents 开发指南

本文档详细说明如何创建、开发和部署 Agent 到 Frameworks Backend。

**目录结构说明：**
- `agents/`（根目录）：Agent 核心框架和所有 Agent 实现
  - 核心框架文件：`base_agent.py`, `base_evaluator.py`, `descriptor.py`, `common_schema.py`, `agent_registry.py`
  - LLM 运行时客户端统一来自：`inference/clients/base/base_client.py`（推荐业务代码直接从 `inference/clients/__init__.py` 导入）
  - Pipeline Agent 子包：`story/`, `screenplay/`, `storyboard/`, `keyframe/`, `video/`, `audio/`
  - 其中 `video/` materializer 会消费 `keyframe` 的图片 URI（按 `shot_id` 对齐）
  - 且 `video/` 会把同一 keyframe 条目的 `prompt_summary` 与图片一起对齐传给视频后端，并追加 storyboard 的 shot 语义字段（`visual_goal` / `action_focus` / `camera.framing_notes` / `keyframe_notes` / `characters_in_frame`）以及 scene 一致性字段（`scene_consistency_pack.location_lock/environment_notes/style_lock`）构造 clip prompt；多 keyframe 被视为同一 shot 的实体一致性锚点（人物/场景），不是时间起止帧
  - `props` 相关路径（KeyFrame 生成 props anchors + Video 注入 props 一致性约束）统一由 `FW_ENABLE_PROP_PIPELINE` 控制（默认 `0` 关闭）
  - 兼容历史配置：`FW_ENABLE_PROP_KEYFRAMES` 与 `FW_VIDEO_ENABLE_PROP_CONSISTENCY` 仍可单独生效；当 `FW_ENABLE_PROP_PIPELINE` 设置时，以它为准
  - `keyframe/` 不再在本地执行增量快照写盘；图片仅通过 `MediaAsset` 返回，由 assistant 统一持久化
  - `audio/` materializer 会在 `final_audio_asset` 之后执行音视频 mux，输出 `final_delivery_asset`
- `story/` 会显式遵循 `target_duration_sec` 约束，并在 evaluator 中校验 `content.estimated_duration.seconds` 容差（默认 ±20%）
- `screenplay/` 会显式遵循 `target_duration_sec` 约束，并在 evaluator 中校验总时长容差（默认 ±20%）
- `storyboard/` 会从 screenplay 的 `blocks[].character_id`、`blocks[].continuity_refs.wardrobe_character_ids` 和 `continuity.character_wardrobe_notes[].character_id` 汇总 `character_locks`，避免动作块未显式写角色 ID 时丢失人物锚点
- `keyframe/` 在构建人物锚点时会同时读取 `scene_consistency_pack.character_locks` 与 `shots[].characters_in_frame`，保证人物全局/场景锚点可生成
  - `keyframe/descriptor.py` 默认使用 `FalImageService` 作为图片生成后端（需配置 `FAL_API_KEY` 与可选 `FAL_IMAGE_MODEL`）
  - `video/descriptor.py` 默认使用 `FalVideoService` 作为视频生成后端（需配置 `FAL_API_KEY` 与可选 `FAL_VIDEO_MODEL`）
  - `audio/descriptor.py` 默认使用 `FalAudioService` 作为 TTS 后端（需配置 `FAL_API_KEY` 与可选 `FAL_TTS_MODEL`）
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

当前 pipeline 执行链路直接使用 `inference` 的统一实现：

- LLM 调用：`inference/clients/base/base_client.py`
- 媒体服务（image/video/audio）：`inference/generation/image_generators/service.py`、`inference/generation/video_generators/service.py`、`inference/generation/audio_generators/service.py`

---

## 目录结构

```
agents/
├── __init__.py                  # 包入口：re-export 所有核心类和注册表
├── README.md                    # 本文档
│
│  # ── 核心框架 ─────────────────────────────────────
├── base_agent.py                # Async LLM BaseAgent（pipeline agents 基类）
├── base_evaluator.py            # BaseEvaluator（L1+L2+L3 质量评估）
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
    build_input=lambda _pid, _did, assets, cfg: YourInput(...),  # 不需要 id 时用 _pid/_did 占位
)
```

说明：Assistant 始终传入 `(project_id, draft_id, assets, config)`；若 agent 不在 prompt/逻辑里使用 id，可从 **Input 模型** 中去掉 `project_id`/`draft_id`，并在 `build_input` 用 `_project_id`/`_draft_id` 忽略前两参。

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

`/api/assistant/sub-agents` 列表与单项详情返回 `asset_key`、`asset_type`、`capabilities`、`description` 等 descriptor 元数据（不含空的 JSON Schema / `contract` 占位字段），便于调用端按资产类型路由。

---

## Agent 自动发现机制

### 工作原理

1. **Pipeline 注册**：Backend 启动时通过 `AGENT_REGISTRY` 注册 `SubAgentDescriptor`
2. **统一模型**：仅使用 descriptor-driven pipeline agent 模型
3. **按需装备**：执行阶段由 Assistant 通过 `get_descriptor()` + 服务内 `LLMClient` 调用 `descriptor.build_equipped_agent(...)`；`AgentRegistry` 只存 descriptor，不缓存装备好的 agent、也不在注册表内持有 LLM 客户端
4. **错误处理**：某个 Agent 加载失败会记录警告，但不会影响其他 Agent

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

## 测试

```bash
# 从项目根目录运行 agents 核心测试
python -m pytest tests/agents/test_agent_core.py -v

# 校验 descriptor 的 assets 读取声明是否完整
python -m pytest tests/agents/test_descriptor_asset_contract.py -v
```

如果仓库目录结构有调整，可通过 `FRAMEWORKERS_ROOT` 指定项目根目录后再运行。

### 评估阈值（临时测试）

- `BaseEvaluator.CREATIVE_PASS_THRESHOLD` 当前为 `0.0`（用于降低创意评估拦截，便于 pipeline 调试）。
- 该设置会显著放宽 Layer 2 creative gate，不建议长期用于正式质量把关。
