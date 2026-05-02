#!/usr/bin/env python3
"""Pie chart of the v4_500 SFT corpus, bucketed by the 11-bucket taxonomy
(cr / intake_img / sub / sub_vid / bilingual / storytelling / style / extend /
highlight / audio / complex) used by categorize.py.

Reads ``training/director/samples_sft_full.v4_500.jsonl`` and re-categorizes
each sample via the SSOT ``categorize()`` rule.

Output: ``sft_category_pie_v4_500.png`` next to this script.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

from categorize import categorize, BUCKET_ORDER  # noqa: E402

SFT_PATH = REPO_ROOT / "training/director/samples_sft_full.v4_500.jsonl"
OUT_PATH = SCRIPT_DIR / "sft_category_pie_v4_500.png"

CATEGORY_DISPLAY_LABEL = {
    "cr":           "creative",
    "intake_img":   "image-ref\ncreative",
    "sub":          "creative\nsubtitle",
    "sub_vid":      "video\nsubtitle",
    "bilingual":    "bilingual\nsubtitle",
    "storytelling": "storytelling",
    "style":        "style\ntransfer",
    "extend":       "video\nextend",
    "highlight":    "highlight\nreel",
    "audio":        "audio\noverlay",
    "complex":      "complex",
}

# 11-color palette: ColorBrewer Set2 + Set1 mix
PALETTE = {
    "cr":           "#66C2A5",
    "intake_img":   "#FC8D62",
    "sub":          "#8DA0CB",
    "sub_vid":      "#5DA5DA",
    "bilingual":    "#E78AC3",
    "storytelling": "#A6D854",
    "style":        "#FFD92F",
    "extend":       "#E5C494",
    "highlight":    "#B3B3B3",
    "audio":        "#FF9F40",
    "complex":      "#9966CC",
}


def parse_chain(sample) -> list[str]:
    for msg in sample["messages"]:
        if msg["role"] == "assistant":
            obj = json.loads(msg["content"])
            return [step["agent_id"] for step in obj.get("plan", [])]
    return []


def main() -> None:
    cat_counts: Counter = Counter()
    with SFT_PATH.open(encoding="utf-8") as f:
        for line in f:
            chain = parse_chain(json.loads(line))
            if chain:
                cat_counts[categorize(chain)] += 1

    total = sum(cat_counts.values())
    sizes = [cat_counts.get(c, 0) for c in BUCKET_ORDER]
    colors = [PALETTE[c] for c in BUCKET_ORDER]

    fig, ax = plt.subplots(figsize=(16, 12))
    wedges, _texts = ax.pie(
        sizes,
        colors=colors,
        startangle=90,
        counterclock=False,
        wedgeprops=dict(edgecolor="white", linewidth=1.8),
    )
    ax.set_aspect("equal")

    for i, wedge in enumerate(wedges):
        n = sizes[i]
        if n == 0:
            continue
        pct = n / total * 100
        cat = BUCKET_ORDER[i]
        display = CATEGORY_DISPLAY_LABEL[cat]
        label = f"{display}\n{n} ({pct:.1f}%)"

        angle_deg = (wedge.theta1 + wedge.theta2) / 2.0
        angle_rad = np.deg2rad(angle_deg)
        x_unit = np.cos(angle_rad)
        y_unit = np.sin(angle_rad)

        xy_anchor = (x_unit, y_unit)
        x_text = 1.36 * x_unit
        y_text = 1.36 * y_unit
        ha = "left" if x_unit >= 0 else "right"
        ax.annotate(
            label,
            xy=xy_anchor,
            xytext=(x_text, y_text),
            ha=ha, va="center",
            fontsize=20,
            fontweight="bold",
            color="#1a1a1a",
            arrowprops=dict(
                arrowstyle="-",
                color="#888888",
                lw=1.0,
                connectionstyle="arc3,rad=0.0",
            ),
        )

    ax.set_xlim(-2.05, 2.05)
    ax.set_ylim(-1.75, 1.75)

    print(f"v4_500 SFT category counts (data: {SFT_PATH.name}):")
    for c in BUCKET_ORDER:
        n = cat_counts.get(c, 0)
        print(f"  {c:<14} {n:>4}  ({n / total * 100:5.1f}%)")
    print(f"  {'TOTAL':<14} {total:>4}")

    plt.tight_layout()
    plt.savefig(OUT_PATH, dpi=140, bbox_inches="tight")
    print(f"Saved: {OUT_PATH}")


if __name__ == "__main__":
    main()
