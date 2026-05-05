# training/director — director routing LoRA training

## 目的
在 Qwen3-8B 上做 SFT LoRA 微调，蒸馏 Gemini 的 director routing 能力到本地权重。RL 阶段是 `train_grpo.py` 的手写 GRPO（DeepSeekMath / R1-style，无 PPO clip，fp32 sampling），替代 2026-04-25 删除的 TRL-based wrapper（之前因 bf16 multinomial NaN 反复崩溃 + 算法不可控）。当前 v4_500 实验在跑 SFT × 3 variant (`no_rationale` / `templated` / `rich`) + 对应 GRPO × 3 variant，sbatch 入口见 `train_{sft,grpo}_v4_*_2gpu.sbatch`。

**Base model（2026-04-27 升级）：** `Qwen/Qwen3-8B`（之前是 Qwen2.5-7B-Instruct）。**Thinking mode 关闭**（`apply_chat_template(..., enable_thinking=False)`）—— routing 是浅推理任务，rationale 字段已是 CoT 通道；开 thinking 会让 token 预算紧张且需要重写训练数据带 `<think>` 包装，得不偿失。任何切回 thinking-on 都需要先重写训练数据。

**历史 baseline 不可比：** Qwen2.5-7B 时代的 LoRA chain accuracy（58.5% overfit / etc.）跟新 Qwen3-8B 跑出来的不在同一坐标系。Qwen3-8B 时代要重跑 Gemini reference + 新 LoRA，两者跨 base model 不直接对比。

**Baseline = Canonical training prompt = `PLAN_UPFRONT_CORE` (fewshots=False, policies=False, topology=0)**（2026-04-24 定）

训练和评估**统一用 `PLAN_UPFRONT_CORE` (fewshots=False, policies=False, topology=0)**：即 `_PLAN_UPFRONT_MINIMAL` + 完整 descriptor catalog + `FW_TOPOLOGY=0`。这是 *诚实能力基线* —— prompt 里没有 §0-§4 policy 预制标答，没有 worked-pattern fewshot 示例，没有 topology 邻居 hint，模型纯靠每个 agent 自己 descriptor 推理 routing。

**Gemini 2.5 Flash reference（fewshots=False, policies=False, topology=0；即 canonical core prompt）—— 两组 eval set 各跑一份：**

| eval set | cases | chain_acc | step_acc | run |
|---|---|---|---|---|
| `eval_cases.json` (v3) | 209 | **76.1%** | 86.9% | `Runtime/eval_routing/20260502_140038_gemini25flash_v3_209_core.json` |
| `eval_cases_v4_500.json` (v4) | 522 | **74.7%** | 85.1% | `Runtime/eval_routing/20260502_135043_gemini25flash_v4500_core.json` |

LoRA 推理时 prompt 必须跟上面 byte-identical（同 core prompt + 同 catalog），eval 比较才有意义；如果 Gemini 跑成 canonical (full scaffold) 那一档（v4_500 上 84.7% chain / 91.0% step，`20260502_113614_gemini25flash_v4500_canonical.json`），那是带 policies + fewshots + topology 三层 scaffold 的"加 buff"参考刻度，**不是 LoRA 对比 baseline**。历史 130-case eval (50.8% chain) 是 Qwen2.5-7B + 旧 catalog 时代的事，已不构成参考。

**为什么不用 CORE_WITH_POLICIES 或 CORE_WITH_FEWSHOTS：** 实测 Gemini 加 policies 从 50.0% → 50.0%（贡献 ≈ 0），加 fewshots / topology 才有 +20 pt 的 delta（4/20 "baseline" 88% 是三层 scaffold 全开在旧 eval 上的结果）。但 scaffold 开着就等于 prompt 里塞"标答"，LoRA 学的是"按模板填空"而不是"descriptor-driven reasoning"。为了让蒸馏目标诚实反映**模型能力**而不是**模板命中率**，canonical 选 `PLAN_UPFRONT_CORE` (fewshots=False, policies=False, topology=0)。Policies / fewshots / topology 保留为**消融 scaffold**，ablation 实验按需叠加。

