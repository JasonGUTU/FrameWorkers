# Director (no Task Stack)

独立编排进程：**不调用** Task Stack（无 `task-stack`、`execution-pointer`、`tasks/*`）。输入来自与 Vue `ChatWindow` 相同的 **`/api/messages/unread`**（用户发送的消息）；输出通过 **`POST /api/messages/create`**（`sender_type: director`）回到聊天列表。

执行仍走 **`POST /api/assistant/execute`**。所有次执行共用同一逻辑任务 id：**`DIRECTOR_STANDALONE_TASK_ID`**（默认 `standalone_chat`），以便 **global_memory** 与 **executions** 在同一任务维度下累积。

### 用户消息 `content`（无 `goal` 特判）

- **字符串**：strip 后作为本轮用户原文种子。  
- **`dict` / `list`**：整段 **`json.dumps`** 成一条文本，**不**再单独读 `goal` 等字段；结构化意图交给 **`merge_session_goal`**（LLM）去理解。

### Assistant `execute` 回到 Director 的是什么（2026-03 起无根级 `results`）

- **传输方式**：`director_nostack` 调用 **`POST /api/assistant/execute`**（见 `NoStackAPIClient.execute_agent`）；Flask 路由在 `dynamic-task-stack/src/assistant/routes.py` 里对成功响应 **`jsonify(serialize_response_value(results)), 200`**。  
- **成功时（HTTP 200）的 JSON 体**：与后端 **`AssistantService.process_results`** 一致，**不含**子代理整包 **`results`**（过大且与 executions 重复）；固定键为 **`task_id`**、**`execution_id`**、**`status`**、**`error`**、**`error_reasoning`**（预留更长失败说明，当前多为 **`null`**）、**`workspace_id`**、**`global_memory_brief`**。  
  - **`global_memory_brief`**：与 **`GET /api/assistant/workspace/memory/brief?task_id=...`** 同形 **`{"global_memory": [...]}`**；每行**仅** **`task_id`**、**`agent_id`**、**`created_at`**、**`execution_result`**（**无** **`content`** / **`artifact_locations`** 等；路径仍在服务端 full memory / 文件树侧）。  
  - 需要完整子代理产出时：用 **`GET /api/assistant/executions/task/{task_id}`** 取最新一条的 **`results`**。  
- **失败时**：请求体不合法、`execute_fields` 违反规则、或执行期异常等 → **4xx/5xx**，body 多为 **`{"error": "..."}`**；与成功体**不同**。  
- **Director 怎么用**：用 **`status` / `error` / `global_memory_brief`** 拼聊天步骤预览；**下一步 sub-agent** 仍由刷新后的 **`memory/brief`** + **`executions`** + **`choose_pipeline_step`** 决定（与是否内联 `results` 无关）。

