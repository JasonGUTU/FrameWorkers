"""Inference smoke test: load trained adapter → generate plan → verify E2E.

Runs the trained model on a fresh user_goal (not in eval, not in train),
forces JSON output, parses via router._parse_plan, and reports success.

Usage (on GPU node):
    PYTHONPATH=. python training/director/infer.py --adapter adapters_full/dpo
    PYTHONPATH=. python training/director/infer.py --adapter adapters_full/sft
    PYTHONPATH=. python training/director/infer.py --adapter-none  # base model only
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))


# Held-out test goals — none of these are in the 100-case eval set or the
# 5-case training set. Designed to exercise each of the 3 known bias types.
TEST_GOALS = [
    # Audio-only on existing video — should NOT trigger creative chain
    ("Add a melancholic erhu background music track to this period drama clip.",
     "IntakeVideo → Music → AudioMix → Compositor"),
    # Pure video extension — should end at VideoExtend, NO Compositor
    ("Extend this memory-flashback scene of the male lead by 10 more seconds.",
     "IntakeVideo → VideoExtend"),
    # Audio-only — Music, NOT Ambience
    ("Add a gentle violin background music track to this urban-romance clip.",
     "IntakeVideo → Music → AudioMix → Compositor"),
]


def _build_system_prompt():
    """Same system prompt shape used in training samples."""
    from training.director.gen_samples import build_system_prompt
    return build_system_prompt()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-model", default="Qwen/Qwen3-8B")
    ap.add_argument("--adapter", default=None,
                    help="Path (relative to training/director/) to LoRA adapter, or unset for base model only.")
    ap.add_argument("--adapter-none", action="store_true",
                    help="Explicitly run without any LoRA adapter (base model baseline).")
    ap.add_argument("--max-new-tokens", type=int, default=1024)
    args = ap.parse_args()

    # Heavy imports guarded
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    from director_agent.router import _parse_plan  # noqa
    from agents import get_agent_registry

    root = Path(__file__).parent
    registry = get_agent_registry()
    allowed = [
        info.get("id") or info.get("name")
        for info in registry.get_all_agents_info()
    ]

    print(f"Loading base model: {args.base_model}")
    tokenizer = AutoTokenizer.from_pretrained(args.base_model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        args.base_model, torch_dtype=torch.bfloat16, device_map="auto",
    )

    if args.adapter and not args.adapter_none:
        from peft import PeftModel
        adapter_path = (root / args.adapter).resolve()
        print(f"Loading adapter: {adapter_path}")
        model = PeftModel.from_pretrained(model, str(adapter_path))
    else:
        print("No adapter loaded (base model baseline).")

    model.eval()
    system_prompt = _build_system_prompt()

    results = []
    for user_goal, expected_shape in TEST_GOALS:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_goal},
        ]
        prompt_text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True,
            enable_thinking=False,  # Qwen3 — direct JSON output, no <think> wrapper
        )
        inputs = tokenizer(prompt_text, return_tensors="pt").to(model.device)

        with torch.no_grad():
            out = model.generate(
                **inputs,
                max_new_tokens=args.max_new_tokens,
                do_sample=False,
                temperature=0.0,
                pad_token_id=tokenizer.pad_token_id,
            )
        prompt_len = inputs.input_ids.shape[1]
        n_new_tokens = out.shape[1] - prompt_len
        full = tokenizer.decode(out[0], skip_special_tokens=True)
        # Extract generated part (after the prompt)
        response = full[len(tokenizer.decode(inputs.input_ids[0], skip_special_tokens=True)):].strip()
        print(f"    n_new_tokens: {n_new_tokens} (cap {args.max_new_tokens})")

        # Parse
        parse_ok = False
        plan_summary = None
        chain_str = ""
        try:
            obj = json.loads(response)
            spec_plan = _parse_plan(obj, allowed, max_steps=20)
            plan_summary = [(s.agent_id, (s.intent or "")[:40]) for s in spec_plan]
            chain_str = " → ".join(s.agent_id.replace("Agent", "") for s in spec_plan)
            parse_ok = True
        except Exception as e:
            plan_summary = f"parse error: {type(e).__name__}: {e}"

        print(f"\n--- user_goal: {user_goal}")
        print(f"    expected shape: {expected_shape}")
        print(f"    actual chain:   {chain_str or plan_summary}")
        print(f"    parse_ok: {parse_ok}")
        results.append({
            "user_goal": user_goal,
            "expected": expected_shape,
            "actual": chain_str,
            "parse_ok": parse_ok,
            "raw_response": response[:500],
        })

    # Summary
    n_parse_ok = sum(1 for r in results if r["parse_ok"])
    print(f"\n=== Inference smoke summary ===")
    print(f"parse_ok: {n_parse_ok}/{len(results)}")

    # Dump for later inspection
    out_path = root / "infer_smoke_results.json"
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
