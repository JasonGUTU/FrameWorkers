"""Regenerate the system prompt in all v4_500 training files using the
current (post-d8c4aec) agent descriptors.

Why this exists: ``_rebalance_to_v4_500_with_gapfill.py`` extracted the
system prompt from existing samples (``samples_sft_full.no_rationale.jsonl``,
generated 2026-04-30 before d8c4aec) and copy-forwarded it. Result: the v4_500
JSONLs ship a stale catalog (no ``creative_brief`` input on Music/Ambience/etc;
no ``narrator_audio``; old ``duration target`` wording on Music/Ambience).
LoRA trained on stale catalog vs evaluated against live (post-d8c4aec)
catalog breaks the "train prompt ≡ inference prompt" rule from
``training/director/CLAUDE.md``.

What this does: for each v4_500 jsonl, recompute messages[0]["content"] via
``gen_samples.build_system_prompt()`` (or the no_rationale variant),
keeping ``messages[1:]`` (user_goal + assistant) byte-identical. In-place
overwrite.
"""
from __future__ import annotations

import json
from pathlib import Path

from gen_samples import build_system_prompt, build_system_prompt_no_rationale

DIR = Path(__file__).resolve().parent

# (filename, schema variant). Schema variant determines which build helper to
# use; rich + templated both keep ``rationale`` field, no_rationale strips it.
TARGETS = [
    ("samples_sft_full.v4_500.jsonl", "rich"),
    ("samples_sft_full.templated.v4_500.jsonl", "rich"),
    ("samples_sft_full.no_rationale.v4_500.jsonl", "no_rationale"),
    ("samples_grpo_v1.v4_500.jsonl", "rich"),
    ("samples_grpo_v1.templated.v4_500.jsonl", "rich"),
    ("samples_grpo_v1.no_rationale.v4_500.jsonl", "no_rationale"),
]


def regen_one(path: Path, variant: str) -> tuple[int, int]:
    new_sys = (
        build_system_prompt_no_rationale()
        if variant == "no_rationale"
        else build_system_prompt()
    )
    new_sys_chars = len(new_sys)

    out_lines: list[str] = []
    n = 0
    old_sys_chars = None
    with path.open(encoding="utf-8") as f:
        for line in f:
            sample = json.loads(line)
            msgs = sample["messages"]
            if old_sys_chars is None:
                old_sys_chars = len(msgs[0]["content"])
            msgs[0]["content"] = new_sys
            out_lines.append(json.dumps(sample, ensure_ascii=False))
            n += 1

    path.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    return n, old_sys_chars or 0, new_sys_chars


def main() -> None:
    for fname, variant in TARGETS:
        p = DIR / fname
        if not p.exists():
            print(f"  [skip] {fname} not found")
            continue
        n, old_chars, new_chars = regen_one(p, variant)
        print(
            f"  {fname:<55} variant={variant:<13} "
            f"samples={n:>4}  sys_chars  {old_chars} -> {new_chars}"
        )


if __name__ == "__main__":
    main()
