# Process Flow Visualizer

独立静态页：无表单。`app.js` 内置示例 **`POST /api/assistant/execute` 请求体**，页面直接展示 HTTP 响应示意及 **Assistant ↔ Sub-agent**、**Assistant ↔ Workspace** 的典型输入输出形状（`agent_id` → `asset_key` 映射写死在脚本内）。

不包含 Task Stack 的 `create task`、也不展示 `GET /api/assistant/executions/task/...`；若需完整 REST 契约见 `dynamic-task-stack/src/assistant/README.md`。

## Run

```bash
cd /home/zhendong_li/frameworkers/FrameWorkers/process-flow-visualizer
python3 -m http.server 3030
```

浏览器打开：`http://localhost:3030`

## 页面结构

1. **HTTP**：内置示例 execute 请求体与成功响应示意（`task_id`、`execution_id`、`status`、`results`、`error`、`workspace_id`）。
2. **Sub-agent 列**：进程内 `build_input` / `run` 约定 + 基于 `EXECUTE_EXAMPLE` 算出的 `typed_input_preview`；输出侧为返回给 Assistant 的字段说明 + 示例 `results`。
3. **Workspace 列**：读入侧为 `list_files` 查询参数与 `hydrate_indexed_assets` 前后 `assets` 键示意；写出侧为持久化步骤摘要与 `_asset_index` 副作用说明。

## 改动记录

- **2026-03-29**：收窄范围——去掉 Task Stack / GET executions 时序、步骤 1–6、retrieval 说明与协议大表；仅保留 execute HTTP 与 Sub-agent、Workspace 两列 I/O。
- **2026-03-29**：去掉表单中的 `descriptor_map` 与 `past_executions`，改用脚本内默认映射且不再模拟历史执行。
- **2026-03-29**：去掉可编辑请求体、字段说明与「刷新预览」；示例请求体固定在 `app.js` 的 `EXECUTE_EXAMPLE`。
- **2026-03-29**：顶部流程图改为单行四节点 + 三条水平连线（HTTP / in-process / I/O），去掉原「竖线 + 双列」结构，避免节点垂直错位与 Sub-agent—Workspace 缺线问题。
