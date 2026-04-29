"""GRPO shape: story_ambience — Narration → Illustration → Narrator → Ambience → AudioMix → Compositor.

10 short-brief samples (target_n=20; remaining 10 in shape_story_ambience_long.py).
"""
from __future__ import annotations


def _make(topic, art_style, descriptor, ambience):
    return {
        "rationale": (
            f"{topic} + {art_style} illustrations + slideshow narration with "
            f"{ambience} ambient bed."
        ),
        "intents": [
            f"Write the narration script from the {descriptor}.",
            f"Generate one {art_style} illustration per {descriptor} scene.",
            f"Produce a measured TTS narrator track for the {descriptor}.",
            f"Generate the {ambience} ambient atmosphere as the audio bed.",
            f"Layer the {ambience} ambient bed under the narrator track into one final mixed wav.",
            f"Compose the final slideshow pairing {art_style} illustrations with mixed narrator-and-ambience audio.",
        ],
    }


SAMPLES: list[dict] = [
    {**_make("Bedtime forest-rabbit tale", "soft watercolor", "forest-rabbit bedtime tale", "soft forest-night"),
     "user_goal": "Make an illustrated audiobook of this bedtime story about a forest rabbit named Pip with soft watercolor illustrations, and lay a soft forest-night ambient sound bed underneath the narrator."},
    {**_make("Children's tide-pool storytime", "watercolor", "tide-pool sea-creature storytime", "gentle ocean-shore"),
     "user_goal": "Produce a children's nature picture-book about the tide-pool sea-creatures along a rocky coast, with watercolor illustrations and a gentle ocean-shore ambient bed under the narration."},
    {**_make("Andean condor-mother storytime", "Inca-textile", "condor-mother feeds-her-chick storytime", "high-Andean-wind"),
     "user_goal": "Make a narrated picture-book about an Andean condor-mother flying to feed her chick, with Inca-textile-pattern illustrations and a high-Andean-wind ambient bed."},
    {**_make("Arctic-fox winter survival storytime", "soft pastel", "Arctic-fox winter survival storytime", "Arctic-wind"),
     "user_goal": "Read this children's picture-book about an Arctic fox surviving its first winter alone, with soft pastel illustrations and an Arctic-wind ambient bed under the narrator."},
    {**_make("Amazon-rainforest jaguar-cub storytime", "tropical watercolor", "Amazon-rainforest jaguar-cub storytime", "tropical-rainforest-bird-and-insect"),
     "user_goal": "Make an illustrated audiobook about an Amazon jaguar cub learning to hunt with her mother, with tropical watercolor illustrations and a tropical-rainforest-bird-and-insect ambient bed."},
    {**_make("Highland-lake selkie tale", "Celtic-knot watercolor", "Highland-lake selkie tale", "Highland-lake-shore"),
     "user_goal": "Make an illustrated audiobook of this Highland-lake selkie tale with Celtic-knot watercolor illustrations and a Highland-lake-shore ambient bed under the narrator."},
    {**_make("Mongolian-steppe horse-foal tale", "Mongolian-folk-art", "Mongolian-steppe horse-foal tale", "open-steppe-wind"),
     "user_goal": "Produce a narrated picture-book about a Mongolian-steppe foal taking its first steps with the herd, with Mongolian-folk-art illustrations and an open-steppe-wind ambient bed."},
    {**_make("Coral-reef clownfish-family storytime", "underwater watercolor", "coral-reef clownfish-family storytime", "underwater-reef"),
     "user_goal": "Make a children's picture-book about a clownfish family on a coral reef with underwater watercolor illustrations and an underwater-reef ambient bed under the narration."},
    {**_make("Tibetan-monastery cat tale", "Tibetan-thangka", "Tibetan-monastery cat tale", "monastery-bell-and-mountain-wind"),
     "user_goal": "Read this Tibetan tale of a small cat who lives at a mountain monastery, with Tibetan-thangka illustrations and a monastery-bell-and-mountain-wind ambient bed."},
    {**_make("Norse-fjord salmon-leap storytime", "Bilibin-style", "Norse-fjord salmon-leap storytime", "fjord-water-and-distant-bird"),
     "user_goal": "Make an illustrated audiobook of this Norse-fjord story of a young salmon leaping upriver to spawn, with Bilibin-style illustrations and a fjord-water-and-distant-bird ambient bed."},
]
