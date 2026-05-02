#!/usr/bin/env python3
"""Generate LaTeX results table from director_routing eval JSON files.

For each eval JSON, computes:
  - Step Success Rate  (sum correct_steps / sum total_steps)
  - Chain Success Rate (correct chains / total cases)

Output: LaTeX `tabular` block printed to stdout.

The script auto-discovers v4500_*.json runs in Runtime/eval_routing/ and pairs
them with the latest gemini baselines on the v3 209-case set. Once v4_500 SFT
and GRPO eval JSONs land, re-run to get the final table.

Usage:
    python gen_results_latex_table.py
    python gen_results_latex_table.py --pick gemini25_pro,gemini3_pro_preview,v4500_grpo_no_rationale,...
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
RUNTIME_DIR = REPO_ROOT / "Runtime/eval_routing"

# Canonical eval-runs to include, in display order.
# Each entry: (display_label, filename_glob_pattern, group)
# group is used for \midrule separation.
CANONICAL_RUNS = [
    # API baselines on v3 209 set — old "canonical" runs, config not fully verified
    ("Gemini-2.5 pro (v3)",        "20260430_180358_gemini25_pro_209_canonical.json", "baseline_v3"),
    ("Gemini-3 pro preview (v3)",  "20260430_180355_gemini3_pro_preview_209_canonical.json", "baseline_v3"),
    # True core-prompt API baselines (FW_TOPOLOGY=0 + --no-fewshots --no-policies, workers=16)
    ("Gemini-2.5 Flash core (v3)", "20260502_140038_gemini25flash_v3_209_core.json", "baseline_core"),
    ("Gemini-2.5 Flash core (v4)", "20260502_135043_gemini25flash_v4500_core.json", "baseline_core"),
    # Best LoRA on v3 209 set
    ("Qwen3-8B SFT (v3)",     "20260430_181000_lora_sft_qwen3_v3tmpl_e4_step712_209.json", "lora_v3"),
    ("Qwen3-8B SFT + GRPO (v3)", "20260501_065510_lora_grpo_qwen3_2gpu_partialreward_from_no_rationale_209.json", "lora_v3"),
    # v4_500 SFT runs (filled in after jobs complete)
    ("Qwen3-8B SFT no-rationale (v4)", "*v4500_sft_no_rationale_*.json",  "v4_sft"),
    ("Qwen3-8B SFT templated (v4)",    "*v4500_sft_templated_*.json",     "v4_sft"),
    ("Qwen3-8B SFT rich (v4)",         "*v4500_sft_rich_*.json",          "v4_sft"),
    # v4_500 GRPO runs
    ("Qwen3-8B SFT + GRPO no-rationale (v4)", "*v4500_grpo_no_rationale_*.json", "v4_grpo"),
    ("Qwen3-8B SFT + GRPO templated (v4)",    "*v4500_grpo_templated_*.json",    "v4_grpo"),
    ("Qwen3-8B SFT + GRPO rich (v4)",         "*v4500_grpo_rich_*.json",         "v4_grpo"),
]


def find_run_file(pattern: str) -> Path | None:
    """Resolve a filename or glob to a single Path. Returns latest match if multiple."""
    if "*" in pattern:
        matches = sorted(RUNTIME_DIR.glob(pattern))
        return matches[-1] if matches else None
    p = RUNTIME_DIR / pattern
    return p if p.exists() else None


def compute_metrics(eval_json: Path) -> tuple[float, float, int]:
    """Return (step_success_rate, chain_success_rate, n_cases). Both rates are 0-100."""
    data = json.loads(eval_json.read_text(encoding="utf-8"))
    results = data.get("results", [])
    if not results:
        return 0.0, 0.0, 0
    total_steps = sum(r.get("total_steps", 0) for r in results)
    correct_steps = sum(r.get("correct_steps", 0) for r in results)
    chain_correct = sum(1 for r in results if r.get("chain_correct"))
    n = len(results)
    step_rate = (correct_steps / total_steps * 100) if total_steps > 0 else 0.0
    chain_rate = (chain_correct / n * 100) if n > 0 else 0.0
    return step_rate, chain_rate, n


def emit_latex(rows: list[tuple[str, str | None, str]]) -> str:
    """Emit a LaTeX tabular block.

    rows: list of (label, file_pattern, group). Missing files render as '—'.
    """
    # Resolve files and metrics
    resolved: list[tuple[str, float | None, float | None, int, str]] = []
    for label, pattern, group in rows:
        f = find_run_file(pattern) if pattern else None
        if f is None:
            resolved.append((label, None, None, 0, group))
        else:
            step, chain, n = compute_metrics(f)
            resolved.append((label, step, chain, n, group))

    # Find best in each column (across all available rows)
    available = [r for r in resolved if r[1] is not None]
    best_step = max((r[1] for r in available), default=0.0)
    best_chain = max((r[2] for r in available), default=0.0)

    # Print
    lines = []
    lines.append(r"\begin{table}[!ht]")
    lines.append(r"\centering")
    lines.append(r"\small")
    lines.append(r"\setlength{\tabcolsep}{5pt}")
    lines.append(r"\begin{tabular}{lcc}")
    lines.append(r"\toprule")
    lines.append(r"\textbf{Method} & \textbf{Step Success} & \textbf{Chain Success} \\")
    lines.append(r"                & \textbf{Rate (\%)}    & \textbf{Rate (\%)} \\")
    lines.append(r"\midrule")

    prev_group = None
    for label, step, chain, n, group in resolved:
        if prev_group is not None and group != prev_group:
            lines.append(r"\midrule")
        prev_group = group

        if step is None:
            step_cell = "—"
            chain_cell = "—"
        else:
            step_cell = f"{step:.1f}"
            chain_cell = f"{chain:.1f}"
            # Bold the best
            if abs(step - best_step) < 0.05:
                step_cell = r"\textbf{" + step_cell + r"}"
            if abs(chain - best_chain) < 0.05:
                chain_cell = r"\textbf{" + chain_cell + r"}"
        lines.append(f"{label:<40} & {step_cell:<14} & {chain_cell} \\\\")

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\caption{Director planning capability across baselines and v4\_500-trained Qwen3-8B variants.}")
    lines.append(r"\label{tab:director_v4_500}")
    lines.append(r"\end{table}")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pick", default=None,
                    help="Comma-separated label substrings to filter (default: all canonical).")
    args = ap.parse_args()

    rows = list(CANONICAL_RUNS)
    if args.pick:
        wanted = [s.strip().lower() for s in args.pick.split(",")]
        rows = [r for r in rows if any(w in r[0].lower() for w in wanted)]

    # Status pre-print to stderr
    import sys
    print("# Run discovery status:", file=sys.stderr)
    for label, pattern, group in rows:
        f = find_run_file(pattern) if pattern else None
        status = f.name if f else "(not found yet)"
        print(f"  [{group}] {label:<45} → {status}", file=sys.stderr)
    print(file=sys.stderr)

    print(emit_latex(rows))


if __name__ == "__main__":
    main()
