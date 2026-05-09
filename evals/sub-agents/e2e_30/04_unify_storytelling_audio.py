#!/usr/bin/env python3
"""Unify storytelling chain to include MusicAgent + AmbienceAgent on every case.

Why: an illustrated audiobook without BGM + ambience is dry and the
configuration delta becomes a confounder in the user study (subjects rate
"missing audio bed" as content quality). All 10 storytelling cases get the
full producer set so the user-study signal is content quality, not setup.

Mutations per storytelling case:
  - expected_chain: every "producer layer" (the layers between NarrationAgent
    and {AudioMixAgent | TranslationAgent | CompositorAgent}) gets rewritten to
    [IllustrationAgent, NarratorAgent, MusicAgent, AmbienceAgent]. If no
    AudioMixAgent layer exists in the original chain, one is inserted right
    after the last producer layer (before Translation/Compositor).
  - user_goal: a case-specific BGM + ambience trigger sentence is appended in
    Chinese, themed to the story (sea creature → 深海大提琴 + 鲸鸣; library
    ghost → 钢琴 + 翻书声; etc.). storytelling_013 only gets an ambience
    trigger because its original goal already specifies "gentle slow piano".

Backups:
  - selection.original.json (v4500 source) — already exists, untouched
  - per-case _meta.chain_before_audio_unify / user_goal_before_audio_unify
"""
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path

PRODUCER_FULL = ["IllustrationAgent", "NarratorAgent", "MusicAgent", "AmbienceAgent"]

# Per-case BGM + ambience suggestion appended to user_goal (case-themed).
# storytelling_013 only adds ambience because its original goal already
# explicitly asks for "gentle, slow piano score".
APPEND_GOAL: dict[str, str] = {
    "storytelling_024": " Add an ethereal cello BGM and deep-sea ambience: water bubbles and distant whale calls.",
    "storytelling_026": " Add a tense piano BGM and library ambience: page rustles, distant footsteps, hollow corridor reverb.",
    "storytelling_004": " Add a slow jazz BGM and farm-night ambience: night wind, crickets, occasional distant dog bark.",
    "storytelling_104": " Add a tender folk acoustic-guitar BGM and arctic ambience: snowstorm wind outside, hearth-fire crackle, soft child laughter.",
    "storytelling_065": " Add an ancient-Greek lyre BGM and pastoral ambience: mountain wind, goat bells, olive-leaf rustle.",
    "storytelling_011": " Add an ethereal flute BGM and forest ambience: stream burble, songbirds, wind through pine needles.",
    "storytelling_013": " Layer in a soft ambience: faint fan hum and distant gentle rain.",
    "storytelling_071": " Add a Greek-orchestral string BGM and temple ambience: parchment unfurling, distant bronze-bell chime, wind through marble columns.",
    "storytelling_047": " Add a Mexican acoustic-guitar BGM and rural ambience: wind through cornstalks, distant singing, intermittent rooster and dog calls.",
    "storytelling_079": " Add a Bengali sitar BGM and mangrove ambience: oar splashes, marsh-bird calls, mangrove leaves rustling.",
}


def is_producer_layer(layer: list[str]) -> bool:
    """A layer is a 'producer' (per-segment generator) iff it contains
    IllustrationAgent or NarratorAgent and none of the structural agents.
    """
    s = set(layer)
    if "IllustrationAgent" not in s and "NarratorAgent" not in s:
        return False
    structural = {"NarrationAgent", "AudioMixAgent", "TranslationAgent",
                  "CompositorAgent", "done"}
    return not (s & structural)


def unify_chain(chain: list[list[str]]) -> list[list[str]]:
    """Replace producer layers with PRODUCER_FULL; insert AudioMixAgent if missing."""
    has_audio_mix = any("AudioMixAgent" in layer for layer in chain)
    audio_mix_inserted = False
    in_producer = False
    new_chain: list[list[str]] = []

    for layer in chain:
        if is_producer_layer(layer):
            new_chain.append(list(PRODUCER_FULL))
            in_producer = True
            continue
        # Just left producer block — inject AudioMix if missing
        if in_producer and not has_audio_mix and not audio_mix_inserted:
            new_chain.append(["AudioMixAgent"])
            audio_mix_inserted = True
        new_chain.append(list(layer))
        in_producer = False
    return new_chain


def main() -> None:
    here = Path(__file__).parent.resolve()
    src = here / "selection.json"
    data = json.loads(src.read_text())

    mutated = 0
    for c in data:
        if c["category"] != "storytelling":
            continue
        m = c["_meta"]
        m["chain_before_audio_unify"] = c["expected_chain"]
        m["user_goal_before_audio_unify"] = c["user_goal"]
        c["expected_chain"] = unify_chain(c["expected_chain"])
        suffix = APPEND_GOAL.get(c["name"], "")
        if suffix:
            c["user_goal"] = c["user_goal"].rstrip() + suffix
        m["shape_layers_str"] = " -> ".join("|".join(sorted(l)) for l in c["expected_chain"])
        m["shape_layer_count"] = len(c["expected_chain"])
        m["audio_unified"] = True
        mutated += 1

    src.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    # Regenerate selection.md
    md: list[str] = [
        "# 30-case selection (seed=42, full audit trail in _meta)\n\n",
        "Source: `eval_cases_v4500_balanced.json`\n",
        "Total: 30 (10 per category × 3 categories)\n",
        "- Rewritten: cr (10) + intake_img (10) → 中文短剧爆款; storytelling (10) topic kept\n",
        "- Renamed: hard_004 → cr_104, hard_007 → cr_107, hard_021 → storytelling_104\n",
        "- Audio unified: storytelling (10) — every chain now has Music + Ambience + AudioMix\n\n",
    ]
    for cat in ["cr", "intake_img", "storytelling"]:
        cat_picks = sorted([c for c in data if c["category"] == cat],
                           key=lambda c: c["name"])
        shape_set = sorted({c["_meta"]["shape_layers_str"] for c in cat_picks})
        rw_count = sum(1 for c in cat_picks if c["_meta"].get("rewritten"))
        au_count = sum(1 for c in cat_picks if c["_meta"].get("audio_unified"))
        md.append(
            f"## {cat} ({len(cat_picks)}, rewritten={rw_count}, "
            f"audio_unified={au_count})\n"
        )
        md.append(f"- unique shapes: **{len(shape_set)}**\n\n")
        md.append("| name | layers | user_goal |\n|---|---|---|\n")
        for c in cat_picks:
            m = c["_meta"]
            goal = c["user_goal"][:160].replace("|", r"\|")
            if len(c["user_goal"]) > 160:
                goal += "..."
            md.append(f"| `{c['name']}` | {m['shape_layer_count']} | {goal} |\n")
        md.append("\n")
    (here / "selection.md").write_text("".join(md))

    print(f"Audio unified: {mutated} storytelling cases")
    cnt = Counter(c["_meta"]["shape_layers_str"] for c in data
                  if c["category"] == "storytelling")
    print(f"\nstorytelling unique shapes after unify: {len(cnt)}")
    for shape, n in cnt.most_common():
        print(f"  [{n}] {shape}")


if __name__ == "__main__":
    main()
