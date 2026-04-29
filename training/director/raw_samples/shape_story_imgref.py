"""Shape: story_imgref —
    IntakeImage → BriefEnricher → Narration → Illustration → Narrator → Compositor.

Storytelling with a reference character image.
"""
from __future__ import annotations

SAMPLES: list[dict] = [
    {
        "user_goal": "Using the uploaded character portrait as the heroine, turn this short folktale into an illustrated audiobook where every picture keeps her appearance consistent with the reference.",
        "rationale": (
            "Short folktale + character-portrait reference + illustrated audiobook. Chain: "
            "IntakeImage → BriefEnricher → Narration → Illustration → Narrator → Compositor."
        ),
        "intents": [
            "Ingest the uploaded heroine portrait as the visual reference.",
            "Enrich the character brief so illustrations keep her appearance consistent.",
            "Write the narration script from the short folktale around the heroine.",
            "Generate one illustration per scene preserving the heroine's reference likeness.",
            "Produce a warm TTS narrator track for the folktale.",
            "Compose the final slideshow pairing reference-consistent illustrations with narrator audio.",
        ],
    },
    {
        "user_goal": "Using this uploaded cat portrait, make an illustrated bedtime story about the cat's adventures in a magical forest.",
        "rationale": (
            "Cat-portrait reference + magical-forest bedtime story."
        ),
        "intents": [
            "Ingest the uploaded cat portrait as the visual reference.",
            "Enrich the cat brief so illustrations keep its appearance consistent.",
            "Write the narration script about the cat's magical-forest adventure.",
            "Generate one illustration per scene preserving the cat's reference likeness.",
            "Produce a gentle TTS narrator track for the cat bedtime story.",
            "Compose the final slideshow pairing reference-consistent illustrations with narrator audio.",
        ],
    },
    {
        "user_goal": "Using this uploaded dog portrait, make an illustrated audiobook about the dog's first winter adventure.",
        "rationale": (
            "Dog-portrait reference + first-winter adventure."
        ),
        "intents": [
            "Ingest the uploaded dog portrait as the visual reference.",
            "Enrich the dog brief for consistent illustration.",
            "Write the narration script about the dog's first-winter adventure.",
            "Generate one illustration per scene preserving the dog's reference likeness.",
            "Produce a cheerful TTS narrator track for the dog adventure.",
            "Compose the final slideshow pairing consistent illustrations with narrator audio.",
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of a little girl, make an illustrated audiobook about her voyage to the moon.",
        "rationale": (
            "Little-girl portrait reference + moon-voyage story."
        ),
        "intents": [
            "Ingest the uploaded little-girl portrait as the visual reference.",
            "Enrich the little-girl brief for consistent illustration.",
            "Write the narration script about the girl's moon voyage.",
            "Generate one illustration per scene preserving the girl's reference likeness.",
            "Produce a dreamy TTS narrator track for the moon voyage.",
            "Compose the final slideshow pairing consistent illustrations with narrator audio.",
        ],
    },
    {
        "user_goal": "Using this uploaded owl portrait, make an illustrated audiobook about the owl who became the forest's night librarian.",
        "rationale": (
            "Owl-portrait reference + forest-librarian story."
        ),
        "intents": [
            "Ingest the uploaded owl portrait as the visual reference.",
            "Enrich the owl brief for consistent illustration.",
            "Write the narration script about the forest-librarian owl.",
            "Generate one illustration per scene preserving the owl's reference likeness.",
            "Produce a wise TTS narrator track for the owl story.",
            "Compose the final slideshow pairing consistent illustrations with narrator audio.",
        ],
    },
    {
        "user_goal": "Using this uploaded bunny portrait, make an illustrated audiobook about the bunny who painted flowers across the meadow.",
        "rationale": (
            "Bunny-portrait reference + flower-painting meadow story."
        ),
        "intents": [
            "Ingest the uploaded bunny portrait as the visual reference.",
            "Enrich the bunny brief for consistent illustration.",
            "Write the narration script about the flower-painting bunny.",
            "Generate one illustration per scene preserving the bunny's reference likeness.",
            "Produce a gentle TTS narrator track for the bunny story.",
            "Compose the final slideshow pairing consistent illustrations with narrator audio.",
        ],
    },
    {
        "user_goal": "Using this uploaded fox portrait, make an illustrated audiobook about the fox who learned to share with the other woodland creatures.",
        "rationale": (
            "Fox-portrait reference + woodland-sharing story."
        ),
        "intents": [
            "Ingest the uploaded fox portrait as the visual reference.",
            "Enrich the fox brief for consistent illustration.",
            "Write the narration script about the sharing fox.",
            "Generate one illustration per scene preserving the fox's reference likeness.",
            "Produce a warm TTS narrator track for the fox story.",
            "Compose the final slideshow pairing consistent illustrations with narrator audio.",
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of a wizard, make an illustrated audiobook about his quest to find the lost starlight.",
        "rationale": (
            "Wizard-portrait reference + lost-starlight quest."
        ),
        "intents": [
            "Ingest the uploaded wizard portrait as the visual reference.",
            "Enrich the wizard brief for consistent illustration.",
            "Write the narration script about the wizard's starlight quest.",
            "Generate one illustration per scene preserving the wizard's reference likeness.",
            "Produce a mystical TTS narrator track for the wizard quest.",
            "Compose the final slideshow pairing consistent illustrations with narrator audio.",
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of a tiny mouse, make an illustrated audiobook about the mouse who built a house out of teacups.",
        "rationale": (
            "Tiny-mouse portrait + teacup-house story."
        ),
        "intents": [
            "Ingest the uploaded mouse portrait as the visual reference.",
            "Enrich the mouse brief for consistent illustration.",
            "Write the narration script about the teacup-house mouse.",
            "Generate one illustration per scene preserving the mouse's reference likeness.",
            "Produce a playful TTS narrator track for the mouse story.",
            "Compose the final slideshow pairing consistent illustrations with narrator audio.",
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of a boy, make an illustrated audiobook about his first balloon-ride across the valley.",
        "rationale": (
            "Boy-portrait reference + first balloon-ride story."
        ),
        "intents": [
            "Ingest the uploaded boy portrait as the visual reference.",
            "Enrich the boy brief for consistent illustration.",
            "Write the narration script about the boy's balloon ride.",
            "Generate one illustration per scene preserving the boy's reference likeness.",
            "Produce a cheerful TTS narrator track for the balloon-ride story.",
            "Compose the final slideshow pairing consistent illustrations with narrator audio.",
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of a hedgehog, make an illustrated audiobook about the hedgehog who collected fallen stars.",
        "rationale": (
            "Hedgehog-portrait reference + fallen-stars-collector story."
        ),
        "intents": [
            "Ingest the uploaded hedgehog portrait as the visual reference.",
            "Enrich the hedgehog brief for consistent illustration.",
            "Write the narration script about the star-collecting hedgehog.",
            "Generate one illustration per scene preserving the hedgehog's reference likeness.",
            "Produce a gentle TTS narrator track for the hedgehog story.",
            "Compose the final slideshow pairing consistent illustrations with narrator audio.",
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of a panda, make an illustrated audiobook about the panda who learned to play the flute.",
        "rationale": (
            "Panda-portrait reference + flute-learning panda story."
        ),
        "intents": [
            "Ingest the uploaded panda portrait as the visual reference.",
            "Enrich the panda brief for consistent illustration.",
            "Write the narration script about the flute-playing panda.",
            "Generate one illustration per scene preserving the panda's reference likeness.",
            "Produce a warm TTS narrator track for the panda story.",
            "Compose the final slideshow pairing consistent illustrations with narrator audio.",
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of a sailor-lady, make an illustrated audiobook about her voyage to the Isle of Stars.",
        "rationale": (
            "Sailor-lady portrait + Isle-of-Stars voyage."
        ),
        "intents": [
            "Ingest the uploaded sailor-lady portrait as the visual reference.",
            "Enrich the sailor-lady brief for consistent illustration.",
            "Write the narration script about the Isle-of-Stars voyage.",
            "Generate one illustration per scene preserving the sailor-lady's reference likeness.",
            "Produce an adventurous TTS narrator track for the voyage.",
            "Compose the final slideshow pairing consistent illustrations with narrator audio.",
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of a grandmother, make an illustrated audiobook about the grandmother who taught stars to dance.",
        "rationale": (
            "Grandmother-portrait reference + stars-dance story."
        ),
        "intents": [
            "Ingest the uploaded grandmother portrait as the visual reference.",
            "Enrich the grandmother brief for consistent illustration.",
            "Write the narration script about the grandmother teaching stars to dance.",
            "Generate one illustration per scene preserving the grandmother's reference likeness.",
            "Produce a tender TTS narrator track for the grandmother story.",
            "Compose the final slideshow pairing consistent illustrations with narrator audio.",
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of an elephant, make an illustrated audiobook about the elephant who learned to paint sunsets.",
        "rationale": (
            "Elephant-portrait reference + sunset-painting elephant story."
        ),
        "intents": [
            "Ingest the uploaded elephant portrait as the visual reference.",
            "Enrich the elephant brief for consistent illustration.",
            "Write the narration script about the sunset-painting elephant.",
            "Generate one illustration per scene preserving the elephant's reference likeness.",
            "Produce a thoughtful TTS narrator track for the elephant story.",
            "Compose the final slideshow pairing consistent illustrations with narrator audio.",
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of a swan, make an illustrated audiobook about the swan who befriended the frozen lake.",
        "rationale": (
            "Swan-portrait reference + frozen-lake-friend story."
        ),
        "intents": [
            "Ingest the uploaded swan portrait as the visual reference.",
            "Enrich the swan brief for consistent illustration.",
            "Write the narration script about the swan and the frozen lake.",
            "Generate one illustration per scene preserving the swan's reference likeness.",
            "Produce a gentle TTS narrator track for the swan story.",
            "Compose the final slideshow pairing consistent illustrations with narrator audio.",
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of a young gardener, make an illustrated audiobook about the gardener who grew a tree of memories.",
        "rationale": (
            "Young-gardener portrait + tree-of-memories story."
        ),
        "intents": [
            "Ingest the uploaded young-gardener portrait as the visual reference.",
            "Enrich the gardener brief for consistent illustration.",
            "Write the narration script about the tree-of-memories gardener.",
            "Generate one illustration per scene preserving the gardener's reference likeness.",
            "Produce a tender TTS narrator track for the gardener story.",
            "Compose the final slideshow pairing consistent illustrations with narrator audio.",
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of a dolphin, make an illustrated audiobook about the dolphin who sang the ocean to sleep.",
        "rationale": (
            "Dolphin-portrait reference + ocean-sleep story."
        ),
        "intents": [
            "Ingest the uploaded dolphin portrait as the visual reference.",
            "Enrich the dolphin brief for consistent illustration.",
            "Write the narration script about the ocean-singing dolphin.",
            "Generate one illustration per scene preserving the dolphin's reference likeness.",
            "Produce a dreamy TTS narrator track for the dolphin story.",
            "Compose the final slideshow pairing consistent illustrations with narrator audio.",
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of a dragon, make an illustrated audiobook about the young dragon who couldn't breathe fire.",
        "rationale": (
            "Dragon-portrait reference + young-dragon-who-can't-breathe-fire story."
        ),
        "intents": [
            "Ingest the uploaded dragon portrait as the visual reference.",
            "Enrich the dragon brief for consistent illustration.",
            "Write the narration script about the young fireless dragon.",
            "Generate one illustration per scene preserving the dragon's reference likeness.",
            "Produce a hopeful TTS narrator track for the dragon story.",
            "Compose the final slideshow pairing consistent illustrations with narrator audio.",
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of a polar bear, make an illustrated audiobook about the polar bear who found summer in her dreams.",
        "rationale": (
            "Polar-bear portrait + summer-dreams story."
        ),
        "intents": [
            "Ingest the uploaded polar-bear portrait as the visual reference.",
            "Enrich the polar-bear brief for consistent illustration.",
            "Write the narration script about the summer-dreaming polar bear.",
            "Generate one illustration per scene preserving the polar-bear's reference likeness.",
            "Produce a contemplative TTS narrator track for the polar-bear story.",
            "Compose the final slideshow pairing consistent illustrations with narrator audio.",
        ],
    },
]
