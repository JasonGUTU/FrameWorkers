#!/usr/bin/env python3
"""Lock GT chain into a deterministic execution sequence.

Why: we are not measuring router flexibility — we are deterministically
testing video / audio generation against fixed inputs. So every agent goes
into its own layer (no more layer-internal sets like [A, B, C]) and is
ordered by MASTER_ORDER, which captures the real producer→consumer
dependencies inside the framework.

Effect:
  - Each agent appears at most once across the chain (already an invariant —
    CLAUDE.md "每个 agent ≤1 次"); any v4500-era repetition is collapsed.
  - Each layer holds exactly one agent (plus a final ["done"] sentinel),
    eliminating routing ambiguity.
  - Layer order is deterministic: pulled from MASTER_ORDER, restricted to
    the set of agents the case actually uses.

Backup: per-case _meta.chain_before_lock keeps the prior shape so we can
diff before/after for each of the 30 cases.
"""
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path

# Producer → consumer order, distilled from agents/__init__.py + each
# descriptor's input labels. Single source of truth for "what runs when".
MASTER_ORDER: list[str] = [
    # Inputs
    "IntakeImageAgent",
    "IntakeVideoAgent",
    "BriefEnricherAgent",
    # Cinematic-only analysis branches (operate on intaken video)
    "VideoAnalysisAgent",
    "HighlightAgent",
    "StyleTransferAgent",
    # Cinematic main line
    "StoryAgent",
    "ScreenplayAgent",
    "KeyFrameAgent",
    "VideoAgent",
    "VideoExtendAgent",
    # Storytelling main line
    "NarrationAgent",
    "IllustrationAgent",
    "NarratorAgent",
    # Film-wide audio beds
    "MusicAgent",
    "AmbienceAgent",
    # Subtitle pipeline (Transcription consumes baked dialogue / narrator wav;
    # Translation consumes Transcription)
    "TranscriptionAgent",
    "TranslationAgent",
    # Final assembly
    "AudioMixAgent",
    "CompositorAgent",
]


def lock_chain(chain: list[list[str]]) -> list[list[str]]:
    """Flatten chain → one agent per layer, sorted by MASTER_ORDER, dedup'd."""
    agents: set[str] = set()
    for layer in chain:
        for a in layer:
            if a != "done":
                agents.add(a)
    unknown = agents - set(MASTER_ORDER)
    if unknown:
        raise RuntimeError(
            f"agents not in MASTER_ORDER: {unknown} — extend MASTER_ORDER"
        )
    locked = [[a] for a in MASTER_ORDER if a in agents]
    locked.append(["done"])
    return locked


def main() -> None:
    here = Path(__file__).parent.resolve()
    src = here / "selection.json"
    data = json.loads(src.read_text())

    locked_count = 0
    diffs: list[str] = []
    for c in data:
        m = c["_meta"]
        m["chain_before_lock"] = c["expected_chain"]
        old_layers = len(c["expected_chain"])
        old_flat = [a for layer in c["expected_chain"] for a in layer]
        c["expected_chain"] = lock_chain(c["expected_chain"])
        new_layers = len(c["expected_chain"])
        m["shape_layers_str"] = " -> ".join(
            "|".join(sorted(l)) for l in c["expected_chain"]
        )
        m["shape_layer_count"] = new_layers
        m["chain_locked"] = True
        locked_count += 1
        # Track shape change
        if old_layers != new_layers:
            diffs.append(f"  {c['name']:20} {old_layers}L → {new_layers}L")

    src.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    # Regenerate selection.md
    md: list[str] = [
        "# 30-case selection (chain locked deterministically 2026-05-09)\n\n",
        "Source: `eval_cases_v4500_balanced.json`\n",
        "Total: 30 (10 per category × 3 categories)\n",
        "- Rewritten: cr (10) + intake_img (10) → 中文短剧爆款; storytelling (10) topic kept\n",
        "- Renamed: hard_004 → cr_104, hard_007 → cr_107, hard_021 → storytelling_104\n",
        "- Audio unified: storytelling (10) — every chain has Music + Ambience + AudioMix\n",
        f"- **Chain locked**: every agent now in its own layer, sorted by MASTER_ORDER. "
        f"Mock upload images generated for {{intake_img × 10, storytelling × 4}}.\n\n",
    ]
    for cat in ["cr", "intake_img", "storytelling"]:
        cat_picks = sorted(
            [c for c in data if c["category"] == cat], key=lambda c: c["name"]
        )
        shape_set = sorted({c["_meta"]["shape_layers_str"] for c in cat_picks})
        rw_count = sum(1 for c in cat_picks if c["_meta"].get("rewritten"))
        au_count = sum(1 for c in cat_picks if c["_meta"].get("audio_unified"))
        lk_count = sum(1 for c in cat_picks if c["_meta"].get("chain_locked"))
        md.append(
            f"## {cat} ({len(cat_picks)}, rewritten={rw_count}, "
            f"audio_unified={au_count}, locked={lk_count})\n"
        )
        md.append(f"- unique shapes (post-lock): **{len(shape_set)}**\n\n")
        md.append("| name | layers | flat sequence |\n|---|---|---|\n")
        for c in cat_picks:
            m = c["_meta"]
            seq = " → ".join(layer[0] for layer in c["expected_chain"])
            md.append(f"| `{c['name']}` | {m['shape_layer_count']} | {seq} |\n")
        md.append("\n")
    (here / "selection.md").write_text("".join(md))

    print(f"Locked {locked_count} chains")
    print("\nLayer-count diffs (old → new):")
    for d in diffs:
        print(d)
    print()
    cnt = Counter(c["_meta"]["shape_layers_str"] for c in data)
    print(f"Total unique shapes after lock: {len(cnt)}")
    for shape, n in cnt.most_common():
        print(f"  [{n}] {shape}")


if __name__ == "__main__":
    main()
