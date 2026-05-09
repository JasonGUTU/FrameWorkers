#!/usr/bin/env python3
"""Rename hard_004 → cr_104, hard_007 → cr_107 for visual consistency with cr_*.

Numbering: keep the original 04 / 07 suffix, add +100 offset to avoid colliding
with cr_001..cr_076 in the source pool. Original name preserved in
`_meta.original_name` for audit.

Note: hard_021 (storytelling) is NOT renamed here — left as-is per user
guidance ("题材没啥问题目前" applied only to topic content; rename was scoped
to the cr_* category alignment issue).
"""
from __future__ import annotations
import json
from pathlib import Path

RENAME = {
    "hard_004": "cr_104",
    "hard_007": "cr_107",
}


def main() -> None:
    here = Path(__file__).parent.resolve()
    src = here / "selection.json"
    data = json.loads(src.read_text())

    renamed = 0
    for c in data:
        if c["name"] in RENAME:
            old = c["name"]
            c["name"] = RENAME[old]
            c["_meta"]["original_name"] = old
            renamed += 1

    src.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    # Regenerate selection.md (same logic as 01_rewrite_cr_intake.py)
    md: list[str] = [
        "# 30-case selection (seed=42, cr+intake_img rewritten + 2 hard_* renamed 2026-05-09)\n\n",
        "Source: `eval_cases_v4500_balanced.json`\n",
        "Total: 30 (10 per category × 3 categories)\n",
        f"Rewritten: cr (10) + intake_img (10) → 中文短剧爆款; storytelling (10) untouched\n",
        f"Renamed: hard_004 → cr_104, hard_007 → cr_107\n\n",
    ]
    for cat in ["cr", "intake_img", "storytelling"]:
        cat_picks = [c for c in data if c["category"] == cat]
        cat_picks_sorted = sorted(cat_picks, key=lambda c: c["name"])
        shape_set = sorted({c["_meta"]["shape_layers_str"] for c in cat_picks})
        rw_count = sum(1 for c in cat_picks if c["_meta"].get("rewritten"))
        md.append(f"## {cat} ({len(cat_picks)}, rewritten={rw_count})\n")
        md.append(f"- unique shapes: **{len(shape_set)}**\n\n")
        md.append("| name | layers | user_goal |\n|---|---|---|\n")
        for c in cat_picks_sorted:
            m = c["_meta"]
            goal = c["user_goal"][:140].replace("|", r"\|")
            if len(c["user_goal"]) > 140:
                goal += "..."
            md.append(f"| `{c['name']}` | {m['shape_layer_count']} | {goal} |\n")
        md.append("\n")
    (here / "selection.md").write_text("".join(md))

    print(f"Renamed {renamed} cases: {RENAME}")


if __name__ == "__main__":
    main()
