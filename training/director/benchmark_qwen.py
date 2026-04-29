"""Benchmark Qwen2.5-7B vs Qwen3-8B token/sec at greedy decode.

Diagnoses whether the GRPO slowdown is fundamentally Qwen3-8B being slower
per-token vs Qwen2.5-7B (separate from rollout-batching / sequence-length
issues). Three settings per model:

  1. Single rollout, batch=1, 300 new tokens
  2. Sequential 4 rollouts, batch=1, 300 new tokens each (= what GRPO does today)
  3. Batched rollout, batch=4, 300 new tokens (= what GRPO would do with batching)
"""
from __future__ import annotations

import time
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


PROMPT = (
    "<|im_start|>system\nYou are a helpful assistant. Generate a JSON plan.<|im_end|>\n"
    "<|im_start|>user\nGenerate a 5-step plan for video creation.<|im_end|>\n"
    "<|im_start|>assistant\n"
)
N_TOKENS = 300


def benchmark(model_name: str, n_tokens: int = N_TOKENS):
    print(f"\n{'='*60}")
    print(f"Loading {model_name}")
    print(f"{'='*60}")

    tok = AutoTokenizer.from_pretrained(model_name)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.bfloat16, device_map={"": 0},
    )

    inputs_single = tok(PROMPT, return_tensors="pt").to(model.device)
    inputs_batched = tok([PROMPT] * 4, return_tensors="pt", padding=True).to(model.device)
    print(f"prompt token len: {inputs_single.input_ids.shape[1]}")

    # ── Warmup ─────────────────────────────────────────────────────────────
    with torch.no_grad():
        _ = model.generate(
            **inputs_single, max_new_tokens=10, do_sample=False,
            pad_token_id=tok.pad_token_id,
        )
    torch.cuda.synchronize()

    # ── Setting 1: single rollout ──────────────────────────────────────────
    torch.cuda.synchronize()
    t0 = time.time()
    with torch.no_grad():
        out = model.generate(
            **inputs_single, max_new_tokens=n_tokens, do_sample=False,
            pad_token_id=tok.pad_token_id,
        )
    torch.cuda.synchronize()
    elapsed_single = time.time() - t0
    n_actual = out.shape[1] - inputs_single.input_ids.shape[1]
    print(f"\n[1] single rollout (batch=1, 1 gen) : "
          f"{n_actual} tok in {elapsed_single:.2f}s "
          f"= {n_actual/elapsed_single:.1f} tok/s")

    # ── Setting 2: sequential 4 rollouts ───────────────────────────────────
    torch.cuda.synchronize()
    t0 = time.time()
    with torch.no_grad():
        for _ in range(4):
            _ = model.generate(
                **inputs_single, max_new_tokens=n_tokens, do_sample=False,
                pad_token_id=tok.pad_token_id,
            )
    torch.cuda.synchronize()
    elapsed_seq = time.time() - t0
    print(f"[2] sequential x4 (batch=1, 4 gen)  : "
          f"{4*n_actual} tok total in {elapsed_seq:.2f}s "
          f"= {4*n_actual/elapsed_seq:.1f} tok/s aggregate")

    # ── Setting 3: batched 4 rollouts ──────────────────────────────────────
    torch.cuda.synchronize()
    t0 = time.time()
    with torch.no_grad():
        out = model.generate(
            **inputs_batched, max_new_tokens=n_tokens, do_sample=False,
            pad_token_id=tok.pad_token_id,
        )
    torch.cuda.synchronize()
    elapsed_batched = time.time() - t0
    n_total_batched = (out.shape[1] - inputs_batched.input_ids.shape[1]) * 4
    print(f"[3] batched rollout (batch=4, 1 gen): "
          f"{n_total_batched} tok total in {elapsed_batched:.2f}s "
          f"= {n_total_batched/elapsed_batched:.1f} tok/s aggregate")

    print(f"\n>>> {model_name}:  "
          f"sequential 4× wall = {elapsed_seq:.2f}s  vs  "
          f"batched 4× wall = {elapsed_batched:.2f}s  "
          f"=> batched speedup {elapsed_seq/elapsed_batched:.2f}×")

    del model
    torch.cuda.empty_cache()


if __name__ == "__main__":
    benchmark("Qwen/Qwen2.5-7B-Instruct")
    benchmark("Qwen/Qwen3-8B")
