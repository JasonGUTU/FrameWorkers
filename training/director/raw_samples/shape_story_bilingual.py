"""Shape: story_bilingual —
    Narration → Illustration → Narrator → Translation → Compositor.

Illustrated audiobook with bilingual subs (narrator transcript translated).
"""
from __future__ import annotations

SAMPLES: list[dict] = [
    {
        "user_goal": "Make an English-Chinese bilingual illustrated audiobook of this short fairytale — narrate in English, burn both English and Chinese subtitles on the slideshow.",
        "rationale": (
            "Short fairytale + English+Chinese bilingual subs. Chain: Narration → Illustration "
            "→ Narrator → Translation → Compositor. Reject Music/Ambience (none requested), "
            "Transcription (we generate the transcript from Narration output; TTS narrator "
            "text + translation layer is the bilingual path)."
        ),
        "intents": [
            "Write the narration script from the short fairytale.",
            "Generate one watercolor illustration per scene.",
            "Produce an English TTS narrator track for the fairytale.",
            "Translate the narration script into Chinese subtitle segments.",
            "Compose the final slideshow pairing illustrations with narrator audio and bilingual English+Chinese captions.",
        ],
    },
    {
        "user_goal": "Make an English-Spanish bilingual illustrated audiobook of this Mexican folk tale about a rabbit and the moon.",
        "rationale": (
            "Mexican rabbit-and-moon folktale + English+Spanish bilingual."
        ),
        "intents": [
            "Write the narration script from the rabbit-and-moon folktale.",
            "Generate one Mexican-folk-art illustration per scene.",
            "Produce an English TTS narrator track for the folktale.",
            "Translate the narration script into Spanish subtitle segments.",
            "Compose the final slideshow pairing illustrations with English narrator and bilingual English+Spanish captions.",
        ],
    },
    {
        "user_goal": "Make an English-Japanese bilingual illustrated audiobook of this short Japanese fairytale about a crane child.",
        "rationale": (
            "Japanese crane-child fairytale + English+Japanese bilingual."
        ),
        "intents": [
            "Write the narration script from the crane-child fairytale.",
            "Generate one ink-and-wash illustration per scene.",
            "Produce an English TTS narrator track for the crane-child tale.",
            "Translate the narration script into Japanese subtitle segments.",
            "Compose the final slideshow pairing illustrations with English narrator and bilingual English+Japanese captions.",
        ],
    },
    {
        "user_goal": "Make an English-French bilingual illustrated audiobook of this Normandy folktale about a fisherman's daughter and a seal.",
        "rationale": (
            "Normandy fisherman-seal folktale + English+French bilingual."
        ),
        "intents": [
            "Write the narration script from the Normandy fisherman-seal folktale.",
            "Generate one soft-watercolor illustration per scene.",
            "Produce an English TTS narrator track for the Normandy tale.",
            "Translate the narration script into French subtitle segments.",
            "Compose the final slideshow pairing illustrations with English narrator and bilingual English+French captions.",
        ],
    },
    {
        "user_goal": "Make an English-Korean bilingual illustrated audiobook of this Korean folk tale about the rabbit on the moon.",
        "rationale": (
            "Korean rabbit-moon folktale + English+Korean bilingual."
        ),
        "intents": [
            "Write the narration script from the Korean rabbit-moon folktale.",
            "Generate one Korean-folk-art illustration per scene.",
            "Produce an English TTS narrator track for the folktale.",
            "Translate the narration script into Korean subtitle segments.",
            "Compose the final slideshow pairing illustrations with English narrator and bilingual English+Korean captions.",
        ],
    },
    {
        "user_goal": "Make an English-German bilingual illustrated audiobook of this Grimm fairytale about the Bremen Town Musicians.",
        "rationale": (
            "Grimm Bremen Town Musicians + English+German bilingual."
        ),
        "intents": [
            "Write the narration script from the Bremen Town Musicians tale.",
            "Generate one retro-storybook illustration per scene.",
            "Produce an English TTS narrator track for the Grimm tale.",
            "Translate the narration script into German subtitle segments.",
            "Compose the final slideshow pairing illustrations with English narrator and bilingual English+German captions.",
        ],
    },
    {
        "user_goal": "Make an English-Italian bilingual illustrated audiobook of this Italian folktale about a violin-maker and a fairy.",
        "rationale": (
            "Italian violin-maker-and-fairy folktale + English+Italian bilingual."
        ),
        "intents": [
            "Write the narration script from the violin-maker-and-fairy folktale.",
            "Generate one soft-pastel illustration per scene.",
            "Produce an English TTS narrator track for the folktale.",
            "Translate the narration script into Italian subtitle segments.",
            "Compose the final slideshow pairing illustrations with English narrator and bilingual English+Italian captions.",
        ],
    },
    {
        "user_goal": "Make an English-Russian bilingual illustrated audiobook of this Russian folktale about the firebird and the wolf.",
        "rationale": (
            "Russian firebird-and-wolf folktale + English+Russian bilingual."
        ),
        "intents": [
            "Write the narration script from the firebird-and-wolf folktale.",
            "Generate one Ivan-Bilibin-style illustration per scene.",
            "Produce an English TTS narrator track for the folktale.",
            "Translate the narration script into Russian subtitle segments.",
            "Compose the final slideshow pairing illustrations with English narrator and bilingual English+Russian captions.",
        ],
    },
    {
        "user_goal": "Make an English-Arabic bilingual illustrated audiobook of this Arabian tale about Scheherazade's first night.",
        "rationale": (
            "Arabian Scheherazade first-night tale + English+Arabic bilingual."
        ),
        "intents": [
            "Write the narration script from the Scheherazade first-night tale.",
            "Generate one Arabic-calligraphic illustration per scene.",
            "Produce an English TTS narrator track for the Scheherazade tale.",
            "Translate the narration script into Arabic subtitle segments.",
            "Compose the final slideshow pairing illustrations with English narrator and bilingual English+Arabic captions.",
        ],
    },
    {
        "user_goal": "Make an English-Hindi bilingual illustrated audiobook of this Panchatantra tale about the monkey and the crocodile.",
        "rationale": (
            "Panchatantra monkey-crocodile + English+Hindi bilingual."
        ),
        "intents": [
            "Write the narration script from the monkey-crocodile Panchatantra tale.",
            "Generate one vibrant Indian-folk illustration per scene.",
            "Produce an English TTS narrator track for the Panchatantra tale.",
            "Translate the narration script into Hindi subtitle segments.",
            "Compose the final slideshow pairing illustrations with English narrator and bilingual English+Hindi captions.",
        ],
    },
    {
        "user_goal": "Make an English-Portuguese bilingual illustrated audiobook of this Brazilian folktale about the Amazon pink dolphin.",
        "rationale": (
            "Brazilian pink-dolphin folktale + English+Portuguese bilingual."
        ),
        "intents": [
            "Write the narration script from the pink-dolphin folktale.",
            "Generate one tropical-watercolor illustration per scene.",
            "Produce an English TTS narrator track for the Brazilian folktale.",
            "Translate the narration script into Portuguese subtitle segments.",
            "Compose the final slideshow pairing illustrations with English narrator and bilingual English+Portuguese captions.",
        ],
    },
    {
        "user_goal": "Make an English-Thai bilingual illustrated audiobook of this Thai folktale about the rice spirit and the harvest.",
        "rationale": (
            "Thai rice-spirit folktale + English+Thai bilingual."
        ),
        "intents": [
            "Write the narration script from the rice-spirit folktale.",
            "Generate one Thai-folk-art illustration per scene.",
            "Produce an English TTS narrator track for the folktale.",
            "Translate the narration script into Thai subtitle segments.",
            "Compose the final slideshow pairing illustrations with English narrator and bilingual English+Thai captions.",
        ],
    },
    {
        "user_goal": "Make an English-Vietnamese bilingual illustrated audiobook of this Vietnamese folktale about the dragon king of the sea.",
        "rationale": (
            "Vietnamese sea-dragon-king folktale + English+Vietnamese bilingual."
        ),
        "intents": [
            "Write the narration script from the sea-dragon-king folktale.",
            "Generate one Vietnamese-folk-art illustration per scene.",
            "Produce an English TTS narrator track for the folktale.",
            "Translate the narration script into Vietnamese subtitle segments.",
            "Compose the final slideshow pairing illustrations with English narrator and bilingual English+Vietnamese captions.",
        ],
    },
    {
        "user_goal": "Make an English-Swedish bilingual illustrated audiobook of this Swedish folktale about the old man of the forest.",
        "rationale": (
            "Swedish old-man-of-forest folktale + English+Swedish bilingual."
        ),
        "intents": [
            "Write the narration script from the old-man-of-forest folktale.",
            "Generate one Swedish-folk-art illustration per scene.",
            "Produce an English TTS narrator track for the folktale.",
            "Translate the narration script into Swedish subtitle segments.",
            "Compose the final slideshow pairing illustrations with English narrator and bilingual English+Swedish captions.",
        ],
    },
    {
        "user_goal": "Make an English-Norwegian bilingual illustrated audiobook of this Norse folktale about a troll under a bridge.",
        "rationale": (
            "Norwegian bridge-troll folktale + English+Norwegian bilingual."
        ),
        "intents": [
            "Write the narration script from the bridge-troll folktale.",
            "Generate one Norse-folk-art illustration per scene.",
            "Produce an English TTS narrator track for the troll tale.",
            "Translate the narration script into Norwegian subtitle segments.",
            "Compose the final slideshow pairing illustrations with English narrator and bilingual English+Norwegian captions.",
        ],
    },
    {
        "user_goal": "Make an English-Finnish bilingual illustrated audiobook of this Kalevala-inspired tale about the singer Väinämöinen.",
        "rationale": (
            "Kalevala Väinämöinen tale + English+Finnish bilingual."
        ),
        "intents": [
            "Write the narration script from the Väinämöinen tale.",
            "Generate one Finnish-folk-art illustration per scene.",
            "Produce an English TTS narrator track for the Väinämöinen tale.",
            "Translate the narration script into Finnish subtitle segments.",
            "Compose the final slideshow pairing illustrations with English narrator and bilingual English+Finnish captions.",
        ],
    },
    {
        "user_goal": "Make an English-Dutch bilingual illustrated audiobook of this Dutch folktale about a windmill spirit.",
        "rationale": (
            "Dutch windmill-spirit folktale + English+Dutch bilingual."
        ),
        "intents": [
            "Write the narration script from the windmill-spirit folktale.",
            "Generate one Dutch-folk-art illustration per scene.",
            "Produce an English TTS narrator track for the folktale.",
            "Translate the narration script into Dutch subtitle segments.",
            "Compose the final slideshow pairing illustrations with English narrator and bilingual English+Dutch captions.",
        ],
    },
    {
        "user_goal": "Make an English-Greek bilingual illustrated audiobook of this Greek myth about Arachne's weaving contest.",
        "rationale": (
            "Arachne Greek myth + English+Greek bilingual."
        ),
        "intents": [
            "Write the narration script from the Arachne myth.",
            "Generate one Greek-vase-style illustration per scene.",
            "Produce an English TTS narrator track for the myth.",
            "Translate the narration script into Greek subtitle segments.",
            "Compose the final slideshow pairing illustrations with English narrator and bilingual English+Greek captions.",
        ],
    },
    {
        "user_goal": "Make an English-Hebrew bilingual illustrated audiobook of this Hebrew folktale about Elijah the Prophet visiting a poor couple.",
        "rationale": (
            "Hebrew Elijah-Prophet folktale + English+Hebrew bilingual."
        ),
        "intents": [
            "Write the narration script from the Elijah-Prophet folktale.",
            "Generate one soft-illumination illustration per scene.",
            "Produce an English TTS narrator track for the folktale.",
            "Translate the narration script into Hebrew subtitle segments.",
            "Compose the final slideshow pairing illustrations with English narrator and bilingual English+Hebrew captions.",
        ],
    },
    {
        "user_goal": "Make an English-Turkish bilingual illustrated audiobook of this Turkish folktale about Nasreddin Hodja and the donkey.",
        "rationale": (
            "Nasreddin Hodja folktale + English+Turkish bilingual."
        ),
        "intents": [
            "Write the narration script from the Nasreddin-Hodja-donkey folktale.",
            "Generate one Turkish-miniature illustration per scene.",
            "Produce an English TTS narrator track for the Hodja folktale.",
            "Translate the narration script into Turkish subtitle segments.",
            "Compose the final slideshow pairing illustrations with English narrator and bilingual English+Turkish captions.",
        ],
    },
]
