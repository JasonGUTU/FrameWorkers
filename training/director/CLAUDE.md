# training/director — director routing LoRA training

## 目的
在 Qwen2.5-7B-Instruct 上做 **SFT + DPO** 两阶段 LoRA 微调，把现在 Gemini flash + fewshot + descriptor 补丁这一套"支架堆"的能力烘进本地权重。目前是 **smoke-test 阶段**（5+5 样本），先把 pipeline 打通再扩量到 1000 SFT + 500 DPO。

## 文件

| 文件 | 作用 |
|---|---|
| `gen_samples.py` | 生成 smoke 样本（硬编码 5 条 SFT + 5 对 DPO）。扩量时改成调 Claude/GPT-5 API |
| `samples_sft.jsonl` | SFT 样本（TRL `SFTTrainer` native messages 格式）|
| `samples_dpo.jsonl` | DPO 偏好对（TRL `DPOTrainer` native `{prompt, chosen, rejected}`）|
| `validate.py` | 5 项 checklist：token 长度 / JSON schema / DPO 长度平衡 / chat template / eval 隔离 |
| `train_lora.py` | 两阶段 LoRA 训练（SFT → DPO），adapter 存 `adapters/sft/` 和 `adapters/dpo/` |
| `infer.py` | 加载 adapter 跑 3 条 held-out test goal（每条专打一种已知 bias）|
| `run_smoke.sh` | 端到端一条命令：validate → SFT → DPO → infer |
| `requirements-training.txt` | torch / transformers / trl / peft / datasets / accelerate |

## GPU 节点一次跑通

```bash
# 排队
srun --ntasks=1 --cpus-per-task=8 --time=4:00:00 --mem-per-cpu=8g \
     --nodelist=sof1-h200-5 --partition=batch --gpus=h200:1 --qos=eccv-2026 --pty bash

# 进去后
source ~/.bashrc && conda activate frameworkers
cd ~/FrameWorkers
bash training/director/run_smoke.sh
```

## 关键约束

1. **Eval 严格 held-out**：`evals/director_routing/eval_cases.json` 的 100 条永远不许进训练集。`validate.py` check #5 会拦。
2. **SFT 和 DPO 的 assistant 输出必须是合法 JSON** 且 schema = `{"rationale": "...", "plan": [{"agent_id": "...", "intent": "..."}, ...]}`，match `director_agent/prompts.py` 的 `PLAN_UPFRONT_SYSTEM` 规定。
3. **DPO chosen/rejected token 长度差 ≤ 10%**，不然模型会偷学"长 = 对"。
4. **System prompt 里的 catalog 是精简版**（agent_id + 一行 purpose，~2K tokens）。如果换回 full catalog（~35K 字符），seq_len 必须上调到 16K 以上，GPU 内存也要相应扩。
5. **同一 agent_id 在一个 plan 里只能出现一次**（`_parse_plan` 会拦）。

## 扩量时 gen_samples.py 要改的地方

现在的 `SFT_SAMPLES` 和 `DPO_PAIRS` 是硬编码列表。扩到 1000 + 500 时替换成：

1. 从 `evals/director_routing/eval_cases.json` 的 20 个独立 chain 按比例抽样（高频 chain 各 80-100 条，低频 chain 各 30-50 条）
2. 每条 chain 作为 target，调 Claude/GPT-5 的 API 生成 user_goal 变体 + rationale
3. Rationale 生成 prompt 必须强制引用 descriptor 规则 + 反 bias 规则（"因为用户没要求分析，不加 VA"）
4. DPO rejected：对每个 chosen 程序化注入 4 种 bias（VA/Ambience/Compositor/missing-IntakeText）配上"找借口"式 rationale（token 长度对齐 chosen ± 5%）
5. 生成后 5-10% spot-check 人工抽查 rationale 不胡扯

## 扩量前后 validate.py 都要过 5/5 checks
