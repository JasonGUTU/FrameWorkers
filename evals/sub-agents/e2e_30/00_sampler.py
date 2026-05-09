#!/usr/bin/env python3
"""Sample 30 representative cases from eval_cases_v4500_balanced.json.

Per-category (cr / intake_img / storytelling): pick 10 with diversity along two axes:
  - chain shape  — bucket by tuple-of-sorted-layers; allocate quotas proportional to
    bucket size (min 1 per shape; sum exactly 10).
  - user_goal genre — within each shape bucket, greedy-pick distinct genres first;
    backfill from remaining.

Reproducible via fixed seed.
"""
from __future__ import annotations

import json
import random
from collections import defaultdict
from pathlib import Path

SEED = 42
N_PER_CAT = 10
TARGET_CATS = ["cr", "intake_img", "storytelling"]

# Order matters: first match wins. Specific genres before generic.
GENRE_KEYWORDS: list[tuple[str, list[str]]] = [
    ("historical_war",     ["three kingdoms", "samurai", "warring states", "siege",
                            "general", "troops", "war epic", "battlefield", "warlord"]),
    ("wuxia_cultivation",  ["wuxia", "cultivation", "martial", "jianghu", "immortal",
                            "sect", "sword", "kung fu", "xianxia"]),
    ("cyberpunk_scifi",    ["cyberpunk", "cyber", "neon", "dystopian", "sci-fi",
                            "mecha", "spaceship", "space station", "android"]),
    ("horror_thriller",    ["horror", "ghost", "haunt", "curse", "thriller",
                            "demon", "paranormal", "eerie"]),
    ("historical_drama",   ["imperial", "dynasty", "palace", "concubine", "court",
                            "kingdom of", "ancient", "ming", "qing", "tang"]),
    ("romance",            ["romance", "sweet", "crush", "wedding", "love story",
                            "sweethe", "lovers"]),
    ("fantasy",            ["fantasy", "dragon", "magic", "wizard", "fairy",
                            "mythical", "myth", "elf"]),
    ("mystery_crime",      ["mystery", "detective", "investigate", "crime",
                            "murder", "whodunit"]),
    ("urban_modern",       ["campus", "office", "urban", "corporate", "workplace",
                            "modern city", "high school", "university"]),
    ("family_slice",       ["family", "mother", "father", "sister", "brother",
                            "parent", "grandfather", "grandmother", "lineage"]),
]


def detect_genre(goal: str) -> str:
    g = goal.lower()
    for genre, kws in GENRE_KEYWORDS:
        if any(kw in g for kw in kws):
            return genre
    return "other"


def shape_of(case: dict) -> tuple[tuple[str, ...], ...]:
    return tuple(tuple(sorted(layer)) for layer in case["expected_chain"])


def allocate_quotas(sizes: list[int], n: int) -> list[int]:
    """Allocate n picks across buckets proportional to size, min 1, sum exactly n.

    Reduces from largest bucket (size>1) until sum==n; grows from bucket with most
    remaining headroom otherwise.
    """
    raw = [max(1, round(s / sum(sizes) * n)) for s in sizes]
    while sum(raw) > n:
        # cap from the bucket that is most over-allocated relative to size,
        # but never below 1
        i = max(range(len(raw)), key=lambda i: (raw[i] - sizes[i] / sum(sizes) * n, raw[i]))
        if raw[i] <= 1:
            break
        raw[i] -= 1
    while sum(raw) < n:
        i = max(range(len(raw)), key=lambda i: sizes[i] - raw[i])
        raw[i] += 1
    return raw


def sample_category(rows: list[dict], n: int, seed: int) -> list[dict]:
    rng = random.Random(seed)
    by_shape: dict = defaultdict(list)
    for c in rows:
        by_shape[shape_of(c)].append(c)
    shapes = sorted(by_shape.keys(), key=lambda s: -len(by_shape[s]))
    quotas = allocate_quotas([len(by_shape[s]) for s in shapes], n)

    picks: list[dict] = []
    for shape, k in zip(shapes, quotas):
        bucket = list(by_shape[shape])
        rng.shuffle(bucket)
        seen_genres: set[str] = set()
        chosen: list[dict] = []
        # pass 1: greedy distinct-genre
        for c in bucket:
            if len(chosen) >= k:
                break
            g = detect_genre(c["user_goal"])
            if g in seen_genres:
                continue
            chosen.append(c)
            seen_genres.add(g)
        # pass 2: backfill
        for c in bucket:
            if len(chosen) >= k:
                break
            if c not in chosen:
                chosen.append(c)
        for c in chosen:
            c2 = dict(c)
            c2["_meta"] = {
                "shape_layers_str": " -> ".join("|".join(layer) for layer in shape),
                "shape_layer_count": len(shape),
                "sampled_genre": detect_genre(c["user_goal"]),
            }
            picks.append(c2)
    return picks


def main() -> None:
    here = Path(__file__).parent.resolve()
    src = Path(
        "/home/zhendong_li/FrameWorkers/evals/director_routing/"
        "eval_cases_v4500_balanced.json"
    )
    data = json.loads(src.read_text())

    selected: list[dict] = []
    for cat in TARGET_CATS:
        rows = [c for c in data if c["category"] == cat]
        selected.extend(sample_category(rows, N_PER_CAT, SEED))

    (here / "selection.json").write_text(
        json.dumps(selected, ensure_ascii=False, indent=2)
    )

    md: list[str] = [
        f"# 30-case selection (seed={SEED})\n\n",
        f"Source: `{src.name}`\n",
        f"Total: {len(selected)} (10 per category × 3 categories)\n\n",
    ]
    for cat in TARGET_CATS:
        cat_picks = [c for c in selected if c["category"] == cat]
        shape_set = sorted({c["_meta"]["shape_layers_str"] for c in cat_picks})
        genre_set = sorted({c["_meta"]["sampled_genre"] for c in cat_picks})
        md.append(f"## {cat} ({len(cat_picks)})\n")
        md.append(
            f"- unique shapes covered: **{len(shape_set)}**  \n"
            f"- distinct genres: **{len(genre_set)}** ({', '.join(genre_set)})\n\n"
        )
        md.append("| name | layers | genre | user_goal |\n|---|---|---|---|\n")
        for c in cat_picks:
            m = c["_meta"]
            goal = c["user_goal"][:110].replace("|", r"\|")
            if len(c["user_goal"]) > 110:
                goal += "..."
            md.append(
                f"| `{c['name']}` | {m['shape_layer_count']} | "
                f"{m['sampled_genre']} | {goal} |\n"
            )
        md.append("\n")
    (here / "selection.md").write_text("".join(md))

    # Console summary
    print(f"Wrote {len(selected)} cases to {here / 'selection.json'}")
    for cat in TARGET_CATS:
        cat_picks = [c for c in selected if c["category"] == cat]
        shapes = sorted({c["_meta"]["shape_layers_str"] for c in cat_picks})
        genres = sorted({c["_meta"]["sampled_genre"] for c in cat_picks})
        print(
            f"  {cat}: {len(cat_picks)} cases, "
            f"{len(shapes)} unique shapes, {len(genres)} genres = {genres}"
        )


if __name__ == "__main__":
    main()
