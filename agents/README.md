# Agents 开发指南

本文档详细说明如何创建、开发和部署 Agent 到 Frameworks Backend。

**目录结构说明：**
- `agents/`（根目录）：Agent 核心框架和所有 Agent 实现
  - 核心框架文件：`base_agent.py`, `base_evaluator.py`, `descriptor.py`, `common_schema.py`, `agent_registry.py`
  - 子 agent 只通过 `InputBundleV2.context["resolved_inputs"]` 读取 Assistant 预解析后的结构化输入（已移除未使用的 `contracts/query.py`、`latest_payload`、以及 bundle 上的 `find_artifacts` / `first_payload`）
  - 媒体 materializer 的 `materialize(..., input_bundle_v2)` 及其内部 helper 统一使用 `InputBundleV2` 类型标注；`contracts/input_bundle_v2.py` 仅保留 `InputBundleV2`（已移除只读子类 `FrozenInputBundleV2`，约定上避免在执行路径中原地修改 Assistant 传入的 bundle）
  - 已删除未接入任何导入链路的占位文件 `input_bundle.py`（原 `ExecutionInputBundle` 未被使用）
  - LLM 运行时客户端统一来自：`inference/clients/base/base_client.py`（推荐业务代码直接从 `inference/clients/__init__.py` 导入）
  - Pipeline Agent 子包：`story/`, `screenplay/`, `storyboard/`, `keyframe/`, `video/`, `audio/`
  - 其中 `video/` materializer 会消费 `keyframe` 的图片 URI（按 `shot_id` 对齐）
  - 且 `video/` 会把同一 keyframe 条目的 `prompt_summary` 与图片一起对齐传给视频后端，并追加 storyboard 的 shot 语义字段（`visual_goal` / `action_focus` / `camera.framing_notes` / `keyframe_notes` / `characters_in_frame`）以及 scene 一致性字段（`scene_consistency_pack.location_lock/environment_notes/style_lock`）构造 clip prompt；多 keyframe 被视为同一 shot 的实体一致性锚点（人物/场景），不是时间起止帧
  - `props` 相关路径（KeyFrame 生成 props anchors + Video 注入 props 一致性约束）统一由 `FW_ENABLE_PROP_PIPELINE` 控制（默认 `0` 关闭）
  - 兼容历史配置：`FW_ENABLE_PROP_KEYFRAMES` 与 `FW_VIDEO_ENABLE_PROP_CONSISTENCY` 仍可单独生效；当 `FW_ENABLE_PROP_PIPELINE` 设置时，以它为准
  - `keyframe/` 不再在本地执行增量快照写盘；图片仅通过 `MediaAsset` 返回，由 assistant 统一持久化
  - 离线从 **storyboard JSON** 一路跑到成片（KeyFrameAgent LLM + fal 出图 → VideoAgent fal）：**`scripts/run_storyboard_to_video.py`**（不经过 Task Stack；可用 `--no-video-materialize` 只跑到 keyframes，或 `--no-keyframe-materialize` + `--no-video-materialize` 只做 KeyFrame LLM+L1/L2）
  - `audio/` materializer 会在 `final_audio_asset` 之后执行音视频 mux，输出 `final_delivery_asset`
- `story/` 会显式遵循 `target_duration_sec` 约束，并在 evaluator 中校验 `content.estimated_duration.seconds` 容差（默认 ±20%）；`StoryConstraints.target_duration_sec` 与 agent 内部回退默认 **10s**（用户未写明长度时 prompt 亦按约 10 秒引导）；`story/descriptor.py` 将 Assistant 注入的整份 `source_text`（常为 Task `description` 对象）在需要时编码为 JSON 字符串再填入 `draft_idea`，不在 Assistant service 层解析具体字段
- `screenplay/` 会显式遵循 `target_duration_sec` 约束，并在 evaluator 中校验总时长容差（默认 ±20%）；`ScreenplayConstraints.target_duration_sec` 与 agent 内部回退默认 **10s**
- `storyboard/` 会从 screenplay 的 `blocks[].character_id`、`blocks[].continuity_refs.wardrobe_character_ids` 和 `continuity.character_wardrobe_notes[].character_id` 汇总 `character_locks`，避免动作块未显式写角色 ID 时丢失人物锚点
- `keyframe/` 在构建人物锚点时会同时读取 `scene_consistency_pack.character_locks` 与 `shots[].characters_in_frame`，保证人物全局/场景锚点可生成
  - `keyframe/descriptor.py` 默认使用 `FalImageService`（需 `FAL_API_KEY`；`FAL_IMAGE_MODEL` 由仓库根 `.env` / `.env.example` 提供，见 `inference/generation/fal_helpers.py`；`fal-ai/nano-banana-2` 时编辑层走 `fal-ai/nano-banana-2/edit`）
  - `video/descriptor.py` 默认使用 `FalVideoService`（需 `FAL_API_KEY`；`FAL_VIDEO_MODEL` 同上来自环境，无 Python 内置默认端点）
  - `audio/descriptor.py` 默认使用 `FalAudioService` 作为 TTS 后端（需配置 `FAL_API_KEY` 与可选 `FAL_TTS_MODEL`）
