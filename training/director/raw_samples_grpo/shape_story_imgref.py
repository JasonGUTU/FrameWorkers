"""GRPO shape: story_imgref — IntakeImage → BriefEnricher → Narration → Illustration → Narrator → Compositor.

20 samples. Storytelling with reference character image input.
"""
from __future__ import annotations


def _make(topic, art_style, descriptor, ref_subject):
    return {
        "rationale": (
            f"{topic} + {art_style} illustrations + slideshow narration with "
            f"{ref_subject} reference image input."
        ),
        "intents": [
            f"Register the user's uploaded {ref_subject} reference image as a captioned workspace artifact.",
            f"Enrich the brief by integrating the {ref_subject} reference image's descriptive content.",
            f"Write the narration script from the {descriptor}, anchored to the {ref_subject} reference.",
            f"Generate one {art_style} illustration per {descriptor} scene, depicting the {ref_subject} reference.",
            f"Produce a measured TTS narrator track for the {descriptor}.",
            f"Compose the final slideshow pairing {art_style} illustrations with the narrator audio.",
        ],
    }


SAMPLES: list[dict] = [
    {**_make("Children's bedtime adventure", "soft watercolor", "child-protagonist bedtime adventure", "child-portrait"),
     "user_goal": "Here's a portrait of my daughter — make an illustrated bedtime audiobook about her going on a forest adventure with talking woodland creatures, with soft watercolor illustrations."},
    {**_make("Storybook hero's journey", "whimsical cartoon", "young-hero's-journey", "boy-portrait"),
     "user_goal": "Here's a photo of my nephew — produce an illustrated picture-book audiobook about him as the hero of a whimsical fantasy adventure, with cartoon illustrations."},
    {**_make("Family-pet adventure", "warm watercolor", "family-pet adventure", "dog-portrait"),
     "user_goal": "Here's a photo of our golden retriever Bailey — make an illustrated audiobook about Bailey discovering a magical garden, with warm watercolor illustrations."},
    {**_make("Grandmother's tales", "sepia-toned", "grandmother's-life storytime", "grandmother-portrait"),
     "user_goal": "Here's an old photo of my grandmother as a young woman — make an illustrated audiobook narrating the stories she used to tell about her childhood, with sepia-toned illustrations."},
    {**_make("Pet cat folktale", "Beatrix-Potter watercolor", "cat-as-protagonist folktale", "cat-portrait"),
     "user_goal": "Here's a photo of my cat Mochi — produce an illustrated audiobook of a folktale where Mochi is the hero, with Beatrix-Potter watercolor illustrations."},
    {**_make("Heroic-children storytime", "bright cartoon", "twin-heroes adventure", "twin-portrait"),
     "user_goal": "Here are photos of my twin daughters — make an illustrated audiobook adventure story about them as twin heroes, with bright cartoon illustrations."},
    {**_make("Pet-bird tale", "Audubon-watercolor", "parrot-as-protagonist tale", "parrot-portrait"),
     "user_goal": "Here's a photo of my parrot Indigo — produce an illustrated audiobook tale about Indigo flying around the world, with Audubon-watercolor illustrations."},
    {**_make("Personalized hero-tale", "ink-and-color-wash", "young-warrior-hero quest tale", "young-woman-portrait"),
     "user_goal": "Here's a photo of my best friend — make an illustrated audiobook of an epic quest tale where she's the young-warrior hero, with ink-and-color-wash illustrations."},
    {**_make("Family-history narration", "sepia-toned", "family-history immigration narration", "family-photo"),
     "user_goal": "Here's an old family photo from the 1920s — produce an illustrated audiobook narrating their immigration story, with sepia-toned illustrations."},
    {**_make("Father's-life storytime", "ink-and-charcoal", "father's-life storytime", "father-portrait"),
     "user_goal": "Here's a photo of my father in his youth — make an illustrated audiobook telling the story of his life, with ink-and-charcoal illustrations."},
    {**_make("Mother-daughter narration", "warm pastel", "mother-and-daughter shared-memory narration", "mother-daughter-photo"),
     "user_goal": "Here's a photo of me and my mother — produce an illustrated audiobook narrating the memories we share, with warm pastel illustrations."},
    {**_make("Pet-rabbit tale", "Beatrix-Potter watercolor", "rabbit-as-protagonist tale", "rabbit-portrait"),
     "user_goal": "Here's a photo of my pet rabbit Cocoa — make an illustrated audiobook of a tale where Cocoa explores a meadow, with Beatrix-Potter watercolor illustrations."},
    {**_make("Childhood-self narration", "soft pastel", "childhood-self memoir narration", "childhood-photo"),
     "user_goal": "Here's a photo of me as a child — produce an illustrated audiobook narrating a memory from that time, with soft pastel illustrations."},
    {**_make("Best-friend tale", "vibrant cartoon", "best-friend-adventure tale", "friend-portrait"),
     "user_goal": "Here's a photo of my best friend — make an illustrated audiobook adventure tale starring her, with vibrant cartoon illustrations."},
    {**_make("Pet-horse story", "watercolor", "pet-horse meadow story", "horse-portrait"),
     "user_goal": "Here's a photo of my horse Comet — produce an illustrated audiobook story about Comet running across a wide meadow, with watercolor illustrations."},
    {**_make("Sibling-adventure tale", "ink-and-color", "siblings adventure tale", "siblings-photo"),
     "user_goal": "Here's a photo of me and my brother — make an illustrated audiobook adventure tale about us as kids, with ink-and-color illustrations."},
    {**_make("Pet-dog journey", "warm watercolor", "pet-dog-cross-country journey", "dog-portrait"),
     "user_goal": "Here's a photo of my dog Scout — produce an illustrated audiobook about Scout's cross-country journey, with warm watercolor illustrations."},
    {**_make("Wedding-portrait tale", "watercolor", "wedding-portrait love-story narration", "wedding-portrait"),
     "user_goal": "Here's our wedding photo — make an illustrated audiobook narrating our love story, with watercolor illustrations."},
    {**_make("Parent's young-self story", "sepia-toned", "parent's young-self story", "parent-young-portrait"),
     "user_goal": "Here's a photo of my dad as a young man — produce an illustrated audiobook of his young-self life-story, with sepia-toned illustrations."},
    {**_make("Family-cat picture-book", "whimsical cartoon", "family-cat picture-book", "cat-portrait"),
     "user_goal": "Here's a photo of our family cat Marshmallow — make an illustrated picture-book audiobook starring Marshmallow, with whimsical cartoon illustrations."},
]
