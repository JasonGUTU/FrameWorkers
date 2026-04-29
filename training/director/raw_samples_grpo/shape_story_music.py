"""GRPO shape: story_music — Narration → Illustration → Narrator → Music → AudioMix → Compositor.

10 short-brief samples (target_n=20; remaining 10 in shape_story_music_long.py).
"""
from __future__ import annotations


def _make(topic, art_style, descriptor, music_kind):
    return {
        "rationale": (
            f"{topic} + {art_style} illustrations + slideshow narration with "
            f"{music_kind} BGM."
        ),
        "intents": [
            f"Write the narration script from the {descriptor}.",
            f"Generate one {art_style} illustration per {descriptor} scene.",
            f"Produce a measured TTS narrator track for the {descriptor}.",
            f"Compose the {music_kind} BGM the user requested.",
            f"Layer the {music_kind} BGM under the narrator track into one final mixed wav.",
            f"Compose the final slideshow pairing {art_style} illustrations with mixed narrator-and-BGM audio.",
        ],
    }


SAMPLES: list[dict] = [
    {**_make("Bedtime sleeping-baby-elephant tale", "soft watercolor", "sleeping-baby-elephant bedtime tale", "soft-piano lullaby"),
     "user_goal": "Make an illustrated bedtime audiobook about a baby elephant settling down to sleep with her herd, with soft watercolor illustrations and a soft-piano lullaby BGM."},
    {**_make("Tang-dynasty poem recitation", "Chinese-ink-wash", "Tang-dynasty poem recitation", "classical guzheng"),
     "user_goal": "Read this classical Tang-dynasty poem aloud with one Chinese-ink-wash illustration per verse and gentle classical guzheng BGM."},
    {**_make("Ojibwe Wenabozho creation tale", "Ojibwe-bead-pattern", "Wenabozho creation tale", "indigenous flute-and-drum"),
     "user_goal": "Produce an illustrated audiobook of this Ojibwe Wenabozho creation tale with Ojibwe-bead-pattern illustrations and indigenous flute-and-drum BGM."},
    {**_make("Greek Orpheus-and-Eurydice myth", "Greek-vase-painting", "Orpheus-and-Eurydice myth", "lyrical solo-cello"),
     "user_goal": "Make an illustrated audiobook of the Greek myth of Orpheus and Eurydice with Greek-vase-painting illustrations and lyrical solo-cello BGM."},
    {**_make("Beatrix-Potter-style hedgehog tale", "Beatrix-Potter watercolor", "Mrs. Tiggywiggle hedgehog tale", "gentle harp"),
     "user_goal": "Make an illustrated storybook about a Beatrix-Potter-style hedgehog named Mrs. Tiggywiggle sorting forest laundry, with Beatrix-Potter watercolor illustrations and gentle harp BGM."},
    {**_make("Carnival-of-the-Animals storytime", "vibrant cartoon", "Carnival-of-the-Animals storytime", "Saint-Saëns-style orchestral"),
     "user_goal": "Produce a children's narrated picture-book about Saint-Saëns's Carnival of the Animals with vibrant cartoon illustrations of each animal and a Saint-Saëns-style orchestral BGM."},
    {**_make("Japanese Momotaro folktale", "ukiyo-e", "Momotaro peach-boy folktale", "Japanese koto-and-flute"),
     "user_goal": "Read this Japanese Momotaro peach-boy folktale aloud with ukiyo-e illustrations and Japanese koto-and-flute BGM."},
    {**_make("Persian Layla-and-Majnun verse", "Persian-miniature", "Layla-and-Majnun romance", "Persian setar"),
     "user_goal": "Make an illustrated audiobook of the Persian Layla-and-Majnun romance with Persian-miniature illustrations and Persian setar BGM."},
    {**_make("African Anansi-trickster tale", "bright Caribbean-palette", "Anansi trickster tale", "Caribbean steel-pan"),
     "user_goal": "Produce an illustrated audiobook of this African Anansi trickster tale, with bright Caribbean-palette illustrations and Caribbean steel-pan BGM."},
    {**_make("Brothers-Grimm Frog-Prince tale", "retro-storybook", "Frog-Prince fairytale", "music-box waltz"),
     "user_goal": "Make an illustrated audiobook of the Brothers-Grimm Frog-Prince fairytale with retro-storybook illustrations and music-box waltz BGM."},
]
