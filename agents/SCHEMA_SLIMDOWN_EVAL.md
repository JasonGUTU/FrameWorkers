# Schema 瘦身评估（Story / KeyFrame / Video / Audio）

在**不削弱现有管线功能**的前提下，评估各 Agent 输出 schema 中哪些块是**执行关键路径**、哪些是**叙事/审计冗余**，以及若删减字段时的风险与推荐顺序。

**结论摘要**

| Agent | Schema 体量主要来源 | 是否适合「砍字段」 | 更稳妥的降载手段 |
|-------|---------------------|-------------------|------------------|
| Story | 曾易全文进入 Screenplay creative prompt | 中等 | **已**：ScreenplayAgent 仅向该次 LLM 嵌入 **字段子集**（`_story_content_embed_for_creative_llm`）；workspace 仍为完整 blueprint |
| KeyFrame | `prompt_summary` + L3 `video_motion_hint` | 低（删字段易丢条件） | 缩短两字段、剥离元数据 |
| Video | 已基本为结构骨架（无 LLM 创意 JSON） | 低 | 仅当合并场景/片段模型时再动 |
| Audio | 旁白与剧本对齐；LLM 只补 mood / ambience | 低 | 限制 `music_cue.mood`、`ambience_bed.description` 长度 |

---

## 1. StoryAgent（`story/schema.py`）

### 1.1 执行上**确实用到**的字段

- **`build_skeleton`（Screenplay）**只读：`story_blueprint` 里的 `scene_outline[]`、`locations[]`（至少 `location_id` + `name`）、根上 `estimated_duration`（若存在则定 `target_duration_sec`）。见 [`screenplay/agent.py`](screenplay/agent.py) `build_skeleton`。
- **Evaluator L1**：`cast`、`story_arc`、`scene_outline` 非空与顺序、`character_id` 与 outline 引用一致等。见 [`story/evaluator.py`](story/evaluator.py)。

### 1.2 大 token / 长文但**不进入 skeleton** 的部分

- **Screenplay** `build_creative_prompt` 对 story `content` 调用 **`_story_content_embed_for_creative_llm`** 后再 `json.dumps`：长叙事键（`cast` 的 profile/motivation/flaw、`locations[].description`、arc 的 conflict/turning_point、scene_outline 的 goal/conflict/turn）**不进入**该次 LLM user；logline、style、精简 cast/locations/arc/summary、outline 网格仍会进入。Workspace 内完整 blueprint 不变。
- 这些字段**不**被 KeyFrame / Video 的 Python 代码直接按字段名读取，但通过 **Screenplay 生成结果**间接影响全场。

### 1.3 瘦身方向（保持功能）

1. **契约分层（已按此思路落地在 ScreenplayAgent）**  
   - 嵌入 LLM 的对象即上述字段子集（**整键省略**，非字符串切片），实现见 **`ScreenplayAgent._story_content_embed_for_creative_llm`**。  
   - 完整 story 仍在 workspace；若产品上要 screenplay LLM **看到**全文人物小传，应改为嵌入完整 `content`（并接受该步上下文变大），而不是在子集里做切片。

2. **仅 policy、不改 schema**  
   - 在 Story agent 的 system prompt 中要求各创意字段**短句上限**（与 evaluator 长度检查配合），不改变 Pydantic 形状。

### 1.4 若直接删 Pydantic 字段

- 必须同步：`story/agent.py` 模板与说明、`story/evaluator.py`、Screenplay 对 blueprint 的假设、Director / 任何持久化 story 的客户端、测试与 README。

---

## 2. KeyFrameAgent（`keyframe/schema.py`）

### 2.1 执行关键路径

- **`prompt_summary`**（全局 / 场景稳定性 / shot L3）：进入 **图像 API**。L3 另设 **`video_motion_hint`** 专供 **I2V** 文本前缀；缺省时 Video **不**把 `prompt_summary` 当前缀。
- **`image_asset.uri`**（materialize 后）：下游 Video 只认 **L3 本地 PNG**。
- **ID 与层级结构**：`entity_id`、`scene_id`、`shot_id`、`keyframe_id`；evaluator 与 manifest 依赖一致性与计数。

### 2.2 偏低风险「可讨论删减」的字段

