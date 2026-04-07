# FrameWorkers — Claude 项目说明

> 本文件是给 AI（Claude）看的全局上下文。**项目内不再为子目录维护 README 作为 AI 上下文**——
> 模块说明就一行写在下方目录树里；要了解细节请直接 `Read` / `Grep` 源码（代码是事实，文档容易腐烂）。
> 真要写局部指令，请在子目录放 `CLAUDE.md` 而不是 README。
> 对外用户向的 README 仅保留：根 `README.md`、`huobao-drama/`、`univa/`、`process-flow-visualizer/`、`interface/`。

## ⚠️ 不要碰的目录（upstream / 参考代码）

以下目录是从外部 clone 来仅供参考的，**不是本项目源码**。不要读、不要改、不要算进架构理解或依赖图：

- `huobao-drama/`（含其自带的 README 和 CLAUDE.md）
- `univa/`（含 `packages/video-export/` 等所有子目录）

如果用户的问题涉及这些目录，先确认是不是真的要看参考代码，否则一律忽略。

## 一句话定位

任务编排 + 多模态 Agent 框架：Director 推理 → Task Stack 编排 → Assistant 执行 sub-agent 流水线 → Workspace 落盘。

## 顶层目录

```
FrameWorkers/
├── agents/                  # Sub-agent 流水线实现 + 注册表（运行时核心）
│   ├── __init__.py          # AGENT_REGISTRY；新 agent 必须在此登记 DESCRIPTOR
│   ├── base_agent.py        # LLMBaseAgent（异步 pipeline 执行体）
│   ├── base_evaluator.py    # 三层评估（结构/创意/资产）+ 重试预算
│   ├── descriptor.py        # SubAgentDescriptor（build_input / build_equipped_agent / run）
│   ├── agent_registry.py    # 文件系统扫描 + 注册聚合
│   ├── common_schema.py
│   ├── contracts/           # input_bundle_v2 等跨 agent 契约
│   ├── story/               # 文本类 agent：agent / schema / evaluator / descriptor
│   ├── screenplay/          # 同上
│   ├── example_agent/       # 模板：照它新建 agent
│   ├── keyframe/            # 媒体类 agent，含 materializer.py
│   ├── video/               # 同上
│   ├── audio/               # 同上
│   └── univa_{keyframe,storyboard,video}/  # univa 系列 agent
├── dynamic-task-stack/      # Flask 后端：Task Stack + Assistant
│   ├── run.py               # 入口（默认 5002）
│   └── src/
│       ├── app.py           # Flask app factory
│       ├── common_http.py   # task_stack + assistant 共用 HTTP 工具
│       ├── task_stack/      # 分层任务管理；routes / state_store / execution_flow / batch_mutator / storage
│       └── assistant/       # 全局 assistant 单例 + descriptor 流水线执行
│           ├── service.py   # AssistantService（核心执行入口）
│           ├── routes.py
│           └── workspace/   # 文件 / global_memory / 日志 / 资产索引
├── director_agent/          # 主 director：轮询后端 → 推理 → 委托 Assistant → 反思 → 更新 task stack
├── director_nostack/        # 备选 director：无 task stack，merge_session_goal 合并消息+memory+execution 选 sub-agent
├── inference/               # LLM 客户端 + 多模态生成（独立库）
│   ├── clients/             # base/ + implementations/（default / gpt5 / custom_model）
│   ├── input_processing/    # ImageUtils / MessageUtils（含 MultimodalUtils 别名）
│   ├── generation/          # image / video / audio 注册表与 Service；fal_helpers 共享 fal.ai 后端
│   └── MODELS.md            # 可用模型清单（保留，给人查）
├── interface/               # Vue 3 + Vite 前端（聊天 / 任务栈监控）
├── process-flow-visualizer/ # 独立可视化小工具
├── scripts/                 # 一次性脚本（如 run_storyboard_to_video.py）
├── tests/                   # agents / assistant / director / inference 测试
├── Runtime/                 # Workspace 运行时落盘目录（不要手改）
├── install_requirements.py  # conda env=frameworkers，可重复执行
└── inference_runtime.yaml
```

## 关键工作流入口

- **启动后端**：`cd dynamic-task-stack && python run.py`（端口 5002）
- **启动 director**：`cd director_agent && python run.py`
- **前端**：`cd interface && npm run dev`
- **核心回归**：`bash tests/run_core_tests.sh`
- **storyboard → video 端到端脚本**：`scripts/run_storyboard_to_video.py`

## 核心约定（强约束，违反请提醒用户）

1. **Sub-agent 解耦**：每个 agent 自包含（schema / evaluator / descriptor / 可选 materializer），互不依赖。
2. **统一格式**：跨 agent 数据走 `agents/contracts/input_bundle_v2.py`，不要在 agent 内部自造对外结构。
3. **不在 assistant 层硬编码 agent 逻辑**：assistant 只负责调度与 workspace 落盘；任何 agent 特定的处理必须放在 agent 自己的 descriptor / materializer 里。
4. **新 agent 注册**：写完后必须在 `agents/__init__.py` 的 `AGENT_REGISTRY` 登记 `DESCRIPTOR`，否则不会被发现。
5. **HTTP 层**：`task_stack` 和 `assistant` 路由共用 `dynamic-task-stack/src/common_http.py` + `api_serialize.serialize_for_api`，不要在 routes 里重复写校验/序列化。
6. **Workspace 单例**：所有 sub-agent 共享一个 workspace（文件 / global_memory / 日志 / asset_manager），不要绕开它直写磁盘。

## 核心数据流

```
用户消息 → Director（推理） → Task Stack（编排）
        → Assistant.execute(agent_id, task_id, execute_fields)
        → descriptor.build_input → build_execution_inputs（global_memory + selected_roles → input_bundle_v2）
        → LLMBaseAgent pipeline → evaluator → materializer（媒体类）
        → Workspace 落盘 → Director 反思
```

## 给 AI 的工作提示

- 改代码前先 `Read` 目标文件 + 同目录测试，不要凭直觉。
- 新增能力时优先复用 `inference/` 已有 client / generator，不要自己起 HTTP 调用。
- 写新 agent 照抄 `agents/example_agent/` 结构。
- 不要为新模块写 README；要写"给 AI 看的局部说明"就放 `CLAUDE.md`。
