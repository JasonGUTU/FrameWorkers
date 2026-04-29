"""GRPO shape: story_bilingual — Narration → Illustration → Narrator → Translation → Compositor.

20 samples (target_n=20, no long_story). Illustrated audiobook with bilingual subtitles.
"""
from __future__ import annotations


def _make(topic, art_style, descriptor, src_lang, tgt_lang):
    return {
        "rationale": (
            f"{topic} + {art_style} illustrations + slideshow narration with "
            f"{src_lang}-and-{tgt_lang} bilingual subtitles."
        ),
        "intents": [
            f"Write the narration script from the {descriptor}.",
            f"Generate one {art_style} illustration per {descriptor} scene.",
            f"Produce a measured {src_lang} TTS narrator track for the {descriptor}.",
            f"Translate the {src_lang} narrator track into {tgt_lang} for the second-language subtitle overlay.",
            f"Compose the final slideshow pairing {art_style} illustrations with the narrator audio and bilingual {src_lang}-and-{tgt_lang} subtitles overlaid.",
        ],
    }


SAMPLES: list[dict] = [
    {**_make("Spanish La-Llorona ghost-tale", "Mexican-retablo", "La-Llorona ghost-tale", "Spanish", "English"),
     "user_goal": "Make an illustrated audiobook of the Spanish La-Llorona ghost-tale with Mexican-retablo illustrations, narrated in Spanish with English subtitles."},
    {**_make("Mandarin Monkey-King adventure", "Chinese-ink-wash", "Monkey-King-Sun-Wukong adventure", "Mandarin", "English"),
     "user_goal": "Read the Chinese Monkey-King-Sun-Wukong adventure aloud with Chinese-ink-wash illustrations, narrated in Mandarin with English subtitles."},
    {**_make("Japanese Momotaro folktale", "ukiyo-e", "Momotaro peach-boy folktale", "Japanese", "English"),
     "user_goal": "Produce an illustrated audiobook of Japan's Momotaro peach-boy folktale with ukiyo-e illustrations, narrated in Japanese with English subtitles."},
    {**_make("French Petit-Chaperon-Rouge tale", "classic-storybook", "Petit-Chaperon-Rouge tale", "French", "English"),
     "user_goal": "Make an illustrated audiobook of the French Petit-Chaperon-Rouge tale with classic-storybook illustrations, narrated in French with English subtitles."},
    {**_make("German Bremen-Town-Musicians tale", "Bavarian-folk", "Bremen-Town-Musicians tale", "German", "English"),
     "user_goal": "Read the German Bremen-Town-Musicians tale aloud with Bavarian-folk illustrations, narrated in German with English subtitles."},
    {**_make("Russian Vasilisa-the-Beautiful tale", "Bilibin-style", "Vasilisa-the-Beautiful tale", "Russian", "English"),
     "user_goal": "Produce an illustrated audiobook of the Russian Vasilisa-the-Beautiful tale with Bilibin-style illustrations, narrated in Russian with English subtitles."},
    {**_make("Hindi Panchatantra fox-and-crow fable", "Mughal-miniature", "Panchatantra fox-and-crow fable", "Hindi", "English"),
     "user_goal": "Make an illustrated audiobook of the Panchatantra fox-and-crow fable with Mughal-miniature illustrations, narrated in Hindi with English subtitles."},
    {**_make("Korean Tangun founding-myth", "Korean-minhwa", "Tangun founding-myth", "Korean", "English"),
     "user_goal": "Read the Korean Tangun founding-myth aloud with Korean-minhwa illustrations, narrated in Korean with English subtitles."},
    {**_make("Italian Pinocchio classic", "classic-storybook", "Pinocchio classic", "Italian", "English"),
     "user_goal": "Produce an illustrated audiobook of the Italian Pinocchio classic with classic-storybook illustrations, narrated in Italian with English subtitles."},
    {**_make("Arabic One-Thousand-and-One-Nights tale", "Arabic-miniature", "One-Thousand-and-One-Nights tale", "Arabic", "English"),
     "user_goal": "Make an illustrated audiobook of an Arabic One-Thousand-and-One-Nights tale with Arabic-miniature illustrations, narrated in Arabic with English subtitles."},
    {**_make("Vietnamese watermelon-king tale", "Vietnamese-folk", "Vietnamese watermelon-king tale", "Vietnamese", "English"),
     "user_goal": "Read the Vietnamese watermelon-king tale aloud with Vietnamese-folk illustrations, narrated in Vietnamese with English subtitles."},
    {**_make("Thai Phra-Aphai-Mani epic", "Thai-mural-style", "Phra-Aphai-Mani epic", "Thai", "English"),
     "user_goal": "Produce an illustrated audiobook of the Thai Phra-Aphai-Mani epic with Thai-mural-style illustrations, narrated in Thai with English subtitles."},
    {**_make("Polish Wawel-dragon legend", "illuminated-manuscript", "Wawel-dragon legend", "Polish", "English"),
     "user_goal": "Make an illustrated audiobook of the Polish Wawel-dragon legend with illuminated-manuscript illustrations, narrated in Polish with English subtitles."},
    {**_make("Hebrew Eve-and-the-snake tale", "Hebrew-illuminated", "Eve-and-the-snake tale", "Hebrew", "English"),
     "user_goal": "Read the Hebrew Eve-and-the-snake tale aloud with Hebrew-illuminated illustrations, narrated in Hebrew with English subtitles."},
    {**_make("Yoruba Sango-thunder-god tale", "Yoruba-adire-cloth", "Sango-thunder-god tale", "Yoruba", "English"),
     "user_goal": "Produce an illustrated audiobook of the Yoruba Sango-thunder-god tale with Yoruba-adire-cloth illustrations, narrated in Yoruba with English subtitles."},
    {**_make("Swahili Anansi-and-tiger Caribbean-version", "bright Caribbean-palette", "Anansi-and-tiger Caribbean-version", "Swahili", "English"),
     "user_goal": "Make an illustrated audiobook of the Swahili-language version of the Anansi-and-tiger trickster tale with bright Caribbean-palette illustrations, narrated in Swahili with English subtitles."},
    {**_make("Tagalog Maria-Makiling forest-spirit tale", "Filipino-watercolor", "Maria-Makiling forest-spirit tale", "Tagalog", "English"),
     "user_goal": "Read the Tagalog Maria-Makiling forest-spirit tale aloud with Filipino-watercolor illustrations, narrated in Tagalog with English subtitles."},
    {**_make("Quechua Pachamama tale", "Inca-textile", "Pachamama mother-earth tale", "Quechua", "Spanish"),
     "user_goal": "Produce an illustrated audiobook of the Quechua Pachamama mother-earth tale with Inca-textile illustrations, narrated in Quechua with Spanish subtitles."},
    {**_make("Maori Maui-fishhook myth", "Maori-whakairo-carving", "Maui-fishhook myth", "Maori", "English"),
     "user_goal": "Make an illustrated audiobook of the Maori Maui-fishhook myth with Maori-whakairo-carving illustrations, narrated in Maori with English subtitles."},
    {**_make("Navajo Spider-Woman creation tale", "Navajo-textile-pattern", "Spider-Woman creation tale", "Navajo", "English"),
     "user_goal": "Read the Navajo Spider-Woman creation tale aloud with Navajo-textile-pattern illustrations, narrated in Navajo with English subtitles."},
]
