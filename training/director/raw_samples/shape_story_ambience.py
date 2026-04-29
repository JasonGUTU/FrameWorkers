"""Shape: story_ambience —
    Narration → Illustration → Narrator → Ambience → AudioMix → Compositor.

Illustrated audiobook with ambient sound bed (no music). Target 20
(10 long-story + 10 short-brief). Here: 10 short-brief.
"""
from __future__ import annotations

SAMPLES: list[dict] = [
    {
        "user_goal": "Narrate this forest-adventure children's story as an illustrated audiobook with a gentle forest-ambience bed (wind through leaves, distant birds).",
        "rationale": (
            "Forest-adventure children's story + forest ambient bed. Chain: Narration → "
            "Illustration → Narrator → Ambience → AudioMix → Compositor. Reject Music (ambient "
            "only asked)."
        ),
        "intents": [
            "Write the narration script from the forest-adventure children's story.",
            "Generate one watercolor illustration per scene.",
            "Produce a gentle TTS narrator track for the forest story.",
            "Generate a forest ambient bed (wind through leaves, distant birds).",
            "Mix the forest ambient with the narrator track for balanced underlay.",
            "Compose the final slideshow pairing illustrations with the mixed narrator+ambient audio.",
        ],
    },
    {
        "user_goal": "Make an illustrated audiobook of this seaside fairytale about a starfish wishing upon a tide, with gentle coastal ambient (waves, distant gulls).",
        "rationale": (
            "Seaside starfish fairytale + coastal ambient bed."
        ),
        "intents": [
            "Write the narration script from the starfish-wish seaside fairytale.",
            "Generate one seaside watercolor illustration per scene.",
            "Produce a gentle TTS narrator track for the starfish tale.",
            "Generate a coastal ambient bed (waves, distant gulls).",
            "Mix the coastal ambient with the narrator track.",
            "Compose the final slideshow pairing illustrations with mixed audio.",
        ],
    },
    {
        "user_goal": "Narrate this cave-adventure story as an illustrated audiobook with an ambient cave bed (dripping water, distant echoes).",
        "rationale": (
            "Cave-adventure story + cave ambient bed."
        ),
        "intents": [
            "Write the narration script from the cave-adventure story.",
            "Generate one cave-themed illustration per scene.",
            "Produce a curious TTS narrator track for the cave story.",
            "Generate a cave ambient bed (drips, distant echoes).",
            "Mix the cave ambient with the narrator track.",
            "Compose the final slideshow pairing illustrations with mixed audio.",
        ],
    },
    {
        "user_goal": "Make an illustrated audiobook of this mountain-goat fable about climbing above the clouds, with mountain-wind ambient bed.",
        "rationale": (
            "Mountain-goat fable + mountain-wind ambient bed."
        ),
        "intents": [
            "Write the narration script from the mountain-goat fable.",
            "Generate one alpine watercolor illustration per scene.",
            "Produce a determined TTS narrator track for the fable.",
            "Generate a mountain-wind ambient bed (high-altitude wind, distant echoes).",
            "Mix the mountain ambient with the narrator track.",
            "Compose the final slideshow pairing illustrations with mixed audio.",
        ],
    },
    {
        "user_goal": "Narrate this thunderstorm-night bedtime tale as an illustrated audiobook with a gentle thunderstorm ambient bed (distant thunder, rain on roof).",
        "rationale": (
            "Thunderstorm-night bedtime tale + thunderstorm ambient bed."
        ),
        "intents": [
            "Write the narration script from the thunderstorm-night bedtime tale.",
            "Generate one cozy-bedroom illustration per scene.",
            "Produce a calm TTS narrator track for the bedtime tale.",
            "Generate a thunderstorm ambient bed (distant thunder, rain on roof).",
            "Mix the thunderstorm ambient with the narrator track.",
            "Compose the final slideshow pairing illustrations with mixed audio.",
        ],
    },
    {
        "user_goal": "Make an illustrated audiobook of this desert-nomad children's tale, with gentle desert-wind ambient bed.",
        "rationale": (
            "Desert-nomad children's tale + desert-wind ambient bed."
        ),
        "intents": [
            "Write the narration script from the desert-nomad children's tale.",
            "Generate one desert-landscape illustration per scene.",
            "Produce a measured TTS narrator track for the desert tale.",
            "Generate a desert-wind ambient bed (sand wind, distant camel bells).",
            "Mix the desert ambient with the narrator track.",
            "Compose the final slideshow pairing illustrations with mixed audio.",
        ],
    },
    {
        "user_goal": "Narrate this Arctic-ice-exploration picture-book tale as an illustrated audiobook with an Arctic-wind ambient bed.",
        "rationale": (
            "Arctic-ice-exploration tale + Arctic-wind ambient bed."
        ),
        "intents": [
            "Write the narration script from the Arctic-exploration tale.",
            "Generate one Arctic illustration per scene.",
            "Produce a gentle TTS narrator track for the Arctic tale.",
            "Generate an Arctic-wind ambient bed (howling wind, distant ice cracks).",
            "Mix the Arctic ambient with the narrator track.",
            "Compose the final slideshow pairing illustrations with mixed audio.",
        ],
    },
    {
        "user_goal": "Make an illustrated audiobook of this rainforest-explorer tale, with tropical-rainforest ambient bed (insects, distant exotic birds).",
        "rationale": (
            "Rainforest-explorer tale + tropical-rainforest ambient bed."
        ),
        "intents": [
            "Write the narration script from the rainforest-explorer tale.",
            "Generate one rainforest illustration per scene.",
            "Produce a curious TTS narrator track for the rainforest tale.",
            "Generate a tropical-rainforest ambient bed (insects, exotic birds, water drips).",
            "Mix the rainforest ambient with the narrator track.",
            "Compose the final slideshow pairing illustrations with mixed audio.",
        ],
    },
    {
        "user_goal": "Narrate this haunted-moor children's tale as an illustrated audiobook with a moor-wind ambient bed (wind through heather, distant owl).",
        "rationale": (
            "Haunted-moor children's tale + moor-wind ambient bed."
        ),
        "intents": [
            "Write the narration script from the haunted-moor tale.",
            "Generate one moody-moor illustration per scene.",
            "Produce an eerie-yet-child-safe TTS narrator track for the moor tale.",
            "Generate a moor-wind ambient bed (wind through heather, distant owl).",
            "Mix the moor ambient with the narrator track.",
            "Compose the final slideshow pairing illustrations with mixed audio.",
        ],
    },
    {
        "user_goal": "Make an illustrated audiobook of this summer-meadow children's tale about fireflies, with gentle summer-meadow ambient bed.",
        "rationale": (
            "Summer-meadow firefly tale + summer-meadow ambient bed."
        ),
        "intents": [
            "Write the narration script from the summer-meadow firefly tale.",
            "Generate one summer-meadow illustration per scene.",
            "Produce a dreamy TTS narrator track for the firefly tale.",
            "Generate a summer-meadow ambient bed (cicadas, distant crickets, soft wind).",
            "Mix the meadow ambient with the narrator track.",
            "Compose the final slideshow pairing illustrations with mixed audio.",
        ],
    },
]
