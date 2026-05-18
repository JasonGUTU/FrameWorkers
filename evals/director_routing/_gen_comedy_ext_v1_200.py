#!/usr/bin/env python3
"""One-off generator for the ComedyStoryAgent plug-and-play eval set.

Produces 100 comedy + 100 non-comedy realistic user film-request goals,
diversified across 10 subgenres per side × 10 goals per subgenre. Each
goal is a one-sentence natural-language film request — no audio /
subtitle / extra-modality language (which would change the expected
chain). Output JSON shape matches evals/director_routing/eval_cases.json:

    [
      {"name": "<id>", "user_goal": "<...>",
       "expected_chain": [["StoryAgent"|"ComedyStoryAgent"],
                          ["ScreenplayAgent"], ...]},
      ...
    ]

Run from repo root:
    PYTHONPATH=. python evals/director_routing/_gen_comedy_ext_v1_200.py
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(REPO_ROOT))


COMEDY_SUBGENRES = [
    ("sitcom", "situational comedy / domestic / workplace ensemble"),
    ("romcom", "romantic comedy — meet-cute, fake-dating, rival-to-lover"),
    ("slapstick", "physical comedy — escalating gags, prop disasters"),
    ("mockumentary", "documentary-style fake interviews around a quirky community"),
    ("satire", "social/political/corporate satire — biting irony of institutions"),
    ("parody", "genre parody — sending up a specific film/show tradition"),
    ("dark_comedy", "dark / black comedy — laughter from morbid, taboo, awkward subjects"),
    ("screwball", "screwball — fast-talking battle-of-the-sexes shenanigans, mistaken identity"),
    ("absurdist", "absurdist / surreal comedy — bizarre premise played deadpan-straight"),
    ("cringe", "cringe / awkward comedy — characters who keep digging deeper holes"),
]

NONCOMEDY_SUBGENRES = [
    ("war_drama", "war drama — moral choice under bombardment / occupation / front-line"),
    ("noir_thriller", "noir / hardboiled detective thriller — 1940s-1960s urban underworld"),
    ("psych_horror", "psychological thriller / horror — dread, paranoia, unreliable narrator"),
    ("family_drama", "family drama — estrangement, inheritance, terminal illness, hidden secret"),
    ("historical", "historical drama — specific named era + region (Tang, Edo, Victorian, etc.)"),
    ("scifi_drama", "sci-fi drama — generation ship, AI consciousness, time loop, climate dystopia"),
    ("wuxia", "wuxia / martial-arts drama — sword sect, vengeance, jianghu"),
    ("crime_heist", "crime drama / heist — cold case, undercover op, robbery gone wrong"),
    ("coming_of_age", "coming-of-age — teen first-summer, music school, immigrant kid"),
    ("supernatural", "supernatural / dark fantasy — ghost, curse, occult ritual"),
]

CASES_PER_SUBGENRE = 10


SYSTEM_PROMPT = (
    "You produce realistic one-sentence film-request user goals that a real "
    "user might type into a chat to ask an AI film generator for a "
    "mini-drama or short film. Be specific (named era / region / occupation "
    "/ protagonist), be concise, vary openings, vary length naturally, "
    "vary tone. Return JSON only — a single object {\"goals\": [\"...\", "
    "\"...\", ...]} with exactly the requested count. No commentary, no "
    "markdown, no code fences."
)


def _user_prompt(subgenre_tag: str, subgenre_desc: str, n: int) -> str:
    return (
        f"Generate {n} DISTINCT one-sentence film-request user_goals in the "
        f"\"{subgenre_tag}\" subgenre ({subgenre_desc}). Each goal is what a "
        f"user types into chat to request a mini-drama / short film. "
        f"Diversify protagonist, setting, era, region, occupation, premise. "
        f"DO NOT mention music / soundtrack / BGM / ambient / subtitles / "
        f"captions / translation / voiceover / narration — the request must "
        f"be a bare film ask so the downstream chain is fixed. Each goal "
        f"should be 1-3 sentences max. Return ONLY:\n"
        f"{{\"goals\": [\"goal 1\", \"goal 2\", ..., \"goal {n}\"]}}"
    )


async def _gen_one_subgenre(
    client,
    side: str,  # "comedy" or "noncomedy"
    tag: str,
    desc: str,
    n: int,
    sem: asyncio.Semaphore,
    *,
    max_attempts: int = 5,
) -> list[str]:
    """One subgenre → list of user_goal strings. Retries CF 502 / transient
    errors with exponential backoff; surfaces final error if all attempts
    fail. Returns whatever goals successfully parsed (possibly < n)."""
    backoff = 4.0
    last_exc: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            async with sem:
                data = await client.chat_json(
                    system_prompt=SYSTEM_PROMPT,
                    user_prompt=_user_prompt(tag, desc, n),
                    model="gemini-2.5-pro",
                    max_tokens=8192,
                )
            goals = data.get("goals") or []
            goals = [str(g).strip() for g in goals if str(g).strip()]
            if len(goals) < n:
                print(
                    f"  WARN: {side}/{tag} returned only "
                    f"{len(goals)}/{n} goals (attempt {attempt})"
                )
            return goals[:n]
        except Exception as exc:  # CF 502 / transient gateway / parse / etc.
            last_exc = exc
            short = str(exc).splitlines()[0][:160]
            if attempt < max_attempts:
                print(
                    f"  retry {side}/{tag} attempt {attempt}/{max_attempts} "
                    f"after {backoff:.1f}s — {short}"
                )
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 60.0)
            else:
                print(
                    f"  FAIL {side}/{tag} after {max_attempts} attempts: {short}"
                )
    return []  # all attempts failed


async def _retry_short(
    client,
    side: str,
    tag: str,
    desc: str,
    have: list[str],
    n: int,
    sem: asyncio.Semaphore,
) -> list[str]:
    """If a subgenre returned < n, do a single retry asking only for the missing count."""
    missing = n - len(have)
    if missing <= 0:
        return have
    print(f"  retry {side}/{tag}: asking for {missing} more")
    extra = await _gen_one_subgenre(client, side, tag, desc, missing, sem)
    out = have + extra
    return out[:n]


async def main() -> None:
    from inference.clients import LLMClient

    out_path = SCRIPT_DIR / "cases_comedy_ext_v1_200.json"

    client = LLMClient()
    sem = asyncio.Semaphore(4)

    # Stage 1: parallel kickoff for all 20 subgenres
    comedy_tasks = [
        _gen_one_subgenre(client, "comedy", tag, desc, CASES_PER_SUBGENRE, sem)
        for tag, desc in COMEDY_SUBGENRES
    ]
    noncomedy_tasks = [
        _gen_one_subgenre(client, "noncomedy", tag, desc, CASES_PER_SUBGENRE, sem)
        for tag, desc in NONCOMEDY_SUBGENRES
    ]
    print(
        f"Stage 1: {len(comedy_tasks)} comedy + {len(noncomedy_tasks)} "
        f"non-comedy subgenres × {CASES_PER_SUBGENRE} goals each"
    )

    comedy_results, noncomedy_results = await asyncio.gather(
        asyncio.gather(*comedy_tasks),
        asyncio.gather(*noncomedy_tasks),
    )

    # Stage 2: top-up any short subgenres
    print("Stage 2: top-up retries for any short subgenres")
    comedy_results = await asyncio.gather(*[
        _retry_short(
            client, "comedy", tag, desc, got, CASES_PER_SUBGENRE, sem
        )
        for (tag, desc), got in zip(COMEDY_SUBGENRES, comedy_results)
    ])
    noncomedy_results = await asyncio.gather(*[
        _retry_short(
            client, "noncomedy", tag, desc, got, CASES_PER_SUBGENRE, sem
        )
        for (tag, desc), got in zip(NONCOMEDY_SUBGENRES, noncomedy_results)
    ])

    # Assemble final JSON
    cases: list[dict] = []
    comedy_chain = [
        ["ComedyStoryAgent"],
        ["ScreenplayAgent"],
        ["KeyFrameAgent"],
        ["VideoAgent"],
        ["CompositorAgent"],
        ["done"],
    ]
    noncomedy_chain = [
        ["StoryAgent"],
        ["ScreenplayAgent"],
        ["KeyFrameAgent"],
        ["VideoAgent"],
        ["CompositorAgent"],
        ["done"],
    ]

    comedy_idx = 1
    for (tag, _), goals in zip(COMEDY_SUBGENRES, comedy_results):
        for g in goals:
            cases.append({
                "name": f"comedy_{comedy_idx:03d}_{tag}",
                "user_goal": g,
                "expected_chain": comedy_chain,
            })
            comedy_idx += 1

    noncomedy_idx = 1
    for (tag, _), goals in zip(NONCOMEDY_SUBGENRES, noncomedy_results):
        for g in goals:
            cases.append({
                "name": f"drama_{noncomedy_idx:03d}_{tag}",
                "user_goal": g,
                "expected_chain": noncomedy_chain,
            })
            noncomedy_idx += 1

    short = [
        (side, tag, n)
        for side, all_pairs, results in [
            ("comedy", COMEDY_SUBGENRES, comedy_results),
            ("noncomedy", NONCOMEDY_SUBGENRES, noncomedy_results),
        ]
        for (tag, _), got in zip(all_pairs, results)
        if (n := len(got)) < CASES_PER_SUBGENRE
    ]
    print(
        f"Total cases assembled: {len(cases)} "
        f"(comedy={comedy_idx-1}, noncomedy={noncomedy_idx-1})"
    )
    if short:
        print(f"Short subgenres (under {CASES_PER_SUBGENRE}): {short}")

    out_path.write_text(
        json.dumps(cases, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    asyncio.run(main())
