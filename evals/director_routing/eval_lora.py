#!/usr/bin/env python3
"""Eval trained director-routing LoRA adapter on the 100-case held-out set.

Loads Qwen2.5-7B-Instruct + PeftModel(adapter), runs ``plan_pipeline_upfront``
semantics LOCALLY (no OpenRouter / LiteLLM), and scores chains with the same
positional-set-match logic as ``eval_routing.py``.

System prompt is the bare variant (PLAN_UPFRONT_SYSTEM_BARE + compact catalog) —
matches what the training pipeline produces. Apples-to-apples baseline is the
bare Gemini run (FW_TOPOLOGY=0 + --no-fewshots).

Usage (on GPU node with the training-env conda activated):
    PYTHONPATH=. python evals/director_routing/eval_lora.py \\
        --adapter training/director/adapters_full/dpo --name lora_dpo

Results are written to ``Runtime/eval_routing/<timestamp>_<name>.json`` —
same schema as ``eval_routing.py`` so the ``director.html`` snapshot loader
can pick them up.
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from evals.director_routing.eval_routing import (  # noqa: E402
    _build_step_records,
    _chain_edit_distance,
    _slot_set,
    _strip_trailing_done,
    export_gt_csv,
    load_cases,
)

DEFAULT_CASES_PATH = SCRIPT_DIR / "eval_cases.json"
DEFAULT_GT_CSV = SCRIPT_DIR / "eval_gt_table.csv"
RUNTIME_DIR = REPO_ROOT / "Runtime" / "eval_routing"


# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------


def load_policy(base_model: str, adapter_path: Optional[str]):
    """Load base model + (optional) LoRA adapter. Returns (model, tokenizer)."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"Loading base model: {base_model}")
    tok = AutoTokenizer.from_pretrained(base_model)
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )

    if adapter_path:
        from peft import PeftModel
        adapter_abs = Path(adapter_path)
        if not adapter_abs.is_absolute():
            adapter_abs = (REPO_ROOT / adapter_abs).resolve()
        print(f"Loading adapter:    {adapter_abs}")
        model = PeftModel.from_pretrained(model, str(adapter_abs))

    model.eval()
    return model, tok


# ---------------------------------------------------------------------------
# Generation + plan parsing
# ---------------------------------------------------------------------------


def _build_system_prompt() -> str:
    from training.director.gen_samples import build_system_prompt
    return build_system_prompt()


def _extract_json_object(text: str) -> Optional[str]:
    """Find the first balanced {...} block in text. Returns None if absent."""
    i = text.find("{")
    if i == -1:
        return None
    depth = 0
    in_str = False
    esc = False
    for j in range(i, len(text)):
        ch = text[j]
        if esc:
            esc = False
            continue
        if ch == "\\":
            esc = True
            continue
        if ch == '"':
            in_str = not in_str
            continue
        if in_str:
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[i : j + 1]
    return None


def generate_plan(
    model,
    tok,
    system_prompt: str,
    user_goal: str,
    *,
    max_new_tokens: int = 1024,
) -> tuple[List[str], Optional[str], str]:
    """Greedy-decode a plan. Returns (chain, error, raw_completion)."""
    import torch

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_goal},
    ]
    inputs = tok.apply_chat_template(
        messages,
        add_generation_prompt=True,
        return_tensors="pt",
        return_dict=True,
    )
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    with torch.inference_mode():
        out = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            temperature=1.0,
            pad_token_id=tok.eos_token_id,
        )
    prompt_len = inputs["input_ids"].shape[1]
    completion = tok.decode(out[0, prompt_len:], skip_special_tokens=True)

    blob = _extract_json_object(completion)
    if blob is None:
        return [], "no JSON object in completion", completion
    try:
        data = json.loads(blob)
    except json.JSONDecodeError as exc:
        return [], f"JSON decode failed: {exc}", completion

    from director_agent.router import _parse_plan
    from agents import get_agent_registry
    allowed = [
        info.get("id") or info.get("name")
        for info in get_agent_registry().get_all_agents_info()
    ]
    try:
        specs = _parse_plan(data, allowed, max_steps=20)
    except Exception as exc:
        return [], f"_parse_plan failed: {exc}", completion
    return [s.agent_id for s in specs], None, completion


# ---------------------------------------------------------------------------
# Case runner + aggregation
# ---------------------------------------------------------------------------


def evaluate_case(
    model,
    tok,
    system_prompt: str,
    case: Dict[str, Any],
    *,
    max_new_tokens: int,
) -> Dict[str, Any]:
    expected_raw = case["expected_chain"]
    expected = [_slot_set(s) for s in _strip_trailing_done(expected_raw)]

    t0 = time.time()
    actual, error, _raw = generate_plan(
        model, tok, system_prompt, case["user_goal"],
        max_new_tokens=max_new_tokens,
    )
    elapsed = time.time() - t0

    steps, correct_steps, total_steps = _build_step_records(actual, expected)
    length_match = len(actual) == len(expected)
    chain_correct = length_match and correct_steps == len(actual) and not error
    edit_distance = _chain_edit_distance(actual, expected)

    return {
        "name": case["name"],
        "user_goal": case["user_goal"],
        "expected_chain_len": len(expected),
        "actual_chain_len": len(actual),
        "length_match": length_match,
        "total_steps": total_steps,
        "correct_steps": correct_steps,
        "chain_correct": chain_correct,
        "edit_distance": edit_distance,
        "actual_chain": actual,
        "steps": steps,
        "elapsed_s": round(elapsed, 2),
        "error": error,
    }


