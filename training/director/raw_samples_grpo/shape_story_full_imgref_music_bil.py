"""GRPO shape: story_full_imgref_music_bil — IntakeImage → BriefEnricher → Narration → Illustration → Narrator → Music → AudioMix → Translation → Compositor.

20 samples. Storytelling with image reference + music + bilingual.
"""
from __future__ import annotations


def _make(topic, art_style, descriptor, ref_subject, music, src_lang, tgt_lang):
    return {
        "rationale": (
            f"{topic} + {art_style} illustrations + slideshow narration with "
            f"{ref_subject} reference image, {music} BGM, and "
            f"{src_lang}-and-{tgt_lang} bilingual subtitles."
        ),
        "intents": [
            f"Register the user's uploaded {ref_subject} reference image as a captioned workspace artifact.",
            f"Enrich the brief by integrating the {ref_subject} reference image's descriptive content.",
            f"Write the narration script from the {descriptor}, anchored to the {ref_subject} reference.",
            f"Generate one {art_style} illustration per {descriptor} scene, depicting the {ref_subject} reference.",
            f"Produce a measured {src_lang} TTS narrator track for the {descriptor}.",
            f"Compose the {music} BGM the user requested.",
            f"Layer the {music} BGM under the narrator track into one final mixed wav.",
            f"Translate the {src_lang} narrator track into {tgt_lang} for the second-language subtitle overlay.",
            f"Compose the final slideshow pairing {art_style} illustrations with mixed narrator-and-BGM audio and bilingual {src_lang}-and-{tgt_lang} subtitles overlaid.",
        ],
    }


