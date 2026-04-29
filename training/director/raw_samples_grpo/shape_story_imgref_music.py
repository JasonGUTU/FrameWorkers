"""GRPO shape: story_imgref_music — IntakeImage → BriefEnricher → Narration → Illustration → Narrator → Music → AudioMix → Compositor.

20 samples. Storytelling with image reference + BGM.
"""
from __future__ import annotations


def _make(topic, art_style, descriptor, ref_subject, music):
    return {
        "rationale": (
            f"{topic} + {art_style} illustrations + slideshow narration with "
            f"{ref_subject} reference image and {music} BGM."
        ),
        "intents": [
            f"Register the user's uploaded {ref_subject} reference image as a captioned workspace artifact.",
            f"Enrich the brief by integrating the {ref_subject} reference image's descriptive content.",
            f"Write the narration script from the {descriptor}, anchored to the {ref_subject} reference.",
            f"Generate one {art_style} illustration per {descriptor} scene, depicting the {ref_subject} reference.",
            f"Produce a measured TTS narrator track for the {descriptor}.",
            f"Compose the {music} BGM the user requested.",
            f"Layer the {music} BGM under the narrator track into one final mixed wav.",
            f"Compose the final slideshow pairing {art_style} illustrations with mixed narrator-and-BGM audio.",
        ],
    }


