"""Validate smoke training samples against 5 downstream-compat checks.

Checks:
  1. Token length: prompt + completion fits in seq_len (tries real Qwen
     tokenizer; falls back to a char-based estimate with conservative mult).
  2. JSON schema: assistant.content parses via json.loads AND matches
     PLAN_UPFRONT_SYSTEM output schema (keys `plan` + `rationale`;
     plan is a list of {agent_id, intent}; agent_ids in AGENT_REGISTRY).
  3. DPO length balance: chosen vs rejected token-count delta ≤ 10%
     (avoid DPO trivially learning "longer = better").
  4. Chat template render: apply_chat_template produces valid text
     with the assistant JSON still parseable (catches special-token
     escaping bugs). Skipped if no tokenizer.
  5. Train/eval isolation: no training user_goal appears in the eval
     set `evals/director_routing/eval_cases.json` (exact or normalized
     match).

Usage:
    PYTHONPATH=. python training/director/validate.py
    PYTHONPATH=. python training/director/validate.py --seq-len 2048
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from agents import get_agent_registry


QWEN_MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"


# ---------------------------------------------------------------------------
# Tokenizer (real or estimated)
# ---------------------------------------------------------------------------

class TokenCounter:
    """Either a real HF tokenizer or a char-based estimator."""

    def __init__(self):
        self.tok = None
        try:
            from transformers import AutoTokenizer  # noqa: WPS433
            self.tok = AutoTokenizer.from_pretrained(QWEN_MODEL_ID)
            self.kind = "real"
        except Exception as exc:
            self.tok = None
            self.kind = "estimate"
            self._warn = f"(no real tokenizer: {type(exc).__name__}: {exc})"

    def count(self, text: str) -> int:
        if self.tok is not None:
            return len(self.tok.encode(text, add_special_tokens=False))
        # Char-based estimate calibrated for Qwen2.5 BBPE:
        #   CJK char    ≈ 1.0 token
        #   Latin char  ≈ 0.25 token
        #   other       ≈ 0.5 token
        cjk = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
        latin = sum(1 for c in text if c.isascii() and (c.isalnum() or c.isspace() or c in "{}[]\":,.-_/"))
        other = len(text) - cjk - latin
        return int(cjk * 1.0 + latin * 0.25 + other * 0.5)

    def apply_chat(self, messages: list[dict]) -> str | None:
        if self.tok is None:
            return None
        return self.tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def normalize_goal(g: str) -> str:
    """Lowercase + strip whitespace + drop punctuation for fuzzy isolation check."""
    s = (g or "").lower().strip()
    return re.sub(r"[\s，。,！!？?、；;：:]+", "", s)


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_token_length(samples_sft, samples_dpo, counter, seq_len):
    fails = []
    # SFT: count full prompt + completion
    for i, rec in enumerate(samples_sft):
        concat = "\n".join(m["content"] for m in rec["messages"])
        n = counter.count(concat)
        if n > seq_len:
            fails.append(f"SFT #{i+1}: {n} tokens > {seq_len}")
    # DPO: count prompt + chosen (worst of the two), and prompt + rejected
    for i, rec in enumerate(samples_dpo):
        prompt_txt = "\n".join(m["content"] for m in rec["prompt"])
        for side in ("chosen", "rejected"):
            resp_txt = "\n".join(m["content"] for m in rec[side])
            n = counter.count(prompt_txt + "\n" + resp_txt)
            if n > seq_len:
                fails.append(f"DPO #{i+1} ({side}): {n} tokens > {seq_len}")
    return fails


def check_json_schema(samples_sft, samples_dpo, allowed_agent_ids):
    fails = []

    def _validate_assistant(content: str, label: str):
        # JSON must parse
        try:
            obj = json.loads(content)
        except json.JSONDecodeError as e:
            return [f"{label}: invalid JSON ({e})"]
        problems = []
        # Must have plan + rationale
        for key in ("plan", "rationale"):
            if key not in obj:
                problems.append(f"{label}: missing key `{key}`")
        plan = obj.get("plan") or []
        if not isinstance(plan, list) or not plan:
            problems.append(f"{label}: plan must be a non-empty list")
        else:
            seen = set()
            for j, step in enumerate(plan):
                if not isinstance(step, dict):
                    problems.append(f"{label}: plan[{j}] must be dict")
                    continue
                aid = step.get("agent_id")
                if aid not in allowed_agent_ids:
                    problems.append(f"{label}: plan[{j}].agent_id `{aid}` not in registry")
                if aid in seen:
                    problems.append(f"{label}: agent_id `{aid}` appears twice")
                seen.add(aid)
                if "intent" not in step:
                    problems.append(f"{label}: plan[{j}] missing `intent`")
        return problems

    for i, rec in enumerate(samples_sft):
        assistant = rec["messages"][-1]
        if assistant["role"] != "assistant":
            fails.append(f"SFT #{i+1}: last message role != assistant")
            continue
        fails.extend(_validate_assistant(assistant["content"], f"SFT #{i+1}"))

    for i, rec in enumerate(samples_dpo):
        for side in ("chosen", "rejected"):
            msg = rec[side][0]
            if msg["role"] != "assistant":
                fails.append(f"DPO #{i+1} ({side}): role != assistant")
                continue
            fails.extend(_validate_assistant(msg["content"], f"DPO #{i+1} ({side})"))
    return fails


def check_dpo_length_balance(samples_dpo, counter, tol=0.10):
    fails = []
    for i, rec in enumerate(samples_dpo):
        c_len = counter.count(rec["chosen"][0]["content"])
        r_len = counter.count(rec["rejected"][0]["content"])
        delta = abs(c_len - r_len) / max(c_len, r_len)
        if delta > tol:
            fails.append(
                f"DPO #{i+1}: chosen={c_len}, rejected={r_len}, "
                f"delta={delta:.1%} > {tol:.0%}"
            )
    return fails


def check_chat_template_render(samples_sft, samples_dpo, counter):
    """Apply chat template; assert assistant JSON still parses after rendering."""
    if counter.tok is None:
        return None  # skipped
    fails = []

    def _assert_render_ok(messages, label):
        rendered = counter.apply_chat(messages)
        if not rendered or not rendered.strip():
            fails.append(f"{label}: empty after chat template render")
            return
        # Find the assistant JSON in the rendered text and try to parse it.
        last_assistant = None
        for m in reversed(messages):
            if m["role"] == "assistant":
                last_assistant = m["content"]
                break
        if last_assistant is None:
            return
        if last_assistant not in rendered:
            fails.append(f"{label}: assistant content not found verbatim in rendered chat")
            return
        try:
            json.loads(last_assistant)
        except json.JSONDecodeError as e:
            fails.append(f"{label}: assistant content no longer valid JSON ({e})")

    for i, rec in enumerate(samples_sft):
        _assert_render_ok(rec["messages"], f"SFT #{i+1}")
    for i, rec in enumerate(samples_dpo):
        for side in ("chosen", "rejected"):
            msgs = list(rec["prompt"]) + list(rec[side])
            _assert_render_ok(msgs, f"DPO #{i+1} ({side})")
    return fails


def check_eval_isolation(samples_sft, samples_dpo, eval_cases_path: Path):
    fails = []
    eval_cases = json.loads(eval_cases_path.read_text(encoding="utf-8"))
    eval_goals = {normalize_goal(c["user_goal"]) for c in eval_cases}

    def _user_goal(messages_or_prompt):
        for m in messages_or_prompt:
            if m["role"] == "user":
                return m["content"]
        return None

    for i, rec in enumerate(samples_sft):
        g = _user_goal(rec["messages"])
        if normalize_goal(g) in eval_goals:
            fails.append(f"SFT #{i+1}: user_goal matches an eval case: {g}")
    for i, rec in enumerate(samples_dpo):
        g = _user_goal(rec["prompt"])
        if normalize_goal(g) in eval_goals:
            fails.append(f"DPO #{i+1}: user_goal matches an eval case: {g}")
    return fails


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seq-len", type=int, default=4096)
    ap.add_argument("--sft", default="samples_sft_full.jsonl",
                    help="SFT jsonl filename (relative to training/director/) or absolute path")
    ap.add_argument("--dpo", default="samples_dpo_full.jsonl",
                    help="DPO jsonl filename (relative to training/director/) or absolute path")
    args = ap.parse_args()

    base = Path(__file__).parent
    sft_path = Path(args.sft) if Path(args.sft).is_absolute() else base / args.sft
    dpo_path = Path(args.dpo) if Path(args.dpo).is_absolute() else base / args.dpo
    eval_path = REPO_ROOT / "evals/director_routing/eval_cases.json"

    samples_sft = load_jsonl(sft_path)
    samples_dpo = load_jsonl(dpo_path)
    registry = get_agent_registry()
    allowed_agent_ids = {
        info.get("id") or info.get("name")
        for info in registry.get_all_agents_info()
    }

    counter = TokenCounter()
    print(f"Tokenizer: {counter.kind}")
    if counter.kind == "estimate":
        print(f"  {counter._warn}")
    print(f"SFT samples: {len(samples_sft)} | DPO pairs: {len(samples_dpo)}")
    print(f"seq_len budget: {args.seq_len}")
    print(f"allowed agent_ids: {len(allowed_agent_ids)}")
    print()

    any_fail = False
    for name, result in [
        ("1. Token length",          check_token_length(samples_sft, samples_dpo, counter, args.seq_len)),
        ("2. JSON schema",           check_json_schema(samples_sft, samples_dpo, allowed_agent_ids)),
        ("3. DPO length balance",    check_dpo_length_balance(samples_dpo, counter)),
        ("4. Chat template render",  check_chat_template_render(samples_sft, samples_dpo, counter)),
        ("5. Train/eval isolation",  check_eval_isolation(samples_sft, samples_dpo, eval_path)),
    ]:
        if result is None:
            print(f"{name}: SKIPPED (no tokenizer)")
            continue
        if not result:
            print(f"{name}: PASS")
        else:
            any_fail = True
            print(f"{name}: FAIL ({len(result)})")
            for msg in result:
                print(f"    • {msg}")

    # Also print aggregate token stats (useful for sizing real training)
    print()
    print("=== Token counts (informational) ===")
    sft_lens = [counter.count("\n".join(m["content"] for m in r["messages"])) for r in samples_sft]
    print(f"SFT: min={min(sft_lens)}  median={sorted(sft_lens)[len(sft_lens)//2]}  max={max(sft_lens)}")
    dpo_lens = []
    for r in samples_dpo:
        prompt = "\n".join(m["content"] for m in r["prompt"])
        for side in ("chosen", "rejected"):
            resp = "\n".join(m["content"] for m in r[side])
            dpo_lens.append(counter.count(prompt + "\n" + resp))
    if dpo_lens:
        print(f"DPO: min={min(dpo_lens)}  median={sorted(dpo_lens)[len(dpo_lens)//2]}  max={max(dpo_lens)}")
    else:
        print("DPO: (none)")

    sys.exit(1 if any_fail else 0)


if __name__ == "__main__":
    main()