**"train prompt ≡ inference prompt"**（byte-for-byte）：训/推/评 三处都用 `PLAN_UPFRONT_CORE` (fewshots=False, policies=False, topology=0)；`gen_samples.build_system_prompt()` 调 `build_plan_system_prompt(core=PLAN_UPFRONT_CORE, ...)`。若未来切 scaffold 配置，三处同步改。

## 文件

**生成训练数据：**

| 文件 | 作用 |
|---|---|
| `gen_samples.py` | 共用 `build_system_prompt()` / `build_agent_catalog()` / `_assistant_response()` helper |
| `build_sft_jsonl.py` | 生成 SFT samples（rich variant：含 rationale 字段） |
| `build_grpo_jsonl.py` | 生成 GRPO samples（prompt + expected_chain，无 assistant message） |
| `build_templated_sft_jsonl.py` / `build_templated_grpo_jsonl.py` | templated variant：rationale 字段填模板化套路 |
| `build_expanded_grpo_data.py` | 扩样脚本（gap-fill 特定 chain shape） |
| `_regen_v4_500_system_prompt.py` | 把 v4_500 数据按当前 system prompt 重新 render |
| `_rebalance_to_v4_500_with_gapfill.py` | v3 → v4_500 重平衡 + gap-fill 工具 |
| `samples_sft_full.v4_500.jsonl`<br>`samples_sft_full.no_rationale.v4_500.jsonl`<br>`samples_sft_full.templated.v4_500.jsonl` | v4_500 SFT 三 variant（**rich** 含真实 rationale；**no_rationale** rationale 字段为空字符串；**templated** rationale 字段填模板化套路） |
| `samples_grpo_v1.{,no_rationale,templated}.v4_500.jsonl` | v4_500 GRPO 三 variant（用于 SFT 之后的 RL 阶段） |
| `validate.py` | 4 项 checklist：token 长度 / JSON schema / chat template / eval 隔离 |

**训练入口（v4_500 当前主流；旧的 `train_sft.sbatch` / `train_grpo.sbatch` 是单 GPU + v3 时代遗留，仍可跑但不是当前实验所用）：**

| 文件 | 作用 |
|---|---|
| `train_sft.py` | SFT LoRA 训练核心；通过 `--samples-path` 切 variant |
| `train_grpo.py` | 手写 GRPO 训练核心（DeepSeekMath / R1-style，无 PPO clip，fp32 sampling）；reward 在 `grpo_reward.py` |
| `grpo_reward.py` | GRPO reward 函数（详见下方"关键约束 #6"）|
| `grpo_loss.py` / `grpo_sampler.py` | GRPO loss / 采样实现细节 |
| `train_sft_v4_{no_rationale,templated,rich}_2gpu.sbatch` | v4_500 SFT 三 variant 的 2-GPU H200 sbatch；末尾自带 522-case eval |
| `train_grpo_v4_{no_rationale,templated,rich}_2gpu.sbatch` | v4_500 GRPO 三 variant 的 2-GPU H200 sbatch；以对应 SFT adapter 为起点；末尾自带 522-case eval |
| `infer.py` / `infer_smoke.sbatch` | 加载 adapter 跑 3 条 held-out test goal smoke |
| `infer_on_training.py` / `.sbatch` | 在训练集上反查（debug overfit/泛化用） |
| `eval_full.sbatch` / `eval_full_no_rationale.sbatch` | 旧 100-case eval sbatch（v3 时代；当前 eval 由 v4 sbatch 末尾内嵌跑） |
| `benchmark_qwen.py` / `.sbatch` | 基础模型推理 benchmark |
| `requirements-training.txt` | torch / transformers / trl / peft / datasets / accelerate |

## 提交训练（v4_500 当前主流）

