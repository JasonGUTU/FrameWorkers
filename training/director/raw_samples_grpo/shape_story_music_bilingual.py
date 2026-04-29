"""GRPO shape: story_music_bilingual — Narration → Illustration → Narrator → Music → AudioMix → Translation → Compositor.

20 samples.
"""
from __future__ import annotations


def _make(topic, art_style, descriptor, music, src_lang, tgt_lang):
    return {
        "rationale": (
            f"{topic} + {art_style} illustrations + slideshow narration with "
            f"{music} BGM and {src_lang}-and-{tgt_lang} bilingual subtitles."
        ),
        "intents": [
            f"Write the narration script from the {descriptor}.",
            f"Generate one {art_style} illustration per {descriptor} scene.",
            f"Produce a measured {src_lang} TTS narrator track for the {descriptor}.",
            f"Compose the {music} BGM the user requested.",
            f"Layer the {music} BGM under the narrator track into one final mixed wav.",
            f"Translate the {src_lang} narrator track into {tgt_lang} for the second-language subtitle overlay.",
            f"Compose the final slideshow pairing {art_style} illustrations with mixed narrator-and-BGM audio and bilingual {src_lang}-and-{tgt_lang} subtitles overlaid.",
        ],
    }


SAMPLES: list[dict] = [
    {**_make("Bilingual bedtime forest-tale", "soft watercolor", "forest-rabbit bedtime tale", "soft-piano lullaby", "Spanish", "English"),
     "user_goal": "Make an illustrated bedtime audiobook of a forest-rabbit tale with soft watercolor illustrations and soft-piano lullaby BGM, narrated in Spanish with English subtitles."},
    {**_make("Bilingual Tang-poem recitation", "Chinese-ink-wash", "Tang-dynasty poem recitation", "classical guzheng", "Mandarin", "English"),
     "user_goal": "Read a classical Tang-dynasty poem aloud with Chinese-ink-wash illustrations and classical guzheng BGM, narrated in Mandarin with English subtitles."},
    {**_make("Bilingual Momotaro tale", "ukiyo-e", "Momotaro peach-boy folktale", "Japanese koto-and-flute", "Japanese", "English"),
     "user_goal": "Produce an illustrated audiobook of the Japanese Momotaro folktale with ukiyo-e illustrations and Japanese koto-and-flute BGM, narrated in Japanese with English subtitles."},
    {**_make("Bilingual Petit-Chaperon tale", "classic-storybook", "Petit-Chaperon-Rouge tale", "music-box waltz", "French", "English"),
     "user_goal": "Make an illustrated audiobook of the French Petit-Chaperon-Rouge tale with classic-storybook illustrations and music-box waltz BGM, narrated in French with English subtitles."},
    {**_make("Bilingual Bremen-Town-Musicians", "Bavarian-folk", "Bremen-Town-Musicians tale", "German-folk strings-and-accordion", "German", "English"),
     "user_goal": "Read the German Bremen-Town-Musicians tale with Bavarian-folk illustrations and German-folk strings-and-accordion BGM, narrated in German with English subtitles."},
    {**_make("Bilingual Vasilisa tale", "Bilibin-style", "Vasilisa-the-Beautiful tale", "Russian balalaika-and-strings", "Russian", "English"),
     "user_goal": "Produce an illustrated audiobook of the Russian Vasilisa-the-Beautiful tale with Bilibin-style illustrations and Russian balalaika-and-strings BGM, narrated in Russian with English subtitles."},
    {**_make("Bilingual Panchatantra fable", "Mughal-miniature", "Panchatantra fox-and-crow fable", "Indian sitar-and-tabla", "Hindi", "English"),
     "user_goal": "Make an illustrated audiobook of the Panchatantra fox-and-crow fable with Mughal-miniature illustrations and Indian sitar-and-tabla BGM, narrated in Hindi with English subtitles."},
    {**_make("Bilingual Tangun myth", "Korean-minhwa", "Tangun founding-myth", "Korean gayageum", "Korean", "English"),
     "user_goal": "Read the Korean Tangun founding-myth with Korean-minhwa illustrations and Korean gayageum BGM, narrated in Korean with English subtitles."},
    {**_make("Bilingual Pinocchio classic", "classic-storybook", "Pinocchio classic", "Italian opera-style strings", "Italian", "English"),
     "user_goal": "Produce an illustrated audiobook of the Italian Pinocchio classic with classic-storybook illustrations and Italian opera-style strings BGM, narrated in Italian with English subtitles."},
    {**_make("Bilingual 1001-Nights tale", "Arabic-miniature", "One-Thousand-and-One-Nights tale", "Arabic oud-and-percussion", "Arabic", "English"),
     "user_goal": "Make an illustrated audiobook of an Arabic 1001-Nights tale with Arabic-miniature illustrations and Arabic oud-and-percussion BGM, narrated in Arabic with English subtitles."},
    {**_make("Bilingual watermelon-king tale", "Vietnamese-folk", "Vietnamese watermelon-king tale", "Vietnamese đàn tranh", "Vietnamese", "English"),
     "user_goal": "Read the Vietnamese watermelon-king tale with Vietnamese-folk illustrations and Vietnamese đàn tranh BGM, narrated in Vietnamese with English subtitles."},
    {**_make("Bilingual Phra-Aphai-Mani epic", "Thai-mural-style", "Phra-Aphai-Mani epic", "Thai ranat-and-flute", "Thai", "English"),
     "user_goal": "Produce an illustrated audiobook of the Thai Phra-Aphai-Mani epic with Thai-mural-style illustrations and Thai ranat-and-flute BGM, narrated in Thai with English subtitles."},
    {**_make("Bilingual Wawel-dragon legend", "illuminated-manuscript", "Wawel-dragon legend", "Polish folk-fiddle", "Polish", "English"),
     "user_goal": "Make an illustrated audiobook of the Polish Wawel-dragon legend with illuminated-manuscript illustrations and Polish folk-fiddle BGM, narrated in Polish with English subtitles."},
    {**_make("Bilingual Eve-and-snake tale", "Hebrew-illuminated", "Eve-and-the-snake tale", "Hebrew-folk strings", "Hebrew", "English"),
     "user_goal": "Read the Hebrew Eve-and-the-snake tale with Hebrew-illuminated illustrations and Hebrew-folk strings BGM, narrated in Hebrew with English subtitles."},
    {**_make("Bilingual Sango thunder-god", "Yoruba-adire-cloth", "Sango-thunder-god tale", "Yoruba talking-drum", "Yoruba", "English"),
     "user_goal": "Produce an illustrated audiobook of the Yoruba Sango-thunder-god tale with Yoruba-adire-cloth illustrations and Yoruba talking-drum BGM, narrated in Yoruba with English subtitles."},
    {**_make("Bilingual Anansi Caribbean-tale", "bright Caribbean-palette", "Anansi-and-tiger Caribbean-version", "Caribbean steel-pan", "Swahili", "English"),
     "user_goal": "Make an illustrated audiobook of the Swahili-language Anansi-and-tiger Caribbean tale with bright Caribbean-palette illustrations and Caribbean steel-pan BGM, narrated in Swahili with English subtitles."},
    {**_make("Bilingual Maria-Makiling tale", "Filipino-watercolor", "Maria-Makiling forest-spirit tale", "Filipino-folk kulintang", "Tagalog", "English"),
     "user_goal": "Read the Tagalog Maria-Makiling forest-spirit tale with Filipino-watercolor illustrations and Filipino-folk kulintang BGM, narrated in Tagalog with English subtitles."},
    {**_make("Bilingual Pachamama tale", "Inca-textile", "Pachamama mother-earth tale", "Andean pan-flute-and-charango", "Quechua", "Spanish"),
     "user_goal": "Produce an illustrated audiobook of the Quechua Pachamama mother-earth tale with Inca-textile illustrations and Andean pan-flute-and-charango BGM, narrated in Quechua with Spanish subtitles."},
    {**_make("Bilingual Maui-fishhook myth", "Maori-whakairo-carving", "Maui-fishhook myth", "Maori-folk koauau", "Maori", "English"),
     "user_goal": "Make an illustrated audiobook of the Maori Maui-fishhook myth with Maori-whakairo-carving illustrations and Maori-folk koauau BGM, narrated in Maori with English subtitles."},
    {**_make("Bilingual Spider-Woman creation", "Navajo-textile-pattern", "Spider-Woman creation tale", "Navajo flute", "Navajo", "English"),
     "user_goal": "Read the Navajo Spider-Woman creation tale with Navajo-textile-pattern illustrations and Navajo flute BGM, narrated in Navajo with English subtitles."},
]
