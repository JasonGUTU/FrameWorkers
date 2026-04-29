"""Shape: style_subtitle — IntakeVideo → StyleTransfer → Transcription → Compositor.

User uploaded video, wants it restyled AND subtitled (monolingual).

Reject: TranslationAgent (monolingual), MusicAgent / AmbienceAgent /
AudioMixAgent (no audio overlay), VideoExtendAgent (no extension),
VideoAnalysisAgent / HighlightAgent (no trim).
"""
from __future__ import annotations

SAMPLES: list[dict] = [
    {
        "user_goal": "Please restyle this English lecture clip as a Ghibli-watercolor animation and add English subtitles.",
        "rationale": (
            "English lecture clip + style transfer + monolingual English subtitles. "
            "IntakeVideoAgent ingests. StyleTransferAgent applies Ghibli-watercolor first (so "
            "the transcription timing matches the restyled frames). TranscriptionAgent "
            "transcribes English speech. CompositorAgent burns English SRT onto the restyled "
            "video. Reject TranslationAgent (same language), MusicAgent / AmbienceAgent / "
            "AudioMixAgent (no audio overlay), VideoExtendAgent (no length change), "
            "VideoAnalysisAgent / HighlightAgent (no trim)."
        ),
        "intents": [
            "Ingest the English lecture clip into the workspace.",
            "Restyle the lecture footage into a Ghibli-watercolor animation aesthetic.",
            "Transcribe the lecturer's English speech into timestamped SRT segments.",
            "Compose the restyled lecture with English captions burned onto the watercolor frames.",
        ],
    },
    {
        "user_goal": "Restyle this Japanese cooking-show clip as anime-action and burn Japanese captions.",
        "rationale": (
            "Japanese cooking clip + anime-action style + Japanese (monolingual) subtitles. "
            "IntakeVideoAgent → StyleTransferAgent (anime-action) → TranscriptionAgent "
            "(Japanese) → CompositorAgent (Japanese SRT burn-in)."
        ),
        "intents": [
            "Ingest the Japanese cooking-show clip into the workspace.",
            "Restyle the cooking-show footage into an anime-action aesthetic.",
            "Transcribe the chef's Japanese narration into timestamped SRT.",
            "Compose the restyled cooking show with Japanese captions burned onto the anime frames.",
        ],
    },
    {
        "user_goal": "Please apply a Van Gogh impasto style to this French-chef interview and add French subtitles.",
        "rationale": (
            "French-chef interview + Van Gogh impasto style + French (monolingual) subtitles. "
            "IntakeVideoAgent → StyleTransferAgent (Van Gogh impasto) → TranscriptionAgent "
            "(French) → CompositorAgent (French SRT)."
        ),
        "intents": [
            "Ingest the French-chef interview into the workspace.",
            "Restyle the interview footage into a Van Gogh impasto oil-painting aesthetic.",
            "Transcribe the chef's French speech into timestamped SRT.",
            "Compose the restyled interview with French captions burned onto the impasto frames.",
        ],
    },
    {
        "user_goal": "Restyle this Spanish soccer-commentary clip as a 1980s VHS look and add Spanish subtitles.",
        "rationale": (
            "Spanish soccer commentary + 1980s VHS style + Spanish (monolingual) subtitles. "
            "IntakeVideoAgent → StyleTransferAgent (1980s VHS) → TranscriptionAgent (Spanish) "
            "→ CompositorAgent (Spanish SRT)."
        ),
        "intents": [
            "Ingest the Spanish soccer-commentary clip into the workspace.",
            "Restyle the commentary footage into a 1980s VHS aesthetic with scanlines.",
            "Transcribe the Spanish commentary into timestamped SRT.",
            "Compose the restyled clip with Spanish captions burned onto the VHS-look frames.",
        ],
    },
    {
        "user_goal": "Please apply a Wes Anderson pastel symmetry style to this Korean travel-vlog and add Korean subtitles.",
        "rationale": (
            "Korean travel-vlog + Wes Anderson pastel style + Korean (monolingual) subtitles. "
            "IntakeVideoAgent → StyleTransferAgent (Wes Anderson) → TranscriptionAgent "
            "(Korean) → CompositorAgent (Korean SRT)."
        ),
        "intents": [
            "Ingest the Korean travel-vlog into the workspace.",
            "Restyle the vlog footage into a Wes Anderson pastel-symmetry aesthetic.",
            "Transcribe the vlogger's Korean narration into timestamped SRT.",
            "Compose the restyled vlog with Korean captions burned onto the pastel frames.",
        ],
    },
    {
        "user_goal": "Restyle this German tech-demo as a neon cyberpunk and add German captions.",
        "rationale": (
            "German tech-demo + neon cyberpunk style + German (monolingual) captions. "
            "IntakeVideoAgent → StyleTransferAgent (neon cyberpunk) → TranscriptionAgent "
            "(German) → CompositorAgent (German SRT)."
        ),
        "intents": [
            "Ingest the German tech-demo video into the workspace.",
            "Restyle the demo footage into a neon cyberpunk visual aesthetic.",
            "Transcribe the presenter's German speech into timestamped SRT.",
            "Compose the restyled demo with German captions burned onto the cyberpunk frames.",
        ],
    },
    {
        "user_goal": "Please apply an ukiyo-e woodblock style to this Italian poetry-reading clip and add Italian captions.",
        "rationale": (
            "Italian poetry reading + ukiyo-e style + Italian (monolingual) captions. "
            "IntakeVideoAgent → StyleTransferAgent (ukiyo-e) → TranscriptionAgent (Italian) → "
            "CompositorAgent (Italian SRT)."
        ),
        "intents": [
            "Ingest the Italian poetry-reading clip into the workspace.",
            "Restyle the poetry-reading footage into a Japanese ukiyo-e woodblock aesthetic.",
            "Transcribe the Italian recitation into timestamped SRT.",
            "Compose the restyled clip with Italian captions burned onto the woodblock frames.",
        ],
    },
    {
        "user_goal": "Restyle this Russian museum-tour clip as a Monet impressionist painting and add Russian subtitles.",
        "rationale": (
            "Russian museum-tour + Monet impressionist style + Russian (monolingual) captions. "
            "IntakeVideoAgent → StyleTransferAgent (Monet impressionist) → TranscriptionAgent "
            "(Russian) → CompositorAgent (Russian SRT)."
        ),
        "intents": [
            "Ingest the Russian museum-tour clip into the workspace.",
            "Restyle the museum-tour footage into a Monet impressionist aesthetic.",
            "Transcribe the Russian narration into timestamped SRT.",
            "Compose the restyled tour with Russian captions burned onto the Monet-look frames.",
        ],
    },
    {
        "user_goal": "Please apply a Pixar-3D-cartoon style to this Portuguese cooking-show and add Portuguese subtitles.",
        "rationale": (
            "Portuguese cooking show + Pixar 3D-cartoon style + Portuguese (monolingual) "
            "captions. IntakeVideoAgent → StyleTransferAgent (Pixar 3D) → TranscriptionAgent "
            "(Portuguese) → CompositorAgent (Portuguese SRT)."
        ),
        "intents": [
            "Ingest the Portuguese cooking-show clip into the workspace.",
            "Restyle the cooking-show footage into a Pixar 3D-cartoon aesthetic.",
            "Transcribe the chef's Portuguese narration into timestamped SRT.",
            "Compose the restyled show with Portuguese captions burned onto the Pixar-look frames.",
        ],
    },
    {
        "user_goal": "Restyle this Arabic news-interview as a film-noir black-and-white look and add Arabic subtitles.",
        "rationale": (
            "Arabic news interview + film-noir B&W style + Arabic (monolingual) captions. "
            "IntakeVideoAgent → StyleTransferAgent (film-noir B&W) → TranscriptionAgent "
            "(Arabic) → CompositorAgent (Arabic SRT)."
        ),
        "intents": [
            "Ingest the Arabic news-interview clip into the workspace.",
            "Restyle the interview footage into a film-noir high-contrast B&W aesthetic.",
            "Transcribe the Arabic dialogue into timestamped SRT.",
            "Compose the restyled interview with Arabic captions burned onto the noir frames.",
        ],
    },
    {
        "user_goal": "Please apply a pastel anime slice-of-life style to this Hindi yoga-session and add Hindi subtitles.",
        "rationale": (
            "Hindi yoga session + pastel anime slice-of-life + Hindi (monolingual) captions. "
            "IntakeVideoAgent → StyleTransferAgent (pastel anime) → TranscriptionAgent (Hindi) "
            "→ CompositorAgent (Hindi SRT)."
        ),
        "intents": [
            "Ingest the Hindi yoga-session clip into the workspace.",
            "Restyle the yoga session into a pastel anime slice-of-life aesthetic.",
            "Transcribe the instructor's Hindi cues into timestamped SRT.",
            "Compose the restyled session with Hindi captions burned onto the pastel-anime frames.",
        ],
    },
    {
        "user_goal": "Restyle this Thai street-food clip as a Studio Ghibli slice-of-life and add Thai captions.",
        "rationale": (
            "Thai street-food + Ghibli slice-of-life style + Thai (monolingual) captions. "
            "IntakeVideoAgent → StyleTransferAgent (Ghibli slice-of-life) → TranscriptionAgent "
            "(Thai) → CompositorAgent (Thai SRT)."
        ),
        "intents": [
            "Ingest the Thai street-food clip into the workspace.",
            "Restyle the street-food footage into a Studio Ghibli slice-of-life aesthetic.",
            "Transcribe the Thai narration into timestamped SRT.",
            "Compose the restyled clip with Thai captions burned onto the Ghibli-look frames.",
        ],
    },
    {
        "user_goal": "Please apply a 1930s silent-film B&W grain style to this Vietnamese dance-performance and add Vietnamese subtitles.",
        "rationale": (
            "Vietnamese dance performance + 1930s silent-film B&W + Vietnamese (monolingual) "
            "captions. IntakeVideoAgent → StyleTransferAgent (1930s silent-film B&W) → "
            "TranscriptionAgent (Vietnamese) → CompositorAgent (Vietnamese SRT)."
        ),
        "intents": [
            "Ingest the Vietnamese dance-performance clip into the workspace.",
            "Restyle the performance into a 1930s silent-film B&W grainy aesthetic.",
            "Transcribe the Vietnamese narration into timestamped SRT.",
            "Compose the restyled performance with Vietnamese captions burned onto the silent-film frames.",
        ],
    },
    {
        "user_goal": "Restyle this Dutch tulip-farm tour as a pointillist Seurat painting and add Dutch subtitles.",
        "rationale": (
            "Dutch tulip tour + Seurat pointillist style + Dutch (monolingual) captions. "
            "IntakeVideoAgent → StyleTransferAgent (Seurat pointillist) → TranscriptionAgent "
            "(Dutch) → CompositorAgent (Dutch SRT)."
        ),
        "intents": [
            "Ingest the Dutch tulip-farm tour into the workspace.",
            "Restyle the tulip-farm footage into a Seurat pointillist painting aesthetic.",
            "Transcribe the Dutch narration into timestamped SRT.",
            "Compose the restyled tour with Dutch captions burned onto the pointillist frames.",
        ],
    },
    {
        "user_goal": "Please apply a Chinese ink-wash style to this Polish stand-up comedy and add Polish captions.",
        "rationale": (
            "Polish stand-up + Chinese ink-wash style + Polish (monolingual) captions. "
            "IntakeVideoAgent → StyleTransferAgent (Chinese ink-wash) → TranscriptionAgent "
            "(Polish) → CompositorAgent (Polish SRT)."
        ),
        "intents": [
            "Ingest the Polish stand-up comedy clip into the workspace.",
            "Restyle the comedy footage into a Chinese ink-wash painting aesthetic.",
            "Transcribe the Polish stand-up monologue into timestamped SRT.",
            "Compose the restyled comedy with Polish captions burned onto the ink-wash frames.",
        ],
    },
    {
        "user_goal": "Restyle this Turkish bazaar walk as a Matisse cutout-collage and add Turkish subtitles.",
        "rationale": (
            "Turkish bazaar walk + Matisse cutout-collage + Turkish (monolingual) captions. "
            "IntakeVideoAgent → StyleTransferAgent (Matisse cutout-collage) → "
            "TranscriptionAgent (Turkish) → CompositorAgent (Turkish SRT)."
        ),
        "intents": [
            "Ingest the Turkish bazaar walkthrough into the workspace.",
            "Restyle the bazaar footage into a Matisse cutout-collage aesthetic.",
            "Transcribe the Turkish narration into timestamped SRT.",
            "Compose the restyled walk with Turkish captions burned onto the cutout-collage frames.",
        ],
    },
    {
        "user_goal": "Please apply a charcoal-sketch grayscale style to this Greek poetry-reading and add Greek captions.",
        "rationale": (
            "Greek poetry reading + charcoal-sketch grayscale + Greek (monolingual) captions. "
            "IntakeVideoAgent → StyleTransferAgent (charcoal sketch) → TranscriptionAgent "
            "(Greek) → CompositorAgent (Greek SRT)."
        ),
        "intents": [
            "Ingest the Greek poetry-reading clip into the workspace.",
            "Restyle the reading footage into a charcoal-sketch grayscale aesthetic.",
            "Transcribe the Greek recitation into timestamped SRT.",
            "Compose the restyled reading with Greek captions burned onto the charcoal frames.",
        ],
    },
    {
        "user_goal": "Restyle this Swedish IKEA-assembly clip as a Cocomelon 3D kid-show and add Swedish subtitles.",
        "rationale": (
            "Swedish IKEA-assembly clip + Cocomelon 3D kid-show style + Swedish (monolingual) "
            "captions. IntakeVideoAgent → StyleTransferAgent (Cocomelon 3D) → "
            "TranscriptionAgent (Swedish) → CompositorAgent (Swedish SRT)."
        ),
        "intents": [
            "Ingest the Swedish IKEA-assembly clip into the workspace.",
            "Restyle the assembly footage into a Cocomelon vibrant 3D kid-show aesthetic.",
            "Transcribe the Swedish narration into timestamped SRT.",
            "Compose the restyled clip with Swedish captions burned onto the Cocomelon frames.",
        ],
    },
    {
        "user_goal": "Please apply a watercolor-children's-book style to this Hebrew prayer-service and add Hebrew subtitles.",
        "rationale": (
            "Hebrew prayer service + watercolor children's-book style + Hebrew (monolingual) "
            "captions. IntakeVideoAgent → StyleTransferAgent (children's-book watercolor) → "
            "TranscriptionAgent (Hebrew) → CompositorAgent (Hebrew SRT)."
        ),
        "intents": [
            "Ingest the Hebrew prayer-service clip into the workspace.",
            "Restyle the service footage into a children's-book watercolor illustration.",
            "Transcribe the Hebrew liturgy into timestamped SRT.",
            "Compose the restyled service with Hebrew captions burned onto the watercolor frames.",
        ],
    },
    {
        "user_goal": "Restyle this Ukrainian folk-dance-festival clip as a 1970s-disco funk look and add Ukrainian captions.",
        "rationale": (
            "Ukrainian folk-dance festival + 1970s-disco funk style + Ukrainian (monolingual) "
            "captions. IntakeVideoAgent → StyleTransferAgent (1970s disco) → "
            "TranscriptionAgent (Ukrainian) → CompositorAgent (Ukrainian SRT)."
        ),
        "intents": [
            "Ingest the Ukrainian folk-dance festival clip into the workspace.",
            "Restyle the festival footage into a 1970s-disco funk visual aesthetic.",
            "Transcribe the Ukrainian narration into timestamped SRT.",
            "Compose the restyled festival clip with Ukrainian captions burned onto the disco frames.",
        ],
    },
    {
        "user_goal": "Please apply a Henri Rousseau jungle-painting style to this Norwegian forest-walk and add Norwegian captions.",
        "rationale": (
            "Norwegian forest walk + Henri Rousseau jungle-painting style + Norwegian "
            "(monolingual) captions. IntakeVideoAgent → StyleTransferAgent (Rousseau jungle) "
            "→ TranscriptionAgent (Norwegian) → CompositorAgent (Norwegian SRT)."
        ),
        "intents": [
            "Ingest the Norwegian forest-walk clip into the workspace.",
            "Restyle the forest-walk footage into a Henri Rousseau jungle-painting aesthetic.",
            "Transcribe the Norwegian narration into timestamped SRT.",
            "Compose the restyled walk with Norwegian captions burned onto the Rousseau frames.",
        ],
    },
    {
        "user_goal": "Restyle this Cantonese dim-sum tutorial as a Warhol pop-art screen-print and add Cantonese captions.",
        "rationale": (
            "Cantonese dim-sum tutorial + Warhol pop-art style + Cantonese (monolingual) "
            "captions. IntakeVideoAgent → StyleTransferAgent (Warhol pop-art) → "
            "TranscriptionAgent (Cantonese) → CompositorAgent (Cantonese SRT)."
        ),
        "intents": [
            "Ingest the Cantonese dim-sum tutorial into the workspace.",
            "Restyle the tutorial footage into a Warhol pop-art screen-print aesthetic.",
            "Transcribe the Cantonese tutorial narration into timestamped SRT.",
            "Compose the restyled tutorial with Cantonese captions burned onto the Warhol frames.",
        ],
    },
    {
        "user_goal": "Please apply a stained-glass cathedral-window look to this Tagalog church-choir clip and add Tagalog subtitles.",
        "rationale": (
            "Tagalog church-choir clip + stained-glass style + Tagalog (monolingual) captions. "
            "IntakeVideoAgent → StyleTransferAgent (stained-glass) → TranscriptionAgent "
            "(Tagalog) → CompositorAgent (Tagalog SRT)."
        ),
        "intents": [
            "Ingest the Tagalog church-choir clip into the workspace.",
            "Restyle the choir footage into a stained-glass cathedral-window aesthetic.",
            "Transcribe the Tagalog choir introduction and announcements into timestamped SRT.",
            "Compose the restyled choir clip with Tagalog captions burned onto the stained-glass frames.",
        ],
    },
    {
        "user_goal": "Restyle this Bengali cultural-dance performance as a Mondrian primary-color geometric abstraction and add Bengali captions.",
        "rationale": (
            "Bengali cultural dance + Mondrian primary-color geometric style + Bengali "
            "(monolingual) captions. IntakeVideoAgent → StyleTransferAgent (Mondrian "
            "geometric) → TranscriptionAgent (Bengali) → CompositorAgent (Bengali SRT)."
        ),
        "intents": [
            "Ingest the Bengali cultural-dance performance clip into the workspace.",
            "Restyle the performance into a Mondrian primary-color geometric abstraction.",
            "Transcribe the Bengali narration into timestamped SRT.",
            "Compose the restyled performance with Bengali captions burned onto the Mondrian frames.",
        ],
    },
    {
        "user_goal": "Please apply a Super-8 home-movie aesthetic to this Malay wedding-ceremony clip and add Malay subtitles.",
        "rationale": (
            "Malay wedding ceremony + Super-8 home-movie aesthetic + Malay (monolingual) "
            "captions. IntakeVideoAgent → StyleTransferAgent (Super-8 home-movie) → "
            "TranscriptionAgent (Malay) → CompositorAgent (Malay SRT)."
        ),
        "intents": [
            "Ingest the Malay wedding-ceremony clip into the workspace.",
            "Restyle the ceremony footage into a vintage Super-8 home-movie aesthetic with light leaks.",
            "Transcribe the Malay ceremony dialogue into timestamped SRT.",
            "Compose the restyled ceremony with Malay captions burned onto the Super-8 frames.",
        ],
    },
    {
        "user_goal": "Restyle this Romanian folk-music performance as an art-nouveau Mucha ornamental aesthetic and add Romanian subtitles.",
        "rationale": (
            "Romanian folk-music performance + art-nouveau Mucha + Romanian (monolingual) "
            "captions. IntakeVideoAgent → StyleTransferAgent (Mucha art-nouveau) → "
            "TranscriptionAgent (Romanian) → CompositorAgent (Romanian SRT)."
        ),
        "intents": [
            "Ingest the Romanian folk-music performance clip into the workspace.",
            "Restyle the performance into an art-nouveau Mucha ornamental aesthetic.",
            "Transcribe the Romanian performance introductions into timestamped SRT.",
            "Compose the restyled performance with Romanian captions burned onto the Mucha frames.",
        ],
    },
    {
        "user_goal": "Please apply a Dali surrealist dreamscape style to this Persian poetry-reading and add Persian captions.",
        "rationale": (
            "Persian poetry reading + Dali surrealist dreamscape + Persian (monolingual) "
            "captions. IntakeVideoAgent → StyleTransferAgent (Dali surrealist) → "
            "TranscriptionAgent (Persian) → CompositorAgent (Persian SRT)."
        ),
        "intents": [
            "Ingest the Persian poetry-reading clip into the workspace.",
            "Restyle the reading footage into a Dali-style surrealist dreamscape aesthetic.",
            "Transcribe the Persian recitation into timestamped SRT.",
            "Compose the restyled reading with Persian captions burned onto the surrealist frames.",
        ],
    },
    {
        "user_goal": "Restyle this Hungarian goulash-demo as a sumi-e ink-painting and add Hungarian subtitles.",
        "rationale": (
            "Hungarian goulash demo + sumi-e ink-painting style + Hungarian (monolingual) "
            "captions. IntakeVideoAgent → StyleTransferAgent (sumi-e) → TranscriptionAgent "
            "(Hungarian) → CompositorAgent (Hungarian SRT)."
        ),
        "intents": [
            "Ingest the Hungarian goulash-demo clip into the workspace.",
            "Restyle the demo footage into a Japanese sumi-e ink-painting aesthetic.",
            "Transcribe the Hungarian narration into timestamped SRT.",
            "Compose the restyled demo with Hungarian captions burned onto the sumi-e frames.",
        ],
    },
    {
        "user_goal": "Please apply a Wes Anderson symmetric pastel style to this Danish architecture-tour and add Danish captions.",
        "rationale": (
            "Danish architecture tour + Wes Anderson pastel symmetry + Danish (monolingual) "
            "captions. IntakeVideoAgent → StyleTransferAgent (Wes Anderson) → "
            "TranscriptionAgent (Danish) → CompositorAgent (Danish SRT)."
        ),
        "intents": [
            "Ingest the Danish architecture-tour clip into the workspace.",
            "Restyle the tour footage into a Wes Anderson pastel-symmetry aesthetic.",
            "Transcribe the Danish narration into timestamped SRT.",
            "Compose the restyled tour with Danish captions burned onto the pastel frames.",
        ],
    },
    {
        "user_goal": "Restyle this Swahili safari-guide commentary as a Moebius comic-book look and add Swahili captions.",
        "rationale": (
            "Swahili safari-guide + Moebius comic-book style + Swahili (monolingual) captions. "
            "IntakeVideoAgent → StyleTransferAgent (Moebius comic) → TranscriptionAgent "
            "(Swahili) → CompositorAgent (Swahili SRT)."
        ),
        "intents": [
            "Ingest the Swahili safari-guide commentary into the workspace.",
            "Restyle the safari commentary footage into a Moebius comic-book aesthetic.",
            "Transcribe the Swahili guide's narration into timestamped SRT.",
            "Compose the restyled commentary with Swahili captions burned onto the comic-book frames.",
        ],
    },
]
