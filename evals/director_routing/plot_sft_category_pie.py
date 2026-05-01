#!/usr/bin/env python3
"""Pie chart of the SFT corpus, bucketed by the 9 task categories used
in ``plot_category_accuracy.py`` so colors / labels line up with the
eval-side bar charts.

Reads ``training/director/samples_sft_full.jsonl`` and the blueprint to
recover each sample's chain shape, then maps shape → eval-bucket via
the shape's ``eval_reference_names`` prefix.

Output: ``sft_category_pie.png`` next to this script.
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
sys.path.insert(0, str(REPO_ROOT))

from training.director.raw_samples._blueprint import SHAPES  # noqa: E402

SFT_PATH = REPO_ROOT / "training/director/samples_sft_full.jsonl"
OUT_PATH = SCRIPT_DIR / "sft_category_pie.png"

CATEGORY_ORDER = [
    "cr", "intake", "sub", "bilingual", "storytelling",
    "style", "extend", "highlight", "complex",
]
CATEGORY_DISPLAY_LABEL = {
    "cr":           "creative",
    "intake":       "image-ref",
    "sub":          "subtitle",
    "bilingual":    "bilingual\nsubtitle",
    "storytelling": "storytelling",
    "style":        "style\ntransfer",
    "extend":       "video\nextend",
    "highlight":    "highlight\nreel",
    "complex":      "complex",
}
PALETTE = [
    "#66C2A5", "#FC8D62", "#8DA0CB", "#E78AC3", "#A6D854",
    "#FFD92F", "#E5C494", "#B3B3B3", "#5DA5DA",
]


def main() -> None:
    shape_to_bucket = {}
    for s in SHAPES:
        cats = Counter(r.split("_", 1)[0] for r in s.eval_reference_names)
        shape_to_bucket[s.slug] = cats.most_common(1)[0][0]

    shape_by_chain = {tuple(s.canonical_chain): s.slug for s in SHAPES}

    cat_counts: Counter = Counter()
    with SFT_PATH.open(encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            asst = next(m for m in rec["messages"] if m["role"] == "assistant")
            payload = json.loads(asst["content"])
            chain = tuple(s["agent_id"] for s in payload["plan"])
            slug = shape_by_chain.get(chain)
            cat_counts[shape_to_bucket.get(slug, "unknown")] += 1

    total = sum(cat_counts.values())
    sizes = [cat_counts.get(c, 0) for c in CATEGORY_ORDER]

    fig, ax = plt.subplots(figsize=(12, 9))
    wedges, _texts = ax.pie(
        sizes,
        colors=PALETTE,
        startangle=90,
        counterclock=False,
        wedgeprops=dict(edgecolor="white", linewidth=1.5),
    )
    ax.set_aspect("equal")

    # All labels live outside the pie, anchored by a leader line.
    # Uniform style — no in-slice text — so the chart reads cleanly
    # regardless of slice size.
    for i, wedge in enumerate(wedges):
        n = sizes[i]
        if n == 0:
            continue
        pct = n / total * 100
        cat = CATEGORY_ORDER[i]
        display = CATEGORY_DISPLAY_LABEL[cat]
        label = f"{display}\n{n} ({pct:.1f}%)"

        # Midpoint angle of the wedge
        angle_deg = (wedge.theta1 + wedge.theta2) / 2.0
        angle_rad = np.deg2rad(angle_deg)
        x_unit = np.cos(angle_rad)
        y_unit = np.sin(angle_rad)

        xy_anchor = (x_unit, y_unit)            # wedge outer edge
        x_text = 1.32 * x_unit
        y_text = 1.32 * y_unit
        ha = "left" if x_unit >= 0 else "right"
        ax.annotate(
            label,
            xy=xy_anchor,
            xytext=(x_text, y_text),
            ha=ha, va="center",
            fontsize=14,
            fontweight="bold",
            color="#1a1a1a",
            arrowprops=dict(
                arrowstyle="-",
                color="#888888",
                lw=0.9,
                connectionstyle="arc3,rad=0.0",
            ),
        )

    # Stretch limits a bit so outside labels don't get clipped.
    ax.set_xlim(-1.7, 1.7)
    ax.set_ylim(-1.5, 1.5)

    print("SFT category counts:")
    for c in CATEGORY_ORDER:
        n = cat_counts.get(c, 0)
        print(f"  {c:<14} {n:>4}  ({n / total * 100:5.1f}%)")
    print(f"  {'TOTAL':<14} {total:>4}")

    plt.tight_layout()
    plt.savefig(OUT_PATH, dpi=140, bbox_inches="tight")
    print(f"Saved: {OUT_PATH}")


if __name__ == "__main__":
    main()
