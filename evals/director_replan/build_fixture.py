"""Build replan-eval fixture from a routing-eval snapshot.

Picks chain_correct=false cases that classify as skip_producer / substitute —
i.e. cases that would actually trigger an [upstream_input_rejected] reject in
production — strats by missing-producer category, and synthesizes a 10-case
fixture for evaluating the director's replan_on_failure prompt.

Usage:
    python build_fixture.py \\
        --snapshot Runtime/eval_routing/<snapshot>.json \\
        --out evals/director_replan/cases/cases.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


# Mapping: missing producer agent → label name as it appears in downstream
# consumers' input slots in the agent catalog. The director's replan prompt
# instructs the LLM to "match missing=[...] to the labels [in catalog]" — so
# these strings must use the same label vocabulary the catalog exposes.
PRODUCER_TO_LABEL: Dict[str, str] = {
    "IntakeVideoAgent": "source_video",
    "IntakeImageAgent": "character_reference",
    "TranslationAgent": "subtitle_tracks",
    "StoryAgent": "story",
    "ScreenplayAgent": "screenplay",
    "KeyFrameAgent": "keyframes_metadata",
    "VideoAgent": "video_package",
    "VideoAnalysisAgent": "video_analysis",
    "MusicAgent": "music",
    "AudioMixAgent": "audio_package",
    "TranscriptionAgent": "source_text",
    "StyleTransferAgent": "style_reference",
    "BriefEnricherAgent": "creative_brief",
    "NarrationAgent": "narration_script",
    "NarratorAgent": "narrator_audio",
    "IllustrationAgent": "illustration_sequence",
    "AmbienceAgent": "ambience",
    "HighlightAgent": "highlight_video",
    "CompositorAgent": "final_video",
    "VideoExtendAgent": "extended_video",
}

# Skip-producer sampling: 8 cases stratified by missing producer.
# Per-bucket cap. TranslationAgent dominates (~54%) so capped at 2; others 1.
# Buckets not present in the actual pool are silently skipped, and the loop
# back-fills any shortfall by taking additional cases from the largest bucket.
SKIP_PRODUCER_CAP: Dict[str, int] = {
    "TranslationAgent": 2,
    "AudioMixAgent": 1,
    "VideoAnalysisAgent": 1,
    "MusicAgent": 1,
    "IntakeVideoAgent": 1,
    "CompositorAgent": 1,
    "BriefEnricherAgent": 1,
    "IntakeImageAgent": 1,
}
N_SKIP_PRODUCER = 8
N_SUBSTITUTE = 2


def expected_flat(case: Dict[str, Any]) -> List[str]:
    return [
        s["expected"][0]
        for s in case["steps"]
        if s.get("expected") and s["expected"][0] != "<none>"
    ]


def classify(case: Dict[str, Any]) -> str:
    actual_set = set(case["actual_chain"])
    expected_set = set(expected_flat(case))
    missing = expected_set - actual_set
    extra = actual_set - expected_set
    if missing and not extra:
        return "skip_producer"
    if missing and extra:
        return "substitute"
    if not missing and extra:
        return "extra_insert"
    return "reorder_only"


def first_wrong_pos(case: Dict[str, Any]) -> Optional[int]:
    for i, s in enumerate(case["steps"]):
        if not s.get("correct", False):
            return i
    return None


def synth_error_string(missing_agents: List[str]) -> str:
    labels = [PRODUCER_TO_LABEL.get(a, a.lower()) for a in missing_agents]
    return (
        "[upstream_input_rejected] "
        "reason=required upstream artifacts not produced by any earlier step; "
        f"missing=[{','.join(labels)}]"
    )


def build_fixture_case(
    case: Dict[str, Any], err_type: str
) -> Optional[Dict[str, Any]]:
    actual = case["actual_chain"]
    expected = expected_flat(case)
    pos = first_wrong_pos(case)
    if pos is None or pos >= len(actual):
        return None
    failed_agent = actual[pos]
    missing_agents = sorted(set(expected) - set(actual))
    if not missing_agents:
        return None
    expected_tail_set = sorted(set(expected[pos:]))
    prefix_consistent = actual[:pos] == expected[:pos]
    return {
        "name": case["name"],
        "type": err_type,
        "user_goal": case["user_goal"],
        "initial_plan": actual,
        "expected_chain": expected,
        "failed_step_index": pos,
        "failed_agent_id": failed_agent,
        "error_string": synth_error_string(missing_agents),
        "missing_agents": missing_agents,
        "expected_must_include_in_new_tail": expected_tail_set,
        "must_not_first_in_new_tail": failed_agent,
        "prefix_consistent": prefix_consistent,
    }


def select_cases(
    wrong: List[Dict[str, Any]],
    cap: Dict[str, int],
    n_skip: int,
    n_substitute: int,
) -> List[Dict[str, Any]]:
    skip_pool: List[Dict[str, Any]] = []
    sub_pool: List[Dict[str, Any]] = []
    for w in wrong:
        cls = classify(w)
        if cls == "skip_producer":
            skip_pool.append(w)
        elif cls == "substitute":
            sub_pool.append(w)

    fixture_cases: List[Dict[str, Any]] = []
    selected_names: set[str] = set()

    def try_add(w: Dict[str, Any], err_type: str) -> bool:
        if w["name"] in selected_names:
            return False
        fc = build_fixture_case(w, err_type)
        if fc is None:
            return False  # invalid case (e.g. chain-truncation) — don't occupy quota
        fixture_cases.append(fc)
        selected_names.add(w["name"])
        return True

    # Pass 1: stratified by missing-producer bucket up to per-bucket cap.
    for ag, want in cap.items():
        candidates = [
            w
            for w in skip_pool
            if ag in (set(expected_flat(w)) - set(w["actual_chain"]))
        ]
        added = 0
        for w in candidates:
            if added >= want:
                break
            if try_add(w, "skip_producer"):
                added += 1

    # Pass 2: top up shortfall from any remaining skip_producer cases.
    skip_count = sum(1 for fc in fixture_cases if fc["type"] == "skip_producer")
    for w in skip_pool:
        if skip_count >= n_skip:
            break
        if try_add(w, "skip_producer"):
            skip_count += 1

    # Substitute: take the first n that build successfully.
    sub_count = 0
    for w in sub_pool:
        if sub_count >= n_substitute:
            break
        if try_add(w, "substitute"):
            sub_count += 1

    return fixture_cases


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--snapshot",
        required=True,
        help="Path to Runtime/eval_routing/<...>.json snapshot",
    )
    ap.add_argument(
        "--out",
        default=os.path.join(
            PROJECT_ROOT, "evals", "director_replan", "cases", "cases.json"
        ),
    )
    args = ap.parse_args()

    snapshot_path = (
        args.snapshot
        if os.path.isabs(args.snapshot)
        else os.path.join(PROJECT_ROOT, args.snapshot)
    )
    snap = json.load(open(snapshot_path))
    wrong = [r for r in snap["results"] if not r.get("chain_correct", False)]
    print(f"Loaded snapshot with {len(snap['results'])} results, {len(wrong)} wrong.")

    fixture = select_cases(wrong, SKIP_PRODUCER_CAP, N_SKIP_PRODUCER, N_SUBSTITUTE)
    print(f"Selected {len(fixture)} fixture cases:")
    for fc in fixture:
        print(
            f"  - {fc['name']:25s} type={fc['type']:15s} "
            f"failed@{fc['failed_step_index']} ({fc['failed_agent_id']}) "
            f"missing={fc['missing_agents']} prefix_ok={fc['prefix_consistent']}"
        )

    out_path = args.out
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    payload = {
        "source_snapshot": os.path.relpath(snapshot_path, PROJECT_ROOT),
        "source_model": snap.get("meta", {}).get("model"),
        "n_cases": len(fixture),
        "cases": fixture,
    }
    with open(out_path, "w") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"\nWrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