**编排中枢在** ``director.py``：类 ``DirectorNoStack``（轮询 + 前端读写）与函数 ``run_nostack_pipeline``（单条用户消息内的合并、逐步路由、Assistant 执行、Director 发帖）。  
每条未读聊天行先作为 **``latest_user_message``**。合并时除 **global_memory**、**最近 execution** 外，还会通过 **`GET /api/messages/list`** 取 **更早的用户聊天原文**（按 ``id`` 排除当前这条，按时间排序，条数上限见 ``DIRECTOR_MERGE_PRIOR_USER_LINES_MAX``），一并交给 **`merge_session_goal``** 压成 **一条**说明字符串，供**整轮**路由与 ``execute_fields.text``。若既无更早用户行、也无 memory、也无 executions，则合并退化为原文（不调合并 LLM）。**合并 LLM 的 system 提示**会要求先判断新一句与历史的关系再写 **`merged_goal`**：**补充**（在旧需求上叠加）、**修正**（局部覆盖）、**推翻/全新**（以最新为主、丢弃被否定的旧用户要求，但仍尊重 memory 里已落盘且用户未要求废弃的事实）、**重述**（同义整理）；语义不清时**默认按补充**处理；**prompt 内写明** prior 段 **由旧到新**（编号 1 最旧、末条为当前轮之前最近一句）、**Latest** 为**最新一轮**。**不**向路由单独传「复用说明」——只决定下一个 **``agent_id``** 或 **done**。路由布尔 **``after_frontend_user_message``**：**仅本 run 第一步**为真；同一条消息内续步为假；用户再发下一条 → 新 run → 第一步再为真。

## 依赖

- 与仓库其余 Python 包一致：使用**根目录**合并后的 **`requirements.txt`**（由 `install_requirements.py` 汇总各子包生成）。本包提供 **`director_nostack/requirements.txt`**（`litellm`、`requests` 等声明），参与合并，确保安装一键环境时包含路由/合并所需的 LiteLLM。包入口 **`director_nostack/__init__.py`** 导出 **`DirectorNoStack`**、**`run_nostack_pipeline`**、**`NoStackAPIClient`** 等（便于嵌入或 REPL）。
- 路由使用 **`inference`** 的 `LLMClient`（LiteLLM），需在 repo 根运行并设置 **`PYTHONPATH=.`**。
- **`prompts.py`**：合并 / 路由的 **system 文案** 与 **user 消息拼装**（与调用逻辑分离）。
- **`LlmSubAgentPlanner`** 在 **`router.py`**（**不** `import director_agent`）：**`merge_session_goal`**、**`choose_pipeline_step`**（内部读 `prompts`）。带 Task Stack 的选路在 **`director_agent/reasoning.py`**。

## 运行

```bash
cd /path/to/FrameWorkers
export PYTHONPATH=.
python -m director_nostack.main
# 或
python director_nostack/run.py
```

环境变量（可选）：

| 变量 | 默认 | 说明 |
|------|------|------|
| `BACKEND_BASE_URL` | `http://localhost:5002` | Flask 后端 |
| `POLLING_INTERVAL` | `2.0` | 轮询秒数 |
| `DIRECTOR_STANDALONE_TASK_ID` | `standalone_chat` | 传给 Assistant 的 `task_id` |
| `DIRECTOR_ROUTING_MODEL` | 见 `config` | 路由 LLM（含 `choose_pipeline_step` / `merge_session_goal`） |
| `DIRECTOR_MERGE_PRIOR_USER_LINES_MAX` | `10` | 合并时最多带入多少条**更早**的用户聊天原文（来自 `/api/messages/list`）；与路由 memory 行数一起控制上下文 |
| `DIRECTOR_ROUTING_MEMORY_ROWS_MAX` | `10` | 路由/合并 prompt 里注入的 **global_memory** 行数（**最近** N 条） |
| `DIRECTOR_ROUTING_MEMORY_JSON_MAX_CHARS` | `200000` | 将 memory 序列化进 prompt 时的最大字符数（防极端 payload） |
| `DIRECTOR_ROUTING_CHAT_JSON_MAX_TOKENS` | `32768` | `merge_session_goal` / `choose_pipeline_step` 调用 **`chat_json`** 的 completion 上限（提供商仍要求有上限） |
| `LOG_LEVEL` | `INFO` | 日志级别 |

## 行为说明（单条用户消息内的「自动多步」）

**一条**用户聊天消息会触发 **内层流水线循环**（仍无 Task Stack）：

0. **一次**（进入循环前）：读 **`memory/brief`**、**最新 execution**、以及 **`/api/messages/list`** 中的**更早用户消息**（排除当前 ``id``）；若任一有内容，则 **`merge_session_goal`** 生成合并说明，否则合并结果即 **本条聊天原文**。
1. 每轮再次刷新 **`memory/brief`** 与 **最新 execution 摘要**，调用 **`choose_pipeline_step`**；仅 **第一步** 传 **`after_frontend_user_message=True`**（刚从前端读到本条未读消息），续步为 **`False`**（前端尚未再发消息）。
2. 路由 LLM 返回 **JSON**（只选下一步 agent 或 done，不负责「复用清单」）：  
   - **`{"action":"run","agent_id":"...","rationale":"..."}`** → 对该 agent 调用一次 **`POST /api/assistant/execute`**（`execute_fields.text` 为**本轮合并后的说明**；下游输入主要由 Assistant 从 memory / resolved_inputs 装配）。  
   - **`{"action":"done","rationale":"..."}`** → 认为用户目标已达成，**结束**本消息对应的流水线，并往聊天里发一条 **Pipeline complete**。
3. 任一步 **`execute` 抛错**、HTTP 返回 **`FAILED` / `error`**，或路由返回非法结构 → **中止**循环并发帖说明。

**`done` 如何判断（无独立代码验收）：** 只有路由 LLM 在 **`choose_pipeline_step`** 里返回 **`{"action":"done",...}`** 时，本 run 才结束；``run_nostack_pipeline`` / ``router`` 把该 JSON 解析为 **`PipelineRouteDecision.finished is True`** 并发 **Pipeline complete**。是否「目标已满足」完全由模型根据 **合并后的 user goal、global_memory、最新 execution 摘要** 自行判断，**没有**单独的规则引擎或步数上限。