- **`StabilityAnchorKeyframe.purpose`**、**`display_name`**：由 [`keyframe/agent.py`](keyframe/agent.py) 填写的说明性字段；**materializer 未读取**（检索 `materializer.py` 无引用）。可用于 UI/日志；删除不改变当前出图/出片逻辑，但可能破坏依赖这些键的外部工具。
- **`Keyframe.constraints_applied`**：同样**未**在 materializer 中消费；偏审计/调试。

### 2.3 瘦身方向（保持功能）

- **缩短 `prompt_summary` + `video_motion_hint`**（模板 + evaluator），而不是删除字段。
- 元数据字段可标为 **optional** 或挪到 `meta`/`_debug` 扩展对象，主 schema 只保留「图 + 短摘要 + ID」。

---

## 3. VideoAgent（`video/schema.py`）

### 3.1 现状

- **LLM-free**：输出由 [`video/agent.py`](video/agent.py) 从 **screenplay** 确定性生成；schema **无创意长文字段**。
- **Materializer** 使用：`scenes[].shot_segments[]`（`shot_id`、`estimated_duration_sec`、`video_asset`）、`transition_plan`、`scene_clip_asset`、`final_video_asset`。

### 3.2 瘦身空间

- **很小**。进一步合并（例如去掉 `TransitionPlan`、内嵌默认 cut）会触及 **assemble_scene** 与 evaluator 的假设。
- 若未来「仅单段成片」模式，才可考虑更扁的 schema；当前不建议为降字数改 Video JSON。

---

## 4. AudioAgent（`audio/schema.py`）

### 4.1 执行关键路径

- **旁白**：`NarrationSegment.text` / `speaker` / 时间戳来自 **screenplay + video** 骨架（[`audio/agent.py`](audio/agent.py)）；与对白长度一致，**不能**在 Audio schema 里无故截断而不改剧本策略。
- **LLM 仅填充**：每场景 **`music_cue.mood`**、**`ambience_bed.description`**（文档与代码一致）。
- **Materializer** 消费：`narration_segments`、`music_cue`、`ambience_bed`、各级 `audio_asset`、`final_audio_asset`、`final_delivery_asset`。

### 4.2 瘦身方向（保持功能）

- **不在** evaluator / prompt 里做人工字符上限来「假装」控制 token；过长由 **TTS/音乐生成 API** 失败暴露，便于调模型或拆场景。
- `AudioAgentInput.constraints: dict` 已较松；若收紧为 `AudioConstraints` 模型，属于类型清晰化而非「变短」。

---

## 5. 跨模块依赖（改 schema 前必查）

- **Screenplay**：统一承载 shots + `scene_consistency_pack` + `keyframe_plan`；KeyFrame / Video / Audio 均依赖其 JSON 形状。
- **Assistant / workspace**：持久化的是各 agent 的**完整 JSON**；删字段需考虑旧 workspace 兼容或迁移。
- **Director**：若读取 task 描述或 memory 中的 artifact 摘要，需确认不依赖将被删除的字段。

---

## 6. 推荐落地顺序（与「只评估、慎改代码」对齐）

1. **Story → Screenplay（已落地）**：**ScreenplayAgent** `_story_content_embed_for_creative_llm` 仅用于 **`build_creative_prompt`** 内嵌 JSON（整键省略，非切片）；**workspace 内 `story_blueprint` 仍为完整 StoryAgent 输出**，`build_skeleton` 仍读完整 `resolved_inputs`。未改 Story Pydantic 形状。  
2. **KeyFrame（已部分落地）**：`purpose` / `display_name` / L3 `constraints_applied` 使用 Pydantic **`Field(..., exclude=True)`**，不再进入 `model_dump` 落盘 JSON；**不参与**图像/视频 API prompt 组装，**不改变**生成结果。未引入单独 `_debug` 顶层块（避免双写）；若需给人看的审计包可另开导出。  
3. **Audio**：不在 L1 做人工字符上限（避免掩盖下游 TTS/音乐 API 的真实长度/ token 错误）；超长由 **调用失败** 暴露。  
4. **Video**：无需求则不动。

本文档随架构决策更新；**实际删 Pydantic 字段**须在上述包内 README 与 `.cursorrules` 映射中同步说明。
