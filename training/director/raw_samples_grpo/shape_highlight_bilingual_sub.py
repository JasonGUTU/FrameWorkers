"""GRPO shape: highlight_bilingual_sub — IntakeVideo → VideoAnalysis → Highlight → Transcription → Translation → Compositor.

20 samples (target_n=20). Highlight reel with bilingual subtitles.
"""
from __future__ import annotations


def _make(topic, focus, src_lang, tgt_lang):
    return {
        "rationale": (
            f"{topic} + {focus} highlight + {src_lang}-and-{tgt_lang} bilingual subtitles. "
            "Reject Music/Ambience/AudioMix, StyleTransfer/VideoExtend."
        ),
        "intents": [
            f"Ingest the user's uploaded {topic} recording into the workspace.",
            f"Analyze the {topic} to locate {focus} moments.",
            f"Extract the {focus} as highlight segments.",
            f"Transcribe the {src_lang} dialogue from the highlight segments.",
            f"Translate the {src_lang} subtitle track into {tgt_lang}.",
            f"Composite the final highlight reel mp4 with bilingual {src_lang}-and-{tgt_lang} subtitles overlaid.",
        ],
    }


SAMPLES: list[dict] = [
    {**_make("Spanish-language soccer match", "goal-and-save", "Spanish", "English"),
     "user_goal": "Cut a highlight reel of goals and saves from my Spanish-commentary soccer match with Spanish-and-English bilingual subtitles."},
    {**_make("Japanese baseball game", "home-run-and-strikeout", "Japanese", "English"),
     "user_goal": "Make a highlight reel of home runs and strikeouts from my Japanese baseball game with Japanese-and-English bilingual subtitles."},
    {**_make("Korean K-drama episode", "main-romance-confession", "Korean", "English"),
     "user_goal": "Cut a highlight reel of main romance-confession scenes from my Korean K-drama episode with Korean-and-English bilingual subtitles."},
    {**_make("French film-school panel", "audience-question-exchange", "French", "English"),
     "user_goal": "Make a highlight reel of audience-question exchanges from my French film-school panel with French-and-English bilingual subtitles."},
    {**_make("German political debate", "sharpest-exchange", "German", "English"),
     "user_goal": "Cut a highlight reel of sharpest exchanges from my German political debate with German-and-English bilingual subtitles."},
    {**_make("Italian opera production", "climactic-aria", "Italian", "English"),
     "user_goal": "Make a highlight reel of climactic arias from my Italian opera production with Italian-and-English bilingual subtitles."},
    {**_make("Russian-ballet performance", "principal-solo", "Russian", "English"),
     "user_goal": "Cut a highlight reel of principal solos from my Russian-ballet performance with Russian-and-English bilingual subtitles."},
    {**_make("Mandarin variety show", "guest-performance", "Mandarin", "English"),
     "user_goal": "Make a highlight reel of guest performances from my Mandarin variety show with Mandarin-and-English bilingual subtitles."},
    {**_make("Hindi cricket Test match", "boundary-and-wicket", "Hindi", "English"),
     "user_goal": "Cut a highlight reel of boundaries and wickets from my Hindi cricket Test match with Hindi-and-English bilingual subtitles."},
    {**_make("Cantonese cooking competition", "elimination-moment", "Cantonese", "English"),
     "user_goal": "Make a highlight reel of elimination moments from my Cantonese cooking competition with Cantonese-and-English bilingual subtitles."},
    {**_make("Arabic news debate", "key-rebuttal", "Arabic", "English"),
     "user_goal": "Cut a highlight reel of key rebuttals from my Arabic news debate with Arabic-and-English bilingual subtitles."},
    {**_make("Turkish soap-opera season", "season-cliffhanger", "Turkish", "English"),
     "user_goal": "Make a highlight reel of cliffhanger moments from my Turkish soap-opera season with Turkish-and-English bilingual subtitles."},
    {**_make("Vietnamese cooking show", "judges-tasting", "Vietnamese", "English"),
     "user_goal": "Cut a highlight reel of judges'-tasting moments from my Vietnamese cooking show with Vietnamese-and-English bilingual subtitles."},
    {**_make("Thai boxing match", "knockdown-moment", "Thai", "English"),
     "user_goal": "Make a highlight reel of knockdown moments from my Thai boxing match with Thai-and-English bilingual subtitles."},
    {**_make("Polish parliamentary session", "vote-tally-moment", "Polish", "English"),
     "user_goal": "Cut a highlight reel of vote-tally moments from my Polish parliamentary session with Polish-and-English bilingual subtitles."},
    {**_make("Portuguese soccer match", "goal-and-save", "Portuguese", "English"),
     "user_goal": "Make a highlight reel of goals and saves from my Portuguese soccer match with Portuguese-and-English bilingual subtitles."},
    {**_make("Greek philosophy debate", "sharpest-exchange", "Greek", "English"),
     "user_goal": "Cut a highlight reel of sharpest exchanges from my Greek philosophy debate with Greek-and-English bilingual subtitles."},
    {**_make("Catalan-language sardana festival", "dance-circle-moment", "Catalan", "Spanish"),
     "user_goal": "Make a highlight reel of dance-circle moments from my Catalan-language sardana festival with Catalan-and-Spanish bilingual subtitles."},
    {**_make("Quechua-language harvest festival", "ritual-moment", "Quechua", "Spanish"),
     "user_goal": "Cut a highlight reel of ritual moments from my Quechua-language harvest festival with Quechua-and-Spanish bilingual subtitles."},
    {**_make("Maori-language hui", "speech-of-welcome", "Maori", "English"),
     "user_goal": "Make a highlight reel of welcome-speeches from my Maori-language hui with Maori-and-English bilingual subtitles."},
]