SAMPLES: list[dict] = [
    {**_make("Bedtime adventure with music", "soft watercolor", "child-protagonist bedtime adventure", "child-portrait", "soft-piano lullaby"),
     "user_goal": "Here's a portrait of my daughter — make an illustrated bedtime audiobook about her forest adventure with soft watercolor illustrations and soft-piano lullaby BGM."},
    {**_make("Heritage memoir with music", "sepia-toned", "grandmother's-life storytime", "grandmother-portrait", "gentle classical-piano"),
     "user_goal": "Here's a photo of my grandmother — produce an illustrated audiobook of her stories with sepia-toned illustrations and gentle classical-piano BGM."},
    {**_make("Family-pet adventure with music", "warm watercolor", "family-pet adventure", "dog-portrait", "playful flute-and-strings"),
     "user_goal": "Here's a photo of my labrador Bella — make an illustrated audiobook about Bella's neighborhood adventures with warm watercolor illustrations and playful flute-and-strings BGM."},
    {**_make("Pet-cat folktale with music", "Beatrix-Potter watercolor", "cat-as-protagonist folktale", "cat-portrait", "music-box waltz"),
     "user_goal": "Here's a photo of my cat Pumpkin — produce an illustrated audiobook of a folktale starring Pumpkin, with Beatrix-Potter watercolor illustrations and music-box waltz BGM."},
    {**_make("Hero-tale with music", "ink-and-color-wash", "young-warrior-hero quest", "young-woman-portrait", "epic orchestral"),
     "user_goal": "Here's a photo of my best friend — make an illustrated audiobook of an epic quest tale where she's the warrior hero, with ink-and-color-wash illustrations and epic orchestral BGM."},
    {**_make("Mother-daughter memory with music", "warm pastel", "mother-and-daughter shared-memory", "mother-daughter-photo", "tender solo-piano"),
     "user_goal": "Here's a photo of me and my mother — produce an illustrated audiobook of our shared memories with warm pastel illustrations and tender solo-piano BGM."},
    {**_make("Childhood-self memoir with music", "soft pastel", "childhood-self memoir", "childhood-photo", "wistful strings"),
     "user_goal": "Here's a photo of me as a child — make an illustrated audiobook of a memory from that time, with soft pastel illustrations and wistful strings BGM."},
    {**_make("Best-friend tale with music", "vibrant cartoon", "best-friend-adventure tale", "friend-portrait", "upbeat indie folk"),
     "user_goal": "Here's a photo of my best friend — produce an illustrated audiobook adventure tale starring her, with vibrant cartoon illustrations and upbeat indie-folk BGM."},
    {**_make("Pet-horse story with music", "watercolor", "pet-horse meadow story", "horse-portrait", "open-prairie acoustic-guitar"),
     "user_goal": "Here's a photo of my horse Comet — make an illustrated audiobook about Comet running across the meadow, with watercolor illustrations and open-prairie acoustic-guitar BGM."},
    {**_make("Sibling-adventure tale with music", "ink-and-color", "siblings adventure tale", "siblings-photo", "playful clarinet-and-strings"),
     "user_goal": "Here's a photo of me and my brother — produce an illustrated audiobook adventure tale about us as kids, with ink-and-color illustrations and playful clarinet-and-strings BGM."},
    {**_make("Pet-dog journey with music", "warm watercolor", "pet-dog cross-country journey", "dog-portrait", "Americana folk"),
     "user_goal": "Here's a photo of my dog Scout — make an illustrated audiobook about Scout's cross-country journey, with warm watercolor illustrations and Americana-folk BGM."},
    {**_make("Wedding-narration with music", "watercolor", "wedding-portrait love-story narration", "wedding-portrait", "romantic strings"),
     "user_goal": "Here's our wedding photo — produce an illustrated audiobook of our love story with watercolor illustrations and romantic-strings BGM."},
    {**_make("Father young-self story with music", "sepia-toned", "father's young-self story", "father-young-portrait", "wistful piano-and-cello"),
     "user_goal": "Here's a photo of my dad as a young man — make an illustrated audiobook of his young-self life-story, with sepia-toned illustrations and wistful piano-and-cello BGM."},
    {**_make("Family-cat picture-book with music", "whimsical cartoon", "family-cat picture-book", "cat-portrait", "playful pizzicato"),
     "user_goal": "Here's a photo of our family cat Mochi — produce an illustrated picture-book audiobook starring Mochi, with whimsical cartoon illustrations and playful pizzicato BGM."},
    {**_make("Hero's-journey with music", "ink-and-color", "young-hero's-journey", "boy-portrait", "epic adventure orchestral"),
     "user_goal": "Here's a photo of my nephew — make an illustrated audiobook of his hero's-journey adventure, with ink-and-color illustrations and epic-adventure orchestral BGM."},
    {**_make("Twin-heroes adventure with music", "bright cartoon", "twin-heroes adventure", "twin-portrait", "playful adventure orchestral"),
     "user_goal": "Here are photos of my twin daughters — produce an illustrated audiobook of their twin-heroes adventure, with bright cartoon illustrations and playful adventure orchestral BGM."},
    {**_make("Pet-bird tale with music", "Audubon-watercolor", "parrot-as-protagonist tale", "parrot-portrait", "tropical guitar-and-percussion"),
     "user_goal": "Here's a photo of my parrot Indigo — make an illustrated audiobook about Indigo flying around the world, with Audubon-watercolor illustrations and tropical guitar-and-percussion BGM."},
    {**_make("Personal mythic-hero with music", "Mughal-miniature", "person-as-mythic-hero tale", "person-portrait", "Indian classical sitar"),
     "user_goal": "Here's a photo of my aunt — produce an illustrated audiobook of a mythic-hero tale where she's the protagonist, with Mughal-miniature illustrations and Indian classical sitar BGM."},
    {**_make("Pet-rabbit tale with music", "Beatrix-Potter watercolor", "rabbit-as-protagonist tale", "rabbit-portrait", "delicate harp-and-flute"),
     "user_goal": "Here's a photo of my pet rabbit Honey — make an illustrated audiobook of a tale where Honey explores a meadow, with Beatrix-Potter watercolor illustrations and delicate harp-and-flute BGM."},
    {**_make("Family-history tale with music", "sepia-toned", "family-history immigration narration", "family-photo", "wistful violin-and-piano"),
     "user_goal": "Here's an old family photo — produce an illustrated audiobook of our family-history immigration story, with sepia-toned illustrations and wistful violin-and-piano BGM."},
]