```bash
source ~/.bashrc && conda activate frameworkers
cd ~/FrameWorkers

# 生成训练数据（如果 samples_*.v4_500.jsonl 不在）
PYTHONPATH=. python training/director/build_sft_jsonl.py            # rich variant
PYTHONPATH=. python training/director/build_templated_sft_jsonl.py  # templated variant
PYTHONPATH=. python training/director/build_grpo_jsonl.py
# no_rationale variant 由 _regen_v4_500_system_prompt.py 把 rich 的 rationale 字段清空生成

# 校验（token 长度 / JSON schema / chat template / eval 隔离）
PYTHONPATH=. python training/director/validate.py --seq-len 8192

# Stage 1: SFT（2-GPU H200，~1h，末尾自带 522-case eval）
sbatch training/director/train_sft_v4_no_rationale_2gpu.sbatch
sbatch training/director/train_sft_v4_templated_2gpu.sbatch
sbatch training/director/train_sft_v4_rich_2gpu.sbatch

# Stage 2: GRPO（手写实现 train_grpo.py；以对应 SFT adapter 为起点；末尾自带 522-case eval）
sbatch training/director/train_grpo_v4_no_rationale_2gpu.sbatch
sbatch training/director/train_grpo_v4_templated_2gpu.sbatch
sbatch training/director/train_grpo_v4_rich_2gpu.sbatch

# eval 结果落 Runtime/eval_routing/<timestamp>_lora_v4500_<variant>_<run_stamp>.json
```

旧的单 GPU `train_sft.sbatch` / `train_grpo.sbatch` + `eval_full.sbatch` 是 v3 时代遗留，仍可跑但不是当前实验所用。

## 关键约束

1. **Eval 严格 held-out**：`evals/director_routing/eval_cases.json`（209 条）和 `evals/director_routing/eval_cases_v4_500.json`（522 条）永远不许进训练集。`validate.py` check #4 会拦（注意 validate.py 当前只检 `eval_cases.json` 这一个文件，加 v4_500 后需要扩到两组）。
2. **SFT assistant 输出必须是合法 JSON** 且 schema = `{"rationale": "...", "plan": [{"agent_id": "...", "intent": "..."}, ...]}`，match `director_agent/prompts.py` 的 plan prompt 规定。
3. **Train prompt ≡ inference prompt**（byte-for-byte）：`gen_samples.build_system_prompt()` 直接调 `director_agent.prompts.build_plan_system_prompt(core=PLAN_UPFRONT_CORE, ...)`，和 production router / Gemini eval 走完全同一条组装路径（见"目的"段落的 canonical prompt 定义）。
4. **Catalog = basic info，不是 scaffold**：完整 descriptor（Inputs/Output/Purpose-routing 每个 agent ~1500 chars × 19+）必须在 prompt 里，LoRA 才能知道每个 agent 能干啥。详见根 CLAUDE.md §8。
5. **同一 agent_id 在一个 plan 里只能出现一次**（`director_agent/router.py::_parse_plan` 会拦；任何未来 RL reward 对此违反必须给 0）。
6. **GRPO reward 是 eval metric 的有意混合，不是 byte-identical**（见 `grpo_reward.py`）：
   - **格式门控**：parse 失败 / unknown agent_id / duplicate agent → R = 0（eval 这边 parse 失败只 flag `error`，step accuracy 仍记 correct_steps；RL 这边硬卡是为了防止 exploration 漂到非法输出）
   - **格式通过**：`R = 0.5 * pos_correct + 0.5 * float(chain_perfect)` ∈ [0, 1]
     - `pos_correct = n_correct / max(len(actual), len(expected))` —— 跟 eval 的 step_accuracy per-case 公式一致（且 set-aware slot：`expected_chain[i]` 可以是 `list[str]`）
     - `chain_perfect = 1` 当 `len(actual) == len(expected)` 且全 slot 命中 —— 跟 eval 的 chain_accuracy per-case 判据一致
   - **为什么不用纯 binary（R = chain_perfect）：** 4 个 rollout 全 0 或全 1 时 σ=0，GRPO advantage 退化为 0，无梯度
   - **为什么不用纯 step_acc（R = pos_correct）：** 模型学"稳定 4/5"而不是"冒险 5/5"（satisficing）；perfect bonus 让 5/5 比 4/5 多奖 2.5×（1.0 vs 0.4）
   - **结论：** reward 是两个 eval 指标的加权混合 + 一道格式门，**有意偏离** "byte-identical to eval metric" 这个朴素目标，目的是给 RL 一个 σ>0 + 拒绝 satisficing 的可学信号。任何改动 reward 公式必须同步更新这条约束。
