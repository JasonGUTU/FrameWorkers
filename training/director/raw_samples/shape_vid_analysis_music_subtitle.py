"""Shape: vid_analysis_music_subtitle —
    IntakeVideo → VideoAnalysis → Transcription → Music → AudioMix → Compositor.

User uploaded a video, asks to analyze it + add subtitles + swap in BGM.
NOTE: eval GT has 7 slots with 4 set-slot positions spanning only 3
distinct agents — one slot is unreachable without duplication.
Training canonical is the logical 6-step chain.
"""
from __future__ import annotations

SAMPLES: list[dict] = [
    {
        "user_goal": "Please analyze this mini-drama clip, add English subtitles from the dialogue, and swap in a gentle piano BGM.",
        "rationale": (
            "User uploaded mini-drama clip, asks for analysis + English subtitles (monolingual) "
            "+ gentle piano BGM. IntakeVideoAgent ingests. VideoAnalysisAgent parses the clip "
            "for dialogue / scene structure. TranscriptionAgent transcribes the English "
            "dialogue. MusicAgent composes the gentle piano cue. AudioMixAgent mixes BGM with "
            "dialogue audio. CompositorAgent burns English SRT and muxes the mixed audio. "
            "Reject TranslationAgent (monolingual), AmbienceAgent (no ambient request), "
            "HighlightAgent (no trimming), StyleTransferAgent (no restyle), VideoExtendAgent "
            "(no length change)."
        ),
        "intents": [
            "Ingest the mini-drama clip into the workspace.",
            "Analyze the clip for dialogue structure and scene content.",
            "Transcribe the English dialogue into timestamped SRT segments.",
            "Compose a gentle piano BGM fitting the mini-drama mood.",
            "Mix the piano BGM with the dialogue audio.",
            "Compose the clip with English captions and mixed piano BGM overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Analyze this Chinese mini-drama, add Chinese subtitles, and swap in a melancholic erhu BGM.",
        "rationale": (
            "Chinese mini-drama + analysis + Chinese (monolingual) subtitles + melancholic erhu "
            "BGM. IntakeVideoAgent → VideoAnalysisAgent → TranscriptionAgent (Chinese) → "
            "MusicAgent (melancholic erhu) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the Chinese mini-drama clip into the workspace.",
            "Analyze the clip for dialogue structure and scene content.",
            "Transcribe the Chinese dialogue into timestamped SRT segments.",
            "Compose a melancholic erhu BGM fitting the Chinese mini-drama mood.",
            "Mix the erhu BGM with the dialogue audio.",
            "Compose the clip with Chinese captions and mixed erhu BGM overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Please analyze this Spanish telenovela clip, add Spanish captions, and swap in a romantic guitar BGM.",
        "rationale": (
            "Spanish telenovela + analysis + Spanish (monolingual) captions + romantic guitar "
            "BGM. IntakeVideoAgent → VideoAnalysisAgent → TranscriptionAgent (Spanish) → "
            "MusicAgent (romantic guitar) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the Spanish telenovela clip into the workspace.",
            "Analyze the clip for dialogue structure and romantic scene content.",
            "Transcribe the Spanish dialogue into timestamped SRT segments.",
            "Compose a romantic guitar BGM fitting the telenovela mood.",
            "Mix the guitar BGM with the dialogue audio.",
            "Compose the clip with Spanish captions and mixed guitar BGM overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Analyze this Korean short-drama clip, add Korean subtitles, and swap in a sparkling K-pop instrumental BGM.",
        "rationale": (
            "Korean short-drama + analysis + Korean subtitles + sparkling K-pop instrumental. "
            "IntakeVideoAgent → VideoAnalysisAgent → TranscriptionAgent (Korean) → MusicAgent "
            "(sparkling K-pop) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the Korean short-drama clip into the workspace.",
            "Analyze the clip for dialogue structure and scene content.",
            "Transcribe the Korean dialogue into timestamped SRT segments.",
            "Compose a sparkling K-pop instrumental BGM fitting the drama vibe.",
            "Mix the K-pop BGM with the dialogue audio.",
            "Compose the clip with Korean captions and mixed K-pop BGM overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Please analyze this French romantic-film clip, add French subtitles, and swap in a mellow accordion BGM.",
        "rationale": (
            "French romantic-film + analysis + French subtitles + mellow accordion BGM. "
            "IntakeVideoAgent → VideoAnalysisAgent → TranscriptionAgent (French) → MusicAgent "
            "(mellow accordion) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the French romantic-film clip into the workspace.",
            "Analyze the clip for dialogue structure and romantic scene content.",
            "Transcribe the French dialogue into timestamped SRT segments.",
            "Compose a mellow accordion BGM fitting the French romantic mood.",
            "Mix the accordion BGM with the dialogue audio.",
            "Compose the clip with French captions and mixed accordion BGM overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Analyze this Japanese drama clip, add Japanese subtitles, and swap in a dramatic strings BGM.",
        "rationale": (
            "Japanese drama + analysis + Japanese subtitles + dramatic strings BGM. "
            "IntakeVideoAgent → VideoAnalysisAgent → TranscriptionAgent (Japanese) → "
            "MusicAgent (dramatic strings) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the Japanese drama clip into the workspace.",
            "Analyze the clip for dialogue structure and scene content.",
            "Transcribe the Japanese dialogue into timestamped SRT segments.",
            "Compose a dramatic strings BGM fitting the Japanese drama tone.",
            "Mix the strings BGM with the dialogue audio.",
            "Compose the clip with Japanese captions and mixed strings BGM overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Please analyze this Italian family-drama clip, add Italian captions, and swap in a warm classical-guitar BGM.",
        "rationale": (
            "Italian family-drama + analysis + Italian captions + warm classical-guitar BGM. "
            "IntakeVideoAgent → VideoAnalysisAgent → TranscriptionAgent (Italian) → MusicAgent "
            "(warm classical guitar) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the Italian family-drama clip into the workspace.",
            "Analyze the clip for dialogue structure and family-scene content.",
            "Transcribe the Italian dialogue into timestamped SRT segments.",
            "Compose a warm classical-guitar BGM fitting the Italian family-drama mood.",
            "Mix the guitar BGM with the dialogue audio.",
            "Compose the clip with Italian captions and mixed guitar BGM overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Analyze this German crime-drama clip, add German subtitles, and swap in a tense ambient-electronic BGM.",
        "rationale": (
            "German crime-drama + analysis + German subtitles + tense ambient-electronic BGM. "
            "IntakeVideoAgent → VideoAnalysisAgent → TranscriptionAgent (German) → MusicAgent "
            "(tense ambient-electronic) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the German crime-drama clip into the workspace.",
            "Analyze the clip for dialogue structure and crime-scene content.",
            "Transcribe the German dialogue into timestamped SRT segments.",
            "Compose a tense ambient-electronic BGM fitting the crime-drama tension.",
            "Mix the ambient BGM with the dialogue audio.",
            "Compose the clip with German captions and mixed ambient BGM overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Please analyze this Hindi Bollywood-film clip, add Hindi subtitles, and swap in a festive tabla-sitar BGM.",
        "rationale": (
            "Hindi Bollywood-film + analysis + Hindi subtitles + festive tabla-sitar BGM. "
            "IntakeVideoAgent → VideoAnalysisAgent → TranscriptionAgent (Hindi) → MusicAgent "
            "(festive tabla-sitar) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the Hindi Bollywood-film clip into the workspace.",
            "Analyze the clip for dialogue structure and scene content.",
            "Transcribe the Hindi dialogue into timestamped SRT segments.",
            "Compose a festive tabla-sitar BGM fitting the Bollywood vibe.",
            "Mix the tabla-sitar BGM with the dialogue audio.",
            "Compose the clip with Hindi captions and mixed tabla-sitar BGM overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Analyze this Russian historical-drama clip, add Russian subtitles, and swap in a solemn orchestral BGM.",
        "rationale": (
            "Russian historical-drama + analysis + Russian subtitles + solemn orchestral BGM. "
            "IntakeVideoAgent → VideoAnalysisAgent → TranscriptionAgent (Russian) → MusicAgent "
            "(solemn orchestral) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the Russian historical-drama clip into the workspace.",
            "Analyze the clip for dialogue structure and historical scene content.",
            "Transcribe the Russian dialogue into timestamped SRT segments.",
            "Compose a solemn orchestral BGM fitting the historical-drama gravitas.",
            "Mix the orchestral BGM with the dialogue audio.",
            "Compose the clip with Russian captions and mixed orchestral BGM overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Please analyze this Thai ghost-story clip, add Thai captions, and swap in an eerie bamboo-flute BGM.",
        "rationale": (
            "Thai ghost-story + analysis + Thai captions + eerie bamboo-flute BGM. "
            "IntakeVideoAgent → VideoAnalysisAgent → TranscriptionAgent (Thai) → MusicAgent "
            "(eerie bamboo flute) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the Thai ghost-story clip into the workspace.",
            "Analyze the clip for dialogue structure and horror-scene content.",
            "Transcribe the Thai dialogue into timestamped SRT segments.",
            "Compose an eerie bamboo-flute BGM fitting the Thai ghost-story mood.",
            "Mix the flute BGM with the dialogue audio.",
            "Compose the clip with Thai captions and mixed flute BGM overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Analyze this Vietnamese family drama clip, add Vietnamese subtitles, and swap in a gentle dan-bau BGM.",
        "rationale": (
            "Vietnamese family drama + analysis + Vietnamese subtitles + gentle dan-bau BGM. "
            "IntakeVideoAgent → VideoAnalysisAgent → TranscriptionAgent (Vietnamese) → "
            "MusicAgent (gentle dan-bau) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the Vietnamese family-drama clip into the workspace.",
            "Analyze the clip for dialogue structure and family-scene content.",
            "Transcribe the Vietnamese dialogue into timestamped SRT segments.",
            "Compose a gentle dan-bau BGM fitting the Vietnamese family-drama mood.",
            "Mix the dan-bau BGM with the dialogue audio.",
            "Compose the clip with Vietnamese captions and mixed dan-bau BGM overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Please analyze this Arabic period-drama clip, add Arabic captions, and swap in a majestic oud-and-strings BGM.",
        "rationale": (
            "Arabic period-drama + analysis + Arabic captions + majestic oud-and-strings BGM. "
            "IntakeVideoAgent → VideoAnalysisAgent → TranscriptionAgent (Arabic) → MusicAgent "
            "(majestic oud-and-strings) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the Arabic period-drama clip into the workspace.",
            "Analyze the clip for dialogue structure and period-scene content.",
            "Transcribe the Arabic dialogue into timestamped SRT segments.",
            "Compose a majestic oud-and-strings BGM fitting the Arabic period-drama mood.",
            "Mix the oud BGM with the dialogue audio.",
            "Compose the clip with Arabic captions and mixed oud BGM overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Analyze this Portuguese fado-themed drama clip, add Portuguese subtitles, and swap in a soulful fado-guitar BGM.",
        "rationale": (
            "Portuguese fado-drama + analysis + Portuguese subtitles + soulful fado-guitar BGM. "
            "IntakeVideoAgent → VideoAnalysisAgent → TranscriptionAgent (Portuguese) → "
            "MusicAgent (soulful fado guitar) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the Portuguese fado-drama clip into the workspace.",
            "Analyze the clip for dialogue structure and fado-scene content.",
            "Transcribe the Portuguese dialogue into timestamped SRT segments.",
            "Compose a soulful fado-guitar BGM fitting the Portuguese fado mood.",
            "Mix the fado BGM with the dialogue audio.",
            "Compose the clip with Portuguese captions and mixed fado BGM overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Please analyze this Turkish soap-opera clip, add Turkish captions, and swap in a dramatic baglama BGM.",
        "rationale": (
            "Turkish soap opera + analysis + Turkish captions + dramatic baglama BGM. "
            "IntakeVideoAgent → VideoAnalysisAgent → TranscriptionAgent (Turkish) → MusicAgent "
            "(dramatic baglama) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the Turkish soap-opera clip into the workspace.",
            "Analyze the clip for dialogue structure and melodramatic scene content.",
            "Transcribe the Turkish dialogue into timestamped SRT segments.",
            "Compose a dramatic baglama BGM fitting the Turkish soap mood.",
            "Mix the baglama BGM with the dialogue audio.",
            "Compose the clip with Turkish captions and mixed baglama BGM overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Analyze this Greek mythology-drama clip, add Greek subtitles, and swap in an epic bouzouki-and-strings BGM.",
        "rationale": (
            "Greek mythology drama + analysis + Greek subtitles + epic bouzouki-and-strings BGM. "
            "IntakeVideoAgent → VideoAnalysisAgent → TranscriptionAgent (Greek) → MusicAgent "
            "(epic bouzouki-and-strings) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the Greek mythology-drama clip into the workspace.",
            "Analyze the clip for dialogue structure and mythological-scene content.",
            "Transcribe the Greek dialogue into timestamped SRT segments.",
            "Compose an epic bouzouki-and-strings BGM fitting the Greek mythology scale.",
            "Mix the bouzouki BGM with the dialogue audio.",
            "Compose the clip with Greek captions and mixed bouzouki BGM overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Please analyze this Polish historical-drama clip, add Polish subtitles, and swap in a haunting folk-violin BGM.",
        "rationale": (
            "Polish historical drama + analysis + Polish subtitles + haunting folk-violin BGM. "
            "IntakeVideoAgent → VideoAnalysisAgent → TranscriptionAgent (Polish) → MusicAgent "
            "(haunting folk violin) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the Polish historical-drama clip into the workspace.",
            "Analyze the clip for dialogue structure and historical-scene content.",
            "Transcribe the Polish dialogue into timestamped SRT segments.",
            "Compose a haunting folk-violin BGM fitting the Polish historical mood.",
            "Mix the violin BGM with the dialogue audio.",
            "Compose the clip with Polish captions and mixed violin BGM overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Analyze this Dutch mystery-drama clip, add Dutch subtitles, and swap in a brooding ambient-drone BGM.",
        "rationale": (
            "Dutch mystery drama + analysis + Dutch subtitles + brooding ambient-drone BGM. "
            "IntakeVideoAgent → VideoAnalysisAgent → TranscriptionAgent (Dutch) → MusicAgent "
            "(brooding ambient drone) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the Dutch mystery-drama clip into the workspace.",
            "Analyze the clip for dialogue structure and mystery-scene content.",
            "Transcribe the Dutch dialogue into timestamped SRT segments.",
            "Compose a brooding ambient-drone BGM fitting the mystery mood.",
            "Mix the drone BGM with the dialogue audio.",
            "Compose the clip with Dutch captions and mixed drone BGM overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Please analyze this Cantonese martial-arts-drama clip, add Cantonese captions, and swap in a traditional suona-and-drum BGM.",
        "rationale": (
            "Cantonese martial-arts drama + analysis + Cantonese captions + traditional "
            "suona-and-drum BGM. IntakeVideoAgent → VideoAnalysisAgent → TranscriptionAgent "
            "(Cantonese) → MusicAgent (suona-and-drum) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the Cantonese martial-arts drama clip into the workspace.",
            "Analyze the clip for dialogue structure and martial-arts scene content.",
            "Transcribe the Cantonese dialogue into timestamped SRT segments.",
            "Compose a traditional suona-and-drum BGM fitting the martial-arts intensity.",
            "Mix the suona BGM with the dialogue audio.",
            "Compose the clip with Cantonese captions and mixed suona BGM overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Analyze this Swahili community drama clip, add Swahili subtitles, and swap in a rhythmic mbira-and-drum BGM.",
        "rationale": (
            "Swahili community drama + analysis + Swahili subtitles + rhythmic mbira-and-drum "
            "BGM. IntakeVideoAgent → VideoAnalysisAgent → TranscriptionAgent (Swahili) → "
            "MusicAgent (mbira-and-drum) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the Swahili community-drama clip into the workspace.",
            "Analyze the clip for dialogue structure and community-scene content.",
            "Transcribe the Swahili dialogue into timestamped SRT segments.",
            "Compose a rhythmic mbira-and-drum BGM fitting the Swahili community mood.",
            "Mix the mbira BGM with the dialogue audio.",
            "Compose the clip with Swahili captions and mixed mbira BGM overlaid on the footage.",
        ],
    },
]
