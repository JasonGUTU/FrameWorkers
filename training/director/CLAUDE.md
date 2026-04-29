# training/director — director routing LoRA training

## 目的
在 Qwen3-8B 上做 SFT LoRA 微调，蒸馏 Gemini 的 director routing 能力到本地权重。RL 阶段（之前是 TRL-based GRPO）2026-04-25 因 bf16 multinomial NaN 反复崩溃 + 算法不可控被全部移除，正在重新设计中（当前 repo 不含 RL 代码）。

**Base model（2026-04-27 升级）：** `Qwen/Qwen3-8B`（之前是 Qwen2.5-7B-Instruct）。**Thinking mode 关闭**（`apply_chat_template(..., enable_thinking=False)`）—— routing 是浅推理任务，rationale 字段已是 CoT 通道；开 thinking 会让 token 预算紧张且需要重写训练数据带 `<think>` 包装，得不偿失。任何切回 thinking-on 都需要先重写训练数据。

**历史 baseline 不可比：** Qwen2.5-7B 时代的 LoRA chain accuracy（58.5% overfit / etc.）跟新 Qwen3-8B 跑出来的不在同一坐标系。Qwen3-8B 时代要重跑 Gemini reference + 新 LoRA，两者跨 base model 不直接对比。

**Baseline = Canonical training prompt = `PLAN_UPFRONT_CORE` (fewshots=False, policies=False, topology=0)**（2026-04-24 定）

训练和评估**统一用 `PLAN_UPFRONT_CORE` (fewshots=False, policies=False, topology=0)**：即 `_PLAN_UPFRONT_MINIMAL` + 完整 descriptor catalog + `FW_TOPOLOGY=0`。这是 *诚实能力基线* —— prompt 里没有 §0-§4 policy 预制标答，没有 worked-pattern fewshot 示例，没有 topology 邻居 hint，模型纯靠每个 agent 自己 descriptor 推理 routing。

**Gemini 2.5 Flash reference（130-case eval, clean descriptors, fewshots=False, policies=False, topology=0, markdown catalog）：**
- chain accuracy: **50.8%** (66/130)
- step accuracy: 68.7%
- run: `Runtime/eval_routing/20260425_204159_gemini_core_markdown_catalog.json`
- prompt format: catalog 由 `_render_catalog_markdown` 渲染（每个 agent 一个 plain-text block，blank-line 分隔），替换之前的 `json.dumps(catalog, indent=2)` 形态。同一组 130 case 上 chain accuracy 不变（66/66），step accuracy 微跌 1.5 pt（581 → 566 / 828），方差内。
- ablation history (4/22 `gemini_core_with_policies` 50.0% on 100-case 旧 eval + 旧 "cinematic default" descriptors / 4/24 `gemini_core_clean_descriptors` 50.8% on JSON-wrapped catalog) 已删除，新格式重跑成为唯一 reference。

**为什么不用 CORE_WITH_POLICIES 或 CORE_WITH_FEWSHOTS：** 实测 Gemini 加 policies 从 50.0% → 50.0%（贡献 ≈ 0），加 fewshots / topology 才有 +20 pt 的 delta（4/20 "baseline" 88% 是三层 scaffold 全开在旧 eval 上的结果）。但 scaffold 开着就等于 prompt 里塞"标答"，LoRA 学的是"按模板填空"而不是"descriptor-driven reasoning"。为了让蒸馏目标诚实反映**模型能力**而不是**模板命中率**，canonical 选 `PLAN_UPFRONT_CORE` (fewshots=False, policies=False, topology=0)。Policies / fewshots / topology 保留为**消融 scaffold**，ablation 实验按需叠加。

**"train prompt ≡ inference prompt"**（byte-for-byte）：训/推/评 三处都用 `PLAN_UPFRONT_CORE` (fewshots=False, policies=False, topology=0)；`gen_samples.build_system_prompt()` 调 `build_plan_system_prompt(core=PLAN_UPFRONT_CORE, ...)`。若未来切 scaffold 配置，三处同步改。

## 文件

| 文件 | 作用 |
|---|---|
| `gen_samples.py` | 共用 `build_system_prompt()` / `build_agent_catalog()` / `_assistant_response()` helper |
| `gen_training_full.py` | 调 teacher LLM 生成 ~1100 SFT samples |
| `gen_by_hand.py` | 手写高质量补样（针对特定 chain shape） |
| `samples_sft_full.jsonl` | 1110 条 SFT（TRL `SFTTrainer` native messages） |
| `validate.py` | 4 项 checklist：token 长度 / JSON schema / chat template / eval 隔离 |
| `train_sft.py` | SFT LoRA（3 epochs 默认）；输出到 `--adapter-dir` |
| `infer.py` | 加载 adapter 跑 3 条 held-out test goal smoke |
| `train_sft.sbatch` | H200 sbatch：validate → SFT → infer smoke |
| `train_sft_overfit.sbatch` | 同上但 SFT 50 epochs（overfit 参考实验）|
| `eval_full.sbatch` | 评估 sbatch：跑 `evals/director_routing/eval_lora.py` on 100 cases |
| `requirements-training.txt` | torch / transformers / trl / peft / datasets / accelerate |

## 提交训练

```bash
# 生成训练数据（如果 samples_sft_full.jsonl 不在）
source ~/.bashrc && conda activate frameworkers
cd ~/FrameWorkers
PYTHONPATH=. python training/director/gen_training_full.py

# 校验
PYTHONPATH=. python training/director/validate.py --seq-len 8192

# Stage 1: SFT（~25 min H200）
sbatch training/director/train_sft.sbatch

# Stage 2: RL —— 算法重新设计中，暂未提供入口

# 评估（100 cases ~13 min H200）
sbatch --export=ALL,ADAPTER=training/director/adapters_full/sft,NAME=lora_sft \
       training/director/eval_full.sbatch
```

## 关键约束

1. **Eval 严格 held-out**：`evals/director_routing/eval_cases.json` 的 130 条永远不许进训练集。`validate.py` check #4 会拦。
2. **SFT assistant 输出必须是合法 JSON** 且 schema = `{"rationale": "...", "plan": [{"agent_id": "...", "intent": "..."}, ...]}`，match `director_agent/prompts.py` 的 plan prompt 规定。
3. **Train prompt ≡ inference prompt**（byte-for-byte）：`gen_samples.build_system_prompt()` 直接调 `director_agent.prompts.build_plan_system_prompt(core=PLAN_UPFRONT_CORE, ...)`，和 production router / Gemini eval 走完全同一条组装路径（见"目的"段落的 canonical prompt 定义）。
4. **Catalog = basic info，不是 scaffold**：完整 descriptor（Inputs/Output/Purpose-routing 每个 agent ~1500 chars × 19+）必须在 prompt 里，LoRA 才能知道每个 agent 能干啥。详见根 CLAUDE.md §8。
5. **同一 agent_id 在一个 plan 里只能出现一次**（`director_agent/router.py::_parse_plan` 会拦；任何未来 RL reward 对此违反必须给 0）。
6. **未来 RL stage 的 reward 必须对齐 eval metric**：eval 用 `correct_positions / max(len(actual), len(expected))` + set-aware slot（`expected_chain[i]` 可以是 `list[str]`）；RL 优化目标必须 byte-identical 到这个公式。LoRA 优化什么 = eval 测什么。
