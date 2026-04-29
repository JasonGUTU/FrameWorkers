"""GRPO shape: story_ultra — IntakeImage → BriefEnricher → Narration → Illustration → Narrator → Music → Ambience → AudioMix → Translation → Compositor.

20 samples. Storytelling with all modifiers (image-ref + music + ambience + bilingual).
"""
from __future__ import annotations


def _make(topic, art_style, descriptor, ref_subject, music, ambience, src_lang, tgt_lang):
    return {
        "rationale": (
            f"{topic} + {art_style} illustrations + slideshow narration with "
            f"{ref_subject} reference image, {music} BGM, {ambience} ambient bed, "
            f"and {src_lang}-and-{tgt_lang} bilingual subtitles."
        ),
        "intents": [
            f"Register the user's uploaded {ref_subject} reference image as a captioned workspace artifact.",
            f"Enrich the brief by integrating the {ref_subject} reference image's descriptive content.",
            f"Write the narration script from the {descriptor}, anchored to the {ref_subject} reference.",
            f"Generate one {art_style} illustration per {descriptor} scene, depicting the {ref_subject} reference.",
            f"Produce a measured {src_lang} TTS narrator track for the {descriptor}.",
            f"Compose the {music} BGM the user requested.",
            f"Generate the {ambience} ambient atmosphere as the audio bed.",
            f"Layer the {music} BGM and {ambience} ambient bed under the narrator track into one final mixed wav.",
            f"Translate the {src_lang} narrator track into {tgt_lang} for the second-language subtitle overlay.",
            f"Compose the final slideshow pairing {art_style} illustrations with mixed narrator-BGM-ambience audio and bilingual {src_lang}-and-{tgt_lang} subtitles overlaid.",
        ],
    }


