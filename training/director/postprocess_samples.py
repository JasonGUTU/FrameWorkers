#!/usr/bin/env python3
"""Post-process ``samples_sft_full.jsonl`` in-place to align with the
post-retirement topology (IntakeTextAgent gone / SubtitleAgent gone).

Why this script exists
======================
The JSONL on disk was produced by the teacher LLM BEFORE two major
retirements:

  1. IntakeTextAgent — retired 2026-04-23 (commit 5550555). Chat/text
     is now persisted as a ``[creative_brief]`` artifact by the
     workspace layer; no agent step at the head of the plan.

  2. SubtitleAgent — retired 2026-04-23 (commit 74f37cc). Subtitle
     flows now route ``TranscriptionAgent → (Translation?) →
     Compositor``; CompositorMaterializer renders segments to SRT via
     pure Python.

100% of the 1110 on-disk SFT samples still reference these retired
agents (system-prompt catalog AND assistant chosen/rejected plans),
so training on them as-is would teach the LoRA to emit plans that
fail ``allowed_ids`` validation on every inference call.

What this script fixes (mechanical, no teacher LLM call)
========================================================
For every sample:
  * **System prompt** — regenerated from the current AGENT_REGISTRY via
    ``gen_samples.build_system_prompt()``. This drops retired agents
    from the catalog and introduces NarrationAgent / IllustrationAgent
    / NarratorAgent so the trained model sees the storytelling chain
    in its context (it still won't EMIT those chains — the user-goal
    + chosen-plan pair in each sample is still cinematic/existing-
    video — but the catalog is at least factually current).
  * **Assistant ``chosen`` plan** — the JSON emitted by the teacher
    under the ``assistant`` role. We parse its JSON, transform its
    ``plan`` list:
      - drop the first step iff it is IntakeTextAgent
      - replace any SubtitleAgent step with TranscriptionAgent
      - dedup consecutive identical single-agent steps (would collapse
        ``Transcription → Subtitle`` sequences into a single
        ``Transcription`` step, matching the eval-case GT semantics)
    Re-serialise and write back.

What this script does NOT do
=============================
It does not GENERATE new storytelling samples — that requires a
teacher LLM call (see ``gen_training_full.py``). Run the storytelling
subset of that script AFTER this post-process to merge in fresh
storytelling samples; the two stages are additive.

Usage
=====
    PYTHONPATH=. python training/director/postprocess_samples.py \
        --in samples_sft_full.jsonl \
        --out samples_sft_full.jsonl

Produces a backup at ``<out>.pre_postprocess_bak`` first.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from collections import Counter
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(REPO_ROOT))

from training.director.gen_samples import build_system_prompt  # noqa: E402


def refactor_plan(plan: list[dict]) -> list[dict]:
    """Mirror the eval GT post-retirement transforms on a chosen/rejected
    plan list.

    Steps:
      (i)   Replace every ``SubtitleAgent`` entry with ``TranscriptionAgent``.
      (ii)  Drop the first entry iff it is ``IntakeTextAgent``.
      (iii) Dedup adjacent identical agent_ids (handles
            Transcription → Subtitle → ... collapsing to a single
            Transcription step after (i)).
    """
    if not isinstance(plan, list):
        return plan

    # (i) Subtitle → Transcription substitution
    substituted: list[dict] = []
    for step in plan:
        if not isinstance(step, dict):
            continue
        aid = step.get("agent_id")
        if aid == "SubtitleAgent":
            new_step = dict(step)
            new_step["agent_id"] = "TranscriptionAgent"
            substituted.append(new_step)
        else:
            substituted.append(step)

    # (ii) strip leading IntakeTextAgent
    if substituted and substituted[0].get("agent_id") == "IntakeTextAgent":
        substituted = substituted[1:]

    # (iii) Dedup consecutive identical agent_ids — keeps the first
    # occurrence's ``intent`` (which usually has the richer wording).
    deduped: list[dict] = []
    prev_aid: str | None = None
    for step in substituted:
        aid = step.get("agent_id")
        if aid and aid == prev_aid:
            continue
        deduped.append(step)
        prev_aid = aid

    return deduped


def postprocess_sample(sample: dict, new_system_prompt: str) -> tuple[dict, dict[str, int]]:
    """Apply all transforms to a single SFT sample.

    Returns (new_sample, stats_delta).
    """
    stats = Counter()
    messages = sample.get("messages", [])
    new_messages: list[dict] = []
    for m in messages:
        if not isinstance(m, dict):
            new_messages.append(m)
            continue
        role = m.get("role")
        content = m.get("content", "")
        if role == "system":
            new_messages.append({"role": "system", "content": new_system_prompt})
            stats["system_replaced"] += 1
            continue
        if role == "assistant":
            # Parse assistant JSON, transform the plan, reserialise.
            try:
                payload = json.loads(content)
            except Exception:
                new_messages.append(m)
                stats["assistant_parse_failed"] += 1
                continue
            original_plan = payload.get("plan")
            new_plan = refactor_plan(original_plan)
            if new_plan != original_plan:
                stats["assistant_plan_changed"] += 1
            payload["plan"] = new_plan
            new_messages.append({
                "role": "assistant",
                "content": json.dumps(payload, ensure_ascii=False),
            })
            continue
        # user / other — copy through unchanged
        new_messages.append(m)
    new_sample = dict(sample)
    new_sample["messages"] = new_messages
    return new_sample, stats


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument(
        "--in",
        dest="in_path",
        type=Path,
        default=SCRIPT_DIR / "samples_sft_full.jsonl",
        help="Input JSONL file (default: samples_sft_full.jsonl in this dir)",
    )
    ap.add_argument(
        "--out",
        dest="out_path",
        type=Path,
        default=None,
        help="Output JSONL (default: overwrite input). A .pre_postprocess_bak backup is always created.",
    )
    args = ap.parse_args()

    in_path: Path = args.in_path
    out_path: Path = args.out_path or in_path
    bak_path = Path(str(out_path) + ".pre_postprocess_bak")

    if not in_path.is_file():
        ap.error(f"Input file does not exist: {in_path}")

    # Backup before any write.
    if out_path == in_path and not bak_path.exists():
        shutil.copy2(in_path, bak_path)
        print(f"Backup saved: {bak_path}")

    new_sys_prompt = build_system_prompt()
    print(f"Built new system prompt: {len(new_sys_prompt):,} chars")

    # Read first, then write — prevents truncation when in_path == out_path
    # (opening the same path for write in 'w' mode before the reader has
    # started iterating silently zeros the input).
    with in_path.open("r", encoding="utf-8") as inf:
        raw_lines = [line.strip() for line in inf if line.strip()]

    totals: Counter = Counter()
    out_lines: list[str] = []
    for line in raw_lines:
        sample = json.loads(line)
        new_sample, delta = postprocess_sample(sample, new_sys_prompt)
        totals.update(delta)
        out_lines.append(json.dumps(new_sample, ensure_ascii=False))

    with out_path.open("w", encoding="utf-8") as outf:
        outf.write("\n".join(out_lines) + "\n")
    written = len(out_lines)

    print(f"Processed {written} samples → {out_path}")
    for k, v in sorted(totals.items()):
        print(f"  {k}: {v}")

    # Quick sanity: ensure no "IntakeTextAgent" or "SubtitleAgent"
    # remains in the chosen plans (system-prompt mentions of retired
    # agents are the regenerated catalog's job — they should all be
    # gone too since build_system_prompt pulls from live registry).
    residue = Counter()
    with out_path.open("r", encoding="utf-8") as f:
        for line in f:
            s = json.loads(line)
            for m in s.get("messages", []):
                if m.get("role") == "assistant":
                    try:
                        payload = json.loads(m.get("content", ""))
                    except Exception:
                        continue
                    for step in payload.get("plan", []) or []:
                        aid = step.get("agent_id") if isinstance(step, dict) else None
                        if aid in {"IntakeTextAgent", "SubtitleAgent"}:
                            residue[aid] += 1
    if residue:
        print(f"⚠ residue in chosen plans: {dict(residue)}")
        return 1
    print("✓ no IntakeTextAgent / SubtitleAgent remaining in chosen plans")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
