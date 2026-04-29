"""Shape: highlight_bilingual_music —
    IntakeVideo → VideoAnalysis → Highlight → Transcription → Translation → Music → AudioMix → Compositor.

Long video + highlight cut + bilingual subs (source + translated) + BGM.
"""
from __future__ import annotations

SAMPLES: list[dict] = [
    {
        "user_goal": "From this 2-hour Japanese tennis match, pull the best rallies, add Japanese + English bilingual subtitles, and add an epic orchestral BGM.",
        "rationale": (
            "Japanese tennis match + rallies highlight + Japanese+English bilingual subs + "
            "epic orchestral BGM. IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → "
            "TranscriptionAgent (Japanese) → TranslationAgent (English) → MusicAgent (epic "
            "orchestral) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 2-hour Japanese tennis-match recording into the workspace.",
            "Analyze the match to locate the best rally / climactic moments.",
            "Extract the best rallies as highlight segments.",
            "Transcribe the Japanese announcer commentary on the rally segments into SRT.",
            "Translate the Japanese SRT segments into English subtitles.",
            "Compose an epic orchestral BGM fitting the rally highlight reel.",
            "Mix the orchestral BGM with the highlight reel's baked audio.",
            "Compose the reel with bilingual Japanese-English captions and orchestral BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "From this 3-hour Korean K-drama, pull the emotional scenes, add Korean + English bilingual subtitles, and add a melancholic piano BGM.",
        "rationale": (
            "Korean K-drama + emotional scenes highlight + Korean+English bilingual subs + "
            "melancholic piano BGM. Same 8-step flow."
        ),
        "intents": [
            "Ingest the 3-hour Korean K-drama recording into the workspace.",
            "Analyze the drama to locate the most emotional / climactic scene moments.",
            "Extract those emotional scenes as highlight segments.",
            "Transcribe the Korean dialogue on the segments into SRT.",
            "Translate the Korean SRT segments into English subtitles.",
            "Compose a melancholic piano BGM fitting the emotional highlight reel.",
            "Mix the piano BGM with the highlight reel's baked audio.",
            "Compose the reel with bilingual Korean-English captions and piano BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Pull the goals from this 2-hour Spanish soccer match, add Spanish + English bilingual captions, and add an energetic Latin-pop BGM.",
        "rationale": (
            "Spanish soccer match + goals + Spanish+English bilingual + energetic Latin-pop "
            "BGM. IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → TranscriptionAgent "
            "(Spanish) → TranslationAgent (English) → MusicAgent (Latin pop) → AudioMixAgent "
            "→ CompositorAgent."
        ),
        "intents": [
            "Ingest the 2-hour Spanish soccer match into the workspace.",
            "Analyze the match to locate goal events.",
            "Extract the goals as highlight segments.",
            "Transcribe the Spanish announcer commentary on the goal segments into SRT.",
            "Translate the Spanish SRT segments into English subtitles.",
            "Compose an energetic Latin-pop BGM fitting the goal highlight reel.",
            "Mix the Latin-pop BGM with the highlight reel's baked audio.",
            "Compose the reel with bilingual Spanish-English captions and Latin-pop BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "From this 2-hour French cooking competition, pull the plating reveals, add French + English bilingual captions, and add a smooth jazz-piano BGM.",
        "rationale": (
            "French cooking competition + plating reveals + French+English bilingual + smooth "
            "jazz-piano BGM."
        ),
        "intents": [
            "Ingest the 2-hour French cooking-competition recording into the workspace.",
            "Analyze the competition to locate plating-reveal moments.",
            "Extract the plating reveals as highlight segments.",
            "Transcribe the French chef / judge dialogue on the segments into SRT.",
            "Translate the French SRT segments into English subtitles.",
            "Compose a smooth jazz-piano BGM fitting the cooking highlight reel.",
            "Mix the jazz BGM with the highlight reel's baked audio.",
            "Compose the reel with bilingual French-English captions and jazz BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Pull the funniest moments from this 2-hour Italian variety show, add Italian + English bilingual subs, and add a playful circus-organ BGM.",
        "rationale": (
            "Italian variety show + funniest moments + Italian+English bilingual + playful "
            "circus-organ BGM."
        ),
        "intents": [
            "Ingest the 2-hour Italian variety show into the workspace.",
            "Analyze the show to locate the funniest / biggest-laugh moments.",
            "Extract those funny moments as highlight segments.",
            "Transcribe the Italian variety dialogue on the segments into SRT.",
            "Translate the Italian SRT segments into English subtitles.",
            "Compose a playful circus-organ BGM fitting the variety highlight reel.",
            "Mix the organ BGM with the highlight reel's baked audio.",
            "Compose the reel with bilingual Italian-English captions and organ BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "From this 2-hour German Bundesliga match, pull the best plays, add German + English bilingual captions, and add an anthemic rock BGM.",
        "rationale": (
            "German Bundesliga + best plays + German+English bilingual + anthemic rock BGM."
        ),
        "intents": [
            "Ingest the 2-hour German Bundesliga match into the workspace.",
            "Analyze the match to locate the best-play moments.",
            "Extract those plays as highlight segments.",
            "Transcribe the German commentary on the segments into SRT.",
            "Translate the German SRT segments into English subtitles.",
            "Compose an anthemic rock BGM fitting the Bundesliga highlight reel.",
            "Mix the rock BGM with the highlight reel's baked audio.",
            "Compose the reel with bilingual German-English captions and rock BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "From this 3-hour Portuguese soccer broadcast, extract the goals, add Portuguese + English bilingual subs, and add a heroic cinematic BGM.",
        "rationale": (
            "Portuguese soccer broadcast + goals + Portuguese+English bilingual + heroic "
            "cinematic BGM."
        ),
        "intents": [
            "Ingest the 3-hour Portuguese soccer-commentary broadcast into the workspace.",
            "Analyze the broadcast to locate goal events.",
            "Extract the goals as highlight segments.",
            "Transcribe the Portuguese commentary on the segments into SRT.",
            "Translate the Portuguese SRT segments into English subtitles.",
            "Compose a heroic cinematic BGM fitting the goal highlight reel.",
            "Mix the cinematic BGM with the highlight reel's baked audio.",
            "Compose the reel with bilingual Portuguese-English captions and cinematic BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "From this 2-hour Russian circus performance, pull the stunts, add Russian + English bilingual captions, and add a whimsical carnival BGM.",
        "rationale": (
            "Russian circus performance + stunts + Russian+English bilingual + whimsical "
            "carnival BGM."
        ),
        "intents": [
            "Ingest the 2-hour Russian circus-performance recording into the workspace.",
            "Analyze the performance to locate signature stunt moments.",
            "Extract the best stunts as highlight segments.",
            "Transcribe the Russian ringmaster announcements on the segments into SRT.",
            "Translate the Russian SRT segments into English subtitles.",
            "Compose a whimsical carnival BGM fitting the circus highlight reel.",
            "Mix the carnival BGM with the highlight reel's baked audio.",
            "Compose the reel with bilingual Russian-English captions and carnival BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Pull the dance moments from this 2-hour Latin-America dance show, add Spanish + English bilingual captions, and add an infectious reggaeton BGM.",
        "rationale": (
            "Latin-America dance show + dance moments + Spanish+English bilingual + infectious "
            "reggaeton BGM."
        ),
        "intents": [
            "Ingest the 2-hour Latin-America dance-show recording into the workspace.",
            "Analyze the show to locate the best dance-performance moments.",
            "Extract the dance moments as highlight segments.",
            "Transcribe the Spanish host / dancer dialogue on the segments into SRT.",
            "Translate the Spanish SRT segments into English subtitles.",
            "Compose an infectious reggaeton BGM fitting the dance highlight reel.",
            "Mix the reggaeton BGM with the highlight reel's baked audio.",
            "Compose the reel with bilingual Spanish-English captions and reggaeton BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "From this 2-hour Turkish drama, pull the emotional scenes, add Turkish + English bilingual subs, and add a haunting string-quartet BGM.",
        "rationale": (
            "Turkish drama + emotional scenes + Turkish+English bilingual + haunting "
            "string-quartet BGM."
        ),
        "intents": [
            "Ingest the 2-hour Turkish drama recording into the workspace.",
            "Analyze the drama to locate emotional-peak moments.",
            "Extract those emotional moments as highlight segments.",
            "Transcribe the Turkish dialogue on the segments into SRT.",
            "Translate the Turkish SRT segments into English subtitles.",
            "Compose a haunting string-quartet BGM fitting the emotional highlight reel.",
            "Mix the quartet BGM with the highlight reel's baked audio.",
            "Compose the reel with bilingual Turkish-English captions and string-quartet BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "From this 2-hour Arabic news-panel discussion, pull the debate heat moments, add Arabic + English bilingual captions, and add a tense electronic BGM.",
        "rationale": (
            "Arabic news panel + heated debate moments + Arabic+English bilingual + tense "
            "electronic BGM."
        ),
        "intents": [
            "Ingest the 2-hour Arabic news-panel discussion into the workspace.",
            "Analyze the discussion to locate the key debate-heating moments.",
            "Extract the debate moments as highlight segments.",
            "Transcribe the Arabic panelist debate on the segments into SRT.",
            "Translate the Arabic SRT segments into English subtitles.",
            "Compose a tense electronic BGM fitting the debate highlight reel.",
            "Mix the electronic BGM with the highlight reel's baked audio.",
            "Compose the reel with bilingual Arabic-English captions and electronic BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Pull the best moments from this 3-hour Hindi cricket match, add Hindi + English bilingual subs, and add an energetic bhangra BGM.",
        "rationale": (
            "Hindi cricket match + best moments + Hindi+English bilingual + energetic bhangra "
            "BGM."
        ),
        "intents": [
            "Ingest the 3-hour Hindi cricket-match into the workspace.",
            "Analyze the match to locate the best cricket play moments.",
            "Extract the best plays as highlight segments.",
            "Transcribe the Hindi cricket commentary on the segments into SRT.",
            "Translate the Hindi SRT segments into English subtitles.",
            "Compose an energetic bhangra BGM fitting the cricket highlight reel.",
            "Mix the bhangra BGM with the highlight reel's baked audio.",
            "Compose the reel with bilingual Hindi-English captions and bhangra BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "From this 2-hour Vietnamese travel documentary, pull the scenic highlights, add Vietnamese + English bilingual captions, and add a melodic bamboo-flute BGM.",
        "rationale": (
            "Vietnamese travel doc + scenic highlights + Vietnamese+English bilingual + "
            "melodic bamboo-flute BGM."
        ),
        "intents": [
            "Ingest the 2-hour Vietnamese travel-documentary into the workspace.",
            "Analyze the documentary to locate the most scenic highlight moments.",
            "Extract those scenic moments as highlight segments.",
            "Transcribe the Vietnamese narration on the segments into SRT.",
            "Translate the Vietnamese SRT segments into English subtitles.",
            "Compose a melodic bamboo-flute BGM fitting the travel highlight reel.",
            "Mix the flute BGM with the highlight reel's baked audio.",
            "Compose the reel with bilingual Vietnamese-English captions and flute BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Pull the ceremony climax moments from this 1-hour Thai wedding, add Thai + English bilingual subs, and add a traditional pinpeat BGM.",
        "rationale": (
            "Thai wedding + ceremony climax + Thai+English bilingual + traditional pinpeat BGM."
        ),
        "intents": [
            "Ingest the hour-long Thai wedding-ceremony recording into the workspace.",
            "Analyze the ceremony to locate climactic ritual moments.",
            "Extract those ceremony moments as highlight segments.",
            "Transcribe the Thai ceremony dialogue on the segments into SRT.",
            "Translate the Thai SRT segments into English subtitles.",
            "Compose a traditional pinpeat BGM fitting the Thai ceremony.",
            "Mix the pinpeat BGM with the highlight reel's baked audio.",
            "Compose the reel with bilingual Thai-English captions and pinpeat BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "From this 2-hour Dutch tulip festival, pull the parade highlights, add Dutch + English bilingual captions, and add a cheerful oompah-band BGM.",
        "rationale": (
            "Dutch tulip festival + parade highlights + Dutch+English bilingual + cheerful "
            "oompah-band BGM."
        ),
        "intents": [
            "Ingest the 2-hour Dutch tulip-festival recording into the workspace.",
            "Analyze the festival to locate parade-highlight moments.",
            "Extract the parade highlights as segments.",
            "Transcribe the Dutch festival announcer on the segments into SRT.",
            "Translate the Dutch SRT segments into English subtitles.",
            "Compose a cheerful oompah-band BGM fitting the tulip-festival parade.",
            "Mix the oompah BGM with the highlight reel's baked audio.",
            "Compose the reel with bilingual Dutch-English captions and oompah BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Pull the signature dance moves from this 1-hour Polish folk-dance competition, add Polish + English bilingual subs, and add a lively polka BGM.",
        "rationale": (
            "Polish folk-dance + signature moves + Polish+English bilingual + lively polka BGM."
        ),
        "intents": [
            "Ingest the hour-long Polish folk-dance competition recording into the workspace.",
            "Analyze the competition to locate the signature dance-move moments.",
            "Extract the signature moves as highlight segments.",
            "Transcribe the Polish emcee commentary on the segments into SRT.",
            "Translate the Polish SRT segments into English subtitles.",
            "Compose a lively polka BGM fitting the folk-dance highlight reel.",
            "Mix the polka BGM with the highlight reel's baked audio.",
            "Compose the reel with bilingual Polish-English captions and polka BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "From this 2-hour Indonesian Balinese dance-drama, pull the ceremonial moments, add Indonesian + English bilingual captions, and add a traditional gamelan BGM.",
        "rationale": (
            "Indonesian Balinese dance-drama + ceremonial moments + Indonesian+English "
            "bilingual + traditional gamelan BGM."
        ),
        "intents": [
            "Ingest the 2-hour Indonesian Balinese dance-drama recording into the workspace.",
            "Analyze the drama to locate ceremonial / ritual-peak moments.",
            "Extract those ceremonial moments as highlight segments.",
            "Transcribe the Indonesian narration on the segments into SRT.",
            "Translate the Indonesian SRT segments into English subtitles.",
            "Compose a traditional gamelan BGM fitting the Balinese dance-drama.",
            "Mix the gamelan BGM with the highlight reel's baked audio.",
            "Compose the reel with bilingual Indonesian-English captions and gamelan BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Pull the best baking moments from this 2-hour Swedish bakery documentary, add Swedish + English bilingual captions, and add a cozy folk-accordion BGM.",
        "rationale": (
            "Swedish bakery doc + best baking + Swedish+English bilingual + cozy folk-accordion "
            "BGM."
        ),
        "intents": [
            "Ingest the 2-hour Swedish bakery-documentary into the workspace.",
            "Analyze the documentary to locate the most-impressive baking moments.",
            "Extract those baking moments as highlight segments.",
            "Transcribe the Swedish baker's narration on the segments into SRT.",
            "Translate the Swedish SRT segments into English subtitles.",
            "Compose a cozy folk-accordion BGM fitting the Swedish bakery mood.",
            "Mix the accordion BGM with the highlight reel's baked audio.",
            "Compose the reel with bilingual Swedish-English captions and accordion BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "From this 2-hour Greek folk-music concert, pull the climax songs, add Greek + English bilingual subs, and add an atmospheric bouzouki BGM.",
        "rationale": (
            "Greek folk-music concert + climax songs + Greek+English bilingual + atmospheric "
            "bouzouki BGM."
        ),
        "intents": [
            "Ingest the 2-hour Greek folk-music concert recording into the workspace.",
            "Analyze the concert to locate the most-intense / climax song performances.",
            "Extract those climax songs as highlight segments.",
            "Transcribe the Greek lyrics and MC announcements on the segments into SRT.",
            "Translate the Greek SRT segments into English subtitles.",
            "Compose an atmospheric bouzouki BGM fitting the Greek folk reel.",
            "Mix the bouzouki BGM with the highlight reel's baked audio.",
            "Compose the reel with bilingual Greek-English captions and bouzouki BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Pull the best moments from this 2-hour Chinese talk show with international guests, add Chinese + English bilingual captions, and add a sparkling electro-pop BGM.",
        "rationale": (
            "Chinese talk show + best moments + Chinese+English bilingual + sparkling "
            "electro-pop BGM."
        ),
        "intents": [
            "Ingest the 2-hour Chinese talk-show recording into the workspace.",
            "Analyze the show to locate the best / most-entertaining moments.",
            "Extract those moments as highlight segments.",
            "Transcribe the Chinese host / guest dialogue on the segments into SRT.",
            "Translate the Chinese SRT segments into English subtitles.",
            "Compose a sparkling electro-pop BGM fitting the talk-show vibe.",
            "Mix the electro-pop BGM with the highlight reel's baked audio.",
            "Compose the reel with bilingual Chinese-English captions and electro-pop BGM overlaid on the cuts.",
        ],
    },
]
