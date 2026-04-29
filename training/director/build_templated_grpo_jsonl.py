"""Build ``samples_grpo_v1.templated.jsonl`` — Track A: chain-free templated.

Mirror of ``build_templated_sft_jsonl.py`` but operates on the GRPO
user_goal pool (``raw_samples_grpo/``) instead of the SFT pool. Imports
the templating helpers (rationale skeletons + per-agent intent variants +
chain-free rationale rendering) from the SFT script so both pipelines
share identical templating logic.

Two record sources (mirroring build_grpo_jsonl.py):
  * **GRPO user_goals** — ``raw_samples_grpo/shape_<slug>.py``, ONLY the
    ``user_goal`` field is used; rationale and intents come from the
    template engine. Tagged ``source="grpo_templated"``.
  * **SFT user_goals** (``--reuse-n N``) — stratified-random sample of
    user_goals from ``samples_sft_full.jsonl``; rationale + intents
    re-templated from scratch. Tagged ``source="sft_reuse_templated"``.

Style intentionally differs from Track B (build_grpo_jsonl.py):
  * Track A rationale = chain-free ("Cinematic mini-drama from a text
    brief with BGM as the only added overlays. Reject: ...")
  * Track B rationale = with-chain flow narrative ("StoryAgent drafts
    the X blueprint. ScreenplayAgent breaks it into Y scenes...")

This produces two parallel datasets for ablation: same user_goal pool,
different rationale-style training signals.

Usage:
    PYTHONPATH=. python training/director/build_templated_grpo_jsonl.py --sanity
    PYTHONPATH=. python training/director/build_templated_grpo_jsonl.py --reuse-n 420
"""
from __future__ import annotations

import argparse
import importlib
import json
import random
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from training.director.build_sft_jsonl import _normalize  # noqa: E402
from training.director.build_grpo_jsonl import (  # noqa: E402
    GRPO_RAW_DIR, SANITY_SLUGS, load_grpo_shape_module, shape_by_chain,
)
from training.director.build_templated_sft_jsonl import (  # noqa: E402
    render_rationale, render_intents,
)
from training.director.gen_samples import build_system_prompt, _assistant_response  # noqa: E402
from training.director.raw_samples._blueprint import SHAPES, ShapeSpec  # noqa: E402


# ── x15 user_goal pool loader (raw_samples_grpo_x15/) ───────────────────────
# Mirror of SFT's load_x15_user_goals but for the GRPO pool (disjoint topics).
GRPO_X15_DIR = REPO_ROOT / "training/director/raw_samples_grpo_x15"
GRPO_X15_IDX_OFFSET = 10000


def load_grpo_x15_user_goals(slug: str) -> list[str]:
    """Import raw_samples_grpo_x15.shape_<slug>(_long).py if present and merge USER_GOALS."""
    merged: list[str] = []
    for suffix in ("", "_long"):
        path = GRPO_X15_DIR / f"shape_{slug}{suffix}.py"
        if not path.is_file():
            continue
        mod_name = f"training.director.raw_samples_grpo_x15.shape_{slug}{suffix}"
        if mod_name in sys.modules:
            del sys.modules[mod_name]
        mod = importlib.import_module(mod_name)
        goals = getattr(mod, "USER_GOALS", None)
        if not isinstance(goals, list):
            raise TypeError(f"{mod_name}.USER_GOALS must be list[str], got {type(goals).__name__}")
        merged.extend(g for g in goals if isinstance(g, str) and g.strip())
    return merged


def build_templated_record(
    *, system_prompt: str, shape: ShapeSpec, user_goal: str, idx: int,
    source: str, gen_id: str, long_story: bool = False,
) -> dict:
    chain = list(shape.canonical_chain)
    rationale = render_rationale(shape.slug, idx, chain)
    intents = render_intents(shape.slug, idx, chain)
    plan = [{"agent_id": a, "intent": it} for a, it in zip(chain, intents)]
    assistant = _assistant_response(rationale, plan)
    return {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_goal.strip()},
            {"role": "assistant", "content": assistant},
        ],
        "shape_slug": shape.slug,
        "source": source,
        "gen_id": gen_id,
        "long_story": long_story,
    }


