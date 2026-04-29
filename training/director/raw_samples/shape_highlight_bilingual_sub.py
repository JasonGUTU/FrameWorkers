"""Shape: highlight_bilingual_sub — IntakeVideo → VideoAnalysis → Highlight → Transcription → Translation → Compositor.

Long video + highlight-cut + bilingual subs (source + translated language).
"""
from __future__ import annotations

SAMPLES: list[dict] = [
    {
        "user_goal": "From this 2-hour Japanese anime-convention panel, pull the funniest moments and add Japanese + English bilingual subtitles.",
        "rationale": (
            "Japanese anime-convention panel + funniest moments highlight + Japanese+English "
            "bilingual subs. IntakeVideoAgent → VideoAnalysisAgent (laugh spikes) → "
            "HighlightAgent → TranscriptionAgent (Japanese) → TranslationAgent (to English) "
            "→ CompositorAgent (bilingual burn-in)."
        ),
        "intents": [
            "Ingest the 2-hour Japanese anime-convention panel into the workspace.",
            "Analyze the panel to locate the funniest / biggest-laugh moments.",
            "Extract those funny moments as highlight segments.",
            "Transcribe the Japanese panelist dialogue on the segments into SRT.",
            "Translate the Japanese SRT segments into English subtitles.",
            "Compose the highlight reel with bilingual Japanese-English captions burned onto the cuts.",
        ],
    },
    {
        "user_goal": "From this 90-minute Spanish soccer match, pull the goals and add Spanish + English bilingual captions.",
        "rationale": (
            "Spanish soccer match + goals highlight + Spanish+English bilingual captions. "
            "IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → TranscriptionAgent "
            "(Spanish) → TranslationAgent (to English) → CompositorAgent (bilingual burn-in)."
        ),
        "intents": [
            "Ingest the 90-minute Spanish soccer match into the workspace.",
            "Analyze the match to locate goal events.",
            "Extract the goals as highlight segments.",
            "Transcribe the Spanish announcer commentary on the goals into SRT.",
            "Translate the Spanish SRT segments into English subtitles.",
            "Compose the goal highlight reel with bilingual Spanish-English captions burned onto the cuts.",
        ],
    },
    {
        "user_goal": "Please pull the best moments from this 3-hour Korean K-drama and add Korean + English bilingual subtitles.",
        "rationale": (
            "Korean K-drama + best-moments highlight + Korean+English bilingual subs. "
            "IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → TranscriptionAgent "
            "(Korean) → TranslationAgent (to English) → CompositorAgent."
        ),
        "intents": [
            "Ingest the 3-hour Korean K-drama recording into the workspace.",
            "Analyze the drama to locate the best / most-climactic scene moments.",
            "Extract those best-moment scenes as highlight segments.",
            "Transcribe the Korean dialogue on the highlight segments into SRT.",
            "Translate the Korean SRT segments into English subtitles.",
            "Compose the highlight reel with bilingual Korean-English captions burned onto the cuts.",
        ],
    },
    {
        "user_goal": "From this 2-hour French cooking-competition, pull the plating reveals and add French + English bilingual captions.",
        "rationale": (
            "French cooking competition + plating-reveals highlight + French+English bilingual "
            "captions. IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → "
            "TranscriptionAgent (French) → TranslationAgent (to English) → CompositorAgent."
        ),
        "intents": [
            "Ingest the 2-hour French cooking-competition recording into the workspace.",
            "Analyze the competition to locate plating-reveal moments.",
            "Extract the plating reveals as highlight segments.",
            "Transcribe the French chef / judge dialogue on the reveal segments into SRT.",
            "Translate the French SRT segments into English subtitles.",
            "Compose the highlight reel with bilingual French-English captions burned onto the cuts.",
        ],
    },
    {
        "user_goal": "Please pull the celebrity-guest's best moments from this 1-hour Chinese talk-show and add Chinese + English bilingual captions.",
        "rationale": (
            "Chinese talk show + celebrity-guest highlight + Chinese+English bilingual captions. "
            "IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → TranscriptionAgent "
            "(Chinese) → TranslationAgent (to English) → CompositorAgent."
        ),
        "intents": [
            "Ingest the hour-long Chinese talk-show episode into the workspace.",
            "Analyze the episode to locate the celebrity guest's standout moments.",
            "Extract those guest moments as highlight segments.",
            "Transcribe the Chinese guest / host dialogue on the segments into SRT.",
            "Translate the Chinese SRT segments into English subtitles.",
            "Compose the highlight reel with bilingual Chinese-English captions burned onto the cuts.",
        ],
    },
    {
        "user_goal": "Pull the funniest moments from this 2-hour Italian variety show and add Italian + English bilingual subtitles.",
        "rationale": (
            "Italian variety show + funniest moments highlight + Italian+English bilingual "
            "subs. IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → TranscriptionAgent "
            "(Italian) → TranslationAgent (to English) → CompositorAgent."
        ),
        "intents": [
            "Ingest the 2-hour Italian variety show into the workspace.",
            "Analyze the show to locate the funniest / biggest-laugh moments.",
            "Extract those funny moments as highlight segments.",
            "Transcribe the Italian variety-show dialogue on the segments into SRT.",
            "Translate the Italian SRT segments into English subtitles.",
            "Compose the highlight reel with bilingual Italian-English captions burned onto the cuts.",
        ],
    },
    {
        "user_goal": "From this 2-hour German Bundesliga match, pull the best plays and add German + English bilingual captions.",
        "rationale": (
            "German Bundesliga match + best-plays highlight + German+English bilingual "
            "captions. IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → "
            "TranscriptionAgent (German) → TranslationAgent (to English) → CompositorAgent."
        ),
        "intents": [
            "Ingest the 2-hour German Bundesliga match into the workspace.",
            "Analyze the match to locate the best-play moments.",
            "Extract those plays as highlight segments.",
            "Transcribe the German commentary on the segments into SRT.",
            "Translate the German SRT segments into English subtitles.",
            "Compose the highlight reel with bilingual German-English captions burned onto the cuts.",
        ],
    },
    {
        "user_goal": "Please pull the best stunts from this 2-hour Russian circus performance and add Russian + English bilingual captions.",
        "rationale": (
            "Russian circus performance + best-stunts highlight + Russian+English bilingual "
            "captions. IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → "
            "TranscriptionAgent (Russian) → TranslationAgent (to English) → CompositorAgent."
        ),
        "intents": [
            "Ingest the 2-hour Russian circus-performance recording into the workspace.",
            "Analyze the performance to locate signature stunt moments.",
            "Extract the best stunts as highlight segments.",
            "Transcribe the Russian ringmaster announcements on the segments into SRT.",
            "Translate the Russian SRT segments into English subtitles.",
            "Compose the highlight reel with bilingual Russian-English captions burned onto the cuts.",
        ],
    },
    {
        "user_goal": "From this 3-hour Portuguese soccer-commentary broadcast, extract the goals and add Portuguese + English bilingual subtitles.",
        "rationale": (
            "Portuguese soccer broadcast + goals highlight + Portuguese+English bilingual "
            "subs. IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → TranscriptionAgent "
            "(Portuguese) → TranslationAgent (to English) → CompositorAgent."
        ),
        "intents": [
            "Ingest the 3-hour Portuguese soccer-commentary broadcast into the workspace.",
            "Analyze the broadcast to locate goal events.",
            "Extract the goals as highlight segments.",
            "Transcribe the Portuguese commentary on the goal segments into SRT.",
            "Translate the Portuguese SRT segments into English subtitles.",
            "Compose the highlight reel with bilingual Portuguese-English captions burned onto the cuts.",
        ],
    },
    {
        "user_goal": "Pull the dance-moments from this 2-hour Latin-America dance-show and add Spanish + English bilingual captions.",
        "rationale": (
            "Latin-America dance show + dance-moments highlight + Spanish+English bilingual "
            "captions. IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → "
            "TranscriptionAgent (Spanish) → TranslationAgent (to English) → CompositorAgent."
        ),
        "intents": [
            "Ingest the 2-hour Latin-America dance-show recording into the workspace.",
            "Analyze the show to locate the best dance-performance moments.",
            "Extract the dance moments as highlight segments.",
            "Transcribe the Spanish host / dancer dialogue on the segments into SRT.",
            "Translate the Spanish SRT segments into English subtitles.",
            "Compose the highlight reel with bilingual Spanish-English captions burned onto the cuts.",
        ],
    },
    {
        "user_goal": "Please pull the emotional moments from this 2-hour Turkish drama and add Turkish + English bilingual subtitles.",
        "rationale": (
            "Turkish drama + emotional moments highlight + Turkish+English bilingual subs. "
            "IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → TranscriptionAgent "
            "(Turkish) → TranslationAgent (to English) → CompositorAgent."
        ),
        "intents": [
            "Ingest the 2-hour Turkish drama recording into the workspace.",
            "Analyze the drama to locate emotional-peak moments.",
            "Extract those emotional moments as highlight segments.",
            "Transcribe the Turkish dialogue on the segments into SRT.",
            "Translate the Turkish SRT segments into English subtitles.",
            "Compose the highlight reel with bilingual Turkish-English captions burned onto the cuts.",
        ],
    },
    {
        "user_goal": "From this 2-hour Arabic news-panel discussion, pull the key debate moments and add Arabic + English bilingual captions.",
        "rationale": (
            "Arabic news panel + key debate moments highlight + Arabic+English bilingual "
            "captions. IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → "
            "TranscriptionAgent (Arabic) → TranslationAgent (to English) → CompositorAgent."
        ),
        "intents": [
            "Ingest the 2-hour Arabic news-panel discussion into the workspace.",
            "Analyze the discussion to locate the key debate-heating moments.",
            "Extract the debate moments as highlight segments.",
            "Transcribe the Arabic panelist debate on the segments into SRT.",
            "Translate the Arabic SRT segments into English subtitles.",
            "Compose the highlight reel with bilingual Arabic-English captions burned onto the cuts.",
        ],
    },
    {
        "user_goal": "Please extract the best moments from this 3-hour Hindi cricket match and add Hindi + English bilingual subtitles.",
        "rationale": (
            "Hindi cricket match + best-moments highlight + Hindi+English bilingual subs. "
            "IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → TranscriptionAgent "
            "(Hindi) → TranslationAgent (to English) → CompositorAgent."
        ),
        "intents": [
            "Ingest the 3-hour Hindi cricket match into the workspace.",
            "Analyze the match to locate the best cricket play moments.",
            "Extract the best plays as highlight segments.",
            "Transcribe the Hindi cricket commentary on the segments into SRT.",
            "Translate the Hindi SRT segments into English subtitles.",
            "Compose the highlight reel with bilingual Hindi-English captions burned onto the cuts.",
        ],
    },
    {
        "user_goal": "From this 2-hour Vietnamese travel-documentary, pull the best scenic moments and add Vietnamese + English bilingual captions.",
        "rationale": (
            "Vietnamese travel doc + best-scenic highlight + Vietnamese+English bilingual "
            "captions. IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → "
            "TranscriptionAgent (Vietnamese) → TranslationAgent (to English) → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 2-hour Vietnamese travel-documentary into the workspace.",
            "Analyze the documentary to locate the most scenic / highlight moments.",
            "Extract those scenic moments as highlight segments.",
            "Transcribe the Vietnamese narration on the segments into SRT.",
            "Translate the Vietnamese SRT segments into English subtitles.",
            "Compose the highlight reel with bilingual Vietnamese-English captions burned onto the cuts.",
        ],
    },
    {
        "user_goal": "Please pull the ceremony-climax moments from this 1-hour Thai wedding ceremony and add Thai + English bilingual subtitles.",
        "rationale": (
            "Thai wedding ceremony + climax moments highlight + Thai+English bilingual subs. "
            "IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → TranscriptionAgent "
            "(Thai) → TranslationAgent (to English) → CompositorAgent."
        ),
        "intents": [
            "Ingest the hour-long Thai wedding-ceremony recording into the workspace.",
            "Analyze the ceremony to locate climactic / ritual-peak moments.",
            "Extract those ceremony moments as highlight segments.",
            "Transcribe the Thai ceremony dialogue on the segments into SRT.",
            "Translate the Thai SRT segments into English subtitles.",
            "Compose the highlight reel with bilingual Thai-English captions burned onto the cuts.",
        ],
    },
    {
        "user_goal": "From this 2-hour Dutch tulip-festival, pull the parade highlights and add Dutch + English bilingual captions.",
        "rationale": (
            "Dutch tulip festival + parade highlights + Dutch+English bilingual captions. "
            "IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → TranscriptionAgent "
            "(Dutch) → TranslationAgent (to English) → CompositorAgent."
        ),
        "intents": [
            "Ingest the 2-hour Dutch tulip-festival recording into the workspace.",
            "Analyze the festival to locate parade-highlight moments.",
            "Extract the parade highlights as segments.",
            "Transcribe the Dutch festival announcer on the segments into SRT.",
            "Translate the Dutch SRT segments into English subtitles.",
            "Compose the highlight reel with bilingual Dutch-English captions burned onto the cuts.",
        ],
    },
    {
        "user_goal": "Please pull the signature-moves from this 1-hour Polish folk-dance competition and add Polish + English bilingual subtitles.",
        "rationale": (
            "Polish folk-dance competition + signature-moves highlight + Polish+English "
            "bilingual subs. IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → "
            "TranscriptionAgent (Polish) → TranslationAgent (to English) → CompositorAgent."
        ),
        "intents": [
            "Ingest the hour-long Polish folk-dance competition recording into the workspace.",
            "Analyze the competition to locate the signature dance-move moments.",
            "Extract the signature moves as highlight segments.",
            "Transcribe the Polish emcee commentary on the segments into SRT.",
            "Translate the Polish SRT segments into English subtitles.",
            "Compose the highlight reel with bilingual Polish-English captions burned onto the cuts.",
        ],
    },
    {
        "user_goal": "From this 2-hour Indonesian Balinese dance-drama, pull the ceremonial moments and add Indonesian + English bilingual captions.",
        "rationale": (
            "Indonesian Balinese dance-drama + ceremonial-moments highlight + Indonesian+English "
            "bilingual captions. IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → "
            "TranscriptionAgent (Indonesian) → TranslationAgent (to English) → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 2-hour Indonesian Balinese dance-drama recording into the workspace.",
            "Analyze the drama to locate ceremonial / ritual-peak moments.",
            "Extract those ceremonial moments as highlight segments.",
            "Transcribe the Indonesian narration on the segments into SRT.",
            "Translate the Indonesian SRT segments into English subtitles.",
            "Compose the highlight reel with bilingual Indonesian-English captions burned onto the cuts.",
        ],
    },
    {
        "user_goal": "Pull the best bread-baking moments from this 2-hour Swedish bakery-documentary and add Swedish + English bilingual captions.",
        "rationale": (
            "Swedish bakery documentary + best-baking moments + Swedish+English bilingual "
            "captions. IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → "
            "TranscriptionAgent (Swedish) → TranslationAgent (to English) → CompositorAgent."
        ),
        "intents": [
            "Ingest the 2-hour Swedish bakery-documentary into the workspace.",
            "Analyze the documentary to locate the most-impressive baking moments.",
            "Extract those baking moments as highlight segments.",
            "Transcribe the Swedish baker's narration on the segments into SRT.",
            "Translate the Swedish SRT segments into English subtitles.",
            "Compose the highlight reel with bilingual Swedish-English captions burned onto the cuts.",
        ],
    },
    {
        "user_goal": "From this 2-hour Greek folk-music concert, pull the climax songs and add Greek + English bilingual subtitles.",
        "rationale": (
            "Greek folk-music concert + climax-songs highlight + Greek+English bilingual subs. "
            "IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → TranscriptionAgent "
            "(Greek) → TranslationAgent (to English) → CompositorAgent."
        ),
        "intents": [
            "Ingest the 2-hour Greek folk-music concert recording into the workspace.",
            "Analyze the concert to locate the most-intense / climax song performances.",
            "Extract those climax songs as highlight segments.",
            "Transcribe the Greek lyrics and MC announcements on the segments into SRT.",
            "Translate the Greek SRT segments into English subtitles.",
            "Compose the highlight reel with bilingual Greek-English captions burned onto the cuts.",
        ],
    },
]
