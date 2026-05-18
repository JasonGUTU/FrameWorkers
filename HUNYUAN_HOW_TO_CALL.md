# HunyuanVideo-I2V 调用速查

self-host FastAPI 包了 Tencent `HunyuanVideoSampler`，每个 SLURM job 占一张 H200，模型常驻 GPU 内存。

## 当前可用 endpoint（截至 2026-05-10 11:00 UTC）

**给同事 / 其他 session 用的 10 张闲置（无业务在跑，PREDICT_LOCK 空）**：

```
http://sof1-h200-3:9100  jid 559584
http://sof1-h200-6:9101  jid 559603
http://sof1-h200-6:9102  jid 559604
http://sof1-h200-6:9103  jid 559605
http://sof1-h200-6:9104  jid 559606
http://sof1-h200-6:9105  jid 559607
http://sof1-h200-7:9106  jid 559608
http://sof1-h200-7:9107  jid 559609
http://sof1-h200-7:9108  jid 559610
http://sof1-h200-7:9109  jid 559611
```

每张 SLURM `--time=50:00:00`，到期自动 expire（用 `squeue -j <jid>` 看剩余时长）。

**正在跑 baseline 的 11 张（不要打）**：9200-9210（jid 559251 / 559281 / 559292 / 559293 / 559284 / 559285 / 559294-298）

## API 契约

### `GET /health`
```json
{"ok": true}
```
sampler 没 ready 时返回 `{"ok": false}`。

### `GET /info`
```json
{
  "loaded": true,
  "hostname": "sof1-h200-3",
  "model": "HunyuanVideo-I2V-13B",
  "default_video_size": [720, 1280],
  "default_video_length": 121
}
```

### `POST /i2v`（核心，纯 image-to-video）

**Request**：
```json
{
  "prompt": "<text 描述场景 + 动作>",
  "image_b64": "<base64-encoded keyframe png/jpg>",
  "duration_sec": 5.0,
  "seed": 0,
  "negative_prompt": "",
  "infer_steps": 50
}
```

字段说明：
- `prompt` (str, required)：纯文本，描述这 5 秒画面 + 镜头/动作。中英文都行。
- `image_b64` (str, required)：base64 PNG/JPG 字节。**Hunyuan 是 i2v，不能空**。第一帧 = 这张图。
- `duration_sec` (float, default=5)：**上限 5**，更大会被静默截断到 5。Hunyuan 内部用 `frames = round((duration*24-1)/4)*4+1`，5s → 121 frames。
- `seed` (int, default=0)：固定可复现。
- `negative_prompt` (str, default="")：空就行。
- `infer_steps` (int, default=50)：50 → ~22 min/shot；25 → ~11 min/shot；质量降低。

**Response (200)**：
```json
{
  "video_b64": "<base64 mp4>",
  "video_length_frames": 121,
  "fps": 24,
  "duration_sec": 5.041,
  "infer_steps": 50,
  "elapsed_sec": 1394.5,
  "seed": 0
}
```

**没有 audio**。Hunyuan 是 silent video model，需要自己后挂音频。

## Concurrency / 性能

- **单 server 只能 1 个 inference 同时跑**（`PREDICT_LOCK = asyncio.Lock`），多个并发 POST 会在 server 端排队。
- **不同 server 互相独立**，可以横向并行。
- 单 shot 50 步 ≈ **22-24 min**（H200 700 GB FP16），25 步 ≈ 11 min。
- HTTP timeout 建议设 `>= 5h`（client 端要等 server 处理 + 队列），避免被自家超时打断 server 还在跑的 inference（被打断时 server 仍会跑完，但 mp4 丢给死 client，叫 "ghost queue"）。

## 最小调用示例

