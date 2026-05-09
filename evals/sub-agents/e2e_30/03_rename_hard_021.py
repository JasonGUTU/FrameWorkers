#!/usr/bin/env python3
"""Rename hard_021 → storytelling_104 for visual consistency with storytelling_*.

Same +100 numbering offset rule used for cr_104 / cr_107 (preserves the
original 21 suffix; +100 to avoid colliding with storytelling_001..099).
Original name preserved in `_meta.original_name` for audit.
"""
from __future__ import annotations
import json
from pathlib import Path

RENAME = {"hard_021": "storytelling_104"}


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

    md: list[str] = [
        "# 30-case selection (seed=42, cr+intake_img rewritten + 3 hard_* renamed)\n\n",
        "Source: `eval_cases_v4500_balanced.json`\n",
        "Total: 30 (10 per category × 3 categories)\n",
        "Rewritten: cr (10) + intake_img (10) → 中文短剧爆款; storytelling (10) untouched\n",
        "Renamed: hard_004 → cr_104, hard_007 → cr_107, hard_021 → storytelling_104\n\n",
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
