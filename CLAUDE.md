# FrameWorkers — Claude 项目说明

> 本文件是给 AI（Claude）看的全局上下文。**项目内不再为子目录维护 README 作为 AI 上下文**——
> 模块说明就一行写在下方目录树里；要了解细节请直接 `Read` / `Grep` 源码（代码是事实，文档容易腐烂）。
> 真要写局部指令，请在子目录放 `CLAUDE.md` 而不是 README。
> 对外用户向的 README 仅保留：根 `README.md`、`process-flow-visualizer/`、`interface/`（上游参考 repo 的 README 在 `references/` 下，不算本项目文档）。

## ⚠️ 不要碰的目录（upstream / 参考代码）

`references/` 下全部是从外部 clone 来仅供参考的，**不是本项目源码**。不要读、不要改、不要算进架构理解或依赖图：

- `references/huobao-drama/`（含其自带的 README 和 CLAUDE.md）
- `references/univa/`（含 `packages/video-export/` 等所有子目录）
- `references/Director/`

如果用户的问题涉及这些目录，先确认是不是真的要看参考代码，否则一律忽略。

## 一句话定位

任务编排 + 多模态 Agent 框架：Director 推理 + 编排 → Plan Stack 持久化 PlanStep → Assistant 执行 sub-agent 流水线 → Workspace 落盘。

