"""GRPO shape: story_imgref_bilingual — IntakeImage → BriefEnricher → Narration → Illustration → Narrator → Translation → Compositor.

20 samples. Storytelling with image reference + bilingual subtitles.
"""
from __future__ import annotations


def _make(topic, art_style, descriptor, ref_subject, src_lang, tgt_lang):
    return {
        "rationale": (
            f"{topic} + {art_style} illustrations + slideshow narration with "
            f"{ref_subject} reference image + {src_lang}-and-{tgt_lang} bilingual subtitles."
        ),
        "intents": [
            f"Register the user's uploaded {ref_subject} reference image as a captioned workspace artifact.",
            f"Enrich the brief by integrating the {ref_subject} reference image's descriptive content.",
            f"Write the narration script from the {descriptor}, anchored to the {ref_subject} reference.",
            f"Generate one {art_style} illustration per {descriptor} scene, depicting the {ref_subject} reference.",
            f"Produce a measured {src_lang} TTS narrator track for the {descriptor}.",
            f"Translate the {src_lang} narrator track into {tgt_lang} for the second-language subtitle overlay.",
            f"Compose the final slideshow pairing {art_style} illustrations with the narrator audio and bilingual {src_lang}-and-{tgt_lang} subtitles overlaid.",
        ],
    }


