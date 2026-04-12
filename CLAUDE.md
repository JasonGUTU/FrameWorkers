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
│   ├── agent_registry.py    # AgentRegistry 单例 + 从 AGENT_REGISTRY 注册聚合
│   ├── common_schema.py     # ArtifactCaption / ImageReferenceEntry / Meta / ImageAsset 等共享 Pydantic 类型
│   ├── story/               # 文本类 agent：agent / schema / evaluator / descriptor
│   ├── screenplay/          # 同上
│   ├── example_agent/       # 模板：照它新建 agent
│   ├── keyframe/            # 媒体类 agent，含 materializer.py
│   ├── video/               # 同上
│   ├── audio/               # 同上
│   ├── intake/              # 4 个 raw upload → caption-rich artifact 的 intake agent（text/image/video/audio）
│   └── univa_{keyframe,storyboard,video}/  # univa 系列 agent
├── dynamic-task-stack/      # Flask 后端：Task Stack + Assistant
│   ├── run.py               # 入口（默认 5002）
│   └── src/
│       ├── app.py           # Flask app factory
│       ├── common_http.py   # task_stack + assistant 共用 HTTP 工具
│       ├── task_stack/      # 分层任务管理；routes / state_store / execution_flow / batch_mutator / storage
│       └── assistant/       # descriptor 流水线执行 + workspace 落盘
│           ├── service.py   # AssistantService（核心执行入口）
│           ├── routes.py
│           └── workspace/   # 文件 / global_memory / 日志 / 资产索引
├── director_agent/          # 主 director：轮询后端 → 推理 → 委托 Assistant → 反思 → 更新 task stack
├── director_nostack/        # 备选 director：无 task stack，merge_session_goal 合并消息+memory+execution 选 sub-agent
├── inference/               # LLM 客户端 + 多模态生成（独立库）
│   ├── clients/             # base/ + implementations/（default / gpt5 / custom_model）
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
2. **统一格式**：跨 agent 数据契约就是 `descriptor.build_input(task_id, resolved_artifacts)` 这一个函数签名 —— `resolved_artifacts` 由 `InputResolver` 输出，类型是 `dict[label_name, ResolvedArtifactEntry | list[ResolvedArtifactEntry]]`。`ResolvedArtifactEntry`（见 `agents/common_schema.py`）字段固定为 `{caption, scope, path, mime, payload?}`，`(single)` label 映射到一个 entry，`(collection)` label 映射到 entry 列表。要给 entry 加字段？只改 `common_schema.py` 的 `ResolvedArtifactEntry` 一处；要加一个 **新 channel**（新的 `build_input` 参数）才需要改 13 处 descriptor 签名——这种 cross-cutting 改动本来就应该在 PR review 里显眼。不要在 agent 内部自造对外结构。
3. **不在 assistant 层硬编码 agent 逻辑**：assistant 只负责调度与 workspace 落盘；任何 agent 特定的处理必须放在 agent 自己的 descriptor / materializer 里。
4. **新 agent 注册**：写完后必须在 `agents/__init__.py` 的 `AGENT_REGISTRY` 登记 `DESCRIPTOR`，否则不会被发现。
5. **HTTP 层**：`task_stack` 和 `assistant` 路由共用 `dynamic-task-stack/src/common_http.py` + `api_serialize.serialize_for_api`，不要在 routes 里重复写校验/序列化。
6. **Workspace 单例**：所有 sub-agent 共享一个 workspace（`file_manager` / `global_memory` / `log_manager` / `artifact_writer` / `input_resolver`），不要绕开它直写磁盘。
7. **对内严控，对外宽进（Postel's Law at the agent layer）**：每个 agent 对**自己的** output schema 严格维护（Pydantic + evaluator），这些 schema 服务的是 agent 自己的评估、持久化、materialization。但是**读上游产物时零假设**：`build_input` 默认应把 `resolved_artifacts[label].payload` 作为 **JSON 文本**透传（`json.dumps(payload, ensure_ascii=False, indent=2)` 塞进 typed_input 的某个 `*_json_text: str` 字段），让 agent 自己的 LLM 从 prompt 里读这段文本、理解上游形状并生成自己的输出。**不要**在 `build_input` 或 agent 代码里写 `payload.get("content").get("scene_outline")` 这种字符串 key 访问 —— 它把上游 schema 的内部字段名硬编码进下游，造成 O(N×M) 的隐性耦合，而且上游漂移后只会静默降级为空 list 而不是报错。**跨 agent 的结构约定（例如 `prop_id = prop_NNN`、`keyframe_count == 1`、`shot_id = sh_NNN` 格式）是 producer 的义务，但是由 LLM 直接产出 + evaluator 捕获 drift + rework 修正**：在 producer 的 user-message template + `system_prompt` 里把格式明确要求出来，在 evaluator 的 `check_structure` 里加格式 / 序号 / count 的正则或相等检查，让 drift 触发 rework。**不要**在 `recompute_metrics` 里"悄悄修正" LLM 输出（那是 silent override，会让真实的 drift 被屏蔽），**也不要**在 consumer 侧做 defensive parse。`recompute_metrics` 只做**纯派生** —— 把 count / sum / 分类统计这种 LLM 从未被要求写（user-message template 里根本不展示的）字段填上。现成参考：`agents/screenplay/descriptor.py` 的 `build_input` + `agents/screenplay/agent.py` 的 `system_prompt` / `SCREENPLAY_OUTPUT_TEMPLATE` / `recompute_metrics` + `agents/screenplay/evaluator.py` 的 `check_structure`（Story → Screenplay 边是这条原则的落地范本）。

## 核心数据流

```
用户消息 → Director（推理） → Task Stack（编排）
        → Assistant.execute_agent_for_task(agent_id, task_id)
        → build_execution_inputs（InputResolver 在 global_memory caption index 上语义召回 → resolved_artifacts dict）
        → descriptor.build_input(task_id, resolved_artifacts) → typed_input
        → LLMBaseAgent pipeline → evaluator → materializer（媒体类）
        → Workspace 落盘 → Director 反思

注意：HTTP body 只有 agent_id + task_id。任何用户原始输入（text/image/video/audio）必须**先**经
`POST /api/workspace/upload` + 跑对应 IntakeXxxAgent 落成 caption-rich workspace artifact，再由
InputResolver 通过 caption index 召回。
```

## 给 AI 的工作提示

- 改代码前先 `Read` 目标文件 + 同目录测试，不要凭直觉。
- 新增能力时优先复用 `inference/` 已有 client / generator，不要自己起 HTTP 调用。
- 写新 agent 照抄 `agents/example_agent/` 结构。
- 不要为新模块写 README；要写"给 AI 看的局部说明"就放 `CLAUDE.md`。
- **讨论设计 / 重构问题时不要偏袒现有代码**。用户质疑一个写法时，先**诚实**评估他的质疑是否成立（通常成立），而不是反射性地为现状辩护。现有代码只是上一次决策的产物，不是真理；"现在就是这么写的"不构成"应该继续这么写"的理由。同样适用于现有文档 / 注释 / CLAUDE.md 自己 —— 如果发现 stale，就地修，不要装没看见。
