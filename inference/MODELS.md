# Supported Models

This file documents the model ids FrameWorkers actually calls at runtime.
Provider resolution consults ``inference_runtime.yaml``'s ``model_provider``
block first; the built-in table in ``inference/config/model_config.py`` is
the fallback when the runtime routing file doesn't cover a model.

Project-wide model policy lives in the root ``CLAUDE.md`` (short version:
**Gemini for LLM, OpenRouter / Gemini-Image for images, Kling for video,
Minimax for TTS**; flux is explicitly banned).

## LLM (Gemini default + GPT-5 opt-in)

| Model ID | Used by | Notes |
|----------|---------|-------|
| `gemini-2.5-flash` | All sub-agents + Director | Default via ``INFERENCE_DEFAULT_MODEL``. Routed through Cloudflare AI Gateway's native-Gemini Worker (`google_genai` client_type using the `google.genai` SDK). |
| `gpt-5` / `gpt-5-mini` | Opt-in per caller | GPT-5 chat completion uses `max_completion_tokens` + `reasoning_effort`; handled by `_build_openai_chat_kwargs`. |
| `gpt-4o` / `gpt-4o-mini` | Reserved | Listed in the built-in provider table for drop-in use. |

The four transport paths inside `LLMClient`:

- **`openai_sdk`** (default for OpenAI) —
  talks to `AsyncOpenAI.chat.completions.create`.
- **`gpt5_sdk`** — same transport as `openai_sdk` but flips on `reasoning_effort`
  and the `max_completion_tokens` param name.
- **`google_genai`** (default for Gemini via CF AI Gateway native-Gemini
  Worker) — talks to `google.genai.Client.aio.models.generate_content` with
  a custom `http_options.base_url`.
- **`litellm`** — fallback when the resolved provider doesn't match any
  of the above.

## Media generation (via `inference/generation`)

| Kind | Default mock | Real backend | Model env var |
|------|--------------|--------------|---------------|
| Image | `MockImageService` (1×1 placeholder PNG) | `FalImageService` via fal.ai, or `ImageService` via OpenRouter | `FAL_IMAGE_MODEL` (e.g. `fal-ai/nano-banana-2`) / `INFERENCE_IMAGE_MODEL` (e.g. `google/gemini-2.5-flash-image`) |
| Video | `MockVideoService` (placeholder MP4 header) | `FalVideoService` with Kling | `FAL_VIDEO_MODEL=fal-ai/kling-video/v2.6/pro/image-to-video` |
| TTS | `MockAudioService` | `FalAudioService` | `FAL_TTS_MODEL=fal-ai/minimax/speech-02-turbo` |
| STT | `MockTranscriptionService` | `FalTranscriptionService` | `FAL_WHISPER_MODEL` |
| Music / ambience | `MockAudioService` (silent WAV) | `FalAudioService` | `FAL_MUSIC_MODEL` / `FAL_AMBIENCE_MODEL` |
| Compositor | `MockCompositorService` | `CompositorService` (ffmpeg-local) | — |
| Video edit | `MockVideoEditService` | `FalVideoEditService` | `FAL_VIDEO_STYLE_MODEL` / `FAL_VIDEO_INPAINT_MODEL` / `FAL_DEPTH_MODEL` / `FAL_SAM_MODEL` |

Real backends are selected per call by `select_*_service()` in
`inference/generation/__init__.py`. Default is mock; set
`FW_USE_REAL_MEDIA_GEN=1` to opt into real providers. For video, an
alternative `WavespeedVideoService` exists and is selected via
`FW_VIDEO_BACKEND=wavespeed`, but CLAUDE.md currently standardises on Kling.

## Using an LLM

```python
from inference import LLMClient

client = LLMClient()  # picks up INFERENCE_DEFAULT_MODEL from .env

result = await client.chat_json(
    system_prompt="You are a strict JSON generator.",
    user_prompt="Return {\"ok\": true}.",
)

text = await client.chat_text(
    system_prompt="Summarize in one sentence.",
    user_prompt="The quick brown fox jumps over the lazy dog.",
)
```

Multimodal (image / audio / video) goes through the same `chat_json` /
`chat_text` API via `media_attachments`:

```python
result = await client.chat_json(
    system_prompt="Describe the attached image.",
    user_prompt="What do you see?",
    media_attachments=[{"type": "image", "path": "/abs/path/shot.png"}],
)
```

See `_build_multimodal_user_content` in
`inference/clients/implementations/default_client.py` for the supported
MIME + size caps (inline video capped at ~20 MB — Gemini's limit).

## Configuring a provider

- **Environment variables** drive API keys and base URLs by default
  (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, and so on — overridable in
  `inference_runtime.yaml` under `provider_key_env`).
- **`inference_runtime.yaml`** is the canonical routing file. It declares
  `model_provider` (model → provider) and `provider_client` (provider →
  `openai_sdk` / `gpt5_sdk` / `google_genai` / `litellm`) so the built-in
  table and client-type defaults can be overridden per deployment.
