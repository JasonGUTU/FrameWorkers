# KeyFrameAgent

## 输出结构 vs 出图范围

- **LLM / JSON**：`global_anchors` → 每场景 `stability_keyframes` → 每镜头 `keyframes[]`（每 shot **一行**：`prompt_summary`、`video_motion_hint`（L3）、`keyframe_id` 等）。`FW_ENABLE_PROP_KEYFRAMES=1` 时骨架可含 **props** 锚点文案。
- **持久化瘦身（不影响出图/出片）**：`StabilityAnchorKeyframe` 的 `purpose` / `display_name` 与 L3 `Keyframe.constraints_applied` 在 Pydantic 上标记 **`exclude=True`** — 仍可在进程内由 skeleton 赋值，仍可从**旧** workspace JSON 反序列化读入，但 **`model_dump` 写入 workspace 的 JSON 不再包含这些键**。`KeyframeMaterializer` 与 `VideoMaterializer` **从不读取**这些字段拼 API prompt，因此**不改变**最终图像/视频生成内容；仅影响落盘体积与依赖这些键的外部工具。
- **KeyframeMaterializer**：**L1** 全局 `img_{entity}_global`；**L2** 场景 `img_{entity}_{scene_id}`，实体为 **characters、locations、props**（props 与 char/loc 同一套 L1→L2 流程）。
- **L3**：每 shot **一张** 静帧 `img_{shot_id}_{keyframe_id}.png`（composition 已含人物/道具/环境）；默认 **edit**，参考优先为 **该场景 location 的 L2** 字节，否则 **t2i**。

## 与 Video 的结构解耦（L3）

- **`prompt_summary`（L3 shot keyframe）**：只服务 **图像** API（L3 edit/t2i）；描述 **单帧** 构图、光、主体、道具。
- **`video_motion_hint`（同一条 L3）**：只服务 **I2V** 文本前缀（`VideoMaterializer` 优先使用）；1–3 句 **可见的细微动势**（推轨、微动、环境动效等），**不要**复述整段静帧描述，**不要**写对白 / 配乐 / 剪辑节奏。
- **VideoMaterializer**：`clip_prompt` 仅在 `video_motion_hint` **非空**时加 I2V 前缀；**不**用 `prompt_summary` 顶替。非空时 clip 正文会省略 scene 的 environment/style/must_avoid 三行（与静帧 + motion 重复）。成片侧 `shot_segments[].video_generation_prompt` 与 `video_generation_constraints_json` 记录实际 API 输入。
- **L1 / L2**：仍仅 `prompt_summary`（无 `video_motion_hint`）。

## Video 如何用图

`VideoMaterializer` 对每个 shot **只加载上述 L3 文件**（第一条 keyframe 行、磁盘可读）；**一张** PNG；若 `video_motion_hint` 非空则前置为 I2V 文本，否则无前缀，仅 screenplay/scene 拼出的正文。**不**拼 L2 双图、**不**从 `stability_keyframes` 给 Video 回退。缺 L3 文件则跳过该镜头出片并打 error 日志。

## 出图 API 文案落盘

`KeyframeMaterializer` 在每次 **generate / edit** 调用前，把**完整**图像 API 字符串写入对应节点的 **`image_generation_prompt`**（含 materializer 追加的 style / must_avoid / L2 编辑前缀等）。用户参考图注入（L0）时写入说明性占位句，而非文生图 prompt。字段随 KeyFrame 执行结果的 workspace JSON 快照持久化。

## 环境变量

- **`FW_ENABLE_PROP_KEYFRAMES`**：默认 **`0`**。为 `1` 时骨架可含 props；**materializer 对 props 走与 char/loc 相同的 L1/L2 出图**（仍受模型与配额约束）。
- **`FW_ENABLE_PROP_PIPELINE`**：为 `1` 时 Video 的 screenplay 约束里会带上 `props_in_frame` 等；与 keyframe 出图范围无关。
- **`FW_KEYFRAME_L2_MODE`**：默认 **`edit`**。场景锚点（`img_{entity}_{scene_id}`）用 **全局锚点图 + `edit_image`**。设为 **`t2i`**（或 `generate` / `text2image` / `txt2img`）时改为 **纯文生图**（`generate_image`），不再参考 L1 图，指令跟随通常更好但与全局图的连续性较弱。

## KeyFrame LLM 文案策略（agent）

- **system / user prompt**（已相对历史版本 **压缩**）：`prompt_summary` 仅描述 **静态图像**；禁止声音、剪辑节奏、对白等；L2/L3 偏短、增量构图。分场景 user 中 **scene context** 为 `location_lock` / `character_locks` / `props_lock` / `style_lock` 的 **紧凑行摘要**（与整段 JSON 信息等价，**不**对 notes 条数做上限截断），不再嵌入完整 `consistency_pack` JSON，避免重复键名；上下文过长时由 LLM/API 报错暴露。
- **`_extract_style_section`** 将 screenplay 的 style 标为 **REFERENCE ONLY**：不再要求「每条 prompt_summary 必须以 style 段开头」，减少与 materializer 后缀的重复噪声。

## L1 / L2 提示词拼接（materializer）

- **全剧 style 合并**：`scene_consistency_pack.style_lock` 里跨场景收集的 `global_style_notes` / `must_avoid` 先做 **空白归一 + casefold 去重**（整句级，不截断字符串），再拼后缀，减轻多场景复制同一段 style 时的重复。
- **L1（全局锚点）**：`prompt_summary` + **`Visual style:`** + 过滤后的 **`Do NOT use:`**（文生图，无参考图，需要全局书面约束）。
- **L2（场景锚点，`edit`）**：较短 **编辑指令前缀** + `prompt_summary` + **仅** **`Do NOT use:`**（**不**再拼 `Visual style:`；参考图已带全场观感）。
- **L3（shot，`edit`，默认）**：与 L2 edit **同构**（前缀 + `prompt_summary` + `must_avoid` 后缀），参考为 **该场景 location 的 L2**；**不**在 L3 edit 上再叠整段 `Visual style:`。
- **L3（shot，`t2i` 回退）**：无可用 L2 location 参考时 `prompt_summary` + **完整** `Visual style` + `must_avoid`（与 L1 后缀同级），因无图可依。
- **`must_avoid` 过滤**：丢弃明显针对 **剪辑 / 声音 / 节奏** 等非静图条目。
