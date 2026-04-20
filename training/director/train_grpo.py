"""GRPO fine-tuning of the director-routing LoRA.

Starting point: Qwen2.5-7B-Instruct + SFT+DPO adapter (from train_lora.py).
GRPO uses the reward in grpo_reward.py (chain_match step-accuracy), no critic,
no separate reward model — the verifier IS the eval scoring.

Dataset: `{prompt, expected_chain}` pairs built from samples_sft_full.jsonl
(training goals, not eval goals — isolation is enforced upstream).

Output: training/director/adapters_full/grpo/  (LoRA on top of DPO adapter)

Usage (after SFT+DPO done):
    PYTHONPATH=. python training/director/train_grpo.py \\
        --adapter-in  training/director/adapters_full/dpo \\
        --adapter-out training/director/adapters_full/grpo \\
        --num-generations 4 \\
        --epochs 1
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


BASE_MODEL = "Qwen/Qwen2.5-7B-Instruct"
SEQ_LEN = 4096
MAX_COMPLETION_LEN = 1024  # JSON plan is ~300-600 tokens; give headroom


GRPO_DEFAULTS = dict(
    learning_rate=1e-6,          # much lower than SFT: RL needs tiny updates
    num_train_epochs=1,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=8,
    bf16=True,
    logging_steps=5,
    save_strategy="epoch",
    report_to="none",
    max_prompt_length=SEQ_LEN - MAX_COMPLETION_LEN,
    max_completion_length=MAX_COMPLETION_LEN,
    beta=0.04,                    # KL coefficient to reference policy
    temperature=0.9,              # sampling during rollout
)


def build_dataset(sft_jsonl: Path):
    """Turn samples_sft_full.jsonl rows into GRPO-compatible entries.

    GRPOTrainer with a conversational-format prompt accepts dataset columns:
      - `prompt` : list[{"role", "content"}]  (chat messages without assistant)
      - `expected_chain` : list[str]          (passed through as kwarg to reward)
    """
    from datasets import Dataset

    rows = []
    with sft_jsonl.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            msgs = rec["messages"]
            assistant = json.loads(msgs[-1]["content"])
            chain = [step["agent_id"] for step in assistant["plan"]]
            rows.append({
                "prompt": msgs[:-1],           # system + user
                "expected_chain": chain,
            })
    return Dataset.from_list(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-model",   default=BASE_MODEL)
    ap.add_argument("--adapter-in",   required=True, help="starting-point LoRA (usually DPO adapter)")
    ap.add_argument("--adapter-out",  required=True, help="output dir for GRPO-refined LoRA")
    ap.add_argument("--sft-path",     default="training/director/samples_sft_full.jsonl")
    ap.add_argument("--num-generations", type=int, default=4,
                    help="rollouts per prompt (GRPO groups completions for relative advantages)")
    ap.add_argument("--epochs",       type=int, default=1)
    ap.add_argument("--per-device-batch", type=int, default=1)
    ap.add_argument("--grad-accum",   type=int, default=8)
    ap.add_argument("--learning-rate", type=float, default=GRPO_DEFAULTS["learning_rate"])
    ap.add_argument("--beta",         type=float, default=GRPO_DEFAULTS["beta"])
    ap.add_argument("--subsample",    type=int, default=None,
                    help="if set, random-sample N training prompts (default: use all 1110)")
    args = ap.parse_args()

    # ── heavy imports inside main so --help works without GPU libs ──────────
    import random
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    from trl import GRPOConfig, GRPOTrainer
    from agents import get_agent_registry
    from training.director.grpo_reward import make_grpo_reward_fn

    sft_path = Path(args.sft_path)
    if not sft_path.is_absolute():
        sft_path = Path.cwd() / sft_path
    adapter_in  = Path(args.adapter_in)
    adapter_out = Path(args.adapter_out)
    adapter_out.mkdir(parents=True, exist_ok=True)

    print(f"Base model     : {args.base_model}")
    print(f"Starting LoRA  : {adapter_in}")
    print(f"Output adapter : {adapter_out}")
    print(f"SFT data       : {sft_path}")

    # ── allowed agent_ids (for reward verifier) ────────────────────────────
    registry = get_agent_registry()
    allowed = {info.get("id") or info.get("name") for info in registry.get_all_agents_info()}
    print(f"allowed agent_ids: {len(allowed)}")

    # ── dataset ────────────────────────────────────────────────────────────
    ds = build_dataset(sft_path)
    if args.subsample:
        random.seed(42)
        idx = random.sample(range(len(ds)), k=min(args.subsample, len(ds)))
        ds = ds.select(idx)
    print(f"GRPO prompts   : {len(ds)}  (rollouts: {len(ds) * args.num_generations})")

    # ── tokenizer ──────────────────────────────────────────────────────────
    tokenizer = AutoTokenizer.from_pretrained(args.base_model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # ── policy = base + DPO adapter (trainable) ────────────────────────────
    base = AutoModelForCausalLM.from_pretrained(
        args.base_model, torch_dtype=torch.bfloat16, device_map="auto",
    )
    policy = PeftModel.from_pretrained(base, str(adapter_in), is_trainable=True)
    print("policy loaded with starting adapter")

    # ── reward ─────────────────────────────────────────────────────────────
    reward_fn = make_grpo_reward_fn(allowed)

    # ── GRPO config ────────────────────────────────────────────────────────
    cfg_kwargs = dict(GRPO_DEFAULTS)
    cfg_kwargs.update(
        output_dir=str(adapter_out),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.per_device_batch,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.learning_rate,
        beta=args.beta,
        num_generations=args.num_generations,
    )
    grpo_cfg = GRPOConfig(**cfg_kwargs)

    trainer = GRPOTrainer(
        model=policy,
        reward_funcs=reward_fn,
        args=grpo_cfg,
        train_dataset=ds,
        processing_class=tokenizer,
    )

    print("\n=== GRPO training ===")
    trainer.train()
    trainer.save_model(str(adapter_out))
    print(f"\nGRPO adapter saved → {adapter_out}")


if __name__ == "__main__":
    main()
