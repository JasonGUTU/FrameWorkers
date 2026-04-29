"""SFT-only LoRA training on director-routing samples.

Output:
    training/director/adapters_full/sft/  — LoRA weights after SFT

The RL stage (previously TRL-based GRPO) was retired 2026-04-25 after
repeated bf16 multinomial NaN crashes; the algorithm is being redesigned
from scratch and is not in this repo right now. SFT is currently the
only training stage.

Usage (on GPU node, after `conda activate director-train` + deps installed):
    PYTHONPATH=. python training/director/train_sft.py
"""

from __future__ import annotations

import argparse
from pathlib import Path


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

BASE_MODEL = "Qwen/Qwen3-8B"
# Full-descriptor system prompt is ~7.5K tokens; 8192 gives ~700 tokens of
# headroom for the assistant-side rationale+plan response.
SEQ_LEN = 8192

LORA_CONFIG = dict(
    r=32,
    lora_alpha=64,
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
)

SFT_CONFIG_DEFAULTS = dict(
    learning_rate=2e-5,
    bf16=True,
    logging_steps=10,
    save_strategy="epoch",
    save_total_limit=1,          # keep only the latest checkpoint (user pref — saves disk)
    report_to="none",
    max_length=SEQ_LEN,
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-model", default=BASE_MODEL)
    ap.add_argument("--sft-path", default=None,
                    help="JSONL path (default: samples_sft_full.jsonl beside this script)")
    ap.add_argument("--adapter-dir", default=None,
                    help="adapter output dir (default: adapters_full/ beside this script)")
    ap.add_argument("--sft-epochs", type=int, default=3)
    ap.add_argument("--per-device-batch", type=int, default=1)
    ap.add_argument("--grad-accum", type=int, default=4)
    ap.add_argument("--resume-from-checkpoint", default=None,
                    help="Path to checkpoint dir to resume from (e.g. "
                         "adapters_overfit_templated/qwen3_20260427_005706/sft/checkpoint-712), "
                         "or 'auto' to auto-detect latest checkpoint in --adapter-dir/sft/")
    args = ap.parse_args()

    root = Path(__file__).parent
    adapter_dir = Path(args.adapter_dir) if args.adapter_dir else root / "adapters_full"
    adapter_dir.mkdir(exist_ok=True, parents=True)
    sft_data_path = Path(args.sft_path) if args.sft_path else root / "samples_sft_full.jsonl"

    # Heavy imports inside main so `--help` works without GPU libs installed.
    import torch
    from datasets import load_dataset
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import LoraConfig
    from trl import SFTConfig, SFTTrainer

    print(f"Loading base model: {args.base_model}")
    tokenizer = AutoTokenizer.from_pretrained(args.base_model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print(f"\n=== SFT ({sft_data_path.name}) ===")
    sft_ds = load_dataset("json", data_files=str(sft_data_path), split="train")
    print(f"SFT dataset: {len(sft_ds)} samples")

    # Pre-render messages → text with enable_thinking=False so SFTTrainer
    # tokenizes raw text (instead of re-applying chat_template at thinking-on
    # default). Keeps train byte-identical to infer.py / eval_lora.py.
    def _render(example):
        return {"text": tokenizer.apply_chat_template(
            example["messages"], tokenize=False, enable_thinking=False,
        )}
    sft_ds = sft_ds.map(_render, remove_columns=["messages"])

    # No device_map — torchrun/accelerate places this rank's model on its own
    # GPU (DDP). device_map="auto" would split layers across GPUs (pipeline
    # parallel) and conflict with DDP under torchrun --nproc_per_node>1.
    model = AutoModelForCausalLM.from_pretrained(
        args.base_model,
        torch_dtype=torch.bfloat16,
    )

    sft_output = adapter_dir / "sft"
    sft_config = SFTConfig(
        output_dir=str(sft_output),
        num_train_epochs=args.sft_epochs,
        per_device_train_batch_size=args.per_device_batch,
        gradient_accumulation_steps=args.grad_accum,
        **SFT_CONFIG_DEFAULTS,
    )
    trainer = SFTTrainer(
        model=model,
        processing_class=tokenizer,
        train_dataset=sft_ds,
        args=sft_config,
        peft_config=LoraConfig(**LORA_CONFIG),
    )
    resume_arg = args.resume_from_checkpoint
    if resume_arg == "auto":
        resume_arg = True  # HF Trainer convention — auto-detect latest checkpoint
    elif resume_arg:
        # Caller passes path relative to cwd (= repo root under sbatch) or absolute.
        # Do NOT prefix with script's parent — that double-counts training/director/.
        print(f"Resuming from checkpoint: {resume_arg}")
    trainer.train(resume_from_checkpoint=resume_arg)
    trainer.save_model(str(sft_output))
    print(f"SFT adapter saved: {sft_output}")
    print("\nNext step: RL stage (TBD — being redesigned).")


if __name__ == "__main__":
    main()
