"""Phase 1: build evals/director_routing/eval_cases_v4_500.json from
the original eval_cases.json by:

  1. Drop 12 cases that the new plan removes (synthetic / noise / +ambience).
  2. Apply categorize() to assign 'category' field on each surviving case.
  3. Renumber surviving cases as <bucket>_<seq>, ordered by chain shape then
     original name within bucket.
  4. Emit eval_cases_v4_500.json (survivors only — new cases come in Phase 3).
  5. Emit rename_table.csv with old_name -> new_name + drop markers for audit.

DOES NOT mutate eval_cases.json.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

THIS = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS))
from categorize import categorize, BUCKET_ORDER  # noqa: E402

SOURCE = THIS / "eval_cases.json"
OUT_JSON = THIS / "eval_cases_v4_500.json"
OUT_CSV = THIS / "rename_table.csv"

# 5 chain-shape keys to drop (12 cases total).
DROP_CHAIN_KEYS = {
    # storytelling + Music + Ambience
    "{NarrationAgent} -> {AmbienceAgent|IllustrationAgent|MusicAgent|NarratorAgent} -> "
    "{AmbienceAgent|IllustrationAgent|MusicAgent|NarratorAgent} -> "
    "{AmbienceAgent|IllustrationAgent|MusicAgent|NarratorAgent} -> "
    "{AmbienceAgent|MusicAgent} -> {AudioMixAgent} -> {CompositorAgent} -> {done}",
    # storytelling + ultra (imgref + M+A+T)
    "{IntakeImageAgent} -> {BriefEnricherAgent} -> {NarrationAgent} -> "
    "{AmbienceAgent|IllustrationAgent|MusicAgent|NarratorAgent} -> "
    "{AmbienceAgent|IllustrationAgent|MusicAgent|NarratorAgent} -> "
    "{AmbienceAgent|IllustrationAgent|MusicAgent|NarratorAgent} -> "
    "{AmbienceAgent|MusicAgent} -> {AudioMixAgent} -> {TranslationAgent} -> "
    "{CompositorAgent} -> {done}",
    # extend + Ambience
    "{IntakeVideoAgent} -> {VideoExtendAgent} -> {AmbienceAgent} -> "
    "{AudioMixAgent} -> {CompositorAgent} -> {done}",
    # highlight + bilingual (sub+translation)
    "{IntakeVideoAgent} -> {VideoAnalysisAgent} -> {HighlightAgent} -> "
    "{TranscriptionAgent} -> {TranslationAgent} -> {CompositorAgent} -> {done}",
    # highlight early-alt noise
    "{IntakeVideoAgent} -> {TranscriptionAgent|VideoAnalysisAgent} -> "
    "{TranscriptionAgent|VideoAnalysisAgent} -> {MusicAgent|TranscriptionAgent} -> "
    "{MusicAgent|TranscriptionAgent} -> {AudioMixAgent} -> {CompositorAgent} -> {done}",
}


def chain_key(expected_chain) -> str:
    parts = []
    for step in expected_chain:
        if isinstance(step, list):
            parts.append("{" + "|".join(sorted(step)) + "}")
        else:
            parts.append(step)
    return " -> ".join(parts)


def main() -> None:
    cases = json.loads(SOURCE.read_text(encoding="utf-8"))

    survivors: list[dict] = []
    drops: list[dict] = []
    for c in cases:
        if chain_key(c["expected_chain"]) in DROP_CHAIN_KEYS:
            drops.append(c)
        else:
            survivors.append(c)

    print(f"original: {len(cases)}, drops: {len(drops)}, survivors: {len(survivors)}")

    # Group survivors by bucket; within bucket sort by (chain_key, original name).
    by_bucket: dict[str, list[dict]] = {b: [] for b in BUCKET_ORDER}
    for c in survivors:
        b = categorize(c["expected_chain"])
        by_bucket[b].append(c)

    rename_rows: list[tuple[str, str, str, str]] = []  # old, new, bucket, action

    new_cases: list[dict] = []
    for bucket in BUCKET_ORDER:
        items = by_bucket[bucket]
        items.sort(key=lambda c: (chain_key(c["expected_chain"]), c["name"]))
        for i, c in enumerate(items, start=1):
            new_name = f"{bucket}_{i:03d}"
            entry = {
                "name": new_name,
                "category": bucket,
                "user_goal": c["user_goal"],
                "expected_chain": c["expected_chain"],
            }
            # carry through optional fields if present
            for k in ("notes", "tags"):
                if k in c:
                    entry[k] = c[k]
            new_cases.append(entry)
            rename_rows.append((c["name"], new_name, bucket, "rename"))

    for d in drops:
        rename_rows.append(
            (d["name"], "(DROPPED)", categorize(d["expected_chain"]), "drop")
        )

    # Write outputs.
    OUT_JSON.write_text(
        json.dumps(new_cases, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote: {OUT_JSON}  ({len(new_cases)} cases)")

    with OUT_CSV.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["old_name", "new_name", "bucket", "action"])
        rename_rows.sort(key=lambda r: (r[2], r[1] if r[3] == "rename" else r[0]))
        w.writerows(rename_rows)
    print(f"wrote: {OUT_CSV}  ({len(rename_rows)} rows)")

    # Per-bucket summary.
    print("\nper-bucket summary (after drop, before Phase 3 expansion):")
    for b in BUCKET_ORDER:
        n = len(by_bucket[b])
        print(f"  {b:<14} {n}")


if __name__ == "__main__":
    main()
