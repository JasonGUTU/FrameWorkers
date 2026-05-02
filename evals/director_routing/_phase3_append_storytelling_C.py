"""Phase 3 sub-batch C: storytelling +imgref+bilingual / +Music+Translation / +imgref+Music+Translation (full) (18 cases)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

THIS = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS))
from categorize import categorize  # noqa: E402

V4 = THIS / "eval_cases_v4_500.json"

IMGREF_BILINGUAL_CHAIN = [
    ["IntakeImageAgent"],
    ["BriefEnricherAgent"],
    ["NarrationAgent"],
    ["IllustrationAgent", "NarratorAgent"],
    ["NarratorAgent", "IllustrationAgent"],
    ["TranslationAgent"],
    ["CompositorAgent"],
    ["done"],
]

MUSIC_TRANSLATION_CHAIN = [
    ["NarrationAgent"],
    ["IllustrationAgent", "NarratorAgent", "MusicAgent"],
    ["NarratorAgent", "IllustrationAgent", "MusicAgent"],
    ["MusicAgent", "NarratorAgent", "IllustrationAgent"],
    ["AudioMixAgent"],
    ["TranslationAgent"],
    ["CompositorAgent"],
    ["done"],
]

IMGREF_FULL_CHAIN = [
    ["IntakeImageAgent"],
    ["BriefEnricherAgent"],
    ["NarrationAgent"],
    ["IllustrationAgent", "NarratorAgent", "MusicAgent"],
    ["NarratorAgent", "IllustrationAgent", "MusicAgent"],
    ["MusicAgent", "NarratorAgent", "IllustrationAgent"],
    ["AudioMixAgent"],
    ["TranslationAgent"],
    ["CompositorAgent"],
    ["done"],
]

BATCHES = [
    {
        "chain": IMGREF_BILINGUAL_CHAIN,
        "cases": [
            ("storytelling_063", "I've uploaded a portrait of an Andalusian flamenco dancer in a red ruffled dress. Use her as the protagonist and tell me a Spanish folktale about her grandmother teaching her the rhythm that calls her late grandfather's spirit during the Día de los Muertos festival, narrate in Spanish with English subtitles."),
            ("storytelling_064", "Here's a watercolor of a Sicilian fisherman mending his nets at dawn. Use him as the protagonist and tell me an Italian folktale about how he once outwitted a sea-witch by reciting his late wife's recipes, narrate in Italian with English subtitles."),
            ("storytelling_065", "I've uploaded a sketch of a Greek shepherd boy with his goats on a dry hillside near Delphi. Use him as the protagonist and tell me a Greek myth about how he heard the oracle's whispered fate carried on the wind, narrate in Greek with English subtitles."),
            ("storytelling_066", "Here's a portrait of a young Vietnamese rice-farmer woman with a conical hat in a paddy field. Use her as the protagonist and tell me a Vietnamese folktale about how she befriends a water-buffalo who speaks only in proverbs, narrate in Vietnamese with English subtitles."),
            ("storytelling_067", "I've attached a sketch of a Māori elder with a moko facial tattoo holding a carved jade pendant. Use him as the storyteller and tell me a Māori legend about how the demigod Maui first slowed the sun, narrate in Māori with English subtitles."),
            ("storytelling_068", "Here's a portrait of a young Brazilian capoeira dancer in a roda circle at sunset. Use him as the protagonist and tell me a Brazilian folktale about how his grandfather smuggled the rhythms of capoeira through generations of plantation work, narrate in Portuguese with English subtitles."),
        ],
    },
    {
        "chain": MUSIC_TRANSLATION_CHAIN,
        "cases": [
            ("storytelling_069", "Tell me a French folktale about a Marseille fishmonger's daughter who falls in love with the lonely lighthouse keeper across the harbor, narrate in French with English subtitles, with a soft accordion-and-piano underscore."),
            ("storytelling_070", "Make an illustrated Japanese fable about a Heian-era courtier who falls in love with a fox-spirit disguised as a noblewoman, narrate in Japanese with English subtitles, with a soft koto-and-bamboo-flute underscore."),
            ("storytelling_071", "Tell me a Greek myth about how the muse Clio chose her first mortal student, an old historian losing his memory, narrate in Greek with English subtitles, with a gentle lyre-and-aulos underscore."),
            ("storytelling_072", "Make an illustrated Indian folk tale about a young weaver's daughter in old Varanasi who weaves prayers for her dying father into a sari that the river goddess accepts, narrate in Hindi with English subtitles, with a sitar-and-tabla underscore."),
            ("storytelling_073", "Tell me an Egyptian tale about a Cairo coffeehouse storyteller in the 1920s who recounts his lost love through Scheherazade-style nightly fragments, narrate in Arabic with English subtitles, with an oud-and-qanun underscore."),
            ("storytelling_074", "Make an illustrated Norwegian folktale about a young rune-carver who helps a forest troll find his missing memories one season at a time, narrate in Norwegian with English subtitles, with a nyckelharpa-and-frame-drum underscore."),
        ],
    },
    {
        "chain": IMGREF_FULL_CHAIN,
        "cases": [
            ("storytelling_075", "I've uploaded a portrait of a Persian poet with a turban and a long beard sitting under a cypress tree. Use him as the protagonist and tell me a Persian poem-cycle about his unrequited love for a singing-girl in a Shiraz garden, narrate in Persian with English subtitles, with a santur-and-tar underscore."),
            ("storytelling_076", "Here's a portrait of an old Cuban tobacco-roller working in a Havana factory. Use him as the protagonist and tell me a Cuban folktale about how he used to roll his late wife's love letters into the cigar he saves for his last day of work, narrate in Spanish with English subtitles, with a soft tres-and-conga underscore."),
            ("storytelling_077", "I've attached a sketch of a Mongolian herder on horseback with his eagle on his glove on the steppe. Use him as the protagonist and tell me a Mongolian folktale about how he tracked his stolen herd across three winters using only the songs his father had taught him, narrate in Mongolian with English subtitles, with a soft khoomei throat-singing-and-morin-khuur underscore."),
            ("storytelling_078", "Here's a portrait of a Scottish Highland piper standing on a misty crag in his clan tartan. Use him as the protagonist and tell me a Highland legend about how his great-grandfather's pipe-tune saved a regiment from a winter ambush in 1746, narrate in Scottish Gaelic with English subtitles, with a bagpipe-and-fiddle underscore."),
            ("storytelling_079", "I've uploaded a portrait of a Bengali boatman steering through the Sundarbans mangroves. Use him as the protagonist and tell me a Bengali folktale about how he once ferried a tiger-spirit safely across the river in exchange for the secret of weaving silver into the sun, narrate in Bengali with English subtitles, with a sarod-and-tabla underscore."),
            ("storytelling_080", "Here's a portrait of an Argentine tango couple mid-step on a 1930s Buenos Aires dance floor. Use them as the protagonists and tell me an Argentine tale about their last performance together before he leaves to fight in a foreign war, narrate in Spanish with English subtitles, with a bandoneón-and-violin tango underscore."),
        ],
    },
]


def main() -> None:
    existing = json.loads(V4.read_text(encoding="utf-8"))
    existing_names = {c["name"] for c in existing}

    new_entries: list[dict] = []
    for batch in BATCHES:
        chain = batch["chain"]
        bucket = categorize(chain)
        if bucket != "storytelling":
            raise SystemExit(f"chain not storytelling: {chain}")
        for name, goal in batch["cases"]:
            if name in existing_names:
                raise SystemExit(f"duplicate: {name}")
            new_entries.append({
                "name": name,
                "category": "storytelling",
                "user_goal": goal,
                "expected_chain": chain,
            })

    print(f"prepared {len(new_entries)} new storytelling cases (sub-batch C)")

    merged = existing + new_entries
    V4.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"appended -> {V4}")
    print(f"total cases now: {len(merged)}")

    from collections import Counter
    from categorize import BUCKET_ORDER
    buckets = Counter(c["category"] for c in merged)
    for b in BUCKET_ORDER:
        print(f"  {b:<14} {buckets.get(b, 0)}")


if __name__ == "__main__":
    main()
