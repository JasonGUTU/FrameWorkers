"""Build ``samples_grpo_v1.jsonl`` from hand-authored GRPO raw samples.

Mirror of ``build_sft_jsonl.py`` but reads from ``raw_samples_grpo/`` and
adds top-level metadata (``shape_slug`` / ``source`` / ``gen_id`` /
``long_story``) so the future RL trainer can distinguish provenance and
fast-path the gold plan.

Two record sources:
  * **Hand-written GRPO** — ``raw_samples_grpo/shape_<slug>.py`` exporting
    ``SAMPLES = [{user_goal, rationale, intents}, ...]``. Tagged
    ``source="grpo_handwritten"``.
  * **SFT reuse** (``--reuse-n N``) — stratified-random sample from
    ``samples_sft_full.jsonl`` proportional to ``shape.target_n``. Tagged
    ``source="sft_reuse"``.

Sister script: ``build_templated_grpo_jsonl.py`` produces a parallel
templated dataset (chain-free rationales) from the SAME user_goal pool.

Usage:
    PYTHONPATH=. python training/director/build_grpo_jsonl.py --sanity
    PYTHONPATH=. python training/director/build_grpo_jsonl.py --reuse-n 420
    PYTHONPATH=. python training/director/build_grpo_jsonl.py --shape extend_only
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
from training.director.gen_samples import build_system_prompt, _assistant_response  # noqa: E402
from training.director.raw_samples._blueprint import SHAPES, ShapeSpec  # noqa: E402

GRPO_RAW_DIR = REPO_ROOT / "training/director/raw_samples_grpo"
SANITY_SLUGS = {"extend_only", "story_pure", "cr_music", "vid_subtitle", "highlight_only"}


def load_grpo_shape_module(slug: str) -> list[dict] | None:
    """Import ``raw_samples_grpo.shape_<slug>`` (and ``_long`` companion)."""
    merged: list = []
    found = False
    for suffix in ("", "_long"):
        path = GRPO_RAW_DIR / f"shape_{slug}{suffix}.py"
        if not path.is_file():
            continue
        found = True
        mod_name = f"training.director.raw_samples_grpo.shape_{slug}{suffix}"
        if mod_name in sys.modules:
            del sys.modules[mod_name]
        mod = importlib.import_module(mod_name)
        samples = getattr(mod, "SAMPLES", None)
        if not isinstance(samples, list):
            raise TypeError(f"{mod_name}.SAMPLES must be a list, got {type(samples).__name__}")
        merged.extend(samples)
    return merged if found else None


def shape_by_chain(plan_agent_ids: list[str]) -> str | None:
    for s in SHAPES:
        if list(s.canonical_chain) == plan_agent_ids:
            return s.slug
    return None


def build_handwritten_record(
    *, system_prompt: str, shape: ShapeSpec, sample: dict, gen_id: str,
    long_story: bool = False,
) -> dict:
    goal = (sample.get("user_goal") or "").strip()
    rationale = (sample.get("rationale") or "").strip()
    intents = sample.get("intents")
    if not goal or not rationale:
        raise ValueError(f"{shape.slug}/{gen_id}: missing user_goal or rationale")
    if not isinstance(intents, list) or len(intents) != len(shape.canonical_chain):
        raise ValueError(
            f"{shape.slug}/{gen_id}: intents len mismatch (got "
            f"{len(intents) if isinstance(intents, list) else 'N/A'}, want {len(shape.canonical_chain)})"
        )
    plan = [
        {"agent_id": a, "intent": it.strip()}
        for a, it in zip(shape.canonical_chain, intents)
    ]
    assistant = _assistant_response(rationale, plan)
    return {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": goal},
            {"role": "assistant", "content": assistant},
        ],
        "shape_slug": shape.slug,
        "source": "grpo_handwritten",
        "gen_id": gen_id,
        "long_story": long_story,
    }


def stratified_sft_reuse(
    sft_path: Path, n_total: int, system_prompt: str, *, seed: int = 7
) -> list[dict]:
    if not sft_path.is_file():
        return []
    by_shape: dict[str, list[dict]] = {}
    with sft_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            asst = next((m for m in r.get("messages", []) if m.get("role") == "assistant"), None)
            if asst is None:
                continue
            try:
                payload = json.loads(asst["content"])
                ids = [s["agent_id"] for s in payload["plan"]]
            except Exception:
                continue
            slug = shape_by_chain(ids)
            if slug is None:
                continue
            by_shape.setdefault(slug, []).append(r)

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
            quotas[slug] += 1
            diff -= 1
        elif quotas[slug] > 1:
            quotas[slug] -= 1
            diff += 1
        i += 1

    out: list[dict] = []
    next_id = 1
    for slug, recs in by_shape.items():
        take = min(quotas.get(slug, 0), len(recs))
        picked = rng.sample(recs, take) if take else []
        for r in picked:
            user_msg = next(m for m in r["messages"] if m["role"] == "user")
            asst_msg = next(m for m in r["messages"] if m["role"] == "assistant")
            out.append({
                "messages": [
                    {"role": "system", "content": system_prompt},
                    user_msg,
                    asst_msg,
                ],
                "shape_slug": slug,
                "source": "sft_reuse",
                "gen_id": f"grpo_reuse_{next_id:04d}",
                "long_story": False,
            })
            next_id += 1
    return out


def write_spot_check(out_path: Path, records: list[dict], n: int = 30, seed: int = 42) -> None:
    rng = random.Random(seed)
    sample = rng.sample(records, min(n, len(records)))
    lines = [
        f"# GRPO (handwritten) spot check — {len(sample)} of {len(records)} samples", "",
        "**Track B (handwritten raw_samples_grpo).** Style: with-chain flow narrative + reject list.",
        "Sister track: samples_grpo_v1.templated.jsonl (chain-free).",
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
    ap.add_argument("--out", type=Path,
                    default=REPO_ROOT / "training/director/samples_grpo_v1.jsonl")
    ap.add_argument("--sft-path", type=Path,
                    default=REPO_ROOT / "training/director/samples_sft_full.jsonl")
    ap.add_argument("--spot-check", type=int, default=30)
    args = ap.parse_args()

    out_path = args.out.with_name("samples_grpo_sanity.jsonl") if args.sanity else args.out

    print("Building canonical system prompt…")
    system_prompt = build_system_prompt()
    print(f"  system prompt: {len(system_prompt):,} chars")

    eval_norm = {
        _normalize(c["user_goal"])
        for c in json.loads((REPO_ROOT / "evals/director_routing/eval_cases.json").read_text(encoding="utf-8"))
    }
    print(f"  eval-isolation set: {len(eval_norm)} normalized goals")

    sft_norm: set[str] = set()
    if args.sft_path.is_file():
        with args.sft_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                r = json.loads(line)
                u = next((m for m in r.get("messages", []) if m.get("role") == "user"), None)
                if u and isinstance(u.get("content"), str):
                    sft_norm.add(_normalize(u["content"]))
        print(f"  SFT existing-goal set: {len(sft_norm)} (used for de-dup of new gen)")

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
    drops_eval = drops_sft = drops_within = 0
    next_id = 1

    for shape in target_shapes:
        raw = load_grpo_shape_module(shape.slug)
        if raw is None:
            print(f"  {shape.slug:34s}  (no GRPO file — skipping)")
            continue
        kept = 0
        for idx, sample in enumerate(raw):
            n = _normalize(sample.get("user_goal") or "")
            if n in eval_norm:
                drops_eval += 1
                print(f"  ⚠ {shape.slug}[{idx}]: eval-collision dropped"); continue
            if n in sft_norm:
                drops_sft += 1
                print(f"  ⚠ {shape.slug}[{idx}]: SFT-dup dropped"); continue
            if n in seen_within:
                drops_within += 1
                print(f"  ⚠ {shape.slug}[{idx}]: within-batch-dup dropped"); continue
            seen_within.add(n)
            new_records.append(build_handwritten_record(
                system_prompt=system_prompt, shape=shape, sample=sample,
                gen_id=f"grpo_{next_id:04d}",
            ))
            next_id += 1
            kept += 1
        print(f"  {shape.slug:34s}  raw={len(raw):3d}  kept={kept:3d}")

    print(f"\nHand-written GRPO records: {len(new_records)}")
    if drops_eval: print(f"  Dropped {drops_eval} (eval-collision)")
    if drops_sft: print(f"  Dropped {drops_sft} (SFT-dup)")
    if drops_within: print(f"  Dropped {drops_within} (within-batch-dup)")

    reuse_records: list[dict] = []
    if args.reuse_n > 0 and not args.sanity:
        reuse_records = stratified_sft_reuse(args.sft_path, args.reuse_n, system_prompt)
        print(f"SFT reuse records: {len(reuse_records)} (target {args.reuse_n})")

    all_records = new_records + reuse_records
    if not all_records:
        raise SystemExit("No records produced — aborting.")

    random.Random(42).shuffle(all_records)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for r in all_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    rel = out_path.relative_to(REPO_ROOT) if out_path.is_relative_to(REPO_ROOT) else out_path
    print(f"\nWrote {rel}  ({len(all_records)} total: "
          f"{len(new_records)} hand-written + {len(reuse_records)} reuse)")

    spot_path = out_path.with_name(out_path.stem + ".spot_check.md")
    write_spot_check(spot_path, all_records, n=args.spot_check)
    spot_rel = spot_path.relative_to(REPO_ROOT) if spot_path.is_relative_to(REPO_ROOT) else spot_path
    print(f"Wrote {spot_rel}  ({min(args.spot_check, len(all_records))} random samples)")


if __name__ == "__main__":
    main()
