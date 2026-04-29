"""Build ``samples_sft_full.jsonl`` from hand-authored raw sample modules.

No teacher API calls — all content is hand-written in
``training/director/raw_samples/shape_<slug>.py`` modules, each exporting
``SAMPLES: list[{user_goal, rationale, intents}]``.

The canonical agent chain for each shape lives in the blueprint
(``raw_samples/_blueprint.py``), so per-shape modules never repeat the
chain — they just enumerate (user_goal, rationale, per-agent intent list).
This guarantees every sample's ``plan`` respects the expected chain.

Per sample, this script:
  1. Joins shape's ``canonical_chain`` with the module's ``intents`` list
     to form ``plan = [{agent_id: chain[i], intent: intents[i]}]``.
  2. Wraps the ``{rationale, plan}`` object as the assistant turn.
  3. Prepends the canonical system prompt built by
     ``gen_samples.build_system_prompt()``.
  4. Emits one JSON line per sample.

After writing the jsonl, it writes a spot-check markdown dump (50 random
samples) for manual quality review before training.

Usage:
    PYTHONPATH=. python training/director/build_sft_jsonl.py
    PYTHONPATH=. python training/director/build_sft_jsonl.py --shape cr_music
        (build only one shape — useful during pilot / iteration)
"""
from __future__ import annotations

import argparse
import importlib
import json
import random
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from training.director.gen_samples import build_system_prompt, _assistant_response  # noqa: E402
from training.director.raw_samples._blueprint import SHAPES, TOTAL_TARGET  # noqa: E402


def _normalize(goal: str) -> str:
    """Mirror validate.py::normalize_goal — strip whitespace + punctuation, lowercase."""
    return re.sub(r"[\s，。,！!？?、；;：:]+", "", (goal or "").lower().strip())


def load_shape_module(slug: str):
    """Import ``raw_samples.shape_<slug>`` (and ``shape_<slug>_long`` if
    present) and return the merged ``SAMPLES`` list.

    Long-story samples live in a separate ``shape_<slug>_long.py`` module
    per shape (so the main file stays readable when a shape has both short
    briefs and 2500-word original-fiction inputs).  Both files contribute
    their ``SAMPLES`` list to the same shape bucket.

    Returns None if neither file exists.
    """
    base_dir = REPO_ROOT / "training/director/raw_samples"
    merged: list = []
    found_any = False
    for suffix in ("", "_long"):
        path = base_dir / f"shape_{slug}{suffix}.py"
        if not path.is_file():
            continue
        found_any = True
        mod_name = f"training.director.raw_samples.shape_{slug}{suffix}"
        if mod_name in sys.modules:
            del sys.modules[mod_name]
        mod = importlib.import_module(mod_name)
        samples = getattr(mod, "SAMPLES", None)
        if not isinstance(samples, list):
            raise TypeError(f"{mod_name}.SAMPLES must be a list, got {type(samples).__name__}")
        merged.extend(samples)
    return merged if found_any else None


def build_record(system_prompt: str, chain: list[str], sample: dict, shape_slug: str, idx: int) -> dict:
    """Wrap one raw sample into a full SFT messages record."""
    goal = sample.get("user_goal")
    rationale = sample.get("rationale")
    intents = sample.get("intents")

    if not isinstance(goal, str) or not goal.strip():
        raise ValueError(f"{shape_slug}[{idx}]: missing user_goal")
    if not isinstance(rationale, str) or not rationale.strip():
        raise ValueError(f"{shape_slug}[{idx}]: missing rationale")
    if not isinstance(intents, list) or len(intents) != len(chain):
        raise ValueError(
            f"{shape_slug}[{idx}]: intents must be list of length {len(chain)}, "
            f"got {type(intents).__name__} len={len(intents) if isinstance(intents, list) else 'N/A'}"
        )
    for j, it in enumerate(intents):
        if not isinstance(it, str) or not it.strip():
            raise ValueError(f"{shape_slug}[{idx}]: intents[{j}] is empty or not a string")

    plan = [{"agent_id": a, "intent": it.strip()} for a, it in zip(chain, intents)]
    assistant = _assistant_response(rationale.strip(), plan)
    return {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": goal.strip()},
            {"role": "assistant", "content": assistant},
        ]
    }