**路由策略（避免“固定流水线”偏置）：** `choose_pipeline_step` 的 system prompt **不再**提示 `story → screenplay → storyboard → …` 这类默认顺序；路由仅根据 **用户目标** 与 **当前 global_memory / 最新 execution 摘要**，从 **allowed agent_id 列表**中选择下一步，或返回 `done`。

**第一次选 sub-agent**：通常 `global_memory` 空、`execution_summary` 为 null，路由根据 **用户目标 + 目录** 选第一个 `run`。

**同一条消息内「再选」**：每跑完一步，下一轮路由会看到 **更新后的 memory 与最后一次 execution**，可继续 `run` 下一个 agent，直到 `done`。

**用户发第二条、第三条消息**：每条新消息各自 **重新**从步骤 1 开始一轮新流水线（共享同一 `task_id`，故 memory / executions 会累积，路由能看到历史）。

## 流程（简）

1. `GET /api/messages/unread?sender_type=user&check_director_read=true`
2. 取最早一条未读用户消息 → `PUT .../read-status`
3. **循环**（直到路由 `done` 或错误）：  
   `sub-agents` + `memory/brief` + `executions/task/...` → **`choose_pipeline_step`** → `run` 则 **`POST /execute`** 并 `POST /messages/create`（director 步骤小结）；`done` 则结束。

## 与 `director_agent` 的差异

| | `director_agent` | `director_nostack` |
|--|------------------|---------------------|
| Task Stack | 使用 | **不使用** |
| 用户输入 | 未读消息 + 任务描述 | **仅**未读聊天消息 |
| `task_id` | 来自栈上任务 | **固定**环境变量 |
| 指针 / 任务状态 API | 使用 | **不使用** |
| 单条用户消息 | 通常一步 + 指针推进 | **内层多步**（路由 `run`/`done`，无步数上限） |

## 测试

仓库内单元测试：`tests/director_nostack/test_director_nostack_unit.py`（Mock HTTP 客户端与 router，不启动后端）。

```bash
PYTHONPATH=. python -m pytest tests/director_nostack/test_director_nostack_unit.py -q
```

**HTTP 端到端（无真实端口）**：`tests/director_nostack/test_director_nostack_http_e2e.py` 用 Flask `test_client` 走与前端相同的消息路由（`POST /api/messages/create` → 未读消费 → `POST /api/assistant/execute`），**路由 LLM 用 Mock**，Assistant 使用测试里注册的桩 sub-agent；用例里的用户文案为**可读的产品向 brief**（例如约 10 秒短片 + 具体故事/情绪与场景）。共享桩与路径在 `tests/director_nostack/conftest.py`。

```bash
PYTHONPATH=. python -m pytest tests/director_nostack/test_director_nostack_http_e2e.py -q
```

**模拟真实前端 + 已启动的后端**：`director_nostack/simulate_frontend.py` 向 `BACKEND_BASE_URL` 发一条用户聊天，并可选地执行**一次** `DirectorNoStack._cycle()`（需配置推理 / 路由模型；若只排队消息可 `--post-only`）。

```bash
cd /path/to/FrameWorkers
export PYTHONPATH=.
# 终端 A：python dynamic-task-stack/run.py
# 终端 B：
python -m director_nostack.simulate_frontend "Short task for the pipeline."
# 仅写入用户消息、不跑本进程内的 Director：
python -m director_nostack.simulate_frontend --post-only "Queued for separate director process."
```

**Live E2E（真实路由 LLM + 可选真实 sub-agent）**：`tests/director_nostack/test_director_nostack_live_e2e.py`，opt-in：`FW_ENABLE_NOSTACK_LIVE_E2E=1`、`FW_ENABLE_LIVE_LLM_TESTS=1`。  
- **桩目录**：默认仅注册 `NostackE2eAgent`（`conftest`），不跑生产媒体。  
- **真实 sub-agent**：`FW_ENABLE_NOSTACK_REAL_AGENTS=1`，使用仓库 `agents/` 注册表；`FW_NOSTACK_REAL_AGENT_IDS` 为逗号列表则只暴露这些 id 给路由；设为 **`*` / `ALL` / `all`** 则**不过滤**，路由可见完整目录（可能从 Story 一路跑到 Video，**耗时长、费用高**）。未设置该变量时测试默认仍只暴露 `StoryAgent`（见用例内默认值）。  
- 可选 **`FW_NOSTACK_EXPECT_VIDEO=1`**：断言执行链中出现至少一次 **`VideoAgent`**（用于验证「文本→视频」意图）。  