SAMPLES: list[dict] = [
    {**_make("Full storytelling — bedtime", "soft watercolor", "child-protagonist bedtime adventure", "child-portrait", "soft-piano lullaby", "Spanish", "English"),
     "user_goal": "Here's a portrait of my daughter — make an illustrated bedtime audiobook about her woodland adventure with soft watercolor illustrations and soft-piano lullaby BGM, narrated in Spanish with English subtitles."},
    {**_make("Full storytelling — heritage memoir", "sepia-toned", "grandmother's-life storytime", "grandmother-portrait", "gentle classical-piano", "Mandarin", "English"),
     "user_goal": "Here's a photo of my grandmother — produce an illustrated audiobook of her stories with sepia-toned illustrations and gentle classical-piano BGM, narrated in Mandarin with English subtitles."},
    {**_make("Full storytelling — pet adventure", "warm watercolor", "family-pet adventure", "dog-portrait", "playful flute-and-strings", "Japanese", "English"),
     "user_goal": "Here's a photo of my shiba inu Yuki — make an illustrated audiobook about Yuki's adventures with warm watercolor illustrations and playful flute-and-strings BGM, narrated in Japanese with English subtitles."},
    {**_make("Full storytelling — pet-cat folktale", "Beatrix-Potter watercolor", "cat-as-protagonist folktale", "cat-portrait", "music-box waltz", "Korean", "English"),
     "user_goal": "Here's a photo of my cat Bori — produce an illustrated audiobook of a folktale starring Bori, with Beatrix-Potter watercolor illustrations and music-box waltz BGM, narrated in Korean with English subtitles."},
    {**_make("Full storytelling — hero quest", "ink-and-color-wash", "young-warrior-hero quest", "young-woman-portrait", "epic orchestral", "Hindi", "English"),
     "user_goal": "Here's a photo of my best friend — make an illustrated audiobook of an epic hero-quest tale with ink-and-color-wash illustrations and epic orchestral BGM, narrated in Hindi with English subtitles."},
    {**_make("Full storytelling — mother-daughter", "warm pastel", "mother-and-daughter shared-memory", "mother-daughter-photo", "tender solo-piano", "French", "English"),
     "user_goal": "Here's a photo of me and my mother — produce an illustrated audiobook of our shared memories with warm pastel illustrations and tender solo-piano BGM, narrated in French with English subtitles."},
    {**_make("Full storytelling — childhood memoir", "soft pastel", "childhood-self memoir", "childhood-photo", "wistful strings", "German", "English"),
     "user_goal": "Here's a photo of me as a child — make an illustrated audiobook of a memory from that time with soft pastel illustrations and wistful strings BGM, narrated in German with English subtitles."},
    {**_make("Full storytelling — best-friend adventure", "vibrant cartoon", "best-friend-adventure tale", "friend-portrait", "upbeat indie folk", "Italian", "English"),
     "user_goal": "Here's a photo of my best friend — produce an illustrated audiobook adventure tale starring her with vibrant cartoon illustrations and upbeat indie-folk BGM, narrated in Italian with English subtitles."},
    {**_make("Full storytelling — pet-horse story", "watercolor", "pet-horse meadow story", "horse-portrait", "open-prairie acoustic-guitar", "Russian", "English"),
     "user_goal": "Here's a photo of my horse Tara — make an illustrated audiobook about Tara running across the meadow with watercolor illustrations and open-prairie acoustic-guitar BGM, narrated in Russian with English subtitles."},
    {**_make("Full storytelling — sibling adventure", "ink-and-color", "siblings adventure tale", "siblings-photo", "playful clarinet-and-strings", "Portuguese", "English"),
     "user_goal": "Here's a photo of me and my brother — produce an illustrated audiobook adventure tale about us with ink-and-color illustrations and playful clarinet-and-strings BGM, narrated in Portuguese with English subtitles."},
    {**_make("Full storytelling — pet-dog journey", "warm watercolor", "pet-dog cross-country journey", "dog-portrait", "Americana folk", "Turkish", "English"),
     "user_goal": "Here's a photo of my dog Mavi — make an illustrated audiobook about Mavi's cross-country journey with warm watercolor illustrations and Americana-folk BGM, narrated in Turkish with English subtitles."},
    {**_make("Full storytelling — wedding narration", "watercolor", "wedding-portrait love-story narration", "wedding-portrait", "romantic strings", "Arabic", "English"),
     "user_goal": "Here's our wedding photo — produce an illustrated audiobook of our love story with watercolor illustrations and romantic-strings BGM, narrated in Arabic with English subtitles."},
    {**_make("Full storytelling — father young-self", "sepia-toned", "father's young-self story", "father-young-portrait", "wistful piano-and-cello", "Polish", "English"),
     "user_goal": "Here's a photo of my dad as a young man — make an illustrated audiobook of his young-self life-story with sepia-toned illustrations and wistful piano-and-cello BGM, narrated in Polish with English subtitles."},
    {**_make("Full storytelling — family cat", "whimsical cartoon", "family-cat picture-book", "cat-portrait", "playful pizzicato", "Greek", "English"),
     "user_goal": "Here's a photo of our family cat Cocoa — produce an illustrated picture-book audiobook starring Cocoa with whimsical cartoon illustrations and playful pizzicato BGM, narrated in Greek with English subtitles."},
    {**_make("Full storytelling — hero's journey", "ink-and-color", "young-hero's-journey", "boy-portrait", "epic adventure orchestral", "Thai", "English"),
     "user_goal": "Here's a photo of my nephew — make an illustrated audiobook of his hero's-journey adventure with ink-and-color illustrations and epic-adventure orchestral BGM, narrated in Thai with English subtitles."},
    {**_make("Full storytelling — twin heroes", "bright cartoon", "twin-heroes adventure", "twin-portrait", "playful adventure orchestral", "Tagalog", "English"),
     "user_goal": "Here are photos of my twin daughters — produce an illustrated audiobook of their twin-heroes adventure with bright cartoon illustrations and playful adventure orchestral BGM, narrated in Tagalog with English subtitles."},
    {**_make("Full storytelling — pet-bird tale", "Audubon-watercolor", "parrot-as-protagonist tale", "parrot-portrait", "tropical guitar-and-percussion", "Indonesian", "English"),
     "user_goal": "Here's a photo of my parrot Pisang — make an illustrated audiobook about Pisang flying around the islands with Audubon-watercolor illustrations and tropical guitar-and-percussion BGM, narrated in Indonesian with English subtitles."},
    {**_make("Full storytelling — mythic hero", "Mughal-miniature", "person-as-mythic-hero tale", "person-portrait", "Indian classical sitar", "Bengali", "English"),
     "user_goal": "Here's a photo of my aunt — produce an illustrated audiobook of a mythic-hero tale starring her with Mughal-miniature illustrations and Indian classical sitar BGM, narrated in Bengali with English subtitles."},
    {**_make("Full storytelling — Andean abuela", "Mexican-retablo", "abuela's-life tale", "grandmother-portrait", "Andean pan-flute", "Spanish", "Quechua"),
     "user_goal": "Here's a photo of my abuela — make an illustrated audiobook of her Andean-village life-story with Mexican-retablo illustrations and Andean pan-flute BGM, narrated in Spanish with Quechua subtitles."},
    {**_make("Full storytelling — childhood friend", "soft pastel", "childhood-friend memoir", "child-portrait", "wistful violin-and-piano", "Hebrew", "English"),
     "user_goal": "Here's a photo of my childhood best friend — produce an illustrated audiobook of our childhood memories with soft pastel illustrations and wistful violin-and-piano BGM, narrated in Hebrew with English subtitles."},
]
