"""Shape: story_music —
    Narration → Illustration → Narrator → Music → AudioMix → Compositor.

Illustrated audiobook with BGM. Target 20 (10 long-story + 10 short-brief).
Here: 10 short-brief.
"""
from __future__ import annotations

SAMPLES: list[dict] = [
    {
        "user_goal": "Make an illustrated audiobook of this lullaby-style bedtime story with a gentle, slow piano score playing softly under the narrator.",
        "rationale": (
            "Lullaby bedtime tale + gentle piano BGM. Chain: Narration → Illustration → "
            "Narrator → Music → AudioMix → Compositor. Reject Ambience (music only)."
        ),
        "intents": [
            "Write the narration script from the lullaby bedtime story.",
            "Generate one soft-pastel illustration per scene.",
            "Produce a gentle TTS narrator track for the lullaby tale.",
            "Compose a gentle slow-piano BGM fitting the lullaby tone.",
            "Mix the piano BGM softly under the narrator track.",
            "Compose the final slideshow pairing illustrations with mixed narrator+music audio.",
        ],
    },
    {
        "user_goal": "Make an illustrated audiobook of this Hans Christian Andersen fairytale with a warm harp-and-celesta BGM under the narration.",
        "rationale": (
            "Andersen fairytale + harp-and-celesta BGM."
        ),
        "intents": [
            "Write the narration script from the Andersen fairytale.",
            "Generate one soft-pastel illustration per scene.",
            "Produce a warm TTS narrator track for the fairytale.",
            "Compose a warm harp-and-celesta BGM fitting the Andersen tone.",
            "Mix the harp BGM softly under the narrator track.",
            "Compose the final slideshow pairing illustrations with mixed audio.",
        ],
    },
    {
        "user_goal": "Make an illustrated audiobook of this Chinese children's fable with a gentle guzheng BGM under the narrator.",
        "rationale": (
            "Chinese children's fable + gentle guzheng BGM."
        ),
        "intents": [
            "Write the narration script from the Chinese children's fable.",
            "Generate one ink-and-wash illustration per scene.",
            "Produce a warm TTS narrator track for the fable.",
            "Compose a gentle guzheng BGM fitting the Chinese fable tone.",
            "Mix the guzheng BGM softly under the narrator track.",
            "Compose the final slideshow pairing illustrations with mixed audio.",
        ],
    },
    {
        "user_goal": "Make an illustrated audiobook of this Celtic fairytale about the fairy folk, with a gentle Celtic-harp BGM.",
        "rationale": (
            "Celtic fairytale + Celtic-harp BGM."
        ),
        "intents": [
            "Write the narration script from the Celtic fairytale.",
            "Generate one Celtic-knot-border illustration per scene.",
            "Produce a lilting TTS narrator track for the fairytale.",
            "Compose a gentle Celtic-harp BGM fitting the fairytale tone.",
            "Mix the harp BGM softly under the narrator track.",
            "Compose the final slideshow pairing illustrations with mixed audio.",
        ],
    },
    {
        "user_goal": "Make an illustrated audiobook of this African children's story about a clever tortoise, with a soft kora-and-mbira BGM.",
        "rationale": (
            "African tortoise children's story + soft kora-and-mbira BGM."
        ),
        "intents": [
            "Write the narration script from the African tortoise children's story.",
            "Generate one vibrant African-folk illustration per scene.",
            "Produce a warm TTS narrator track for the tortoise story.",
            "Compose a soft kora-and-mbira BGM fitting the African tone.",
            "Mix the BGM softly under the narrator track.",
            "Compose the final slideshow pairing illustrations with mixed audio.",
        ],
    },
    {
        "user_goal": "Make an illustrated audiobook of this Andean children's story about a condor and a llama, with gentle pan-flute BGM.",
        "rationale": (
            "Andean condor-and-llama story + gentle pan-flute BGM."
        ),
        "intents": [
            "Write the narration script from the Andean condor-and-llama story.",
            "Generate one Andean-style illustration per scene.",
            "Produce a warm TTS narrator track for the Andean story.",
            "Compose a gentle pan-flute BGM fitting the Andean tone.",
            "Mix the pan-flute BGM softly under the narrator track.",
            "Compose the final slideshow pairing illustrations with mixed audio.",
        ],
    },
    {
        "user_goal": "Make an illustrated audiobook of this Scandinavian fairy-tale about a kind giant, with a gentle accordion-and-strings BGM.",
        "rationale": (
            "Scandinavian kind-giant fairytale + gentle accordion-and-strings BGM."
        ),
        "intents": [
            "Write the narration script from the Scandinavian kind-giant fairytale.",
            "Generate one Scandinavian-folk-art illustration per scene.",
            "Produce a warm TTS narrator track for the kind-giant tale.",
            "Compose a gentle accordion-and-strings BGM fitting the Scandinavian tone.",
            "Mix the BGM softly under the narrator track.",
            "Compose the final slideshow pairing illustrations with mixed audio.",
        ],
    },
    {
        "user_goal": "Make an illustrated audiobook of this Japanese children's tale about a bamboo cutter finding a tiny princess, with gentle koto BGM.",
        "rationale": (
            "Japanese bamboo-cutter-and-princess tale + gentle koto BGM."
        ),
        "intents": [
            "Write the narration script from the bamboo-cutter-and-princess tale.",
            "Generate one ink-and-wash illustration per scene.",
            "Produce a gentle TTS narrator track for the tale.",
            "Compose a gentle koto BGM fitting the Japanese tone.",
            "Mix the koto BGM softly under the narrator track.",
            "Compose the final slideshow pairing illustrations with mixed audio.",
        ],
    },
    {
        "user_goal": "Make an illustrated audiobook of this Native-American children's story about how the rainbow was born, with gentle Navajo-flute BGM.",
        "rationale": (
            "Native-American rainbow story + gentle Navajo-flute BGM."
        ),
        "intents": [
            "Write the narration script from the rainbow-origin story.",
            "Generate one Native-American-style illustration per scene.",
            "Produce a warm TTS narrator track for the rainbow story.",
            "Compose a gentle Navajo-flute BGM fitting the Native-American tone.",
            "Mix the flute BGM softly under the narrator track.",
            "Compose the final slideshow pairing illustrations with mixed audio.",
        ],
    },
    {
        "user_goal": "Make an illustrated audiobook of this Spanish children's tale about a firefly who wanted to be a star, with gentle Spanish-guitar BGM.",
        "rationale": (
            "Spanish firefly-and-star tale + gentle Spanish-guitar BGM."
        ),
        "intents": [
            "Write the narration script from the firefly-and-star tale.",
            "Generate one soft watercolor illustration per scene.",
            "Produce a warm TTS narrator track for the firefly tale.",
            "Compose a gentle Spanish-guitar BGM fitting the Spanish tone.",
            "Mix the guitar BGM softly under the narrator track.",
            "Compose the final slideshow pairing illustrations with mixed audio.",
        ],
    },
]
