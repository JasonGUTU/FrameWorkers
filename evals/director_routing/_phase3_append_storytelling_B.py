"""Phase 3 sub-batch B: storytelling +bilingual / +imgref pure / +imgref+Music (18 cases)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

THIS = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS))
from categorize import categorize  # noqa: E402

V4 = THIS / "eval_cases_v4_500.json"

BILINGUAL_CHAIN = [
    ["NarrationAgent"],
    ["IllustrationAgent", "NarratorAgent"],
    ["NarratorAgent", "IllustrationAgent"],
    ["TranslationAgent"],
    ["CompositorAgent"],
    ["done"],
]

IMGREF_PURE_CHAIN = [
    ["IntakeImageAgent"],
    ["BriefEnricherAgent"],
    ["NarrationAgent"],
    ["IllustrationAgent", "NarratorAgent"],
    ["NarratorAgent", "IllustrationAgent"],
    ["CompositorAgent"],
    ["done"],
]

IMGREF_MUSIC_CHAIN = [
    ["IntakeImageAgent"],
    ["BriefEnricherAgent"],
    ["NarrationAgent"],
    ["IllustrationAgent", "NarratorAgent", "MusicAgent"],
    ["NarratorAgent", "IllustrationAgent", "MusicAgent"],
    ["MusicAgent", "NarratorAgent", "IllustrationAgent"],
    ["AudioMixAgent"],
    ["CompositorAgent"],
    ["done"],
]

BATCHES = [
    {
        "chain": BILINGUAL_CHAIN,
        "cases": [
            ("storytelling_045", "Tell me an Italian folktale about a baker's apprentice in 17th-century Bologna who discovers his master's bread is being stolen by a hungry ghost from the cellar, narrate in Italian with English subtitles."),
            ("storytelling_046", "Make an illustrated audiobook of a Brothers Grimm-style German fairy tale about a young chimney sweep who befriends a forest witch in the Black Forest, narrate in German with English subtitles."),
            ("storytelling_047", "Tell me a Mexican folktale about a young cornfield farmer in Oaxaca who learns to read the wind from his grandmother and saves his village from drought, narrate in Spanish with English subtitles."),
            ("storytelling_048", "Make an illustrated story about a Russian folk-hero shepherd who outwits Baba Yaga to rescue his sister from her hut on chicken legs, narrate in Russian with English subtitles."),
            ("storytelling_049", "Tell me an illustrated audiobook of a Persian poem-cycle about a master rug-weaver in 12th-century Isfahan who weaves his daughter's lost lover into the patterns of his last carpet, narrate in Persian (Farsi) with English subtitles."),
            ("storytelling_050", "Make an illustrated Korean folktale about a humble water-carrier in old Joseon-era Seoul who befriends a fox-spirit and shares her gift of seeing through illusions, narrate in Korean with English subtitles."),
        ],
    },
    {
        "chain": IMGREF_PURE_CHAIN,
        "cases": [
            ("storytelling_051", "I've uploaded a charcoal sketch of an old Welsh fisherman with a long-stemmed pipe and a weathered face. Use him as the protagonist and tell me an illustrated story about his last morning out on the bay before retirement, where he meets a seal he believes is his late wife."),
            ("storytelling_052", "I've attached a photo of an orange tabby barn cat curled in a hayloft window. Use her as the protagonist and tell me an illustrated bedtime tale about her midnight rounds across the farm, watching over the sleeping animals until dawn."),
            ("storytelling_053", "Here's a watercolor of a snow-covered alpine village at twilight. Use it as the setting and tell me an illustrated winter folktale about a baker's daughter who delivers bread to the village's hidden recluse and finds a different door each visit."),
            ("storytelling_054", "I've uploaded a sketch of a young Tibetan Buddhist monk standing on a high cliff at sunrise. Use him as the protagonist and tell me an illustrated story about his three-year pilgrimage to a remote mountain monastery, including the small kindnesses he receives along the road."),
            ("storytelling_055", "Here's a concept-art painting of an underwater coral kingdom with bioluminescent towers. Use it as the setting and tell me an illustrated story about a young mermaid scholar who discovers a forbidden language carved into the deepest reef walls."),
            ("storytelling_056", "I've attached a portrait of a 1920s Harlem flapper in a beaded dress holding a long cigarette holder. Use her as the protagonist and tell me an illustrated story about her last night at the Cotton Club before she leaves New York for Paris."),
        ],
    },
    {
        "chain": IMGREF_MUSIC_CHAIN,
        "cases": [
            ("storytelling_057", "Using this uploaded portrait of a 17th-century pirate captain with a salt-bleached beard, tell me an illustrated tale about her last voyage searching for her brother's lost ship, with a sea-shanty accordion-and-fiddle underscore."),
            ("storytelling_058", "I've uploaded a sketch of an elder Lakota chief in winter ceremonial regalia. Use him as the storyteller and tell me an illustrated tribal legend about how the buffalo first taught humans to share their food, with a soft frame-drum-and-wood-flute underscore."),
            ("storytelling_059", "Here's a portrait of a young ballerina in pointe shoes warming up at the barre. Use her as the protagonist and tell me an illustrated story about her audition for the Bolshoi after a near-career-ending ankle injury, with a delicate classical-piano-and-strings score."),
            ("storytelling_060", "I've attached a photo of an old Irish fiddler playing on a stone bridge in County Kerry. Use him as the protagonist and tell me an illustrated story about how he learned the tune that calls fish home from his uncle as a child, with a Celtic fiddle-and-tin-whistle underscore."),
            ("storytelling_061", "Here's concept art of a battered Roman gladiator standing in the arena holding his broken sword. Use him as the protagonist and tell me an illustrated tale about his refusal to kill his old slave-trainer in the final match, with a slow brass-and-strings epic underscore."),
            ("storytelling_062", "I've uploaded concept art of a thatched witch's cottage in a misty forest clearing. Use it as the setting and tell me an illustrated dark fairy tale about a young apothecary's apprentice who comes seeking a cure but stays for an apprenticeship, with a soft harp-and-celesta underscore."),
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

    print(f"prepared {len(new_entries)} new storytelling cases (sub-batch B)")

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