## 改动记录

- **2026-03-30**：路由上下文：**merge** 默认更早用户行 **10** 条（`DIRECTOR_MERGE_PRIOR_USER_LINES_MAX`）；**global_memory** 注入 **最近 10 行**（`DIRECTOR_ROUTING_MEMORY_ROWS_MAX`）；**`chat_json`** completion 默认 **32768**（`DIRECTOR_ROUTING_CHAT_JSON_MAX_TOKENS`）。小上下文 + 大 completion 上限，避免靠压 `max_tokens` 硬扛长 history。
- **2026-03-30**：**`router.LlmSubAgentPlanner`** 的 **`merge_session_goal`** 与 **`choose_pipeline_step`** 改为调用 **`LLMClient.chat_json`**（provider **JSON mode**），不再用 **`chat_text` + 手工 `json.loads`**，避免路由/合并模型输出**截断或非纯 JSON** 导致解析失败。
- **2026-03-30**：**`tests/director_nostack/conftest.py`** 增加 **`_nostack_http_e2e_ignore_shell_real_agents`**（先于 Assistant LLM 桩 fixture）：在 **`test_director_nostack_http_e2e.py`** 内强制 **`FW_ENABLE_NOSTACK_REAL_AGENTS=0`**，避免 shell 里开 **真实** 注册表时 HTTP 端到端仍期望 **`NostackE2eAgent`** 桩却拿不到 LLM 桩、执行 500。
- **2026-03-30**：**`router._parse_router_json`** 与 **`director_agent/reasoning.py`** 对齐：仅对整段 strip 后 **`json.loads`**，非法 JSON 抛 **`ValueError`**（不静默从 markdown 中抠 JSON）。**`merge_session_goal`** 在 LLM/解析失败时仍回退到最近用户行（**`logger.error`**）；若 JSON 合法但 **`merged_goal`** 缺失/类型不对/去空白后为空，回退到最近用户行并 **`logger.warning`**（可审计）。
- **2026-03-30**：新增 **`director_nostack/requirements.txt`**（并入根目录合并依赖，含 **`litellm`**）。
- **2026-03-30**：HTTP E2E 用例中用户 **`content` / `merge_session_goal` / `execute_fields.text`** 改为**约 10 秒视频 + 叙事**的完整英文 brief（更易读、贴近真实聊天输入）。
- **2026-03-30**：新增 **`tests/director_nostack/test_director_nostack_http_e2e.py`**（Flask test_client 模拟前端发消息 + Director 一轮循环）与 **`director_nostack/simulate_frontend.py`**（对运行中后端 POST 用户消息并可选单次 `_cycle`）；**`tests/director_nostack/conftest.py`** 提供 Assistant LLM 桩与 E2E 用 sub-agent 注册表。
- **2026-03-29**：**`memory/brief`** / **`global_memory_brief`** 行仅 **`task_id` · `agent_id` · `created_at` · `execution_result`**（去掉 **`artifact_locations`**）；`prompts` 已注明 slim 行。
- **2026-03-29**：与后端对齐：成功体增加 **`error_reasoning`**（预留，多为 **`null`**）；同路由错误 JSON 含 **`error`** + **`error_reasoning`**。
- **2026-03-29**：与后端对齐：`POST /api/assistant/execute` 成功体含 **`global_memory_brief`**、**不含**根级 **`results`**；聊天预览改为展示 brief 行；完整产出走 **`GET .../executions/task/...`**。
- **2026-03-29**：无 Task Stack 初版与后续收敛：编排集中在 **`director.py`**（**`DirectorNoStack`**、**`run_nostack_pipeline`**、**`orchestrate_user_turn`**）；**`router.LlmSubAgentPlanner`**（**`merge_session_goal`** / **`choose_pipeline_step`**，`action: run|done`，无步数上限）；**`prompts.py`**；依赖根目录 **`requirements.txt`**；**`tests/director_nostack/`**。
- **2026-03-29**：**`chat_content_as_user_text`**：结构化 `content` 整段 **`json.dumps`**，不设 **`goal`** 等字段特判；**`api_client.execute_agent`** 与上文「Assistant `execute` 回到 Director」写明 HTTP JSON 契约。
- **2026-03-29**：合并与路由 UX：**更早用户行**（`/api/messages/list` 排除当前 id）+ memory + execution → **`merge_session_goal`**；**`after_frontend_user_message`** 仅本 run 第一步为真；**`router`** 去 Task Stack 专用分支与重复拼装。