def run(
    *,
    adapter: Optional[str],
    base_model: str,
    cases_path: Path,
    name: Optional[str],
    max_new_tokens: int,
) -> None:
    cases = load_cases(str(cases_path))
    export_gt_csv(cases, str(DEFAULT_GT_CSV))

    system_prompt = _build_system_prompt()
    model, tok = load_policy(base_model, adapter)

    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_tag = name or (Path(adapter).name if adapter else "base")
    output_path = RUNTIME_DIR / f"{ts}_lora_{model_tag}.json"

    total_expected_steps = sum(
        len(_strip_trailing_done(c["expected_chain"])) for c in cases
    )
    print(f"Adapter:    {adapter or '<none — base model only>'}")
    print(f"Prompt:     bare (system prompt len={len(system_prompt)} chars)")
    print(f"Cases:      {len(cases)}")
    print(f"GT slots:   {total_expected_steps}")
    print(f"Output:     {output_path}")
    print("=" * 90)

    t_start = time.time()
    results: List[Dict[str, Any]] = []
    for i, case in enumerate(cases, 1):
        r = evaluate_case(model, tok, system_prompt, case,
                          max_new_tokens=max_new_tokens)
        results.append(r)
        mark = "OK " if r["chain_correct"] else "XX "
        print(
            f"[{i:3d}/{len(cases)}] {mark} {r['name'][:40]:40s} "
            f"{r['correct_steps']}/{r['total_steps']} "
            f"(edit={r['edit_distance']}, {r['elapsed_s']}s)"
        )

    total_elapsed = time.time() - t_start
    n_chain_correct = sum(1 for r in results if r["chain_correct"])
    chain_accuracy = n_chain_correct / len(cases) if cases else 0.0
    sum_correct_steps = sum(r["correct_steps"] for r in results)
    sum_total_steps = sum(r["total_steps"] for r in results)
    step_accuracy = sum_correct_steps / sum_total_steps if sum_total_steps else 0.0
    mean_edit = statistics.mean(r["edit_distance"] for r in results) if results else 0.0
    perfect_edit = sum(1 for r in results if r["edit_distance"] == 0)
    errors = [r["name"] for r in results if r["error"]]

    # Match eval_routing.py's legacy schema so director.html can load this
    # without a schema branch. The LoRA-specific fields go in `meta` too.
    length_match_count = sum(1 for r in results if r["length_match"])
    summary = {
        "meta": {
            "model": f"lora:{model_tag}",
            "timestamp": ts,
            "name": name or model_tag,
            "elapsed_s": round(total_elapsed, 2),
            "workers": 1,
            "max_steps": 20,
            "total_chains": len(cases),
            "perfect_chains": n_chain_correct,
            "chain_accuracy_pct": round(chain_accuracy * 100, 1),
            "total_steps": sum_total_steps,
            "correct_steps": sum_correct_steps,
            "step_accuracy_pct": round(step_accuracy * 100, 1),
            "length_match_count": length_match_count,
            "length_match_pct": round(length_match_count / len(cases) * 100, 1) if cases else 0.0,
            "mean_edit_distance": round(mean_edit, 2),
            "median_edit_distance": statistics.median(r["edit_distance"] for r in results) if results else 0,
            "planner_errors": errors,
            "base_model": base_model,
            "adapter": adapter,
            "perfect_edit_count": perfect_edit,
        },
        "results": results,
    }
    output_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print("=" * 90)
    print(f"chain_accuracy     : {chain_accuracy:.3f}  ({n_chain_correct}/{len(cases)})")
    print(f"step_accuracy      : {step_accuracy:.3f}  ({sum_correct_steps}/{sum_total_steps})")
    print(f"mean edit distance : {mean_edit:.2f}")
    print(f"perfect edit count : {perfect_edit}/{len(cases)}")
    print(f"total elapsed      : {total_elapsed:.1f}s")
    print(f"results            : {output_path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--adapter", default=None,
                    help="Path to LoRA adapter dir. Omit for base-model-only baseline.")
    ap.add_argument("--base-model", default="Qwen/Qwen2.5-7B-Instruct")
    ap.add_argument("--cases", type=Path, default=DEFAULT_CASES_PATH)
    ap.add_argument("--name", default=None,
                    help="Optional label suffix for the results JSON.")
    ap.add_argument("--max-new-tokens", type=int, default=1024)
    args = ap.parse_args()
    run(
        adapter=args.adapter,
        base_model=args.base_model,
        cases_path=args.cases,
        name=args.name,
        max_new_tokens=args.max_new_tokens,
    )


if __name__ == "__main__":
    main()
