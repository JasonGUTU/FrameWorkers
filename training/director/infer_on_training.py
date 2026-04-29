"""Run LoRA inference on SFT training data; emit failed records for GRPO mining.

For each training sample in samples_sft_full.templated.jsonl:
  1. Extract (system_prompt, user_goal) from messages[0:2].
  2. Extract gt_chain (flat list of agent_ids) from messages[2].assistant.plan.
  3. Generate predicted plan with LoRA(adapter).
  4. Mark `chain_correct = (predicted_chain == gt_chain)`.

Output:
  - JSONL of every record + verdict (for inspection).
  - JSONL of FAILED records only (chain_correct=False), formatted same as
    SFT training record so it can be appended directly to GRPO data.

Usage:
    PYTHONPATH=. python training/director/infer_on_training.py \\
        --adapter training/director/adapters_grpo_base/qwen3_v3tmpl_e4_step712 \\
        --sft-jsonl training/director/samples_sft_full.templated.jsonl \\
        --out-all training/director/infer_on_training_all.jsonl \\
        --out-fail training/director/infer_on_training_failed.jsonl
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))


def load_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def gt_chain_from_record(rec: dict) -> List[str]:
    """Extract flat ground-truth chain from training record."""
    asst = json.loads(rec["messages"][2]["content"])
    return [step["agent_id"] for step in asst["plan"]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--adapter", required=True,
                    help="Path to LoRA adapter (e.g. adapters_grpo_base/qwen3_v3tmpl_e4_step712)")
    ap.add_argument("--base-model", default="Qwen/Qwen3-8B")
    ap.add_argument("--sft-jsonl", default="training/director/samples_sft_full.templated.jsonl")
    ap.add_argument("--out-all", default="training/director/infer_on_training_all.jsonl",
                    help="JSONL with all records + verdicts (for inspection)")
    ap.add_argument("--out-fail", default="training/director/infer_on_training_failed.jsonl",
                    help="JSONL of failed records only (chain_correct=False)")
    ap.add_argument("--max-new-tokens", type=int, default=1024)
    ap.add_argument("--limit", type=int, default=None,
                    help="Limit to first N samples (for smoke test)")
    args = ap.parse_args()

    # Late-load to avoid torch import at script-help time
    from evals.director_routing.eval_lora import load_policy, generate_plan

    sft_path = REPO_ROOT / args.sft_jsonl if not Path(args.sft_jsonl).is_absolute() else Path(args.sft_jsonl)
    samples = load_jsonl(sft_path)
    if args.limit:
        samples = samples[: args.limit]
    print(f"Loaded {len(samples)} SFT samples from {sft_path}")

    adapter_path = args.adapter if Path(args.adapter).is_absolute() else str(REPO_ROOT / args.adapter)
    print(f"Loading model: {args.base_model}  adapter: {adapter_path}")
    model, tok = load_policy(args.base_model, adapter_path)

    out_all_path = REPO_ROOT / args.out_all if not Path(args.out_all).is_absolute() else Path(args.out_all)
    out_fail_path = REPO_ROOT / args.out_fail if not Path(args.out_fail).is_absolute() else Path(args.out_fail)
    out_all_path.parent.mkdir(parents=True, exist_ok=True)
    out_fail_path.parent.mkdir(parents=True, exist_ok=True)

    n_correct = 0
    n_fail = 0
    n_error = 0
    t_start = time.time()

    with out_all_path.open("w", encoding="utf-8") as f_all, \
         out_fail_path.open("w", encoding="utf-8") as f_fail:
        for i, rec in enumerate(samples):
            system_prompt = rec["messages"][0]["content"]
            user_goal = rec["messages"][1]["content"]
            gt_chain = gt_chain_from_record(rec)

            actual, error, _raw = generate_plan(
                model, tok, system_prompt, user_goal,
                max_new_tokens=args.max_new_tokens,
            )

            chain_correct = (not error) and (actual == gt_chain)
            verdict = {
                "idx": i,
                "user_goal": user_goal,
                "gt_chain": gt_chain,
                "predicted_chain": actual,
                "chain_correct": chain_correct,
                "error": error,
            }
            f_all.write(json.dumps(verdict, ensure_ascii=False) + "\n")
            if not chain_correct:
                # Emit the ORIGINAL SFT record (full messages) so it can be
                # appended directly to GRPO training data.
                f_fail.write(json.dumps(rec, ensure_ascii=False) + "\n")
                n_fail += 1
                if error:
                    n_error += 1
            else:
                n_correct += 1

            if (i + 1) % 50 == 0 or (i + 1) == len(samples):
                elapsed = time.time() - t_start
                rate = (i + 1) / elapsed
                eta = (len(samples) - i - 1) / rate if rate > 0 else 0
                print(f"  [{i+1:4}/{len(samples)}] correct={n_correct} fail={n_fail} "
                      f"err={n_error} | {rate:.2f} sample/s | ETA {eta/60:.1f} min",
                      flush=True)

    print(f"\n=== DONE ===")
    print(f"  total: {len(samples)}")
    print(f"  correct: {n_correct} ({100*n_correct/len(samples):.1f}%)")
    print(f"  failed:  {n_fail} ({100*n_fail/len(samples):.1f}%)")
    print(f"    of which parse errors: {n_error}")
    print(f"  all-records output: {out_all_path}")
    print(f"  failed-only output: {out_fail_path}")


if __name__ == "__main__":
    main()