def stratified_sft_user_goals(sft_path: Path, n_total: int, *, seed: int = 7) -> list[tuple[str, str]]:
    """Sample ``n_total`` (slug, user_goal) pairs from SFT, stratified by shape."""
    if not sft_path.is_file():
        return []
    by_shape: dict[str, list[str]] = {}
    with sft_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            user_msg = next((m for m in r.get("messages", []) if m.get("role") == "user"), None)
            asst = next((m for m in r.get("messages", []) if m.get("role") == "assistant"), None)
            if user_msg is None or asst is None:
                continue
            try:
                payload = json.loads(asst["content"])
                ids = [s["agent_id"] for s in payload["plan"]]
            except Exception:
                continue
            slug = shape_by_chain(ids)
            if slug is None:
                continue
            by_shape.setdefault(slug, []).append(user_msg["content"])

    rng = random.Random(seed)
    weights = {s.slug: s.target_n for s in SHAPES}
    available = list(by_shape)
    total_weight = sum(weights[s] for s in available) or 1
    quotas = {s: max(1, round(n_total * weights[s] / total_weight)) for s in available}
    diff = n_total - sum(quotas.values())
    ordered = sorted(available, key=lambda s: -weights[s])
    i = 0
    while diff != 0 and ordered:
        slug = ordered[i % len(ordered)]
        if diff > 0:
            quotas[slug] += 1; diff -= 1
        elif quotas[slug] > 1:
            quotas[slug] -= 1; diff += 1
        i += 1

    out: list[tuple[str, str]] = []
    for slug, goals in by_shape.items():
        take = min(quotas.get(slug, 0), len(goals))
        picked = rng.sample(goals, take) if take else []
        for g in picked:
            out.append((slug, g))
    return out


