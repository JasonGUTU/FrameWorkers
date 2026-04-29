"""GRPO shape: story_music_ambience — Narration → Illustration → Narrator → Music → Ambience → AudioMix → Compositor.

20 samples. Storytelling with both BGM AND ambient layers.
"""
from __future__ import annotations


def _make(topic, art_style, descriptor, music, ambience):
    return {
        "rationale": (
            f"{topic} + {art_style} illustrations + slideshow narration with "
            f"{music} BGM and {ambience} ambient bed."
        ),
        "intents": [
            f"Write the narration script from the {descriptor}.",
            f"Generate one {art_style} illustration per {descriptor} scene.",
            f"Produce a measured TTS narrator track for the {descriptor}.",
            f"Compose the {music} BGM the user requested.",
            f"Generate the {ambience} ambient atmosphere as the audio bed.",
            f"Layer the {music} BGM and {ambience} ambient bed under the narrator track into one final mixed wav.",
            f"Compose the final slideshow pairing {art_style} illustrations with mixed narrator-BGM-ambience audio.",
        ],
    }


SAMPLES: list[dict] = [
    {**_make("Bedtime forest-tale", "soft watercolor", "forest-rabbit bedtime tale", "soft-piano lullaby", "soft forest-night"),
     "user_goal": "Make an illustrated bedtime audiobook of a forest-rabbit tale with soft watercolor illustrations, soft-piano lullaby BGM, and a soft forest-night ambient bed."},
    {**_make("Tide-pool nature storytime", "watercolor", "tide-pool storytime", "gentle harp", "gentle ocean-shore"),
     "user_goal": "Produce a children's nature picture-book about a tide pool with watercolor illustrations, gentle harp BGM, and a gentle ocean-shore ambient bed."},
    {**_make("Andean condor storytime", "Inca-textile", "Andean condor storytime", "pan-flute folk", "high-Andean-wind"),
     "user_goal": "Make an illustrated audiobook about an Andean condor with Inca-textile illustrations, pan-flute-folk BGM, and a high-Andean-wind ambient bed."},
    {**_make("Arctic-fox winter survival", "soft pastel", "Arctic-fox winter survival", "minimal Nordic-strings", "Arctic-wind"),
     "user_goal": "Read an illustrated audiobook about an Arctic fox surviving winter with soft pastel illustrations, minimal Nordic-strings BGM, and an Arctic-wind ambient bed."},
    {**_make("Amazon jaguar storytime", "tropical watercolor", "Amazon jaguar storytime", "shamanic flute-and-drum", "tropical-rainforest-bird-and-insect"),
     "user_goal": "Produce an illustrated audiobook about an Amazon jaguar cub with tropical watercolor illustrations, shamanic flute-and-drum BGM, and a tropical-rainforest-bird-and-insect ambient bed."},
    {**_make("Highland selkie tale", "Celtic-knot watercolor", "Highland-lake selkie tale", "Celtic-harp-and-flute", "Highland-lake-shore"),
     "user_goal": "Make an illustrated audiobook of a Highland-lake selkie tale with Celtic-knot watercolor illustrations, Celtic-harp-and-flute BGM, and a Highland-lake-shore ambient bed."},
    {**_make("Mongolian-steppe foal tale", "Mongolian-folk-art", "Mongolian-steppe foal tale", "morin-khuur folk", "open-steppe-wind"),
     "user_goal": "Produce an illustrated audiobook about a Mongolian-steppe foal with Mongolian-folk-art illustrations, morin-khuur-folk BGM, and an open-steppe-wind ambient bed."},
    {**_make("Coral-reef clownfish tale", "underwater watercolor", "coral-reef clownfish tale", "ambient marimba-and-flute", "underwater-reef"),
     "user_goal": "Read an illustrated audiobook about a coral-reef clownfish family with underwater watercolor illustrations, ambient marimba-and-flute BGM, and an underwater-reef ambient bed."},
    {**_make("Tibetan-monastery cat tale", "Tibetan-thangka", "Tibetan-monastery cat tale", "Tibetan singing-bowl", "monastery-bell-and-mountain-wind"),
     "user_goal": "Make an illustrated audiobook of a Tibetan-monastery cat tale with Tibetan-thangka illustrations, Tibetan singing-bowl BGM, and a monastery-bell-and-mountain-wind ambient bed."},
    {**_make("Norse-fjord salmon storytime", "Bilibin-style", "Norse-fjord salmon storytime", "Nordic-strings-and-harp", "fjord-water-and-distant-bird"),
     "user_goal": "Produce an illustrated audiobook about a Norse-fjord salmon's leap with Bilibin-style illustrations, Nordic-strings-and-harp BGM, and a fjord-water-and-distant-bird ambient bed."},
    {**_make("Australian-outback emu tale", "Aboriginal-dot-painting", "Australian-outback emu tale", "didgeridoo-and-clapsticks", "outback-night-cricket"),
     "user_goal": "Make an illustrated audiobook about an Australian-outback emu chick with Aboriginal-dot-painting illustrations, didgeridoo-and-clapsticks BGM, and an outback-night-cricket ambient bed."},
    {**_make("Desert-nomad-girl tale", "Arabic-miniature", "desert-nomad-girl tale", "oud-and-frame-drum", "Saharan-wind-and-camel-bell"),
     "user_goal": "Read an illustrated audiobook about a desert-nomad girl with Arabic-miniature illustrations, oud-and-frame-drum BGM, and a Saharan-wind-and-camel-bell ambient bed."},
    {**_make("Bali rice-terrace storytime", "Balinese-batik", "Bali rice-terrace storytime", "gamelan", "rice-terrace-water-and-frog"),
     "user_goal": "Produce an illustrated audiobook about a Bali rice-terrace storytime with Balinese-batik illustrations, gamelan BGM, and a rice-terrace-water-and-frog ambient bed."},
    {**_make("Saharan-camel-caravan tale", "Bedouin-miniature", "Saharan-camel-caravan tale", "ney-and-percussion", "desert-wind-and-distant-camel"),
     "user_goal": "Make an illustrated audiobook of a Saharan-camel-caravan tale with Bedouin-miniature illustrations, ney-and-percussion BGM, and a desert-wind-and-distant-camel ambient bed."},
    {**_make("Bay-of-Bengal fishing tale", "Pattachitra", "Bay-of-Bengal fishing tale", "Bengali sitar-and-tabla", "coastal-shore-and-gull"),
     "user_goal": "Read an illustrated audiobook about a Bay-of-Bengal fishing-girl tale with Pattachitra illustrations, Bengali sitar-and-tabla BGM, and a coastal-shore-and-gull ambient bed."},
    {**_make("Himalayan snow-leopard tale", "Tibetan-thangka", "Himalayan snow-leopard tale", "Tibetan flute-and-bell", "snow-mountain-wind"),
     "user_goal": "Produce an illustrated audiobook of a Himalayan snow-leopard tale with Tibetan-thangka illustrations, Tibetan flute-and-bell BGM, and a snow-mountain-wind ambient bed."},
    {**_make("Pacific-island sea-turtle tale", "Polynesian-tapa-cloth", "Pacific-island sea-turtle tale", "ukulele-and-pan-flute", "ocean-shore-and-distant-bird"),
     "user_goal": "Make an illustrated audiobook of a Pacific-island sea-turtle tale with Polynesian-tapa-cloth illustrations, ukulele-and-pan-flute BGM, and an ocean-shore-and-distant-bird ambient bed."},
    {**_make("Korean-pine snow-tiger tale", "Korean-minhwa", "Korean-pine snow-tiger tale", "Korean gayageum-and-flute", "snow-pine-forest"),
     "user_goal": "Read an illustrated audiobook of a Korean-pine snow-tiger tale with Korean-minhwa illustrations, Korean gayageum-and-flute BGM, and a snow-pine-forest ambient bed."},
    {**_make("Madagascar lemur-cub tale", "Madagascar-folk", "Madagascar lemur-cub tale", "Malagasy valiha", "rainforest-bird-and-insect"),
     "user_goal": "Produce an illustrated audiobook of a Madagascar lemur-cub tale with Madagascar-folk illustrations, Malagasy-valiha BGM, and a rainforest-bird-and-insect ambient bed."},
    {**_make("Highland-loch swan tale", "Celtic-knot watercolor", "Highland-loch swan tale", "Celtic-harp lyrical", "Highland-loch-shore"),
     "user_goal": "Make an illustrated audiobook of a Highland-loch swan tale with Celtic-knot watercolor illustrations, Celtic-harp-lyrical BGM, and a Highland-loch-shore ambient bed."},
]
