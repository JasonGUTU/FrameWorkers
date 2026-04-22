# training/director — director routing LoRA training

## 目的
在 Qwen2.5-7B-Instruct 上做 **SFT + DPO** 两阶段 LoRA 微调，把 Gemini + fewshot + topology 这一套"支架堆"的 routing 能力烘进本地权重。训练和评估统一用 **bare prompt**（fewshots 剥掉、topology 关掉），对齐 Gemini no_few_shots_no_topology ≈ 61% 的 apples-to-apples 基线。当前 bare DPO adapter 评估为 **69%**（+8 点正向 lift）。

## 文件

| 文件 | 作用 |
|---|---|
| `gen_samples.py` | 共用的 `build_system_prompt()` / `build_compact_catalog()` / `_assistant_response()` helpers |
| `gen_training_full.py` | 调 teacher LLM（Claude Sonnet / GPT-5）生成 1000 SFT + 500 DPO |
| `gen_dpo.py` | 从 SFT 采样生成 DPO 偏好对（4 类 bias 注入 + Qwen-token 长度对齐） |
| `gen_by_hand.py` | 手写高质量补样（针对特定 chain shape） |
| `samples_sft_full.jsonl` | 1110 条 SFT（TRL `SFTTrainer` native messages） |
| `samples_dpo_full.jsonl` | 500 对 DPO（TRL `DPOTrainer` native `{prompt, chosen, rejected}`） |
| `validate.py` | 5 项 checklist：token 长度 / JSON schema / DPO 长度平衡 / chat template / eval 隔离 |
| `train_lora.py` | 两阶段 LoRA 训练（SFT → DPO），adapter 输出到 `--adapter-dir` |
| `train_grpo.py` / `grpo_reward.py` | GRPO 代码（预写，待 bucket 失败时启用） |
| `infer.py` | 加载 adapter 跑 3 条 held-out test goal smoke |
| `train_full.sbatch` | H200 sbatch：validate → SFT → DPO → infer smoke |
| `train_grpo.sbatch` | GRPO sbatch（依赖 `adapters_full/dpo` 存在） |
| `eval_full.sbatch` | 评估 sbatch：跑 `evals/director_routing/eval_lora.py` on 100 cases |
| `requirements-training.txt` | torch / transformers / trl / peft / datasets / accelerate |

## 提交训练

```bash
# 生成训练数据（如果 samples_*_full.jsonl 不在）
source ~/.bashrc && conda activate frameworkers
cd ~/FrameWorkers
PYTHONPATH=. python training/director/gen_training_full.py
PYTHONPATH=. python training/director/gen_dpo.py

# 校验
PYTHONPATH=. python training/director/validate.py --seq-len 4096

# 提交训练（SFT + DPO ~25 min H200）
sbatch training/director/train_full.sbatch

# 跑完后评估（100 cases ~13 min H200）
sbatch --export=ALL,ADAPTER=training/director/adapters_full/dpo,NAME=lora_dpo \
       training/director/eval_full.sbatch
```

## 关键约束

1. **Eval 严格 held-out**：`evals/director_routing/eval_cases.json` 的 100 条永远不许进训练集。`validate.py` check #5 会拦。
2. **SFT 和 DPO 的 assistant 输出必须是合法 JSON** 且 schema = `{"rationale": "...", "plan": [{"agent_id": "...", "intent": "..."}, ...]}`，match `director_agent/prompts.py` 的 `PLAN_UPFRONT_SYSTEM_BARE` 规定。
3. **DPO chosen/rejected Qwen-token 长度差 ≤ 10%**（validate.py check #3），否则模型会偷学"长 = 对"。`gen_dpo.py::_length_align` 用真实 tokenizer 对齐到 ±8%。
4. **System prompt 里的 catalog 是精简版**（agent_id + 一行 purpose，~2K tokens）。训练 + 评估都走 `build_system_prompt()` 同一个 builder。
5. **同一 agent_id 在一个 plan 里只能出现一次**（`_parse_plan` 会拦）。
6. **Bare 命名约定**：`PLAN_UPFRONT_SYSTEM_BARE` = fewshots 剥掉；`FW_TOPOLOGY=0` = 关 topology 注入。bare LoRA 训练 + bare eval 是 apples-to-apples 的唯一正确组合。