### curl
```bash
# 1) 准备 body：base64 编码 image，构造 JSON
python3 -c '
import os, json, base64
img = open("/path/to/keyframe.png", "rb").read()
print(json.dumps({
  "prompt": "A young woman gasps and looks up at falling cherry blossoms, soft sunlight",
  "image_b64": base64.b64encode(img).decode(),
  "duration_sec": 5.0,
  "infer_steps": 50,
}))' > /tmp/body.json

# 2) POST（注意 max-time 给足，server ~22 min）
curl -sS --max-time 1800 \
  -H "Content-Type: application/json" \
  --data-binary @/tmp/body.json \
  http://sof1-h200-3:9100/i2v > /tmp/resp.json

# 3) decode mp4
python3 -c '
import json, base64
d = json.load(open("/tmp/resp.json"))
open("/tmp/out.mp4","wb").write(base64.b64decode(d["video_b64"]))
print(f"mp4 {len(d[\"video_b64\"])//4*3} bytes, fps={d[\"fps\"]}, frames={d[\"video_length_frames\"]}")
'
```

参考脚本：`/scratch/zhendong_li/test_single_shot.sh <endpoint>`（已测通）。

### Python httpx
```python
import asyncio, base64, httpx, json

async def i2v(endpoint: str, image_path: str, prompt: str) -> bytes:
    body = {
        "prompt": prompt,
        "image_b64": base64.b64encode(open(image_path, "rb").read()).decode(),
        "duration_sec": 5.0,
        "infer_steps": 50,
    }
    async with httpx.AsyncClient(timeout=18000.0) as c:
        r = await c.post(f"{endpoint}/i2v", json=body)
        r.raise_for_status()
        d = r.json()
    return base64.b64decode(d["video_b64"])

mp4 = asyncio.run(i2v(
    "http://sof1-h200-3:9100",
    "/path/to/keyframe.png",
    "A young woman gasps...",
))
open("out.mp4", "wb").write(mp4)
```

### N-shot 并行（同一 endpoint 没意义，跨 endpoint 才有）

```python
import asyncio, httpx
sem = asyncio.Semaphore(8)  # fal.ai 速率上限提示，hunyuan 不需要

async def render(endpoint, image_path, prompt):
    async with sem:
        return await i2v(endpoint, image_path, prompt)

# 把 N 个 shot 分到 K 个 endpoint 上 round-robin
endpoints = ["http://sof1-h200-3:9100", "http://sof1-h200-6:9101", ...]
mp4s = await asyncio.gather(*[
    render(endpoints[i % len(endpoints)], shots[i].image, shots[i].prompt)
    for i in range(len(shots))
])
```

## 常见坑

1. **PREDICT_LOCK 串行**：同一 server 即使你并发发 8 个 POST，server 端只跑 1 个，其他排队。要并行就横向上 N 个 endpoint。
2. **client 死了 server 不会停**：`asyncio.to_thread` 跑 PyTorch inference 不响应 cancel。client 断了 server 仍跑完那一个，浪费 22 min GPU。kill 客户端不能立刻让 server idle。
3. **Hunyuan 5s 上限**：传 `duration_sec=10` 会被截到 5。
4. **没有 audio**：mp4 是无声 video stream。要 audio 自己挂模型再 ffmpeg mux。
5. **首张 server load 32s**：刚 sbatch 起来 sampler 还没就绪时 `/health` 返回 `{"ok": false}`。先 `curl /health` 直到 ok。
6. **idle 不会被 reaper 杀**：server 内部有 `keep_busy_loop` 持续 2048×2048 matmul 维持 GPU util ~100%（真请求来时立即让出），cluster idle-killer 不会误判。

## 关闭 server

```bash
scancel <jid>
# 模型 unload，GPU 释放，PyTorch 进程随 SLURM job 一起死
```

## 起新 server

```bash
cd /home/zhendong_li/HunyuanVideo-I2V
sbatch --export=ALL,HUNYUAN_PORT=<port> hunyuan_server.sbatch
# port 自己选不冲突的（避开 9100-9210）
# sbatch 已默认 --exclude=sof1-h200-5（broken node）
```

server 代码：`/home/zhendong_li/HunyuanVideo-I2V/hunyuan_server.py`
sbatch 脚本：`/home/zhendong_li/HunyuanVideo-I2V/hunyuan_server.sbatch`