SAMPLES: list[dict] = [
    {**_make("Ultra-storytelling bedtime", "soft watercolor", "child-protagonist bedtime adventure", "child-portrait", "soft-piano lullaby", "soft forest-night", "Spanish", "English"),
     "user_goal": "Here's a portrait of my daughter — make an illustrated bedtime audiobook of her woodland adventure with soft watercolor illustrations, soft-piano lullaby BGM, soft forest-night ambient, narrated in Spanish with English subtitles."},
    {**_make("Ultra-storytelling heritage memoir", "sepia-toned", "grandmother's-life storytime", "grandmother-portrait", "gentle classical-piano", "vintage-radio-and-tea-cup", "Mandarin", "English"),
     "user_goal": "Here's a photo of my grandmother — produce an illustrated audiobook of her stories with sepia-toned illustrations, gentle classical-piano BGM, vintage-radio-and-tea-cup ambient, narrated in Mandarin with English subtitles."},
    {**_make("Ultra-storytelling pet adventure", "warm watercolor", "family-pet adventure", "dog-portrait", "playful flute-and-strings", "neighborhood-park-and-distant-bird", "Japanese", "English"),
     "user_goal": "Here's a photo of my shiba inu Yuki — make an illustrated audiobook of Yuki's adventures with warm watercolor illustrations, playful flute-and-strings BGM, neighborhood-park-and-distant-bird ambient, narrated in Japanese with English subtitles."},
    {**_make("Ultra-storytelling immigration", "sepia-toned", "family-immigration narration", "family-photo", "wistful violin-and-piano", "ocean-liner-and-distant-horn", "Vietnamese", "English"),
     "user_goal": "Here's an old family photo — produce an illustrated audiobook of our immigration story with sepia-toned illustrations, wistful violin-and-piano BGM, ocean-liner-and-distant-horn ambient, narrated in Vietnamese with English subtitles."},
    {**_make("Ultra-storytelling pet-cat folktale", "Beatrix-Potter watercolor", "cat-as-protagonist folktale", "cat-portrait", "music-box waltz", "cottage-fireplace-and-distant-rain", "Korean", "English"),
     "user_goal": "Here's a photo of my cat Bori — make an illustrated audiobook of a folktale starring Bori with Beatrix-Potter watercolor illustrations, music-box waltz BGM, cottage-fireplace-and-distant-rain ambient, narrated in Korean with English subtitles."},
    {**_make("Ultra-storytelling hero quest", "ink-and-color-wash", "young-warrior-hero quest", "young-woman-portrait", "epic orchestral", "ancient-ruin-wind", "Hindi", "English"),
     "user_goal": "Here's a photo of my best friend — produce an illustrated audiobook of an epic hero-quest tale with ink-and-color-wash illustrations, epic orchestral BGM, ancient-ruin-wind ambient, narrated in Hindi with English subtitles."},
    {**_make("Ultra-storytelling mother-daughter", "warm pastel", "mother-and-daughter shared-memory", "mother-daughter-photo", "tender solo-piano", "spring-meadow-and-distant-bird", "French", "English"),
     "user_goal": "Here's a photo of me and my mother — make an illustrated audiobook of our shared memories with warm pastel illustrations, tender solo-piano BGM, spring-meadow-and-distant-bird ambient, narrated in French with English subtitles."},
    {**_make("Ultra-storytelling childhood memoir", "soft pastel", "childhood-self memoir", "childhood-photo", "wistful strings", "school-yard-and-distant-laughter", "German", "English"),
     "user_goal": "Here's a photo of me as a child — produce an illustrated audiobook of a memory from that time with soft pastel illustrations, wistful strings BGM, school-yard-and-distant-laughter ambient, narrated in German with English subtitles."},
    {**_make("Ultra-storytelling best-friend tale", "vibrant cartoon", "best-friend-adventure tale", "friend-portrait", "upbeat indie folk", "summer-festival-and-crowd", "Italian", "English"),
     "user_goal": "Here's a photo of my best friend — make an illustrated audiobook adventure tale starring her with vibrant cartoon illustrations, upbeat indie-folk BGM, summer-festival-and-crowd ambient, narrated in Italian with English subtitles."},
    {**_make("Ultra-storytelling pet-horse", "watercolor", "pet-horse meadow story", "horse-portrait", "open-prairie acoustic-guitar", "open-prairie-wind-and-bird", "Russian", "English"),
     "user_goal": "Here's a photo of my horse Tara — produce an illustrated audiobook about Tara running across the meadow with watercolor illustrations, open-prairie acoustic-guitar BGM, open-prairie-wind-and-bird ambient, narrated in Russian with English subtitles."},
    {**_make("Ultra-storytelling sibling adventure", "ink-and-color", "siblings adventure tale", "siblings-photo", "playful clarinet-and-strings", "summer-camp-and-distant-canoe", "Portuguese", "English"),
     "user_goal": "Here's a photo of me and my brother — make an illustrated audiobook adventure tale about us with ink-and-color illustrations, playful clarinet-and-strings BGM, summer-camp-and-distant-canoe ambient, narrated in Portuguese with English subtitles."},
    {**_make("Ultra-storytelling pet-dog journey", "warm watercolor", "pet-dog cross-country journey", "dog-portrait", "Americana folk", "highway-and-distant-train", "Turkish", "English"),
     "user_goal": "Here's a photo of my dog Mavi — produce an illustrated audiobook about Mavi's cross-country journey with warm watercolor illustrations, Americana-folk BGM, highway-and-distant-train ambient, narrated in Turkish with English subtitles."},
    {**_make("Ultra-storytelling wedding narration", "watercolor", "wedding-portrait love-story narration", "wedding-portrait", "romantic strings", "garden-cicada-and-distant-bell", "Arabic", "English"),
     "user_goal": "Here's our wedding photo — make an illustrated audiobook of our love story with watercolor illustrations, romantic-strings BGM, garden-cicada-and-distant-bell ambient, narrated in Arabic with English subtitles."},
    {**_make("Ultra-storytelling father young-self", "sepia-toned", "father's young-self story", "father-young-portrait", "wistful piano-and-cello", "old-radio-and-distant-train", "Polish", "English"),
     "user_goal": "Here's a photo of my dad as a young man — produce an illustrated audiobook of his young-self life-story with sepia-toned illustrations, wistful piano-and-cello BGM, old-radio-and-distant-train ambient, narrated in Polish with English subtitles."},
    {**_make("Ultra-storytelling family cat", "whimsical cartoon", "family-cat picture-book", "cat-portrait", "playful pizzicato", "kitchen-clock-and-distant-tea-kettle", "Greek", "English"),
     "user_goal": "Here's a photo of our family cat Cocoa — make an illustrated picture-book audiobook starring Cocoa with whimsical cartoon illustrations, playful pizzicato BGM, kitchen-clock-and-distant-tea-kettle ambient, narrated in Greek with English subtitles."},
    {**_make("Ultra-storytelling hero's journey", "ink-and-color", "young-hero's-journey", "boy-portrait", "epic adventure orchestral", "ancient-temple-and-mountain-wind", "Thai", "English"),
     "user_goal": "Here's a photo of my nephew — produce an illustrated audiobook of his hero's-journey adventure with ink-and-color illustrations, epic-adventure orchestral BGM, ancient-temple-and-mountain-wind ambient, narrated in Thai with English subtitles."},
    {**_make("Ultra-storytelling twin heroes", "bright cartoon", "twin-heroes adventure", "twin-portrait", "playful adventure orchestral", "playground-and-distant-laughter", "Tagalog", "English"),
     "user_goal": "Here are photos of my twin daughters — make an illustrated audiobook of their twin-heroes adventure with bright cartoon illustrations, playful adventure orchestral BGM, playground-and-distant-laughter ambient, narrated in Tagalog with English subtitles."},
    {**_make("Ultra-storytelling pet-bird", "Audubon-watercolor", "parrot-as-protagonist tale", "parrot-portrait", "tropical guitar-and-percussion", "tropical-rainforest-bird-and-insect", "Indonesian", "English"),
     "user_goal": "Here's a photo of my parrot Pisang — produce an illustrated audiobook about Pisang flying around the islands with Audubon-watercolor illustrations, tropical guitar-and-percussion BGM, tropical-rainforest-bird-and-insect ambient, narrated in Indonesian with English subtitles."},
    {**_make("Ultra-storytelling mythic hero", "Mughal-miniature", "person-as-mythic-hero tale", "person-portrait", "Indian classical sitar", "Indian-temple-and-distant-bell", "Bengali", "English"),
     "user_goal": "Here's a photo of my aunt — make an illustrated audiobook of a mythic-hero tale starring her with Mughal-miniature illustrations, Indian classical sitar BGM, Indian-temple-and-distant-bell ambient, narrated in Bengali with English subtitles."},
    {**_make("Ultra-storytelling Andean abuela", "Mexican-retablo", "abuela's-life tale", "grandmother-portrait", "Andean pan-flute", "Andean-village-and-distant-bell", "Spanish", "Quechua"),
     "user_goal": "Here's a photo of my abuela — produce an illustrated audiobook of her Andean-village life-story with Mexican-retablo illustrations, Andean pan-flute BGM, Andean-village-and-distant-bell ambient, narrated in Spanish with Quechua subtitles."},
]