def write_spot_check(out_path: Path, records: list[dict], n: int = 30, seed: int = 42) -> None:
    rng = random.Random(seed)
    sample = rng.sample(records, min(n, len(records)))
    lines = [
        f"# GRPO (templated) spot check — {len(sample)} of {len(records)} samples", "",
        "**Track A (templated chain-free).** Variation: 3 rationale skeletons × per-sample shuffled reject list × 3 intent variants per agent (md5-hash picked).",
        "Sister track: samples_grpo_v1.jsonl (with-chain flow narrative).",
        "", "---", "",
    ]
    for i, r in enumerate(sample, 1):
        u = next(m for m in r["messages"] if m["role"] == "user")["content"]
        a = next(m for m in r["messages"] if m["role"] == "assistant")["content"]
        p = json.loads(a)
        u_show = u if len(u) < 400 else u[:400] + f"... [+{len(u)-400} chars]"
        lines.append(f"## #{i}  ({r['shape_slug']}, {r['source']}, {r['gen_id']})")
        lines.append(f"**user_goal** ({len(u)} chars):"); lines.append("")
        lines.append(f"> {u_show}"); lines.append("")
        lines.append(f"**rationale:** {p['rationale']}"); lines.append("")
        lines.append("**plan:**")
        for step in p["plan"]:
            lines.append(f"  - `{step['agent_id']}` — {step['intent']}")
        lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sanity", action="store_true")
    ap.add_argument("--shape", default=None)
    ap.add_argument("--reuse-n", type=int, default=0)
    ap.add_argument("--out", type=Path, default=None,
                    help="Output jsonl path (default depends on --include-x15)")
    ap.add_argument("--sft-path", type=Path,
                    default=REPO_ROOT / "training/director/samples_sft_full.jsonl")
    ap.add_argument("--spot-check", type=int, default=30)
    ap.add_argument("--include-x15", action="store_true",
                    help="Also merge raw_samples_grpo_x15/ (USER_GOALS schema). Output "
                         "defaults to samples_grpo_v1.templated.x15.jsonl.")
    args = ap.parse_args()

    if args.out is None:
        default_name = "samples_grpo_v1.templated.x15.jsonl" if args.include_x15 \
                       else "samples_grpo_v1.templated.jsonl"
        args.out = REPO_ROOT / "training/director" / default_name
    out_path = args.out.with_name("samples_grpo_sanity.templated.jsonl") if args.sanity else args.out

    print("Building canonical system prompt…")
    system_prompt = build_system_prompt()
    print(f"  system prompt: {len(system_prompt):,} chars")

    eval_norm = {
        _normalize(c["user_goal"])
        for c in json.loads((REPO_ROOT / "evals/director_routing/eval_cases.json").read_text(encoding="utf-8"))
    }
    print(f"  eval-isolation set: {len(eval_norm)} normalized goals")

    if args.sanity:
        target_shapes = [s for s in SHAPES if s.slug in SANITY_SLUGS]
    elif args.shape:
        target_shapes = [s for s in SHAPES if s.slug == args.shape]
        if not target_shapes:
            raise SystemExit(f"Unknown shape: {args.shape!r}")
    else:
        target_shapes = list(SHAPES)

    new_records: list[dict] = []
    seen_within: set[str] = set()
    drops_eval = drops_within = 0
    next_id = 1

    for shape in target_shapes:
        raw = load_grpo_shape_module(shape.slug)
        if raw is None:
            print(f"  {shape.slug:34s}  (no GRPO file — skipping)")
            continue
        kept = 0
        for idx, sample in enumerate(raw):
            goal = (sample.get("user_goal") or "").strip()
            n = _normalize(goal)
            if n in eval_norm:
                drops_eval += 1; continue
            if n in seen_within:
                drops_within += 1; continue
            seen_within.add(n)
            new_records.append(build_templated_record(
                system_prompt=system_prompt, shape=shape, user_goal=goal, idx=idx,
                source="grpo_templated", gen_id=f"grpo_tmpl_{next_id:04d}",
            ))
            next_id += 1; kept += 1
        print(f"  {shape.slug:34s}  raw={len(raw):3d}  kept={kept:3d}")

    print(f"\nTemplated GRPO records: {len(new_records)}")
    if drops_eval: print(f"  Dropped {drops_eval} (eval-collision)")
    if drops_within: print(f"  Dropped {drops_within} (within-batch-dup)")

    # ── x15 user_goal pass (raw_samples_grpo_x15/) ──────────────────────────
    x15_records: list[dict] = []
    if args.include_x15 and not args.sanity:
        print("\n--- Merging raw_samples_grpo_x15/ user_goals ---")
        x15_id = 1
        for shape in target_shapes:
            x15_goals = load_grpo_x15_user_goals(shape.slug)
            if not x15_goals:
                print(f"  {shape.slug:34s}  (no x15 module yet — skipping)")
                continue
            kept = 0
            for offset, goal in enumerate(x15_goals):
                goal = goal.strip()
                if not goal:
                    continue
                n = _normalize(goal)
                if n in eval_norm:
                    drops_eval += 1
                    continue
                if n in seen_within:
                    drops_within += 1
                    continue
                seen_within.add(n)
                x15_records.append(build_templated_record(
                    system_prompt=system_prompt, shape=shape, user_goal=goal,
                    idx=GRPO_X15_IDX_OFFSET + offset,
                    source="grpo_templated_x15",
                    gen_id=f"grpo_tmpl_x15_{x15_id:05d}",
                ))
                x15_id += 1
                kept += 1
            print(f"  {shape.slug:34s}  x15-pool={len(x15_goals):4d}  kept={kept:4d}")
        print(f"GRPO-x15 records: {len(x15_records)}")

    reuse_records: list[dict] = []
    if args.reuse_n > 0 and not args.sanity:
        sft_pairs = stratified_sft_user_goals(args.sft_path, args.reuse_n)
        reuse_id = 1
        for slug, goal in sft_pairs:
            n = _normalize(goal)
            if n in eval_norm:
                drops_eval += 1; continue
            if n in seen_within:
                drops_within += 1; continue
            seen_within.add(n)
            shape = next((s for s in SHAPES if s.slug == slug), None)
            if shape is None: continue
            reuse_records.append(build_templated_record(
                system_prompt=system_prompt, shape=shape, user_goal=goal,
                idx=10000 + reuse_id,
                source="sft_reuse_templated", gen_id=f"grpo_tmpl_reuse_{reuse_id:04d}",
            ))
            reuse_id += 1
        print(f"SFT-reuse-templated records: {len(reuse_records)} (target {args.reuse_n})")

    all_records = new_records + reuse_records + x15_records
    if not all_records:
        raise SystemExit("No records produced — aborting.")

    random.Random(42).shuffle(all_records)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for r in all_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    rel = out_path.relative_to(REPO_ROOT) if out_path.is_relative_to(REPO_ROOT) else out_path
    suffix = f" + {len(x15_records)} x15" if x15_records else ""
    print(f"\nWrote {rel}  ({len(all_records)} total: "
          f"{len(new_records)} new-templated + {len(reuse_records)} sft-reuse-templated{suffix})")

    spot_path = out_path.with_name(out_path.stem + ".spot_check.md")
    write_spot_check(spot_path, all_records, n=args.spot_check)
    spot_rel = spot_path.relative_to(REPO_ROOT) if spot_path.is_relative_to(REPO_ROOT) else spot_path
    print(f"Wrote {spot_rel}  ({min(args.spot_check, len(all_records))} random samples)")


if __name__ == "__main__":
    main()
