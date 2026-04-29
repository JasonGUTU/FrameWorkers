"""Shape: extend_subtitle — IntakeVideo → VideoExtend → Transcription → Compositor.

User uploaded a short video, wants it extended AND subtitled (same
language).  Order: extend first (so subtitle timing covers the full
extended length), then transcribe, then compositor burns SRT.

Reject: TranslationAgent (monolingual), MusicAgent / AmbienceAgent /
AudioMixAgent (no audio overlay), StyleTransferAgent (no restyle),
VideoAnalysisAgent / HighlightAgent (no trimming).
"""
from __future__ import annotations

SAMPLES: list[dict] = [
    {
        "user_goal": "Please extend this 8-second lecture clip to 25 seconds and add English subtitles. The lecturer speaks English.",
        "rationale": (
            "User uploaded a short English lecture clip, asks to extend AND add English "
            "subtitles. IntakeVideoAgent ingests. VideoExtendAgent continues the lecture to "
            "~25 seconds first so subtitle timing covers the full extended length. "
            "TranscriptionAgent transcribes the extended English speech. CompositorAgent burns "
            "English SRT. Reject TranslationAgent (same language), MusicAgent / AmbienceAgent / "
            "AudioMixAgent (no audio overlay), StyleTransferAgent (no restyle), "
            "VideoAnalysisAgent / HighlightAgent (no trimming)."
        ),
        "intents": [
            "Ingest the 8-second English lecture clip into the workspace.",
            "Extend the lecture clip to ~25 seconds preserving the speaker's delivery.",
            "Transcribe the extended English lecture speech into timestamped SRT.",
            "Compose the extended lecture with English captions burned onto the frames.",
        ],
    },
    {
        "user_goal": "I have a 6-second Spanish cooking demo. Please extend to 20 seconds and add Spanish subtitles.",
        "rationale": (
            "Short Spanish cooking demo + extend + Spanish (monolingual) subtitles. "
            "IntakeVideoAgent ingests, VideoExtendAgent extends to ~20 seconds, "
            "TranscriptionAgent transcribes Spanish speech, CompositorAgent burns SRT. No "
            "translation, no audio, no style change."
        ),
        "intents": [
            "Ingest the 6-second Spanish cooking-demo clip into the workspace.",
            "Extend the cooking demo to ~20 seconds preserving the chef's action.",
            "Transcribe the extended Spanish narration into timestamped SRT.",
            "Compose the extended demo with Spanish captions burned onto the footage.",
        ],
    },
    {
        "user_goal": "Please extend this 5-second Japanese anime-BTS clip to 15 seconds and add Japanese subtitles.",
        "rationale": (
            "Japanese anime-BTS clip + extend + Japanese (monolingual) subtitles. "
            "IntakeVideoAgent ingests, VideoExtendAgent extends to ~15 seconds, "
            "TranscriptionAgent transcribes Japanese dialogue, CompositorAgent burns Japanese "
            "SRT."
        ),
        "intents": [
            "Ingest the 5-second Japanese anime-BTS clip into the workspace.",
            "Extend the BTS clip to ~15 seconds continuing the production scene.",
            "Transcribe the extended Japanese dialogue into timestamped SRT.",
            "Compose the extended BTS clip with Japanese captions burned onto the frames.",
        ],
    },
    {
        "user_goal": "Extend this 7-second French fashion-show backstage clip to 20 seconds and add French subtitles.",
        "rationale": (
            "French backstage clip + extend + French (monolingual) subtitles. IntakeVideoAgent "
            "→ VideoExtendAgent (~20s) → TranscriptionAgent (French speech) → CompositorAgent "
            "(French SRT burn-in)."
        ),
        "intents": [
            "Ingest the 7-second French fashion-show backstage clip into the workspace.",
            "Extend the backstage clip to ~20 seconds continuing the backstage motion.",
            "Transcribe the extended French dialogue into timestamped SRT.",
            "Compose the extended clip with French captions burned onto the backstage footage.",
        ],
    },
    {
        "user_goal": "Please extend this 5-second Korean street-food clip to 18 seconds and add Korean subtitles.",
        "rationale": (
            "Korean street-food clip + extend + Korean (monolingual) subtitles. "
            "IntakeVideoAgent → VideoExtendAgent (~18s) → TranscriptionAgent (Korean speech) "
            "→ CompositorAgent (Korean SRT)."
        ),
        "intents": [
            "Ingest the 5-second Korean street-food clip into the workspace.",
            "Extend the street-food clip to ~18 seconds continuing the cooking action.",
            "Transcribe the extended Korean narration into timestamped SRT.",
            "Compose the extended clip with Korean captions burned onto the street-food footage.",
        ],
    },
    {
        "user_goal": "Extend this 4-second English TED-style talk clip to 15 seconds and add English captions.",
        "rationale": (
            "English TED-style clip + extend + English captions. IntakeVideoAgent → "
            "VideoExtendAgent (~15s) → TranscriptionAgent (English) → CompositorAgent "
            "(English SRT)."
        ),
        "intents": [
            "Ingest the 4-second English TED-style talk clip into the workspace.",
            "Extend the talk clip to ~15 seconds continuing the speaker's delivery.",
            "Transcribe the extended English talk into timestamped SRT.",
            "Compose the extended talk with English captions burned onto the talk footage.",
        ],
    },
    {
        "user_goal": "I have a short 6-second Mandarin news-anchor clip. Please extend to 20 seconds and add Mandarin subtitles.",
        "rationale": (
            "Mandarin news-anchor clip + extend + Mandarin (monolingual) captions. "
            "IntakeVideoAgent → VideoExtendAgent (~20s) → TranscriptionAgent (Mandarin) → "
            "CompositorAgent (Mandarin SRT)."
        ),
        "intents": [
            "Ingest the 6-second Mandarin news-anchor clip into the workspace.",
            "Extend the news clip to ~20 seconds continuing the anchor's delivery.",
            "Transcribe the extended Mandarin news segment into timestamped SRT.",
            "Compose the extended news clip with Mandarin captions burned onto the anchor footage.",
        ],
    },
    {
        "user_goal": "Extend this 7-second German tech-talk clip to 25 seconds and add German captions.",
        "rationale": (
            "German tech-talk clip + extend + German (monolingual) captions. IntakeVideoAgent "
            "→ VideoExtendAgent (~25s) → TranscriptionAgent (German) → CompositorAgent "
            "(German SRT)."
        ),
        "intents": [
            "Ingest the 7-second German tech-talk clip into the workspace.",
            "Extend the tech-talk clip to ~25 seconds continuing the presenter's explanation.",
            "Transcribe the extended German speech into timestamped SRT.",
            "Compose the extended talk with German captions burned onto the presenter footage.",
        ],
    },
    {
        "user_goal": "Please extend this 5-second Italian tour-guide clip to 18 seconds and add Italian captions.",
        "rationale": (
            "Italian tour-guide clip + extend + Italian (monolingual) captions. "
            "IntakeVideoAgent → VideoExtendAgent (~18s) → TranscriptionAgent (Italian) → "
            "CompositorAgent (Italian SRT)."
        ),
        "intents": [
            "Ingest the 5-second Italian tour-guide clip into the workspace.",
            "Extend the tour-guide clip to ~18 seconds continuing the guide's narration.",
            "Transcribe the extended Italian narration into timestamped SRT.",
            "Compose the extended clip with Italian captions burned onto the tour footage.",
        ],
    },
    {
        "user_goal": "Extend this 8-second Russian museum-tour clip to 25 seconds and add Russian subtitles.",
        "rationale": (
            "Russian museum-tour + extend + Russian (monolingual) captions. IntakeVideoAgent → "
            "VideoExtendAgent (~25s) → TranscriptionAgent (Russian) → CompositorAgent "
            "(Russian SRT)."
        ),
        "intents": [
            "Ingest the 8-second Russian museum-tour clip into the workspace.",
            "Extend the museum-tour clip to ~25 seconds continuing the guide's narration.",
            "Transcribe the extended Russian narration into timestamped SRT.",
            "Compose the extended tour clip with Russian captions burned onto the museum footage.",
        ],
    },
    {
        "user_goal": "Please extend this 4-second Portuguese soccer-commentary clip to 15 seconds and add Portuguese subtitles.",
        "rationale": (
            "Portuguese soccer commentary + extend + Portuguese (monolingual) subtitles. "
            "IntakeVideoAgent → VideoExtendAgent (~15s) → TranscriptionAgent (Portuguese) → "
            "CompositorAgent (Portuguese SRT)."
        ),
        "intents": [
            "Ingest the 4-second Portuguese soccer-commentary clip into the workspace.",
            "Extend the commentary clip to ~15 seconds continuing the announcer's call.",
            "Transcribe the extended Portuguese commentary into timestamped SRT.",
            "Compose the extended clip with Portuguese captions burned onto the soccer footage.",
        ],
    },
    {
        "user_goal": "Extend this 6-second Arabic poetry-reading clip to 20 seconds and add Arabic captions.",
        "rationale": (
            "Arabic poetry reading + extend + Arabic (monolingual) captions. IntakeVideoAgent "
            "→ VideoExtendAgent (~20s) → TranscriptionAgent (Arabic) → CompositorAgent "
            "(Arabic SRT)."
        ),
        "intents": [
            "Ingest the 6-second Arabic poetry-reading clip into the workspace.",
            "Extend the poetry-reading clip to ~20 seconds continuing the recitation.",
            "Transcribe the extended Arabic recitation into timestamped SRT.",
            "Compose the extended clip with Arabic captions burned onto the reading footage.",
        ],
    },
    {
        "user_goal": "Please extend this 5-second Hindi yoga-instruction clip to 18 seconds and add Hindi subtitles.",
        "rationale": (
            "Hindi yoga-instruction clip + extend + Hindi (monolingual) captions. "
            "IntakeVideoAgent → VideoExtendAgent (~18s) → TranscriptionAgent (Hindi) → "
            "CompositorAgent (Hindi SRT)."
        ),
        "intents": [
            "Ingest the 5-second Hindi yoga-instruction clip into the workspace.",
            "Extend the yoga clip to ~18 seconds continuing the instructor's cues.",
            "Transcribe the extended Hindi instruction into timestamped SRT.",
            "Compose the extended yoga clip with Hindi captions burned onto the instruction footage.",
        ],
    },
    {
        "user_goal": "Extend this 7-second Thai cooking-demo clip to 22 seconds and add Thai captions.",
        "rationale": (
            "Thai cooking demo + extend + Thai (monolingual) captions. IntakeVideoAgent → "
            "VideoExtendAgent (~22s) → TranscriptionAgent (Thai) → CompositorAgent "
            "(Thai SRT)."
        ),
        "intents": [
            "Ingest the 7-second Thai cooking-demo clip into the workspace.",
            "Extend the cooking-demo clip to ~22 seconds continuing the cooking action.",
            "Transcribe the extended Thai narration into timestamped SRT.",
            "Compose the extended demo with Thai captions burned onto the cooking footage.",
        ],
    },
    {
        "user_goal": "Please extend this 4-second Vietnamese travel-vlog clip to 15 seconds and add Vietnamese captions.",
        "rationale": (
            "Vietnamese travel vlog + extend + Vietnamese (monolingual) captions. "
            "IntakeVideoAgent → VideoExtendAgent (~15s) → TranscriptionAgent (Vietnamese) → "
            "CompositorAgent (Vietnamese SRT)."
        ),
        "intents": [
            "Ingest the 4-second Vietnamese travel-vlog clip into the workspace.",
            "Extend the vlog clip to ~15 seconds continuing the vlogger's narration.",
            "Transcribe the extended Vietnamese narration into timestamped SRT.",
            "Compose the extended vlog with Vietnamese captions burned onto the travel footage.",
        ],
    },
    {
        "user_goal": "Extend this 5-second Dutch museum-guide clip to 18 seconds and add Dutch subtitles.",
        "rationale": (
            "Dutch museum-guide + extend + Dutch (monolingual) captions. IntakeVideoAgent → "
            "VideoExtendAgent (~18s) → TranscriptionAgent (Dutch) → CompositorAgent "
            "(Dutch SRT)."
        ),
        "intents": [
            "Ingest the 5-second Dutch museum-guide clip into the workspace.",
            "Extend the guide clip to ~18 seconds continuing the museum commentary.",
            "Transcribe the extended Dutch narration into timestamped SRT.",
            "Compose the extended clip with Dutch captions burned onto the guide footage.",
        ],
    },
    {
        "user_goal": "Please extend this 6-second Polish stand-up comedy clip to 20 seconds and add Polish captions.",
        "rationale": (
            "Polish stand-up + extend + Polish (monolingual) captions. IntakeVideoAgent → "
            "VideoExtendAgent (~20s) → TranscriptionAgent (Polish) → CompositorAgent "
            "(Polish SRT)."
        ),
        "intents": [
            "Ingest the 6-second Polish stand-up comedy clip into the workspace.",
            "Extend the comedy clip to ~20 seconds continuing the comedian's bit.",
            "Transcribe the extended Polish monologue into timestamped SRT.",
            "Compose the extended clip with Polish captions burned onto the stand-up footage.",
        ],
    },
    {
        "user_goal": "Extend this 8-second Turkish bazaar-walkthrough clip to 25 seconds and add Turkish subtitles.",
        "rationale": (
            "Turkish bazaar walkthrough + extend + Turkish (monolingual) captions. "
            "IntakeVideoAgent → VideoExtendAgent (~25s) → TranscriptionAgent (Turkish) → "
            "CompositorAgent (Turkish SRT)."
        ),
        "intents": [
            "Ingest the 8-second Turkish bazaar-walkthrough clip into the workspace.",
            "Extend the walkthrough clip to ~25 seconds continuing the bazaar stroll.",
            "Transcribe the extended Turkish narration into timestamped SRT.",
            "Compose the extended clip with Turkish captions burned onto the bazaar footage.",
        ],
    },
    {
        "user_goal": "Please extend this 5-second Greek taverna-tour clip to 18 seconds and add Greek captions.",
        "rationale": (
            "Greek taverna tour + extend + Greek (monolingual) captions. IntakeVideoAgent → "
            "VideoExtendAgent (~18s) → TranscriptionAgent (Greek) → CompositorAgent "
            "(Greek SRT)."
        ),
        "intents": [
            "Ingest the 5-second Greek taverna-tour clip into the workspace.",
            "Extend the tour clip to ~18 seconds continuing the taverna tour.",
            "Transcribe the extended Greek narration into timestamped SRT.",
            "Compose the extended clip with Greek captions burned onto the taverna footage.",
        ],
    },
    {
        "user_goal": "Extend this 4-second Swedish IKEA-style walkthrough clip to 15 seconds and add Swedish subtitles.",
        "rationale": (
            "Swedish walkthrough + extend + Swedish (monolingual) captions. IntakeVideoAgent "
            "→ VideoExtendAgent (~15s) → TranscriptionAgent (Swedish) → CompositorAgent "
            "(Swedish SRT)."
        ),
        "intents": [
            "Ingest the 4-second Swedish walkthrough clip into the workspace.",
            "Extend the walkthrough clip to ~15 seconds continuing the narrator's instructions.",
            "Transcribe the extended Swedish narration into timestamped SRT.",
            "Compose the extended clip with Swedish captions burned onto the walkthrough footage.",
        ],
    },
    {
        "user_goal": "Please extend this 6-second Cantonese dim-sum demo clip to 20 seconds and add Cantonese captions.",
        "rationale": (
            "Cantonese dim-sum demo + extend + Cantonese (monolingual) captions. "
            "IntakeVideoAgent → VideoExtendAgent (~20s) → TranscriptionAgent (Cantonese) → "
            "CompositorAgent (Cantonese SRT)."
        ),
        "intents": [
            "Ingest the 6-second Cantonese dim-sum demo clip into the workspace.",
            "Extend the dim-sum demo clip to ~20 seconds continuing the preparation.",
            "Transcribe the extended Cantonese narration into timestamped SRT.",
            "Compose the extended clip with Cantonese captions burned onto the dim-sum footage.",
        ],
    },
    {
        "user_goal": "Extend this 5-second Norwegian fjord-kayaking clip to 18 seconds and add Norwegian subtitles.",
        "rationale": (
            "Norwegian fjord-kayaking + extend + Norwegian (monolingual) captions. "
            "IntakeVideoAgent → VideoExtendAgent (~18s) → TranscriptionAgent (Norwegian) → "
            "CompositorAgent (Norwegian SRT)."
        ),
        "intents": [
            "Ingest the 5-second Norwegian fjord-kayaking clip into the workspace.",
            "Extend the kayaking clip to ~18 seconds continuing the paddling motion.",
            "Transcribe the extended Norwegian narration into timestamped SRT.",
            "Compose the extended clip with Norwegian captions burned onto the kayaking footage.",
        ],
    },
    {
        "user_goal": "Please extend this 7-second Hebrew Torah-reading clip to 22 seconds and add Hebrew subtitles.",
        "rationale": (
            "Hebrew Torah reading + extend + Hebrew (monolingual) captions. IntakeVideoAgent "
            "→ VideoExtendAgent (~22s) → TranscriptionAgent (Hebrew) → CompositorAgent "
            "(Hebrew SRT)."
        ),
        "intents": [
            "Ingest the 7-second Hebrew Torah-reading clip into the workspace.",
            "Extend the Torah-reading clip to ~22 seconds continuing the recitation.",
            "Transcribe the extended Hebrew reading into timestamped SRT.",
            "Compose the extended reading with Hebrew captions burned onto the Torah-reading footage.",
        ],
    },
    {
        "user_goal": "Extend this 6-second Ukrainian folk-song-performance clip to 20 seconds and add Ukrainian subtitles.",
        "rationale": (
            "Ukrainian folk-song performance + extend + Ukrainian (monolingual) captions. "
            "IntakeVideoAgent → VideoExtendAgent (~20s) → TranscriptionAgent (Ukrainian) → "
            "CompositorAgent (Ukrainian SRT)."
        ),
        "intents": [
            "Ingest the 6-second Ukrainian folk-song performance clip into the workspace.",
            "Extend the performance clip to ~20 seconds continuing the folk-song delivery.",
            "Transcribe the extended Ukrainian lyrics into timestamped SRT.",
            "Compose the extended performance with Ukrainian captions burned onto the stage footage.",
        ],
    },
    {
        "user_goal": "Please extend this 4-second Czech theater-scene clip to 15 seconds and add Czech captions.",
        "rationale": (
            "Czech theater scene + extend + Czech (monolingual) captions. IntakeVideoAgent → "
            "VideoExtendAgent (~15s) → TranscriptionAgent (Czech) → CompositorAgent "
            "(Czech SRT)."
        ),
        "intents": [
            "Ingest the 4-second Czech theater-scene clip into the workspace.",
            "Extend the scene clip to ~15 seconds continuing the performers' dialogue.",
            "Transcribe the extended Czech dialogue into timestamped SRT.",
            "Compose the extended scene with Czech captions burned onto the theater footage.",
        ],
    },
    {
        "user_goal": "Extend this 5-second Hungarian folk-dance demonstration to 18 seconds and add Hungarian subtitles.",
        "rationale": (
            "Hungarian folk-dance demo + extend + Hungarian (monolingual) captions. "
            "IntakeVideoAgent → VideoExtendAgent (~18s) → TranscriptionAgent (Hungarian) → "
            "CompositorAgent (Hungarian SRT)."
        ),
        "intents": [
            "Ingest the 5-second Hungarian folk-dance demonstration into the workspace.",
            "Extend the demonstration clip to ~18 seconds continuing the dance steps.",
            "Transcribe the extended Hungarian narration into timestamped SRT.",
            "Compose the extended demo with Hungarian captions burned onto the folk-dance footage.",
        ],
    },
    {
        "user_goal": "Please extend this 8-second Indonesian batik-making demo to 25 seconds and add Indonesian captions.",
        "rationale": (
            "Indonesian batik-making demo + extend + Indonesian (monolingual) captions. "
            "IntakeVideoAgent → VideoExtendAgent (~25s) → TranscriptionAgent (Indonesian) → "
            "CompositorAgent (Indonesian SRT)."
        ),
        "intents": [
            "Ingest the 8-second Indonesian batik-making demo into the workspace.",
            "Extend the demo clip to ~25 seconds continuing the batik-making process.",
            "Transcribe the extended Indonesian narration into timestamped SRT.",
            "Compose the extended demo with Indonesian captions burned onto the batik footage.",
        ],
    },
    {
        "user_goal": "Extend this 6-second Finnish sauna-culture clip to 20 seconds and add Finnish subtitles.",
        "rationale": (
            "Finnish sauna clip + extend + Finnish (monolingual) captions. IntakeVideoAgent → "
            "VideoExtendAgent (~20s) → TranscriptionAgent (Finnish) → CompositorAgent "
            "(Finnish SRT)."
        ),
        "intents": [
            "Ingest the 6-second Finnish sauna-culture clip into the workspace.",
            "Extend the sauna-culture clip to ~20 seconds continuing the scene.",
            "Transcribe the extended Finnish narration into timestamped SRT.",
            "Compose the extended clip with Finnish captions burned onto the sauna footage.",
        ],
    },
    {
        "user_goal": "Please extend this 4-second Malay nasi-lemak cooking clip to 15 seconds and add Malay captions.",
        "rationale": (
            "Malay nasi-lemak cooking clip + extend + Malay (monolingual) captions. "
            "IntakeVideoAgent → VideoExtendAgent (~15s) → TranscriptionAgent (Malay) → "
            "CompositorAgent (Malay SRT)."
        ),
        "intents": [
            "Ingest the 4-second Malay nasi-lemak cooking clip into the workspace.",
            "Extend the cooking clip to ~15 seconds continuing the preparation.",
            "Transcribe the extended Malay narration into timestamped SRT.",
            "Compose the extended cooking clip with Malay captions burned onto the nasi-lemak footage.",
        ],
    },
    {
        "user_goal": "Extend this 7-second Romanian folk-craft demo to 22 seconds and add Romanian captions.",
        "rationale": (
            "Romanian folk-craft demo + extend + Romanian (monolingual) captions. "
            "IntakeVideoAgent → VideoExtendAgent (~22s) → TranscriptionAgent (Romanian) → "
            "CompositorAgent (Romanian SRT)."
        ),
        "intents": [
            "Ingest the 7-second Romanian folk-craft demonstration into the workspace.",
            "Extend the demo clip to ~22 seconds continuing the craft process.",
            "Transcribe the extended Romanian narration into timestamped SRT.",
            "Compose the extended demo with Romanian captions burned onto the folk-craft footage.",
        ],
    },
]
