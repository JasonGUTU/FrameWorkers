"""Phase 3 sub-batch A: storytelling pure + Music + Ambience (14 cases).

Includes 6 longstory variants (按比例 inherit from original distribution).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

THIS = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS))
from categorize import categorize  # noqa: E402

V4 = THIS / "eval_cases_v4_500.json"

PURE_CHAIN = [
    ["NarrationAgent"],
    ["IllustrationAgent", "NarratorAgent"],
    ["NarratorAgent", "IllustrationAgent"],
    ["CompositorAgent"],
    ["done"],
]

MUSIC_CHAIN = [
    ["NarrationAgent"],
    ["IllustrationAgent", "NarratorAgent", "MusicAgent"],
    ["NarratorAgent", "IllustrationAgent", "MusicAgent"],
    ["MusicAgent", "NarratorAgent", "IllustrationAgent"],
    ["AudioMixAgent"],
    ["CompositorAgent"],
    ["done"],
]

AMBIENCE_CHAIN = [
    ["NarrationAgent"],
    ["IllustrationAgent", "NarratorAgent", "AmbienceAgent"],
    ["NarratorAgent", "IllustrationAgent", "AmbienceAgent"],
    ["AmbienceAgent", "NarratorAgent", "IllustrationAgent"],
    ["AudioMixAgent"],
    ["CompositorAgent"],
    ["done"],
]

BATCHES = [
    {
        "chain": PURE_CHAIN,
        "cases": [
            ("storytelling_031", "Here's my story I want to process: In a quiet alpine village where the houses leaned together as if sharing secrets, there lived a baker named Hettie who kneaded her dough alone every morning before sunrise. Her grandmother had taught her that bread was a kind of conversation between flour and time, and that the best loaves carried within them a memory of someone gone. When the village children began disappearing one by one — first Tomas, then little Greta — Hettie noticed that her oven smelled different each morning, like cinnamon and fresh snow, and she began to wonder what she had been baking into the loaves she sent to the school each day. Make this into a soft illustrated audiobook with calm narration."),
            ("storytelling_032", "Here's my story I want to process: When the lighthouse on Skellig Point was decommissioned in 1962, the keeper Padraig refused to leave. He continued to climb the spiral stairs every evening at dusk and light the lamp by hand, even though the new automated beacon down the coast already swept the sea. His daughter Maeve, now grown and living in Dublin, came back each Christmas to find him a little smaller, the lighthouse a little dimmer, and his stories about the gulls a little stranger. The year he turned ninety, she found a brass key in his coat pocket that did not match any lock in the lighthouse. Tell this as an illustrated audiobook with simple narration."),
            ("storytelling_033", "Make an illustrated audiobook of this children's bedtime tale about a small koala named Otis who learns to climb the tallest eucalyptus in the forest by listening to the wind, calm narration with pencil-drawing illustrations."),
            ("storytelling_034", "Tell me an Aesop-style fable about a vain peacock and a humble sparrow who share a winter together, narrated in a warm older-storyteller voice with watercolor illustrations."),
        ],
    },
    {
        "chain": MUSIC_CHAIN,
        "cases": [
            ("storytelling_035", "Here's my story I want to process: Tomohiro had been a koto player for forty years, but the day his teacher Master Aida died, every string he plucked sounded like a question without an answer. He stopped performing. He stopped teaching. He sat in his small apartment in Kyoto and listened to the rain on the window screen for six months. In the seventh month, a young girl named Hana knocked on his door and said her grandmother had told her, before she died, that Tomohiro was the only one who could still play the song the river sang. Make this into an illustrated audiobook with a soft koto-and-shakuhachi underscore."),
            ("storytelling_036", "Here's my story I want to process: At the back of the antique shop where Esme worked there was a music box she had been forbidden to wind. Her great-aunt Henrietta had been clear about it: \"Some music belongs to the dead, and it is rude to wake them.\" But on the night of her twenty-first birthday, Esme stayed late after closing, alone with the smell of camphor and old wood. The shop felt heavier than usual. She picked up the music box, ran her thumb across its little brass key, and turned it once, just to listen. Make this into an illustrated audiobook with a delicate music-box-and-piano score."),
            ("storytelling_037", "Make a Hawaiian folk-story illustrated audiobook about a young pearl-diver who befriends a sea turtle that guides her to a sunken ancestor's village, with a soft ukulele-and-slack-key-guitar underscore."),
            ("storytelling_038", "Tell me an illustrated audiobook of a Tang-dynasty mountain-hermit poem cycle about an old scholar watching seasons pass on his bamboo balcony, narrated slowly with a guzheng-and-bamboo-flute underscore."),
            ("storytelling_039", "Make an illustrated story about an orphaned boy in 1890s Naples who teaches himself accordion by ear in his uncle's bakery and saves the family business by playing for tourists at dawn, with a soft accordion-led score."),
        ],
    },
    {
        "chain": AMBIENCE_CHAIN,
        "cases": [
            ("storytelling_040", "Here's my story I want to process: Ahmed worked the night shift at a roadside motel along Route 95 in northern Maine, where the only sounds were the wind, the wood paneling creaking with cold, and the occasional truck passing on the highway. He had been there for nine years. Nobody came in after midnight unless they were lost. On the night of December 23rd, the bell over the door rang at 2:47 AM, and a woman walked in carrying nothing but a paper map folded into a tight square. She did not look cold. She did not look tired. She asked him for a room with a north-facing window. Tell this as an illustrated audiobook with constant howling-wind ambience and faint highway sounds."),
            ("storytelling_041", "Here's my story I want to process: The botanical greenhouse on Vandermeer Avenue had stood empty for eleven years when Iris was hired to inventory the surviving plants for the city's preservation board. She arrived on a Tuesday with a notebook, a ladder, and a flashlight. Inside, the air was thick and warm, smelling of rust and damp soil. There were ferns she could not name, palms that bent at impossible angles, and at the far end of the third aisle, a bird-of-paradise plant that bloomed despite no one having watered it for over a decade. She walked toward it slowly. Make this into an illustrated audiobook with constant tropical-greenhouse ambience — ferns dripping, distant glass creaking, faint bird calls."),
            ("storytelling_042", "Tell me an illustrated woodland tale about a young fox cub learning to hunt during her first autumn, with constant forest ambience — leaves rustling, distant birdsong, occasional twig snaps under paw."),
            ("storytelling_043", "Make an illustrated audiobook about a fisherman's daughter on a Norwegian fjord who waits for her father's return through three seasons, with constant coastal ambience — wave breaks, gull cries, ropes creaking against wood."),
            ("storytelling_044", "Tell me an illustrated story about an old desert nomad teaching his grandson to read the stars on a long journey, with constant desert-night ambience — wind across sand, camel breath, distant howls."),
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

    print(f"prepared {len(new_entries)} new storytelling cases (sub-batch A)")

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