def write_spot_check(out_path: Path, records: list[dict], n: int = 50, seed: int = 42) -> None:
    rng = random.Random(seed)
    sample = rng.sample(records, min(n, len(records)))
    lines = [
        f"# Spot check — {len(sample)} of {len(records)} SFT samples",
        "",
        "**Checklist:**",
        "1. rationale explicitly justifies every agent in the chain AND names 2-4 "
        "agents that were NOT included with a reason.",
        "2. intents are agent-specific (mention the user_goal's topic), not generic.",
        "3. long-story samples preserve the full story verbatim in user_goal.",
        "",
        "---",
        "",
    ]
    for i, r in enumerate(sample, 1):
        user_msg = next(m for m in r["messages"] if m["role"] == "user")
        asst_msg = next(m for m in r["messages"] if m["role"] == "assistant")
        payload = json.loads(asst_msg["content"])
        goal = user_msg["content"]
        goal_preview = goal if len(goal) < 400 else goal[:400] + f"... [+{len(goal)-400} chars]"
        lines.append(f"## #{i}")
        lines.append(f"**user_goal** ({len(goal)} chars):")
        lines.append("")
        lines.append(f"> {goal_preview}")
        lines.append("")
        lines.append(f"**rationale:** {payload['rationale']}")
        lines.append("")
        lines.append("**plan:**")
        for step in payload["plan"]:
            lines.append(f"  - `{step['agent_id']}` — {step['intent']}")
        lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--shape", default=None,
        help="Restrict build to ONE shape slug (pilot mode). Default: build all 42.",
    )
    ap.add_argument(
        "--out", type=Path, default=None,
        help="Output jsonl path (default: training/director/samples_sft_full.jsonl)",
    )
    ap.add_argument(
        "--strict", action="store_true",
        help="Require every shape module to be present (default: warn+skip missing, "
             "so partial builds work during authoring).",
    )
    ap.add_argument("--spot-check", type=int, default=50)
    args = ap.parse_args()

    out_root = Path(__file__).parent
    out_path = args.out if args.out else out_root / "samples_sft_full.jsonl"

    print("Building canonical system prompt…")
    system_prompt = build_system_prompt()
    print(f"  system prompt: {len(system_prompt):,} chars")

    # Collect eval goals for isolation check
    eval_path = REPO_ROOT / "evals/director_routing/eval_cases.json"
    eval_goals_norm = {
        _normalize(c["user_goal"]) for c in json.loads(eval_path.read_text(encoding="utf-8"))
    }
    print(f"  eval-goal isolation set: {len(eval_goals_norm)} normalized goals")

    # Iterate shapes
    selected_shapes = [s for s in SHAPES if args.shape in (None, s.slug)]
    if not selected_shapes:
        raise SystemExit(f"No shape matching --shape={args.shape!r}")

    all_records: list[dict] = []
    seen_goals: set[str] = set()
    collision_with_eval = 0
    collision_within_train = 0

    per_shape_summary: list[tuple[str, int, int]] = []  # (slug, target, actual)
    for shape in selected_shapes:
        raw = load_shape_module(shape.slug)
        if raw is None:
            msg = f"  {shape.slug:34s}  MISSING shape_{shape.slug}.py"
            if args.strict:
                raise SystemExit(msg.strip())
            print(msg)
            per_shape_summary.append((shape.slug, shape.target_n, 0))
            continue
        if len(raw) != shape.target_n:
            print(f"  ⚠ {shape.slug}: have {len(raw)} samples, blueprint target is {shape.target_n}")
        shape_kept = 0
        for idx, sample in enumerate(raw):
            goal = (sample.get("user_goal") or "").strip()
            norm = _normalize(goal)
            if norm in eval_goals_norm:
                collision_with_eval += 1
                print(f"  ⚠ {shape.slug}[{idx}]: goal collides with eval — dropping")
                continue
            if norm in seen_goals:
                collision_within_train += 1
                print(f"  ⚠ {shape.slug}[{idx}]: duplicate goal within training — dropping")
                continue
            seen_goals.add(norm)
            rec = build_record(system_prompt, list(shape.canonical_chain), sample, shape.slug, idx)
            all_records.append(rec)
            shape_kept += 1
        per_shape_summary.append((shape.slug, shape.target_n, shape_kept))
        print(f"  {shape.slug:34s}  target={shape.target_n:3d}  kept={shape_kept:3d}")

    print("\n" + "=" * 60)
    print(f"Total records: {len(all_records)}  (blueprint target: {TOTAL_TARGET})")
    if collision_with_eval:
        print(f"Dropped {collision_with_eval} samples (eval-goal collision)")
    if collision_within_train:
        print(f"Dropped {collision_within_train} samples (within-train duplicates)")

    if not all_records:
        raise SystemExit("No records to write — aborting.")

    # Shuffle deterministically before writing so training sees mixed shapes
    random.Random(42).shuffle(all_records)

    def _rel(p: Path) -> str:
        try:
            return str(p.relative_to(Path.cwd()))
        except ValueError:
            return str(p)

    with out_path.open("w", encoding="utf-8") as f:
        for r in all_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"\nWrote {_rel(out_path)}  ({len(all_records)} samples)")

    spot_path = out_path.with_name(out_path.stem + ".spot_check.md")
    write_spot_check(spot_path, all_records, n=args.spot_check)
    print(f"Wrote {_rel(spot_path)}  ({min(args.spot_check, len(all_records))} random samples)")

    # Per-shape authoring status
    print("\n=== Per-shape status ===")
    missing = [s for s, _, k in per_shape_summary if k == 0]
    partial = [(s, t, k) for s, t, k in per_shape_summary if 0 < k < t]
    complete = [(s, t, k) for s, t, k in per_shape_summary if k >= t and t > 0]
    print(f"  complete: {len(complete)} / {len(per_shape_summary)}")
    print(f"  partial : {len(partial)}")
    print(f"  missing : {len(missing)}")
    if partial:
        print("  partial shapes:")
        for s, t, k in partial:
            print(f"    {s:34s}  {k}/{t}")
    if missing:
        print("  missing shapes:")
        for s in missing:
            print(f"    {s}")

    print("\nNext: PYTHONPATH=. python training/director/validate.py --seq-len 8192")


if __name__ == "__main__":
    main()