- `audio/agent.py` 在 skeleton-first 的 creative-fill 阶段对输出做严格 JSON 约束（禁止 `TypeOf:` 等类型提示行），避免 `chat_json` 因非 JSON 输出而失败
  - 示例 Agent：`example_agent/`
- `common_schema.Meta` 不包含 `project_id`；LLM 输出中的 `meta` 仅使用该模型已声明字段（与外部服务如 Cloudflare 请求头里的 `project_id` 无关）

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
├── __init__.py                  # 包入口：`AGENT_REGISTRY`、`get_agent_registry`、类型与类 re-export（evaluator 不经全局 `AGENT_ID_TO_*` 映射）
├── README.md                    # 本文档
│
│  # ── 核心框架 ─────────────────────────────────────
├── base_agent.py                # Async LLM BaseAgent（pipeline agents 基类）
├── base_evaluator.py            # BaseEvaluator（L1+L2+L3 质量评估）
├── descriptor.py                # SubAgentDescriptor / BaseMaterializer / MediaAsset
├── contracts/                   # V2 契约：InputBundleV2 / OutputEnvelopeV2 / NamingSpecV2
├── common_schema.py             # 共享 Pydantic 模型（Meta, ImageAsset 等）；编排作用域用 Task Stack 的 task_id（见根 .cursorrules 的 workspace 命名约定）
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

    def check_structure(self, output, input_bundle_v2=None):
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
    agent_id="YourAgent",
    asset_key="your_output",
    agent_factory=lambda llm: YourAgent(llm_client=llm),
    evaluator_factory=YourEvaluator,
    build_input=lambda _task_id, input_bundle_v2, cfg: YourInput(...),
)
```

说明：Assistant 调用 `build_input(task_id, input_bundle_v2)`（**无** 第三个 `config` 参数）。结构化上游产物由 **`input_bundle_v2.context["resolved_inputs"]`** 提供（键为语义 **role**，由输入打包 LLM 从 `global_memory.artifact_locations` 选出并加载）；`input_bundle_v2.hints` 含 `source_text`（来自 `execute_fields.text`）以及可选 **`image` / `video` / `audio`**（来自 `execute_fields` 同名字段）。**`global_memory`** 仅在执行 `inputs` 顶层存在，供编排与审计，不合并进 bundle。时长、语言等创作约束由各 agent 的 **LLM 从正文与上游 JSON 推断**，不在 Python 层做关键词/正则解析。磁盘 **`global_memory.md`** 条目可含完整 `content` 与 **`artifact_locations`**；HTTP **`memory/brief`** 仅四键薄行（无 `content`、无 **`artifact_locations`**）。另可有 **`input_package`**（输入打包 LLM 的 `rationale` / `selected_roles` 等元信息）。

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

`/api/assistant/sub-agents` 列表与单项详情返回 `asset_key`、`capabilities`、`description` 等 descriptor 元数据（不含空的 JSON Schema / `contract` 占位字段），便于调用端按资产键路由。

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
- **Descriptor 常量（推荐统一）**：
  - 输出资产键：`OUTPUT_ASSET_KEY = "xxx"`
  - 上游输入语义角色（role）由 Assistant 的输入打包 LLM 从 `CATALOG_ENTRY` 推导并回填；descriptor 侧不再推荐定义 `INPUT_<NAME>_ASSET_KEY = "yyy"` 常量来手工索引上游产物。
  - 用户文本覆盖键：`USER_TEXT_KEY = "user_xxx"`（如该 agent 支持 `user_text_key`）

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

# 校验 descriptor 与输入契约（含 asset_key 等）
python -m pytest tests/agents/test_descriptor_asset_contract.py -v
```

如果仓库目录结构有调整，可通过 `FRAMEWORKERS_ROOT` 指定项目根目录后再运行。

### 评估阈值（临时测试）

- `BaseEvaluator.CREATIVE_PASS_THRESHOLD` 当前为 `0.0`（用于降低创意评估拦截，便于 pipeline 调试）。
- 该设置会显著放宽 Layer 2 creative gate，不建议长期用于正式质量把关。
