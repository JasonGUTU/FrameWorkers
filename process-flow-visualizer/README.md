# Process Flow Visualizer

独立静态页：无表单。`app.js` 内置示例 **`POST /api/assistant/execute` 请求体**，页面直接展示 HTTP 响应示意及 **Assistant ↔ Sub-agent**、**Assistant ↔ Workspace** 的典型输入输出形状（`agent_id` → `asset_key` 映射写死在脚本内）。

不包含 Task Stack 的 `create task`。`POST /execute` 成功体示意含 `global_memory_brief`、不含根级 `results`；完整子代理 dict 见 `GET /api/assistant/executions/task/...` 列表项的 `results`。完整 REST 契约见 `dynamic-task-stack/src/assistant/README.md`。

## Run

```bash
cd /home/zhendong_li/frameworkers/FrameWorkers/process-flow-visualizer
python3 -m http.server 3030
```

浏览器打开：`http://localhost:3030`

## 页面结构

1. **DirectorNoStack 编排循环**：3 个阶段 — Poll & Consume（轮询消息 + 标记已读 + 拉取 agents/memory）→ Merge Goal（LLM 合并历史上下文与新消息）→ Pipeline Loop（**每步一次路由 LLM**：choose_pipeline_step → execute_agent → 发回 chat 消息；路由不假设固定 pipeline 顺序，仅基于 goal + memory + execution 选择下一步或 done）。
2. **HTTP**：内置示例 execute 请求体与成功响应示意（`task_id`、`execution_id`、`status`、`error`、`error_reasoning`、`workspace_id`、`global_memory_brief`）。
3. **Sub-agent 列**：进程内 `build_input` / `run` 约定 + 基于 `EXECUTE_EXAMPLE` 算出的 `typed_input_preview`；输出侧仅 **`ExecutionResult`（`agents/base_agent.py`）字段说明**。`execution.results` / HTTP `results` 的 dict 形状见 **HTTP** 卡。
4. **Workspace 列**：**READ** 标题为 **数据流** `Workspace → Assistant`（副标题标明由 Assistant 发起调用）；**WRITE** 为 `Assistant → Workspace`。块内为典型 get/list 与 persist 步骤示意。

## 改动记录

- **2026-03-30（续 5）**：删除 **`get_task_file_tree_text`** / **`MemoryManager.file_tree_text_for_task`**；编排仅 **`get_workspace_root_file_tree_text`**。
- **2026-03-30（续 4）**：LLM #1 / #2 上下文仅保留 **`workspace_file_tree`**（全根树），移除 **`task_runtime_file_tree`** 注入；Workspace 卡 READ 改为 **`get_workspace_root_file_tree_text`** 说明。
- **2026-03-30（续 3）**：Execute 阶段补充 **dict → hydrate → InputBundleV2 → build_input → run**；Build Inputs 调整顺序并写明 **role**（memory 约定键 vs LLM #1 勾选）；Persist 显式 **LLM #3**；**task 文件树** 说明为编排事实、非 memory 配图；merge 说明主改 **relative_path**。
- **2026-03-30（续 2）**：`get_memory_brief` 的 returns 说明改为与后端一致：薄行仅四键，**无** `content`、**无** `artifact_locations`；并注明 execute 用 `list_memory_entries`。
- **2026-03-30（续）**：Workspace READ 中 `list_memory_entries` 的说明改为「供输入打包 LLM（选 `selected_roles`）」；与后端默认 **`ASSISTANT_GLOBAL_MEMORY_CONTEXT_ENTRIES_MAX=20`** 表述一致（仍以仓库为准）。
- **2026-03-30**：Build Inputs 卡第一步改为 `list_memory_entries`（execute 真实路径）；LLM `chat_json` 的 `max_tokens` 与编排侧 **LLM #1 / #2 / #3** 编号与 `service.py` 对齐；Persist 卡补充 **LLM #3** 摘要再 `add_memory_entry`；`package_data` 与测试说明去掉已删除的 `FrozenInputBundleV2`，改为 **`InputBundleV2`** 与「约定不原地修改」。
- **2026-03-29**：`global_memory_brief` 示例行去掉 `artifact_locations`（与 `get_memory_brief` 四键薄行一致）。
- **2026-03-29**：HTTP 成功示意增加 `error_reasoning`（占位 `null`），与 `POST /execute` 契约一致。
- **2026-03-29**：HTTP 成功响应示意改为 `global_memory_brief`、去掉根级 `results`（与 `process_results` 一致）；文档说明 executions API 承载整包 `results`。
- **2026-03-29**：新增 DirectorNoStack 编排循环卡（3 阶段：Poll & Consume → Merge Goal → Pipeline Loop）；顶部流程图增加 Chat 节点和 Director ↔ Chat 的 poll/reply 箭头。

- **2026-03-29**：Workspace READ 中区分 `get_memory_brief`（Director / HTTP brief）与 `list_memory_entries`（execute 内 `build_execution_inputs`）。
- **2026-03-29**：Workspace 卡 READ/WRITE 标题改为**数据流方向**（`Workspace → Assistant` / `Assistant → Workspace`），避免将「Assistant 调 Workspace 读」误解为数据指向 Workspace。
- **2026-03-29**：Sub-agent 输出列仅保留 `ExecutionResult` 字段说明；HTTP `results` 保留完整 dict 示意（含 `_persist_plan_meta`、`_asset_index`）；去掉杜撰的 `produced_by` / `asset_key`。
- **2026-03-29**：收窄范围——去掉 Task Stack / GET executions 时序、步骤 1–6、retrieval 说明与协议大表；仅保留 execute HTTP 与 Sub-agent、Workspace 两列 I/O。
- **2026-03-29**：去掉表单中的 `descriptor_map` 与 `past_executions`，改用脚本内默认映射且不再模拟历史执行。
- **2026-03-29**：去掉可编辑请求体、字段说明与「刷新预览」；示例请求体固定在 `app.js` 的 `EXECUTE_EXAMPLE`。
- **2026-03-29**：顶部流程图改为单行四节点 + 三条水平连线（HTTP / in-process / I/O），去掉原「竖线 + 双列」结构，避免节点垂直错位与 Sub-agent—Workspace 缺线问题。
