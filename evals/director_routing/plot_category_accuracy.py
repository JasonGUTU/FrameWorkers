#!/usr/bin/env python3
"""Plot per-category chain accuracy from a director_routing eval result.

Categories follow the canonical 9-bucket taxonomy declared in
``eval_cases.md`` (cr / intake / sub / bilingual / storytelling / style /
extend / highlight / complex), bucketed by case-name prefix on the first
underscore.

Default input: the highest-scoring run we have on disk
(20260428_094034_lora_qwen3_grpo_4gpu_partialreward — 83.1%).

Output PNG lands next to this script as ``category_accuracy_<run>.png``.

Usage:
    python plot_category_accuracy.py
    python plot_category_accuracy.py --file <path-to-result.json>
"""
from __future__ import annotations

import argparse
import json
from collections import OrderedDict
from pathlib import Path

import matplotlib.pyplot as plt


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
DEFAULT_RESULT = (
    REPO_ROOT
    / "Runtime/eval_routing"
    / "20260428_094034_lora_qwen3_grpo_4gpu_partialreward_20260428_093935.json"
)

# Canonical order from eval_cases.md (also keeps complex on the right since
# it dominates the count).
CATEGORY_ORDER = [
    "cr",
    "intake",
    "sub",
    "bilingual",
    "storytelling",
    "style",
    "extend",
    "highlight",
    "complex",
]

# Plot-only display labels for each category. Two lines so the chart is
# legible without forcing the reader to know the short slug.
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


def category_of(name: str) -> str:
    """Bucket a case name to one of the 9 canonical categories."""
    return name.split("_", 1)[0] if name else "unknown"


def compute_per_category(results: list[dict]) -> "OrderedDict[str, tuple[int, int]]":
    """Return ordered ``{category: (correct, total)}``."""
    buckets: dict[str, list[bool]] = {c: [] for c in CATEGORY_ORDER}
    for r in results:
        cat = category_of(r.get("name", ""))
        buckets.setdefault(cat, []).append(bool(r.get("chain_correct")))
    out: OrderedDict[str, tuple[int, int]] = OrderedDict()
    for cat in CATEGORY_ORDER:
        bs = buckets.get(cat, [])
        out[cat] = (sum(bs), len(bs))
    # Surface any unexpected categories
    for cat, bs in buckets.items():
        if cat not in CATEGORY_ORDER:
            out[cat] = (sum(bs), len(bs))
    return out


def plot(stats: "OrderedDict[str, tuple[int, int]]", overall: float, run_name: str, out_path: Path) -> None:
    cats = list(stats.keys())
    labels = [CATEGORY_DISPLAY_LABEL.get(c, c) for c in cats]
    accs = [(c / t * 100) if t else 0.0 for (c, t) in stats.values()]
    counts = [t for (_, t) in stats.values()]

    fig, ax = plt.subplots(figsize=(14, 7.5))
    # Hand-curated palette: ColorBrewer Set2 (8 distinct pastels, gentler
    # than tab10) + a 9th soft sky blue for the last category.
    pretty_palette = [
        "#66C2A5",  # teal-green
        "#FC8D62",  # warm salmon
        "#8DA0CB",  # cool lavender
        "#E78AC3",  # rose pink
        "#A6D854",  # fresh green
        "#FFD92F",  # sunny yellow
        "#E5C494",  # tan
        "#B3B3B3",  # neutral gray
        "#5DA5DA",  # sky blue
    ]
    bar_colors = [pretty_palette[i % len(pretty_palette)] for i in range(len(labels))]
    bars = ax.bar(labels, accs, color=bar_colors, edgecolor="#333333", linewidth=0.8)

    # Overall accuracy line
    ax.axhline(overall * 100, color="#C44E52", linestyle="--", linewidth=1.4,
               label=f"overall = {overall * 100:.1f}%")

    for bar, acc, n in zip(bars, accs, counts):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1.0,
            f"{acc:.0f}%\n(n={n})",
            ha="center", va="bottom", fontsize=14,
        )

    ax.set_ylim(0, 115)
    ax.set_ylabel("Chain accuracy (%)", fontsize=18, fontweight="bold")
    ax.set_xlabel("Category", fontsize=18, fontweight="bold")
    ax.tick_params(axis="x", labelsize=16)
    ax.tick_params(axis="y", labelsize=14)
    ax.legend(loc="upper right", fontsize=14)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(out_path, dpi=140)
    print(f"Saved: {out_path}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", type=Path, default=DEFAULT_RESULT,
                    help=f"Eval result JSON. Default: {DEFAULT_RESULT.name}")
    args = ap.parse_args()

    if not args.file.is_file():
        raise SystemExit(f"Result file not found: {args.file}")

    payload = json.loads(args.file.read_text(encoding="utf-8"))
    results = payload.get("results", [])
    meta = payload.get("meta", {})
    run_name = meta.get("name") or args.file.stem

    if not results:
        raise SystemExit(f"No results in {args.file}")

    stats = compute_per_category(results)
    overall = sum(c for (c, _) in stats.values()) / sum(t for (_, t) in stats.values())

    print(f"Run: {run_name}")
    print(f"Total cases: {sum(t for (_, t) in stats.values())}")
    print(f"Overall chain accuracy: {overall * 100:.1f}%")
    print(f"\n{'category':<14} {'correct':>8}/{'total':<5} {'acc':>7}")
    print("-" * 40)
    for cat, (correct, total) in stats.items():
        acc = (correct / total * 100) if total else 0.0
        print(f"{cat:<14} {correct:>8}/{total:<5} {acc:>6.1f}%")

    out_path = SCRIPT_DIR / f"category_accuracy_{run_name}.png"
    plot(stats, overall, run_name, out_path)


if __name__ == "__main__":
    main()
