#!/usr/bin/env python3
"""Align storytelling cases with framework reality.

1. CHAIN REMOVE — IntakeImageAgent + BriefEnricherAgent stripped from 4 cases
   (storytelling_004 / 065 / 079 / 104). storytelling line's downstream does
   NOT consume uploaded portrait — IllustrationAgent's character anchors are
   self-t2i'd from NarrationAgent.cast.appearance_prompt (text only).
2. USER_GOAL REWRITE — 5 cases (004 / 065 / 071 / 079 / 104):
   - 004 / 065 / 079 / 104: drop "I've uploaded X" phrase, inline visual
     description so NarrationAgent still has cast.appearance_prompt material.
   - 065 / 071 / 079: flip Translation direction (narrate in English with
     Greek/Bengali subs) — Greek/Bengali not supported by Minimax TTS.
   - 104: drop "no music underneath" sentence (contradicts audio_unify).
"""
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path

CHAIN_REMOVE_CASES = {"storytelling_004", "storytelling_065",
                      "storytelling_079", "storytelling_104"}

NEW_GOALS: dict[str, str] = {
    "storytelling_004": (
        "Tell me a slow illustrated story about a chubby white-and-tabby barn "
        "cat with alert green eyes, on her midnight patrol of the farm where "
        "she protects three sleeping kittens from a barn owl. Please add "
        "gentle nighttime music. Add a slow jazz BGM and farm-night ambience: "
        "night wind, crickets, occasional distant dog bark."
    ),
    "storytelling_065": (
        "Tell me a Greek myth in pencil-and-watercolor sketch style about a "
        "young Greek shepherd boy in a worn linen tunic, standing among three "
        "goats on a dry sunlit hillside near Delphi, who heard the oracle's "
        "whispered fate carried on the wind. Narrate in English with Greek "
        "subtitles. Add an ancient-Greek lyre BGM and pastoral ambience: "
        "mountain wind, goat bells, olive-leaf rustle."
    ),
    "storytelling_071": (
        "Tell me a Greek myth about how the muse Clio chose her first mortal "
        "student, an old historian losing his memory who is the last keeper "
        "of the village chronicle, and the bargain the muse strikes with him "
        "to preserve the chronicle one final time, narrate in English with "
        "Greek subtitles, with a gentle lyre-and-aulos underscore. Add a "
        "Greek-orchestral string BGM and temple ambience: parchment "
        "unfurling, distant bronze-bell chime, wind through marble columns."
    ),
    "storytelling_079": (
        "Tell me a Bengali folktale in watercolor portrait style about a "
        "middle-aged Bengali boatman in a white kurta, weathered face, calmly "
        "steering a wooden country boat through narrow Sundarbans mangrove "
        "channels, who once ferried a tiger-spirit safely across the river "
        "in exchange for the secret of weaving silver into the sun. Narrate "
        "in English with Bengali subtitles, with a sarod-and-tabla "
        "underscore. Add a Bengali sitar BGM and mangrove ambience: oar "
        "splashes, marsh-bird calls, mangrove leaves rustling."
    ),
    "storytelling_104": (
        "I'd like an illustrated audiobook in soft watercolor style about an "
        "elderly Inuit grandmother in a fur-trimmed parka braiding her "
        "grandchild's hair inside a snow-house, telling them an old Inuktitut "
        "creation myth where the sun and moon were once two siblings playing "
        "a game of throwing seal-bones across the polar sky. Add a tender "
        "folk acoustic-guitar BGM and arctic ambience: snowstorm wind "
        "outside, hearth-fire crackle, soft child laughter."
    ),
}


def remove_intake_layers(chain: list[list[str]]) -> list[list[str]]:
    return [layer for layer in chain
            if layer != ["IntakeImageAgent"] and layer != ["BriefEnricherAgent"]]


def main() -> None:
    here = Path(__file__).parent.resolve()
    src = here / "selection.json"
    data = json.loads(src.read_text())

    rewritten = chain_stripped = 0
    for c in data:
        m = c["_meta"]
        if c["name"] in NEW_GOALS:
            m["user_goal_before_align"] = c["user_goal"]
            c["user_goal"] = NEW_GOALS[c["name"]]
            m["user_goal_realigned"] = True
            rewritten += 1
        if c["name"] in CHAIN_REMOVE_CASES:
            m["chain_before_align"] = c["expected_chain"]
            c["expected_chain"] = remove_intake_layers(c["expected_chain"])
            m["shape_layers_str"] = " -> ".join(
                "|".join(sorted(l)) for l in c["expected_chain"])
            m["shape_layer_count"] = len(c["expected_chain"])
            m["chain_realigned"] = True
            chain_stripped += 1

    src.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    md: list[str] = [
        "# 30-case selection (storytelling realigned 2026-05-09)\n\n",
        f"- {rewritten} user_goals rewritten, {chain_stripped} chains stripped of IntakeImage+Brief\n\n",
    ]
    for cat in ["cr", "intake_img", "storytelling"]:
        cat_picks = sorted([c for c in data if c["category"] == cat],
                           key=lambda c: c["name"])
        shape_set = sorted({c["_meta"]["shape_layers_str"] for c in cat_picks})
        md.append(f"## {cat} ({len(cat_picks)}, unique shapes={len(shape_set)})\n\n")
        md.append("| name | layers | flat sequence |\n|---|---|---|\n")
        for c in cat_picks:
            m = c["_meta"]
            seq = " → ".join(layer[0] for layer in c["expected_chain"])
            md.append(f"| `{c['name']}` | {m['shape_layer_count']} | {seq} |\n")
        md.append("\n")
    (here / "selection.md").write_text("".join(md))

    print(f"Realigned: {rewritten} goals, {chain_stripped} chains stripped")
    cnt = Counter(c["_meta"]["shape_layers_str"] for c in data
                  if c["category"] == "storytelling")
    print(f"\nstorytelling unique shapes: {len(cnt)}")
    for shape, n in cnt.most_common():
        print(f"  [{n}] {shape}")


if __name__ == "__main__":
    main()
