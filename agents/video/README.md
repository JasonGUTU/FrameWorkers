# Video agent — materializer & I2V prompting

## Video backend (`FW_VIDEO_BACKEND`)

- **`fal`**（默认）：`FalVideoService`，环境变量见根目录 `.env.example`（`FAL_API_KEY`、`FAL_VIDEO_MODEL` 等）。
- **`wavespeed`**：设置 **`FW_VIDEO_BACKEND=wavespeed`** 时使用 `WavespeedVideoService`（`WAVESPEED_API_KEY` 必填；可选 `WAVESPEED_VIDEO_PROVIDER`、`WAVESPEED_VIDEO_T2V_MODEL`、`WAVESPEED_VIDEO_I2V_MODEL`、`WAVESPEED_VIDEO_ASPECT_RATIO`）。与仓库内 UniVA MCP 工具共用 WaveSpeed HTTP API 形态；实现 lives in `inference/generation/`（不依赖 `univa/` 包导入）。

自检脚本：`scripts/wavespeed_text_to_video_smoke.py`（扣费）。详见 `inference/README.md`（UniVA / WaveSpeed 分层说明）。

## Clip prompt (`VideoMaterializer`)

- Loads **one** on-disk L3 keyframe PNG per shot (first loadable row in `keyframes` JSON). No L2 fallback.
- **`clip_prompt`** body is built from screenplay shot metadata (`_build_clip_prompt`): shot id, visual goal, action, characters, scene context (location / time), camera, framing, anchor count, task focus.
- **I2V prefix**: only when **`video_motion_hint`** on that keyframe row is non-empty — it is prepended as `{motion} | {body}`. **`prompt_summary` is never used as a substitute** for an empty motion hint.
- When the motion hint is **non-empty**, the clip body **omits** the three “tone” lines (scene environment notes, style notes, must avoid) to avoid duplicating what the still + motion already convey; uses a shorter ref line and **drops** the trailing duplicate “Task focus” line (action is already in “Action focus”).
- When **`video_motion_hint` is empty**, there is **no** motion prefix; the full body including those tone lines is kept.
- Structured constraints passed to the video backend include `keyframe_prompt_summaries` and `keyframe_video_motion_hints` (parallel to the loaded row).
- After materialization, each `shot_segments[]` row gets **`video_generation_prompt`** (the `clip_prompt` passed to `generate_clip`) and **`video_generation_constraints_json`** (JSON text of `consistency_constraints`, empty object omitted).

## Related docs

- Keyframe field semantics: `agents/keyframe/README.md`
- Cross-agent overview: `agents/README.md`
