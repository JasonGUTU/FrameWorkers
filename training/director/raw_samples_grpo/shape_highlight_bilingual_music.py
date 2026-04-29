"""GRPO shape: highlight_bilingual_music — IntakeVideo → VideoAnalysis → Highlight → Transcription → Translation → Music → AudioMix → Compositor.

20 samples (target_n=20). Highlight reel with bilingual subs + BGM.
"""
from __future__ import annotations


def _make(topic, focus, src_lang, tgt_lang, music):
    return {
        "rationale": (
            f"{topic} + {focus} highlight + {src_lang}-and-{tgt_lang} bilingual subtitles "
            f"+ {music} BGM. Reject AmbienceAgent, StyleTransfer/VideoExtend."
        ),
        "intents": [
            f"Ingest the user's uploaded {topic} recording into the workspace.",
            f"Analyze the {topic} to locate {focus} moments.",
            f"Extract the {focus} as highlight segments.",
            f"Transcribe the {src_lang} dialogue from the highlight segments.",
            f"Translate the {src_lang} subtitle track into {tgt_lang}.",
            f"Compose the {music} BGM the user requested.",
            f"Layer the {music} BGM under the highlight segments into one final mixed wav.",
            f"Composite the final highlight reel mp4 with bilingual {src_lang}-and-{tgt_lang} subtitles and mixed audio.",
        ],
    }


SAMPLES: list[dict] = [
    {**_make("Spanish soccer match", "goal-and-save", "Spanish", "English", "stadium-anthem"),
     "user_goal": "Make a highlight reel of goals from my Spanish-commentary soccer match with Spanish-and-English bilingual subtitles and stadium-anthem BGM."},
    {**_make("Japanese baseball game", "home-run-and-strikeout", "Japanese", "English", "stadium-organ"),
     "user_goal": "Cut a highlight reel of home runs from my Japanese baseball game with Japanese-and-English bilingual subtitles and stadium-organ BGM."},
    {**_make("Korean K-drama episode", "romance-confession", "Korean", "English", "tender-piano"),
     "user_goal": "Make a highlight reel of romance-confession scenes from my Korean K-drama with Korean-and-English bilingual subtitles and tender-piano BGM."},
    {**_make("French film panel", "audience-question", "French", "English", "Parisian-cafe-strings"),
     "user_goal": "Cut a highlight reel of audience questions from my French film panel with French-and-English bilingual subtitles and Parisian-cafe-strings BGM."},
    {**_make("German political debate", "sharpest-exchange", "German", "English", "tense-strings"),
     "user_goal": "Make a highlight reel of sharpest exchanges from my German political debate with German-and-English bilingual subtitles and tense-strings BGM."},
    {**_make("Italian opera production", "climactic-aria", "Italian", "English", "swelling-strings"),
     "user_goal": "Cut a highlight reel of climactic arias from my Italian opera production with Italian-and-English bilingual subtitles and swelling-strings BGM."},
    {**_make("Russian-ballet performance", "principal-solo", "Russian", "English", "Tchaikovsky-style-strings"),
     "user_goal": "Make a highlight reel of principal solos from my Russian-ballet performance with Russian-and-English bilingual subtitles and Tchaikovsky-style-strings BGM."},
    {**_make("Mandarin variety show", "guest-performance", "Mandarin", "English", "celebratory-orchestral"),
     "user_goal": "Cut a highlight reel of guest performances from my Mandarin variety show with Mandarin-and-English bilingual subtitles and celebratory-orchestral BGM."},
    {**_make("Hindi cricket Test", "boundary-and-wicket", "Hindi", "English", "Indian-celebratory"),
     "user_goal": "Make a highlight reel of boundaries and wickets from my Hindi cricket Test with Hindi-and-English bilingual subtitles and Indian-celebratory BGM."},
    {**_make("Cantonese cooking competition", "elimination-moment", "Cantonese", "English", "playful-piano"),
     "user_goal": "Cut a highlight reel of elimination moments from my Cantonese cooking competition with Cantonese-and-English bilingual subtitles and playful-piano BGM."},
    {**_make("Arabic news debate", "key-rebuttal", "Arabic", "English", "tense-strings-and-percussion"),
     "user_goal": "Make a highlight reel of key rebuttals from my Arabic news debate with Arabic-and-English bilingual subtitles and tense-strings-and-percussion BGM."},
    {**_make("Turkish soap-opera season", "cliffhanger", "Turkish", "English", "Turkish-strings"),
     "user_goal": "Cut a highlight reel of cliffhanger moments from my Turkish soap-opera season with Turkish-and-English bilingual subtitles and Turkish-strings BGM."},
    {**_make("Vietnamese cooking show", "judges-tasting", "Vietnamese", "English", "Vietnamese-strings"),
     "user_goal": "Make a highlight reel of judges'-tasting moments from my Vietnamese cooking show with Vietnamese-and-English bilingual subtitles and Vietnamese-strings BGM."},
    {**_make("Thai boxing match", "knockdown", "Thai", "English", "Thai-percussion"),
     "user_goal": "Cut a highlight reel of knockdowns from my Thai boxing match with Thai-and-English bilingual subtitles and Thai-percussion BGM."},
    {**_make("Polish parliamentary session", "vote-tally", "Polish", "English", "tense-orchestral"),
     "user_goal": "Make a highlight reel of vote-tally moments from my Polish parliamentary session with Polish-and-English bilingual subtitles and tense-orchestral BGM."},
    {**_make("Portuguese soccer match", "goal-and-save", "Portuguese", "English", "stadium-fado"),
     "user_goal": "Cut a highlight reel of goals from my Portuguese soccer match with Portuguese-and-English bilingual subtitles and stadium-fado BGM."},
    {**_make("Greek philosophy debate", "sharpest-exchange", "Greek", "English", "tense-strings"),
     "user_goal": "Make a highlight reel of sharpest exchanges from my Greek philosophy debate with Greek-and-English bilingual subtitles and tense-strings BGM."},
    {**_make("Catalan sardana festival", "dance-circle", "Catalan", "Spanish", "Catalan-cobla-band"),
     "user_goal": "Cut a highlight reel of dance-circle moments from my Catalan sardana festival with Catalan-and-Spanish bilingual subtitles and Catalan-cobla-band BGM."},
    {**_make("Quechua harvest festival", "ritual-moment", "Quechua", "Spanish", "Andean-pan-flute"),
     "user_goal": "Make a highlight reel of ritual moments from my Quechua harvest festival with Quechua-and-Spanish bilingual subtitles and Andean-pan-flute BGM."},
    {**_make("Maori hui", "speech-of-welcome", "Maori", "English", "Maori-folk-koauau"),
     "user_goal": "Cut a highlight reel of welcome speeches from my Maori hui with Maori-and-English bilingual subtitles and Maori-folk-koauau BGM."},
]
