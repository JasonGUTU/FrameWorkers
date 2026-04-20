"""Two-stage LoRA smoke training: SFT → DPO on 5+5 samples.

Purpose: prove the training pipeline is wired end-to-end (tokenizer,
chat template, loss, optimizer, adapter save/load) BEFORE scaling to
1000 SFT + 500 DPO. Not about learning — 5 samples won't generalize.

Stage 1 (SFT):
    Full sample (system + user + assistant) through SFTTrainer with
    completion-only loss (prompt tokens get -100, assistant JSON gets
    cross-entropy). Trains LoRA adapters on Qwen2.5-7B-Instruct.

Stage 2 (DPO):
    Same base model, loads the SFT adapter as initial policy + frozen
    reference. Runs DPOTrainer on 5 (prompt, chosen, rejected) triples.

Output:
    training/director/adapters/sft/       — LoRA weights after SFT
    training/director/adapters/dpo/       — LoRA weights after SFT + DPO

Usage (on GPU node, after `conda activate frameworkers` + deps installed):
    PYTHONPATH=. python training/director/train_lora.py
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


# ---------------------------------------------------------------------------
# Config (small numbers: this is a smoke test, not real training)
# ---------------------------------------------------------------------------

BASE_MODEL = "Qwen/Qwen2.5-7B-Instruct"
SEQ_LEN = 4096

LORA_CONFIG = dict(
    r=32,
    lora_alpha=64,
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
)

SFT_CONFIG = dict(
    learning_rate=2e-5,
    num_train_epochs=3,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,   # effective batch = 4 (small dataset)
    bf16=True,
    logging_steps=1,
    save_strategy="epoch",
    report_to="none",
    max_length=SEQ_LEN,
)

DPO_CONFIG = dict(
    learning_rate=5e-7,
    num_train_epochs=1,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    bf16=True,
    beta=0.1,
    logging_steps=1,
    save_strategy="epoch",
    report_to="none",
    max_length=SEQ_LEN,
)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["sft", "dpo", "both"], default="both")
    ap.add_argument("--base-model", default=BASE_MODEL)
    args = ap.parse_args()

    root = Path(__file__).parent
    adapter_dir = root / "adapters"
    adapter_dir.mkdir(exist_ok=True)

    # Heavy imports are inside main so `--help` works without GPU libs installed
    import torch
    from datasets import load_dataset
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import LoraConfig

    print(f"Loading base model: {args.base_model}")
    tokenizer = AutoTokenizer.from_pretrained(args.base_model)
    # Qwen 2.5 default pad is eos — fine for training
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # -----------------------------------------------------------------------
    # Stage 1: SFT
    # -----------------------------------------------------------------------
    if args.stage in ("sft", "both"):
        from trl import SFTConfig, SFTTrainer

        print("\n=== Stage 1: SFT on 5 samples ===")
        sft_ds = load_dataset(
            "json",
            data_files=str(root / "samples_sft.jsonl"),
            split="train",
        )
        print(f"SFT dataset: {len(sft_ds)} samples")

        model = AutoModelForCausalLM.from_pretrained(
            args.base_model,
            torch_dtype=torch.bfloat16,
            device_map="auto",
        )

        sft_output = adapter_dir / "sft"
        sft_config = SFTConfig(
            output_dir=str(sft_output),
            **SFT_CONFIG,
        )
        trainer = SFTTrainer(
            model=model,
            processing_class=tokenizer,
            train_dataset=sft_ds,
            args=sft_config,
            peft_config=LoraConfig(**LORA_CONFIG),
        )
        trainer.train()
        trainer.save_model(str(sft_output))
        print(f"SFT adapter saved: {sft_output}")

        # Free memory before DPO
        del trainer, model
        torch.cuda.empty_cache() if torch.cuda.is_available() else None

    # -----------------------------------------------------------------------
    # Stage 2: DPO (starts from the SFT adapter)
    # -----------------------------------------------------------------------
    if args.stage in ("dpo", "both"):
        from trl import DPOConfig, DPOTrainer
        from peft import PeftModel

        print("\n=== Stage 2: DPO on 5 pairs (starting from SFT adapter) ===")
        dpo_ds = load_dataset(
            "json",
            data_files=str(root / "samples_dpo.jsonl"),
            split="train",
        )
        print(f"DPO dataset: {len(dpo_ds)} pairs")

        # Policy model = base + SFT adapter (trainable)
        policy = AutoModelForCausalLM.from_pretrained(
            args.base_model,
            torch_dtype=torch.bfloat16,
            device_map="auto",
        )
        sft_adapter = adapter_dir / "sft"
        if sft_adapter.exists():
            policy = PeftModel.from_pretrained(
                policy, str(sft_adapter), is_trainable=True,
            )
        else:
            print(f"WARN: no SFT adapter at {sft_adapter}, running DPO from base model directly")

        dpo_output = adapter_dir / "dpo"
        dpo_config = DPOConfig(
            output_dir=str(dpo_output),
            **DPO_CONFIG,
        )
        dpo_trainer = DPOTrainer(
            model=policy,
            ref_model=None,         # TRL uses the frozen base when peft is active
            processing_class=tokenizer,
            train_dataset=dpo_ds,
            args=dpo_config,
        )
        dpo_trainer.train()
        dpo_trainer.save_model(str(dpo_output))
        print(f"DPO adapter saved: {dpo_output}")

    print("\nDone. Next step: training/director/infer.py --adapter adapters/dpo")


if __name__ == "__main__":
    main()