> **唯一 Director：`director_agent/`**。一条 user message → Upfront planner 产出完整 pipeline 计划 → 一次 `POST /api/plan-stack/modify` 批量写入 Plan Stack → 按 execution pointer 顺序跑每个 PlanStep。
>
> **失败走 replan-or-halt，不是静态 DAG**：PlanStep 返回 FAILED 时，director 调 `planner.replan_on_failure(...)` → `ReplanDecision`。replanner 内部 3 次 LLM retry 吸收抖动（network / malformed JSON / empty sample，对齐 `aplan_pipeline_upfront`），最终两条路径：**replan**（`remove_steps_from_layers` 删光 PENDING tail + 追加新 layer 承载新 tail，pointer 自然走到新 layer 第 0 步）/ **halt**（replanner 给不出 actionable tail 或 `MAX_REPLAN_ROUNDS` 耗尽 → director 发 "Pipeline halted: …" 消息后 `return`，executor 不再静默推进 pointer，等用户下一条消息触发新 plan）。**没有 "retry" 路径**（PlanStep 不会从 FAILED 重置为 PENDING + pointer 回滚），**也没有 "skip" 路径**（不会静默跳过失败 step 继续跑残余 pending tail）—— 这两种行为在旧文档里出现过，已与代码同步删除。已 COMMIT 的 step（COMPLETED / CANCELLED / FAILED）永不被改写，committed history append-only。Plan Stack 的数据单元就是 `PlanStep` = 一次计划中的 agent execution；`AgentExecution.step_id` 外键回指。

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
│   ├── ambience/ audio_mix/ music/ narration/ narrator/   # 音频类 agent（各自独立目录，无统一 audio/ 父目录）
│   ├── intake/              # raw upload → caption-rich artifact 的 intake agent：intake_image / intake_video（text 已退役走 workspace.persist_raw_upload，audio 未实现）
│   └── univa_{keyframe,storyboard,video}/  # 本项目自研的 univa 系列 agent（与 references/univa/ 零代码依赖，仅命名致敬）；**当前未挂入 AGENT_REGISTRY，runtime 不会调用**
├── plan-stack-backend/      # Flask 后端：Plan Stack + Assistant
│   ├── run.py               # 入口（默认 5002）
│   └── src/
│       ├── app.py           # Flask app factory
│       ├── common_http.py   # plan_stack + assistant 共用 HTTP 工具
│       ├── plan_stack/      # Plan Stack 分层管理：routes / state_store / execution_flow / batch_mutator / storage
│       └── assistant/       # descriptor 流水线执行 + workspace 落盘
│           ├── service.py   # AssistantService（核心执行入口）
│           ├── routes.py
│           └── workspace/   # 文件 / global_memory / 日志 / 资产索引
├── director_agent/          # 唯一 director：Upfront planner 生成完整 pipeline 计划 → 写入 Plan Stack → 推进 execution pointer
├── inference/               # LLM 客户端 + 多模态生成（独立库）
│   ├── clients/             # base/ + implementations/（default / gpt5 / custom_model）
│   ├── generation/          # image / video / audio 注册表与 Service；fal_helpers 共享 fal.ai 后端
│   └── MODELS.md            # 可用模型清单（保留，给人查）
├── interface/               # Vue 3 + Vite 前端（聊天 / 任务栈监控）
├── process-flow-visualizer/ # 独立可视化小工具
├── scripts/                 # 一次性脚本（如 run_storyboard_to_video.py）
├── tests/                   # agents / assistant / director / inference 测试
├── _workspaces/             # Workspace 运行时落盘目录（不要手改）
├── install_requirements.py  # conda env=frameworkers，可重复执行
└── inference_runtime.yaml
```

## 关键工作流入口

- **启动后端**：`cd plan-stack-backend && python run.py`（端口 5002）
- **启动 director**：`cd director_agent && python run.py`
- **前端**：`cd interface && npm run dev`
- **核心回归**：`bash tests/run_core_tests.sh`
- **storyboard → video 端到端脚本**：`scripts/run_storyboard_to_video.py`

## 核心约定（强约束，违反请提醒用户）

1. **Sub-agent 解耦**：每个 agent 自包含（schema / evaluator / descriptor / 可选 materializer），互不依赖。
2. **统一格式**：跨 agent 数据契约就是 `descriptor.build_input(step_id, resolved_artifacts)` 这一个函数签名 —— `resolved_artifacts` 由 `InputResolver` 输出，类型是 `dict[label_name, ResolvedArtifactEntry | list[ResolvedArtifactEntry]]`。`ResolvedArtifactEntry`（见 `agents/common_schema.py`）字段固定为 `{caption, scope, path, mime, payload?}`，`(single)` label 映射到一个 entry，`(collection)` label 映射到 entry 列表。要给 entry 加字段？只改 `common_schema.py` 的 `ResolvedArtifactEntry` 一处；要加一个 **新 channel**（新的 `build_input` 参数）才需要改 13 处 descriptor 签名——这种 cross-cutting 改动本来就应该在 PR review 里显眼。不要在 agent 内部自造对外结构。
3. **不在 assistant 层硬编码 agent 逻辑**：assistant 只负责调度与 workspace 落盘；任何 agent 特定的处理必须放在 agent 自己的 descriptor / materializer 里。
4. **新 agent 注册**：写完后必须在 `agents/__init__.py` 的 `AGENT_REGISTRY` 登记 `DESCRIPTOR`，否则不会被发现。
5. **HTTP 层**：`plan_stack`（URL 对外 `/api/plan-stack`）和 `assistant` 路由共用 `plan-stack-backend/src/common_http.py` + `api_serialize.serialize_for_api`，不要在 routes 里重复写校验/序列化。
6. **Workspace 单例**：所有 sub-agent 共享一个 workspace（`file_manager` / `global_memory` / `log_manager` / `artifact_writer` / `input_resolver`），不要绕开它直写磁盘。
7. **对内严控，对外宽进（Postel's Law at the agent layer）**：每个 agent 对**自己的** output schema 严格维护（Pydantic + evaluator），这些 schema 服务的是 agent 自己的评估、持久化、materialization。但是**读上游产物时零假设**：`build_input` 默认应把 `resolved_artifacts[label].payload` 作为 **JSON 文本**透传（`json.dumps(payload, ensure_ascii=False, indent=2)` 塞进 typed_input 的某个 `*_json_text: str` 字段），让 agent 自己的 LLM 从 prompt 里读这段文本、理解上游形状并生成自己的输出。**不要**在 `build_input` 或 agent 代码里写 `payload.get("content").get("scene_outline")` 这种字符串 key 访问 —— 它把上游 schema 的内部字段名硬编码进下游，造成 O(N×M) 的隐性耦合，而且上游漂移后只会静默降级为空 list 而不是报错。**跨 agent 的结构约定（例如 `prop_id = prop_NNN`、`keyframe_count == 1`、`shot_id = sh_NNN` 格式）是 producer 的义务，但是由 LLM 直接产出 + evaluator 捕获 drift + rework 修正**：在 producer 的 user-message template + `system_prompt` 里把格式明确要求出来，在 evaluator 的 `check_structure` 里加格式 / 序号 / count 的正则或相等检查，让 drift 触发 rework。**不要**在 `recompute_metrics` 里"悄悄修正" LLM 输出（那是 silent override，会让真实的 drift 被屏蔽），**也不要**在 consumer 侧做 defensive parse。`recompute_metrics` 只做**纯派生** —— 把 count / sum / 分类统计这种 LLM 从未被要求写（user-message template 里根本不展示的）字段填上。现成参考：`agents/screenplay/descriptor.py` 的 `build_input` + `agents/screenplay/agent.py` 的 `system_prompt` / `SCREENPLAY_OUTPUT_TEMPLATE` / `recompute_metrics` + `agents/screenplay/evaluator.py` 的 `check_structure`（Story → Screenplay 边是这条原则的落地范本）。

8. **Director prompt 构成：basic info ≠ scaffold**。Director 做 routing 看到的 prompt 必须按"信息类别"严格分层，任何 ablation / 训练数据构造之前都要先把每块归类清楚，不能笼统叫"bare"。

   **basic info（必须在 prompt 里，不可剥）：**
   - Task 定义 + 输出 JSON schema
   - 结构规则（framework invariants：每个 agent ≤1 次 / plan 非空 / flat order 等；text intake 已退役，chat/文本上传由 `workspace.persist_raw_upload` 直接落成 `[creative_brief]` 全局 artifact，plan 不再从 IntakeTextAgent 起步）
   - `allowed_ids`（20 个 agent 名字列表，以 `agents/__init__.py::AGENT_REGISTRY` 为准）
   - **每个 agent 的完整 descriptor**（`AgentSpec` 的 `inputs / output_description / purpose_and_trigger` 三段，由 `render_catalog_entry()` 渲染成 ~1500 chars/agent × 20）—— 这**不是** scaffold，是告诉 planner "每个 agent 能干啥 / 吃啥 / 产啥" 的基本事实。跟"找人干活必须知道他能干啥"一个意思。`training/director/gen_samples.py::build_compact_catalog()` 之前输出的 degenerate `{id, purpose=id}` 是残缺的 basic info，必须改成至少给 `purpose_and_trigger` 一行。

   **scaffold（可选加分项，三者独立 ablation）：**
   - **fewshots**：`_PLAN_UPFRONT_FEWSHOTS` 的 7 条 worked pattern 示例（"看例子"）。开关：`LlmSubAgentPlanner(fewshots=True|False)`。
   - **topology**：`topology.py::get_topology_block()` 注入到每个 catalog entry 尾部的 upstream/downstream hint 块（"看邻居"）。开关：`FW_TOPOLOGY=0|1` env var。
   - **routing policies**：`_PLAN_UPFRONT_CORE` 里"CREATIVE FLOW AUDIO / SUBTITLE INCLUSION / HIGHLIGHT TERMINAL / VIDEO_ANALYSIS INCLUSION" 4 条明示规则（"按规则条文"）。**当前硬编码在 core 里，应该抽成独立段 + 独立 flag**，与前两个同级。

   **命名规则：** 谈 ablation 时必须明确写"(fewshots=X, topology=Y, policies=Z)" 三元组。**禁止用"bare"一个词含糊指代**——之前 Gemini 61%（basic info 完整 + 无 fewshot + 无 topology + 有 policy）和 LoRA 训练数据（basic info 缺 descriptor + 无 fewshot + 无 topology + 有 policy）两个完全不同的 prompt 都被叫 "bare"，导致整个 ablation 对比错乱。

   **训练 LoRA 的准则：** LoRA 推理时的 prompt = LoRA 训练时的 prompt。两边都必须给 basic info（包含 descriptor），不给相当于让 LoRA 靠 SFT 统计规律硬背"agent 能干啥"，是次优设计。训练时想学什么 scaffold-free 行为就只在训练 prompt 里剥那几个 scaffold flag，basic info 保留。

## 核心数据流

```
用户消息 → Director Upfront planner 生成整条 PlanStep array
        → 一次 POST /api/plan-stack/modify 批量建 PlanStep + 挂进 Plan Stack
        → Director 按 execution pointer 顺序调 POST /api/assistant/execute {agent_id, step_id}
        → Assistant.execute_agent_for_step(agent_id, step_id)
        → build_execution_inputs（InputResolver 在 global_memory caption index 上语义召回 → resolved_artifacts dict）
        → descriptor.build_input(step_id, resolved_artifacts) → typed_input
        → LLMBaseAgent pipeline → evaluator → materializer（媒体类）
        → Workspace 落盘 → 回到 Director：FAILED 走 replan（retry / replan-tail / skip，见上文），否则 advance_execution_pointer

