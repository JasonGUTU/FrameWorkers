"""Cleanup: drop the n=2 highlight shape (highlight_015 / _016) and renumber.

Chain `IntakeVideo → VideoAnalysis → Highlight → Transcription → {Music|Translation}×2`
only had 2 cases, below the n=5 floor. Per drop-n<=3 rule: drop.

After drop, renumber highlight sequentially highlight_001..N.
Other buckets untouched.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

THIS = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS))
from categorize import categorize  # noqa: E402

V4 = THIS / "eval_cases_v4_500.json"

DROP_NAMES = {"highlight_015", "highlight_016"}


def main() -> None:
    cases = json.loads(V4.read_text(encoding="utf-8"))
    print(f"before: {len(cases)} cases")

    survivors = [c for c in cases if c["name"] not in DROP_NAMES]
    dropped = [c for c in cases if c["name"] in DROP_NAMES]

    if len(dropped) != len(DROP_NAMES):
        raise SystemExit(f"expected to drop {len(DROP_NAMES)} cases, found {len(dropped)}")

    # Verify all dropped were highlight bucket
    for c in dropped:
        if c["category"] != "highlight":
            raise SystemExit(f"unexpected drop: {c['name']} category={c['category']}")

    # Renumber highlight bucket sequentially, preserving relative order
    next_idx = 1
    seen_highlight = 0
    for c in survivors:
        if c["category"] == "highlight":
            seen_highlight += 1
            c["name"] = f"highlight_{seen_highlight:03d}"

    print(f"dropped: {sorted(c['name'] for c in dropped)}")
    print(f"renumbered highlight bucket: {seen_highlight} cases sequential")

    # Save
    V4.write_text(
        json.dumps(survivors, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"after:  {len(survivors)} cases")

    # Re-verify
    new_cases = json.loads(V4.read_text(encoding="utf-8"))
    bad = [c for c in new_cases if categorize(c["expected_chain"]) != c["category"]]
    if bad:
        raise SystemExit(f"category mismatch after cleanup: {bad}")
    names = [c["name"] for c in new_cases]
    if len(names) != len(set(names)):
        raise SystemExit("duplicate names after cleanup")

    from collections import Counter
    from categorize import BUCKET_ORDER
    buckets = Counter(c["category"] for c in new_cases)
    print("\nfinal per-bucket counts:")
    for b in BUCKET_ORDER:
        print(f"  {b:<14} {buckets.get(b, 0)}")


if __name__ == "__main__":
    main()
