"""Build expanded GRPO training set from base + hard-example failures.

Logic:
  - base = samples_grpo_v1.templated.jsonl (1396 samples)
  - failed = infer_on_training_failed.jsonl (failed cases mined from
    SFT training data via LoRA(checkpoint-712) inference)
  - If len(failed) > cap (default 420): random sample `cap` items
  - If len(failed) <= cap: take all
  - Output: base + sampled_failed (concatenated, NO dedup — failures may
    duplicate templated user_goals; that's intended as implicit upweight)

Usage:
    PYTHONPATH=. python training/director/build_expanded_grpo_data.py \\
        --base training/director/samples_grpo_v1.templated.jsonl \\
        --failed training/director/infer_on_training_failed.jsonl \\
        --cap 420 \\
        --out training/director/samples_grpo_v1.expanded.jsonl
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def load_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="training/director/samples_grpo_v1.templated.jsonl")
    ap.add_argument("--failed", default="training/director/infer_on_training_failed.jsonl")
    ap.add_argument("--cap", type=int, default=420,
                    help="Max number of failed samples to include (random subsample if more)")
    ap.add_argument("--out", default="training/director/samples_grpo_v1.expanded.jsonl")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    def resolve(p: str) -> Path:
        path = Path(p)
        return path if path.is_absolute() else REPO_ROOT / p

    base_path = resolve(args.base)
    failed_path = resolve(args.failed)
    out_path = resolve(args.out)

    base = load_jsonl(base_path)
    failed = load_jsonl(failed_path)
    print(f"base    ({base_path.name}): {len(base)} samples")
    print(f"failed  ({failed_path.name}): {len(failed)} samples")
    print(f"cap: {args.cap}")

    if len(failed) > args.cap:
        random.seed(args.seed)
        sampled_failed = random.sample(failed, args.cap)
        print(f"  → random.sample {args.cap} of {len(failed)} (seed={args.seed})")
    else:
        sampled_failed = failed
        print(f"  → take all {len(failed)} (≤ cap)")

    expanded = base + sampled_failed
    print(f"expanded total: {len(expanded)} = {len(base)} base + {len(sampled_failed)} hard")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for rec in expanded:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"WROTE: {out_path}")


if __name__ == "__main__":
    main()
