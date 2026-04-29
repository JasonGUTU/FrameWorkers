"""GRPO shape: highlight_subtitle — IntakeVideo → VideoAnalysis → Highlight → Transcription → Compositor.

30 samples (target_n=30). Highlight reel with subtitles overlaid.
"""
from __future__ import annotations


def _make(topic, highlight_focus, lang):
    return {
        "rationale": (
            f"{topic} + {highlight_focus} highlight + same-language {lang} subtitles. "
            "Reject MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay), "
            "TranslationAgent (no bilingual), StyleTransfer/VideoExtend (no restyle / length change)."
        ),
        "intents": [
            f"Ingest the user's uploaded {topic} recording into the workspace.",
            f"Analyze the {topic} to locate {highlight_focus} moments.",
            f"Extract the {highlight_focus} as highlight segments.",
            f"Transcribe the highlight-segment {lang} dialogue into timestamped subtitle segments.",
            f"Composite the final highlight reel mp4 with {lang} subtitles overlaid.",
        ],
    }


SAMPLES: list[dict] = [
    {**_make("English-language wedding-day video", "vow-and-toast", "English"),
     "user_goal": "Cut my English-language wedding-day video to highlight just vows and toasts, with English subtitles."},
    {**_make("Spanish cooking-show season", "judging-moments", "Spanish"),
     "user_goal": "Pull only the judging moments from my Spanish cooking-show season recordings with Spanish subtitles."},
    {**_make("Japanese baseball game", "home-run-and-strikeout", "Japanese"),
     "user_goal": "Highlight just the home runs and strikeouts from my Japanese baseball game with Japanese subtitles."},
    {**_make("French film-school panel discussion", "audience-question", "French"),
     "user_goal": "Cut my French film-school panel-discussion recording to just the audience-question exchanges with French subtitles."},
    {**_make("German political debate", "sharpest-exchange", "German"),
     "user_goal": "Pull just the sharpest exchanges from my German political debate with German subtitles."},
    {**_make("Italian opera production", "climactic-aria", "Italian"),
     "user_goal": "Highlight just the climactic arias from my Italian opera production recording with Italian subtitles."},
    {**_make("Russian-ballet performance", "principal-dancer-solo", "Russian"),
     "user_goal": "Cut my Russian-ballet performance to just the principal dancer's solos with Russian subtitles."},
    {**_make("Mandarin variety show", "guest-performance", "Mandarin"),
     "user_goal": "Pull just the guest-performance segments from my Mandarin variety show with Mandarin subtitles."},
    {**_make("Hindi cricket Test match", "boundary-and-wicket", "Hindi"),
     "user_goal": "Highlight just the boundaries and wickets from my Hindi-commentary cricket Test match with Hindi subtitles."},
    {**_make("Korean K-drama episode", "main-romance-confession", "Korean"),
     "user_goal": "Cut my Korean K-drama episode to just the main romance-confession scenes with Korean subtitles."},
    {**_make("Cantonese cooking competition", "elimination-moment", "Cantonese"),
     "user_goal": "Pull just the elimination moments from my Cantonese cooking competition with Cantonese subtitles."},
    {**_make("Arabic news debate", "key-rebuttal", "Arabic"),
     "user_goal": "Highlight just the key rebuttals from my Arabic news debate with Arabic subtitles."},
    {**_make("Turkish soap-opera season", "season-cliffhanger", "Turkish"),
     "user_goal": "Cut my Turkish soap-opera season recording to just the cliffhanger moments with Turkish subtitles."},
    {**_make("Vietnamese cooking show", "judges-tasting", "Vietnamese"),
     "user_goal": "Pull just the judges'-tasting moments from my Vietnamese cooking show with Vietnamese subtitles."},
    {**_make("Thai boxing match", "knockdown-moment", "Thai"),
     "user_goal": "Highlight just the knockdown moments from my Thai boxing match with Thai subtitles."},
    {**_make("Polish parliamentary session", "vote-tally-moment", "Polish"),
     "user_goal": "Cut my Polish parliamentary session recording to just the vote-tally moments with Polish subtitles."},
    {**_make("Portuguese soccer match", "goal-and-save", "Portuguese"),
     "user_goal": "Pull just the goals and saves from my Portuguese soccer match with Portuguese subtitles."},
    {**_make("Dutch art-fair tour", "artist-introduction", "Dutch"),
     "user_goal": "Highlight just the artist-introduction segments from my Dutch art-fair tour with Dutch subtitles."},
    {**_make("Swedish ice-hockey final", "goal-and-fight", "Swedish"),
     "user_goal": "Cut my Swedish ice-hockey final to just the goals and fights with Swedish subtitles."},
    {**_make("Norwegian-fjord travel show", "ferry-arrival", "Norwegian"),
     "user_goal": "Pull just the ferry-arrival moments from my Norwegian-fjord travel show with Norwegian subtitles."},
    {**_make("Finnish-forest hiking show", "wildlife-sighting", "Finnish"),
     "user_goal": "Highlight just the wildlife-sighting moments from my Finnish-forest hiking show with Finnish subtitles."},
    {**_make("Hebrew rabbinical seminar", "key-question-and-answer", "Hebrew"),
     "user_goal": "Cut my Hebrew rabbinical seminar to just the key Q&A exchanges with Hebrew subtitles."},
    {**_make("Persian poetry recital", "encore-recitation", "Persian"),
     "user_goal": "Pull just the encore-recitation segments from my Persian poetry recital with Persian subtitles."},
    {**_make("Bengali theatre performance", "act-finale", "Bengali"),
     "user_goal": "Highlight just the act-finale moments from my Bengali theatre performance with Bengali subtitles."},
    {**_make("Tamil dance competition", "winner-routine", "Tamil"),
     "user_goal": "Cut my Tamil dance competition to just the winning routines with Tamil subtitles."},
    {**_make("Yoruba elder-council meeting", "decisive-vote", "Yoruba"),
     "user_goal": "Pull just the decisive-vote moments from my Yoruba elder-council meeting with Yoruba subtitles."},
    {**_make("Swahili Mombasa-port news", "vessel-arrival-announcement", "Swahili"),
     "user_goal": "Highlight just the vessel-arrival announcements from my Swahili Mombasa-port news with Swahili subtitles."},
    {**_make("Tagalog noontime variety show", "celebrity-interview", "Tagalog"),
     "user_goal": "Cut my Tagalog noontime variety show to just the celebrity-interview segments with Tagalog subtitles."},
    {**_make("Indonesian wayang performance", "battle-scene", "Indonesian"),
     "user_goal": "Pull just the battle scenes from my Indonesian wayang performance with Indonesian subtitles."},
    {**_make("Greek-island wedding-festival", "dance-circle-moment", "Greek"),
     "user_goal": "Highlight just the dance-circle moments from my Greek-island wedding-festival with Greek subtitles."},
]