SAMPLES: list[dict] = [
    {**_make("Bilingual children's bedtime story", "soft watercolor", "child-protagonist bedtime adventure", "child-portrait", "Spanish", "English"),
     "user_goal": "Here's a portrait of my daughter — make an illustrated bedtime audiobook about her woodland adventure with soft watercolor illustrations, narrated in Spanish with English subtitles."},
    {**_make("Bilingual heritage memoir", "sepia-toned", "grandmother's-life storytime", "grandmother-portrait", "Mandarin", "English"),
     "user_goal": "Here's a photo of my grandmother — produce an illustrated audiobook of the stories she used to tell, with sepia-toned illustrations, narrated in Mandarin with English subtitles."},
    {**_make("Bilingual family-pet adventure", "warm watercolor", "family-pet adventure", "dog-portrait", "Japanese", "English"),
     "user_goal": "Here's a photo of our shiba inu Yuki — make an illustrated audiobook about Yuki's neighborhood adventures, with warm watercolor illustrations, narrated in Japanese with English subtitles."},
    {**_make("Bilingual immigration narration", "sepia-toned", "family-immigration narration", "family-photo", "Vietnamese", "English"),
     "user_goal": "Here's an old family photo from our refugee passage — produce an illustrated audiobook of our immigration story, with sepia-toned illustrations, narrated in Vietnamese with English subtitles."},
    {**_make("Bilingual pet-cat folktale", "Beatrix-Potter watercolor", "cat-as-protagonist folktale", "cat-portrait", "Korean", "English"),
     "user_goal": "Here's a photo of my cat Bori — make an illustrated audiobook of a folktale starring Bori, with Beatrix-Potter watercolor illustrations, narrated in Korean with English subtitles."},
    {**_make("Bilingual hero-tale", "ink-and-color-wash", "young-warrior-hero quest", "young-woman-portrait", "Hindi", "English"),
     "user_goal": "Here's a photo of my best friend — produce an illustrated audiobook of an epic quest tale where she's the warrior hero, with ink-and-color-wash illustrations, narrated in Hindi with English subtitles."},
    {**_make("Bilingual mother-daughter narration", "warm pastel", "mother-and-daughter shared-memory", "mother-daughter-photo", "French", "English"),
     "user_goal": "Here's a photo of me and my mother — make an illustrated audiobook of the memories we share, with warm pastel illustrations, narrated in French with English subtitles."},
    {**_make("Bilingual childhood-self narration", "soft pastel", "childhood-self memoir", "childhood-photo", "German", "English"),
     "user_goal": "Here's a photo of me as a child — produce an illustrated audiobook of a memory from that time, with soft pastel illustrations, narrated in German with English subtitles."},
    {**_make("Bilingual best-friend tale", "vibrant cartoon", "best-friend-adventure tale", "friend-portrait", "Italian", "English"),
     "user_goal": "Here's a photo of my best friend — make an illustrated audiobook adventure tale starring her, with vibrant cartoon illustrations, narrated in Italian with English subtitles."},
    {**_make("Bilingual pet-horse story", "watercolor", "pet-horse meadow story", "horse-portrait", "Russian", "English"),
     "user_goal": "Here's a photo of my horse Tara — produce an illustrated audiobook about Tara running across the meadow, with watercolor illustrations, narrated in Russian with English subtitles."},
    {**_make("Bilingual sibling-adventure tale", "ink-and-color", "siblings adventure tale", "siblings-photo", "Portuguese", "English"),
     "user_goal": "Here's a photo of me and my brother — make an illustrated audiobook adventure tale about us, with ink-and-color illustrations, narrated in Portuguese with English subtitles."},
    {**_make("Bilingual pet-dog journey", "warm watercolor", "pet-dog cross-country journey", "dog-portrait", "Turkish", "English"),
     "user_goal": "Here's a photo of my dog Mavi — produce an illustrated audiobook about Mavi's cross-country journey, with warm watercolor illustrations, narrated in Turkish with English subtitles."},
    {**_make("Bilingual wedding-narration", "watercolor", "wedding-portrait love-story narration", "wedding-portrait", "Arabic", "English"),
     "user_goal": "Here's our wedding photo — make an illustrated audiobook of our love story, with watercolor illustrations, narrated in Arabic with English subtitles."},
    {**_make("Bilingual parent's young-self story", "sepia-toned", "parent's young-self story", "parent-young-portrait", "Polish", "English"),
     "user_goal": "Here's a photo of my dad as a young man — produce an illustrated audiobook of his young-self life-story, with sepia-toned illustrations, narrated in Polish with English subtitles."},
    {**_make("Bilingual family-cat picture-book", "whimsical cartoon", "family-cat picture-book", "cat-portrait", "Greek", "English"),
     "user_goal": "Here's a photo of our family cat Cocoa — make an illustrated picture-book audiobook starring Cocoa, with whimsical cartoon illustrations, narrated in Greek with English subtitles."},
    {**_make("Bilingual hero's-journey tale", "ink-and-color", "young-hero's-journey", "boy-portrait", "Thai", "English"),
     "user_goal": "Here's a photo of my nephew — produce an illustrated audiobook of his hero's journey adventure, with ink-and-color illustrations, narrated in Thai with English subtitles."},
    {**_make("Bilingual twin-heroes adventure", "bright cartoon", "twin-heroes adventure", "twin-portrait", "Tagalog", "English"),
     "user_goal": "Here are photos of my twin daughters — make an illustrated audiobook of their twin-heroes adventure, with bright cartoon illustrations, narrated in Tagalog with English subtitles."},
    {**_make("Bilingual pet-bird tale", "Audubon-watercolor", "parrot-as-protagonist tale", "parrot-portrait", "Indonesian", "English"),
     "user_goal": "Here's a photo of my parrot Pisang — produce an illustrated audiobook about Pisang flying around the islands, with Audubon-watercolor illustrations, narrated in Indonesian with English subtitles."},
    {**_make("Bilingual personal hero", "Mughal-miniature", "person-as-mythic-hero tale", "person-portrait", "Bengali", "English"),
     "user_goal": "Here's a photo of my aunt — make an illustrated audiobook of a mythic-hero tale where she's the protagonist, with Mughal-miniature illustrations, narrated in Bengali with English subtitles."},
    {**_make("Bilingual abuela tale", "Mexican-retablo", "abuela's-life tale", "grandmother-portrait", "Spanish", "Quechua"),
     "user_goal": "Here's a photo of my abuela — produce an illustrated audiobook of her Andean-village life-story, with Mexican-retablo illustrations, narrated in Spanish with Quechua subtitles."},
]
