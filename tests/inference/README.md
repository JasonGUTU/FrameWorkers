# Inference live / smoke tests

## Kling + 横向合并 helper（可选冒烟）

`test_fal_kling_merged_keyframe_live.py` 在 **真实 fal.ai** 上验证 **`VideoMaterializer._merge_keyframe_images_for_video_api`**：两张任意 PNG → 横向 composite（含 Kling 宽高比 letterbox）→ 单张 conditioning → Kling。**默认 Video 管线不拼接多图**，该测试与主路径解耦。

**默认跳过**；需同时：

- `FW_ENABLE_FAL_VIDEO_MERGED_KEYFRAME_LIVE=1`
- `FAL_API_KEY` 已设置
- `FAL_VIDEO_MODEL` 已设置（通常与 `.env` 中 Kling 端点一致）

图源目录（PNG 可能在 `KeyFrameAgent/` 下，也可能在 **`KeyFrameAgent/image/`** —— 与 workspace 落盘一致；测试会先查根目录再查 `image/`）：

- 若设置了 `FW_MERGED_KEYFRAME_IMAGE_DIR`（相对仓库根），解析为该目录或（若 PNG 在子目录）其下的 `image/`。
- 否则若存在固定路径 `.../workspace_global_20260403_132858/.../KeyFrameAgent` 且（根或 `image/`）含所需 PNG，则用之。
- 否则在 `Runtime/live_e2e_outputs/workspace_*/artifacts/media/KeyFrameAgent` 中 **按路径名降序** 自动选**第一个**在根或 `image/` 下同时含有 `img_char_001_sc_001.png` 与 `img_loc_001_sc_001.png` 的目录。

`FAL_API_KEY` / `FAL_VIDEO_MODEL`：测试模块会调用 `ensure_fal_runtime_env_loaded()` 合并仓库根 `.env` / `.env.example`，一般无需在 shell 里手动 `export`（密钥仍须在 `.env` 中）。

运行（先 `conda activate frameworkers`，见根目录 `.cursorrules`）：

```bash
FW_ENABLE_FAL_VIDEO_MERGED_KEYFRAME_LIVE=1 \
  pytest tests/inference/test_fal_kling_merged_keyframe_live.py -v -s --tb=short
```

若找不到上述 PNG，测试会 **skip**。