注意：execute HTTP body 只有 agent_id + step_id。任何用户原始输入（text/image/video/audio）必须**先**经
`POST /api/workspace/upload` + 跑对应 IntakeXxxAgent 落成 caption-rich workspace artifact，再由
InputResolver 通过 caption index 召回。
```

## 模型约束（强约束）

- **图片生成禁止用 flux**。两条 image gen 路径并存（不同 agent 系统选不同 backend）：
  - **`agents/keyframe/` (Director pipeline) → Gemini**：直连 Google `gemini-3.1-flash-image-preview`（nano-banana 升级线，identity 保持 + 细节比 `gemini-2.5-flash-image` 更好；单帧延迟 ~25 s vs 7 s，N-shot 走 `asyncio.gather` 并行抵销），通过 CF AI Gateway 的 native-Gemini Worker（`GEMINI_API_KEY` + `GEMINI_BASE_URL`，与聊天 LLM 同一条入口），实现见 `image_generators/service.py::GeminiImageService`，由 `select_image_service()` 在 `FW_USE_REAL_MEDIA_GEN=1` 时选中。Model id 来自 `INFERENCE_IMAGE_MODEL`（保留对旧 `google/` 前缀的容忍）；切回 `gemini-2.5-flash-image` 只改 env 不改代码。`FalImageService` 类还在但 select 不再走它；不再读 `FAL_IMAGE_MODEL`，OpenRouter 旧路径同样未启用。
  - **`sub_agents/keyframe/` (sub_agents 实验流水线) → gpt-image-2**：OpenAI 直连（`OPENAI_API_KEY`），anchor 和 storyboard sheet 都用 gpt-image-2。anchor 是 t2i 1536×1024 **3-view 单图**，方向标签**全部固定通用**（不写 per-instance 字段）：character 走 `FRONT / SIDE / BACK`，location 走 `FRONT / BACK / OVERHEAD`（FRONT = 模型自己识别的 iconic / approach 视角，BACK = 180° 反向，OVERHEAD = 鸟瞰）。方向标签 PIL 后处理 overlay，下游 i2i prompt 显式指明用哪段（如 "use the BACK section of [Image 1]"）。storyboard 仍是 multi-image i2i edit 1536×1024（grid 映射在 `_SHOT_PLAN_SYSTEM`）。实证（sh_003 A/B）：multi-panel sheet 一致性 + per-panel 分辨率上 gpt-image-2 优于 Gemini；安全方面 multi-panel 上下文稀释了单 panel 的暴力词权重，反而比单 panel solo 路径更不易触发 OpenAI safety filter。实现见 `sub_agents/keyframe/agent.py::_render_anchor` / `_render_style_anchor` / `_gpt_image_2_call`。
- **视频生成有两条独立的 backend 选择路径**：
  - `sub_agents/pipeline.py` (sub_agents 实验流水线) — **默认 Seedance 2.0** (`bytedance/seedance-2.0/reference-to-video` via fal)。由 `FW_SUB_AGENTS_VIDEO_BACKEND` env 切换：`seedance` (默认) / `happyhorse` (`$0.14/s 720p`，便宜但 beat-following 弱，会跳过 transitional beats) / `veo`。Seedance 价格 `$0.3024/s 720p`（standard image-ref tier），15s 单 shot $4.54。`[Image N]` → `@Image{N}` 翻译。`generate_audio=False` 默认开（防中文字幕泄漏），声音走下游单独 TTS。实证（sh_003 A/B）：Seedance 对 storyboard sheet 的 per-panel 时序跟随明显优于 HappyHorse；HappyHorse 会丢掉非 iconic 的 transitional beat（如 sh_003 beat 4 "cleaved beast"）。实现见 `sub_agents/pipeline.py::_call_video_seedance`。
  - `inference/generation/video_generators/service.py` (`agents/` Director pipeline) — **默认 fal/Kling v3 Pro**，Hunyuan / Wavespeed 备用。由 `FW_VIDEO_BACKEND` env 切换：
  - `FW_VIDEO_BACKEND=fal`（**代码默认，env 不显式设时就是这条**）→ `FalVideoService`，model 从 `.env::FAL_VIDEO_MODEL` 读（当前 `fal-ai/kling-video/v3/pro/image-to-video`，支持 3/5/10/15 秒 clip）。
  - `FW_VIDEO_BACKEND=hunyuan` → `HunyuanVideoService`，POST 到 `http://<node>:<port>/i2v`，端点 URL 来自 `HUNYUAN_VIDEO_ENDPOINT_URL`。仅 eval baseline 脚本（`evals/sub-agents/run_hunyuan_baseline_naive*.py` / `run_e2e_30_hunyuan.py`）显式设这个值；production 不走这条。Hunyuan server 起 / 停 / 调用方法见 `HUNYUAN_HOW_TO_CALL.md`。注意 Hunyuan I2V 训练分布 cap 在 ≈5s（129 frames @ 24fps），10s/15s 不支持——只对它做对比时才会触到这个限制。
  - `FW_VIDEO_BACKEND=wavespeed` → `WavespeedVideoService` 备用通路。
  实现见 `inference/generation/video_generators/service.py`，由 `select_video_service()` 在 `FW_USE_REAL_MEDIA_GEN=1` 时根据 `FW_VIDEO_BACKEND` 选中对应 backend。Kling 允许 duration 取值 = `{3,5,10,15}`（v3 enum），`FalVideoService._kling_duration_enum` 按 model slug `/v3/` 还是 `/v2.6/` 在内部 snap 到对应集合。
- API 表和前端页面里关于模型的描述必须跟 `.env` + 代码实际使用的一致，不要写错。

## 给 AI 的工作提示

- 改代码前先 `Read` 目标文件 + 同目录测试，不要凭直觉。
- 新增能力时优先复用 `inference/` 已有 client / generator，不要自己起 HTTP 调用。
- 写新 agent 照抄 `agents/example_agent/` 结构。
- 不要为新模块写 README；要写"给 AI 看的局部说明"就放 `CLAUDE.md`。
- **讨论设计 / 重构问题时不要偏袒现有代码**。用户质疑一个写法时，先**诚实**评估他的质疑是否成立（通常成立），而不是反射性地为现状辩护。现有代码只是上一次决策的产物，不是真理；"现在就是这么写的"不构成"应该继续这么写"的理由。同样适用于现有文档 / 注释 / CLAUDE.md 自己 —— 如果发现 stale，就地修，不要装没看见。
