"""Shape: extend_style_subtitle — IntakeVideo → VideoExtend → StyleTransfer → Transcription → Compositor.

Uploaded video: extended → restyled → subtitled.  Order: extend first
(longer baseline), then style transfer covers the full extended length,
then transcribe the extended audio, then Compositor burns SRT.
"""
from __future__ import annotations

SAMPLES: list[dict] = [
    {
        "user_goal": "Please extend this 5-second English lecture clip to 15 seconds, restyle as Ghibli watercolor, and add English captions.",
        "rationale": (
            "English lecture + extend-to-15s + Ghibli watercolor style + English (monolingual) "
            "captions. IntakeVideoAgent → VideoExtendAgent (~15s) → StyleTransferAgent (Ghibli) "
            "→ TranscriptionAgent (English) → CompositorAgent (English SRT on styled frames)."
        ),
        "intents": [
            "Ingest the 5-second English lecture clip into the workspace.",
            "Extend the lecture clip to ~15 seconds continuing the speaker's delivery.",
            "Restyle the extended lecture clip into a Ghibli watercolor aesthetic.",
            "Transcribe the extended English lecture speech into timestamped SRT.",
            "Compose the styled-extended lecture with English captions burned onto the watercolor frames.",
        ],
    },
    {
        "user_goal": "Extend this 6-second Japanese anime-BTS clip to 20 seconds, restyle as ukiyo-e, and add Japanese captions.",
        "rationale": (
            "Japanese anime-BTS + extend-to-20s + ukiyo-e style + Japanese (monolingual) "
            "captions. IntakeVideoAgent → VideoExtendAgent (~20s) → StyleTransferAgent "
            "(ukiyo-e) → TranscriptionAgent (Japanese) → CompositorAgent."
        ),
        "intents": [
            "Ingest the 6-second Japanese anime-BTS clip into the workspace.",
            "Extend the BTS clip to ~20 seconds continuing the production scene.",
            "Restyle the extended BTS clip into a Japanese ukiyo-e woodblock aesthetic.",
            "Transcribe the extended Japanese BTS dialogue into timestamped SRT.",
            "Compose the styled-extended clip with Japanese captions burned onto the ukiyo-e frames.",
        ],
    },
    {
        "user_goal": "Please extend this 5-second French chef clip to 18 seconds, apply Van Gogh impasto, and add French subtitles.",
        "rationale": (
            "French chef clip + extend-to-18s + Van Gogh impasto style + French (monolingual) "
            "captions. IntakeVideoAgent → VideoExtendAgent (~18s) → StyleTransferAgent (Van "
            "Gogh impasto) → TranscriptionAgent (French) → CompositorAgent."
        ),
        "intents": [
            "Ingest the 5-second French chef clip into the workspace.",
            "Extend the chef clip to ~18 seconds continuing the cooking action.",
            "Restyle the extended chef clip into a Van Gogh impasto oil-painting aesthetic.",
            "Transcribe the extended French speech into timestamped SRT.",
            "Compose the styled-extended clip with French captions burned onto the impasto frames.",
        ],
    },
    {
        "user_goal": "Extend this 4-second Spanish soccer-commentary clip to 12 seconds, restyle as 1980s VHS, and add Spanish captions.",
        "rationale": (
            "Spanish soccer commentary + extend-to-12s + 1980s VHS style + Spanish (monolingual) "
            "captions. IntakeVideoAgent → VideoExtendAgent (~12s) → StyleTransferAgent (1980s "
            "VHS) → TranscriptionAgent (Spanish) → CompositorAgent."
        ),
        "intents": [
            "Ingest the 4-second Spanish soccer-commentary clip into the workspace.",
            "Extend the commentary clip to ~12 seconds continuing the announcer's call.",
            "Restyle the extended commentary into a 1980s VHS aesthetic with scanlines.",
            "Transcribe the extended Spanish commentary into timestamped SRT.",
            "Compose the styled-extended clip with Spanish captions burned onto the VHS frames.",
        ],
    },
    {
        "user_goal": "Please extend this 5-second Korean travel-vlog clip to 15 seconds, apply Wes Anderson pastel style, and add Korean subtitles.",
        "rationale": (
            "Korean travel vlog + extend-to-15s + Wes Anderson pastel + Korean (monolingual) "
            "captions. IntakeVideoAgent → VideoExtendAgent (~15s) → StyleTransferAgent (Wes "
            "Anderson) → TranscriptionAgent (Korean) → CompositorAgent."
        ),
        "intents": [
            "Ingest the 5-second Korean travel-vlog clip into the workspace.",
            "Extend the vlog clip to ~15 seconds continuing the vlogger's narration.",
            "Restyle the extended vlog into a Wes Anderson pastel-symmetry aesthetic.",
            "Transcribe the extended Korean narration into timestamped SRT.",
            "Compose the styled-extended vlog with Korean captions burned onto the pastel frames.",
        ],
    },
    {
        "user_goal": "Extend this 6-second German tech-demo to 20 seconds, restyle as neon cyberpunk, and add German captions.",
        "rationale": (
            "German tech-demo + extend-to-20s + neon cyberpunk style + German (monolingual) "
            "captions. IntakeVideoAgent → VideoExtendAgent (~20s) → StyleTransferAgent (neon "
            "cyberpunk) → TranscriptionAgent (German) → CompositorAgent."
        ),
        "intents": [
            "Ingest the 6-second German tech-demo clip into the workspace.",
            "Extend the demo to ~20 seconds continuing the presenter's explanation.",
            "Restyle the extended demo into a neon cyberpunk visual aesthetic.",
            "Transcribe the extended German speech into timestamped SRT.",
            "Compose the styled-extended demo with German captions burned onto the cyberpunk frames.",
        ],
    },
    {
        "user_goal": "Please extend this 7-second Italian poetry-reading to 22 seconds, apply ukiyo-e style, and add Italian subtitles.",
        "rationale": (
            "Italian poetry reading + extend-to-22s + ukiyo-e style + Italian (monolingual) "
            "captions. IntakeVideoAgent → VideoExtendAgent (~22s) → StyleTransferAgent "
            "(ukiyo-e) → TranscriptionAgent (Italian) → CompositorAgent."
        ),
        "intents": [
            "Ingest the 7-second Italian poetry-reading clip into the workspace.",
            "Extend the reading clip to ~22 seconds continuing the recitation.",
            "Restyle the extended reading into a Japanese ukiyo-e woodblock aesthetic.",
            "Transcribe the extended Italian recitation into timestamped SRT.",
            "Compose the styled-extended reading with Italian captions burned onto the ukiyo-e frames.",
        ],
    },
    {
        "user_goal": "Extend this 5-second Russian museum-tour clip to 15 seconds, restyle as Monet impressionist, and add Russian subtitles.",
        "rationale": (
            "Russian museum tour + extend-to-15s + Monet impressionist + Russian (monolingual) "
            "captions. IntakeVideoAgent → VideoExtendAgent (~15s) → StyleTransferAgent "
            "(Monet) → TranscriptionAgent (Russian) → CompositorAgent."
        ),
        "intents": [
            "Ingest the 5-second Russian museum-tour clip into the workspace.",
            "Extend the tour clip to ~15 seconds continuing the guide's narration.",
            "Restyle the extended tour into a Monet impressionist aesthetic.",
            "Transcribe the extended Russian narration into timestamped SRT.",
            "Compose the styled-extended tour with Russian captions burned onto the Monet frames.",
        ],
    },
    {
        "user_goal": "Please extend this 4-second Portuguese street-food clip to 12 seconds, apply Pixar 3D-cartoon style, and add Portuguese captions.",
        "rationale": (
            "Portuguese street-food + extend-to-12s + Pixar 3D style + Portuguese (monolingual) "
            "captions. IntakeVideoAgent → VideoExtendAgent (~12s) → StyleTransferAgent (Pixar "
            "3D) → TranscriptionAgent (Portuguese) → CompositorAgent."
        ),
        "intents": [
            "Ingest the 4-second Portuguese street-food clip into the workspace.",
            "Extend the street-food clip to ~12 seconds continuing the cooking action.",
            "Restyle the extended street-food clip into a Pixar 3D-cartoon aesthetic.",
            "Transcribe the extended Portuguese narration into timestamped SRT.",
            "Compose the styled-extended clip with Portuguese captions burned onto the Pixar frames.",
        ],
    },
    {
        "user_goal": "Extend this 5-second Arabic news-interview clip to 18 seconds, restyle as film-noir B&W, and add Arabic captions.",
        "rationale": (
            "Arabic news interview + extend-to-18s + film-noir B&W style + Arabic (monolingual) "
            "captions. IntakeVideoAgent → VideoExtendAgent (~18s) → StyleTransferAgent "
            "(film-noir B&W) → TranscriptionAgent (Arabic) → CompositorAgent."
        ),
        "intents": [
            "Ingest the 5-second Arabic news-interview clip into the workspace.",
            "Extend the interview clip to ~18 seconds continuing the dialogue.",
            "Restyle the extended interview into a film-noir high-contrast B&W aesthetic.",
            "Transcribe the extended Arabic dialogue into timestamped SRT.",
            "Compose the styled-extended interview with Arabic captions burned onto the noir frames.",
        ],
    },
    {
        "user_goal": "Please extend this 6-second Hindi yoga-session clip to 20 seconds, apply pastel anime slice-of-life style, and add Hindi subtitles.",
        "rationale": (
            "Hindi yoga session + extend-to-20s + pastel anime style + Hindi (monolingual) "
            "captions. IntakeVideoAgent → VideoExtendAgent (~20s) → StyleTransferAgent "
            "(pastel anime slice-of-life) → TranscriptionAgent (Hindi) → CompositorAgent."
        ),
        "intents": [
            "Ingest the 6-second Hindi yoga-session clip into the workspace.",
            "Extend the session clip to ~20 seconds continuing the instructor's cues.",
            "Restyle the extended session into a pastel anime slice-of-life aesthetic.",
            "Transcribe the extended Hindi instruction into timestamped SRT.",
            "Compose the styled-extended session with Hindi captions burned onto the pastel-anime frames.",
        ],
    },
    {
        "user_goal": "Extend this 4-second Thai street-food clip to 15 seconds, restyle as Ghibli slice-of-life, and add Thai captions.",
        "rationale": (
            "Thai street-food + extend-to-15s + Ghibli slice-of-life + Thai (monolingual) "
            "captions. IntakeVideoAgent → VideoExtendAgent (~15s) → StyleTransferAgent "
            "(Ghibli slice-of-life) → TranscriptionAgent (Thai) → CompositorAgent."
        ),
        "intents": [
            "Ingest the 4-second Thai street-food clip into the workspace.",
            "Extend the street-food clip to ~15 seconds continuing the cooking action.",
            "Restyle the extended clip into a Studio Ghibli slice-of-life aesthetic.",
            "Transcribe the extended Thai narration into timestamped SRT.",
            "Compose the styled-extended clip with Thai captions burned onto the Ghibli frames.",
        ],
    },
    {
        "user_goal": "Please extend this 5-second Vietnamese dance-performance to 15 seconds, apply 1930s silent-film B&W, and add Vietnamese subtitles.",
        "rationale": (
            "Vietnamese dance performance + extend-to-15s + 1930s silent-film B&W + Vietnamese "
            "(monolingual) captions. IntakeVideoAgent → VideoExtendAgent (~15s) → "
            "StyleTransferAgent (1930s silent-film B&W) → TranscriptionAgent (Vietnamese) → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 5-second Vietnamese dance-performance clip into the workspace.",
            "Extend the performance to ~15 seconds continuing the choreography.",
            "Restyle the extended performance into a 1930s B&W silent-film grainy aesthetic.",
            "Transcribe the extended Vietnamese narration into timestamped SRT.",
            "Compose the styled-extended performance with Vietnamese captions burned onto the silent-film frames.",
        ],
    },
    {
        "user_goal": "Extend this 6-second Dutch tulip-farm tour to 18 seconds, restyle as Seurat pointillist, and add Dutch captions.",
        "rationale": (
            "Dutch tulip-farm tour + extend-to-18s + Seurat pointillist + Dutch (monolingual) "
            "captions. IntakeVideoAgent → VideoExtendAgent (~18s) → StyleTransferAgent "
            "(Seurat pointillist) → TranscriptionAgent (Dutch) → CompositorAgent."
        ),
        "intents": [
            "Ingest the 6-second Dutch tulip-farm tour into the workspace.",
            "Extend the tour clip to ~18 seconds continuing the guide's narration.",
            "Restyle the extended tour into a Seurat pointillist painting aesthetic.",
            "Transcribe the extended Dutch narration into timestamped SRT.",
            "Compose the styled-extended tour with Dutch captions burned onto the pointillist frames.",
        ],
    },
    {
        "user_goal": "Please extend this 5-second Polish stand-up comedy clip to 15 seconds, apply Chinese ink-wash style, and add Polish captions.",
        "rationale": (
            "Polish stand-up + extend-to-15s + Chinese ink-wash style + Polish (monolingual) "
            "captions. IntakeVideoAgent → VideoExtendAgent (~15s) → StyleTransferAgent "
            "(Chinese ink-wash) → TranscriptionAgent (Polish) → CompositorAgent."
        ),
        "intents": [
            "Ingest the 5-second Polish stand-up comedy clip into the workspace.",
            "Extend the comedy clip to ~15 seconds continuing the comedian's bit.",
            "Restyle the extended comedy into a Chinese ink-wash aesthetic.",
            "Transcribe the extended Polish monologue into timestamped SRT.",
            "Compose the styled-extended comedy with Polish captions burned onto the ink-wash frames.",
        ],
    },
    {
        "user_goal": "Extend this 4-second Turkish bazaar-walkthrough to 12 seconds, restyle as Matisse cutout-collage, and add Turkish subtitles.",
        "rationale": (
            "Turkish bazaar walkthrough + extend-to-12s + Matisse cutout-collage + Turkish "
            "(monolingual) captions. IntakeVideoAgent → VideoExtendAgent (~12s) → "
            "StyleTransferAgent (Matisse cutout) → TranscriptionAgent (Turkish) → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 4-second Turkish bazaar-walkthrough into the workspace.",
            "Extend the walkthrough to ~12 seconds continuing the bazaar stroll.",
            "Restyle the extended walkthrough into a Matisse cutout-collage aesthetic.",
            "Transcribe the extended Turkish narration into timestamped SRT.",
            "Compose the styled-extended walk with Turkish captions burned onto the cutout-collage frames.",
        ],
    },
    {
        "user_goal": "Please extend this 5-second Greek poetry-reading to 18 seconds, apply charcoal-sketch grayscale, and add Greek captions.",
        "rationale": (
            "Greek poetry reading + extend-to-18s + charcoal-sketch grayscale + Greek "
            "(monolingual) captions. IntakeVideoAgent → VideoExtendAgent (~18s) → "
            "StyleTransferAgent (charcoal sketch) → TranscriptionAgent (Greek) → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 5-second Greek poetry-reading clip into the workspace.",
            "Extend the reading to ~18 seconds continuing the recitation.",
            "Restyle the extended reading into a charcoal-sketch grayscale aesthetic.",
            "Transcribe the extended Greek recitation into timestamped SRT.",
            "Compose the styled-extended reading with Greek captions burned onto the charcoal frames.",
        ],
    },
    {
        "user_goal": "Extend this 6-second Swedish IKEA-assembly clip to 20 seconds, restyle as Cocomelon 3D kid-show, and add Swedish subtitles.",
        "rationale": (
            "Swedish IKEA assembly + extend-to-20s + Cocomelon 3D kid-show + Swedish "
            "(monolingual) captions. IntakeVideoAgent → VideoExtendAgent (~20s) → "
            "StyleTransferAgent (Cocomelon 3D) → TranscriptionAgent (Swedish) → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 6-second Swedish IKEA-assembly clip into the workspace.",
            "Extend the assembly clip to ~20 seconds continuing the narrator's instructions.",
            "Restyle the extended assembly into a Cocomelon vibrant 3D kid-show aesthetic.",
            "Transcribe the extended Swedish narration into timestamped SRT.",
            "Compose the styled-extended clip with Swedish captions burned onto the Cocomelon frames.",
        ],
    },
    {
        "user_goal": "Please extend this 4-second Hebrew prayer-service clip to 12 seconds, apply watercolor children's-book style, and add Hebrew subtitles.",
        "rationale": (
            "Hebrew prayer service + extend-to-12s + watercolor children's-book style + "
            "Hebrew (monolingual) captions. IntakeVideoAgent → VideoExtendAgent (~12s) → "
            "StyleTransferAgent (watercolor children's-book) → TranscriptionAgent (Hebrew) "
            "→ CompositorAgent."
        ),
        "intents": [
            "Ingest the 4-second Hebrew prayer-service clip into the workspace.",
            "Extend the service clip to ~12 seconds continuing the recitation.",
            "Restyle the extended service into a watercolor children's-book aesthetic.",
            "Transcribe the extended Hebrew liturgy into timestamped SRT.",
            "Compose the styled-extended service with Hebrew captions burned onto the watercolor frames.",
        ],
    },
    {
        "user_goal": "Extend this 5-second Cantonese dim-sum tutorial to 15 seconds, restyle as Warhol pop-art, and add Cantonese captions.",
        "rationale": (
            "Cantonese dim-sum tutorial + extend-to-15s + Warhol pop-art + Cantonese "
            "(monolingual) captions. IntakeVideoAgent → VideoExtendAgent (~15s) → "
            "StyleTransferAgent (Warhol pop-art) → TranscriptionAgent (Cantonese) → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 5-second Cantonese dim-sum tutorial into the workspace.",
            "Extend the tutorial to ~15 seconds continuing the preparation.",
            "Restyle the extended tutorial into a Warhol pop-art screen-print aesthetic.",
            "Transcribe the extended Cantonese narration into timestamped SRT.",
            "Compose the styled-extended tutorial with Cantonese captions burned onto the Warhol frames.",
        ],
    },
]
