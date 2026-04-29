"""Shape: story_ultra — IntakeImage → BriefEnricher → Narration → Illustration → Narrator → Music → Ambience → AudioMix → Translation → Compositor.

Full ultra storytelling chain — image reference + music + ambience + bilingual subtitle.
Per-sample tailored: each rationale and each intent references the user_goal's protagonist + all asks."""
from __future__ import annotations


SAMPLES: list[dict] = [
    {
        "user_goal": 'Using this uploaded portrait of a fox-protagonist, make a bilingual English-Chinese illustrated audiobook of the folk tale where the fox and the crow share a riddle at dusk, with a gentle flute and forest-dusk ambient (distant owl, wind) under the narrator.',
        "rationale": (
            "Long-form illustrated-storytelling brief — full ultra chain: image-reference upload + music + ambience + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief, both audio layers (music + ambience), and bilingual subtitle. IntakeImageAgent ingests the upload. BriefEnricherAgent folds the image visual into the brief. NarrationAgent writes the narrator script (enriched). IllustrationAgent generates reference-styled illustrations. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AmbienceAgent generates the ambient bed. AudioMixAgent combines narrator + music + ambience into one final mixed wav. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), TranscriptionAgent (narrator already produces a timed SRT)."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Polish the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Generate one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music + ambience into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio (narrator + music + ambience), both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Using this uploaded portrait of a shepherdess, make a bilingual English-Spanish illustrated audiobook of the folk tale where she crosses the dreaming valley to find her lost lamb, with a Celtic harp and mountain-valley ambient (distant sheep, wind) under the narrator.',
        "rationale": (
            "Long-form illustrated-storytelling brief — full ultra chain: image-reference upload + music + ambience + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief, both audio layers (music + ambience), and bilingual subtitle. IntakeImageAgent ingests the upload. BriefEnricherAgent folds the image visual into the brief. NarrationAgent writes the narrator script (enriched). IllustrationAgent generates reference-styled illustrations. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AmbienceAgent generates the ambient bed. AudioMixAgent combines narrator + music + ambience into one final mixed wav. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), TranscriptionAgent (narrator already produces a timed SRT)."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Outline the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Plan one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music + ambience into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio (narrator + music + ambience), both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Using this uploaded portrait of a grandmother-weaver, make a bilingual English-Italian illustrated audiobook of the folk tale where her woven shawls hold centuries of family memories, with a gentle mandolin and Tuscan-courtyard ambient (cicadas, distant bells) under the narrator.',
        "rationale": (
            "Long-form illustrated-storytelling brief — full ultra chain: image-reference upload + music + ambience + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief, both audio layers (music + ambience), and bilingual subtitle. IntakeImageAgent ingests the upload. BriefEnricherAgent folds the image visual into the brief. NarrationAgent writes the narrator script (enriched). IllustrationAgent generates reference-styled illustrations. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AmbienceAgent generates the ambient bed. AudioMixAgent combines narrator + music + ambience into one final mixed wav. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), TranscriptionAgent (narrator already produces a timed SRT)."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Draft the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Render one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music + ambience into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio (narrator + music + ambience), both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Using this uploaded portrait of a sea-witch, make a bilingual English-Portuguese illustrated audiobook of the folk tale where she returns lost letters to widowed fishermen, with a haunting celesta and stormy-coast ambient (waves, wind) under the narrator.',
        "rationale": (
            "Long-form illustrated-storytelling brief — full ultra chain: image-reference upload + music + ambience + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief, both audio layers (music + ambience), and bilingual subtitle. IntakeImageAgent ingests the upload. BriefEnricherAgent folds the image visual into the brief. NarrationAgent writes the narrator script (enriched). IllustrationAgent generates reference-styled illustrations. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AmbienceAgent generates the ambient bed. AudioMixAgent combines narrator + music + ambience into one final mixed wav. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), TranscriptionAgent (narrator already produces a timed SRT)."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Compose the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Design one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music + ambience into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio (narrator + music + ambience), both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Using this uploaded portrait of a little snow-crane, make a bilingual English-Japanese illustrated audiobook of the folk tale where the crane teaches winter children how to find warmth, with a gentle koto and snowy-field ambient (soft snow, distant crows) under the narrator.',
        "rationale": (
            "Long-form illustrated-storytelling brief — full ultra chain: image-reference upload + music + ambience + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief, both audio layers (music + ambience), and bilingual subtitle. IntakeImageAgent ingests the upload. BriefEnricherAgent folds the image visual into the brief. NarrationAgent writes the narrator script (enriched). IllustrationAgent generates reference-styled illustrations. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AmbienceAgent generates the ambient bed. AudioMixAgent combines narrator + music + ambience into one final mixed wav. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), TranscriptionAgent (narrator already produces a timed SRT)."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Polish the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Generate one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music + ambience into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio (narrator + music + ambience), both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Using this uploaded portrait of a wise bear, make a bilingual English-German illustrated audiobook of the folk tale where the bear shares his honey with every hungry forest creature, with a soft acoustic guitar and forest-summer ambient (birds, insects, creek) under the narrator.',
        "rationale": (
            "Long-form illustrated-storytelling brief — full ultra chain: image-reference upload + music + ambience + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief, both audio layers (music + ambience), and bilingual subtitle. IntakeImageAgent ingests the upload. BriefEnricherAgent folds the image visual into the brief. NarrationAgent writes the narrator script (enriched). IllustrationAgent generates reference-styled illustrations. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AmbienceAgent generates the ambient bed. AudioMixAgent combines narrator + music + ambience into one final mixed wav. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), TranscriptionAgent (narrator already produces a timed SRT)."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Outline the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Plan one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music + ambience into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio (narrator + music + ambience), both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Using this uploaded portrait of a desert-nomad girl, make a bilingual English-Arabic illustrated audiobook of the folk tale where the nomad-girl finds the last oasis of the singing sands, with a ney-and-oud and desert-wind ambient (sand whispers, camel bells) under the narrator.',
        "rationale": (
            "Long-form illustrated-storytelling brief — full ultra chain: image-reference upload + music + ambience + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief, both audio layers (music + ambience), and bilingual subtitle. IntakeImageAgent ingests the upload. BriefEnricherAgent folds the image visual into the brief. NarrationAgent writes the narrator script (enriched). IllustrationAgent generates reference-styled illustrations. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AmbienceAgent generates the ambient bed. AudioMixAgent combines narrator + music + ambience into one final mixed wav. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), TranscriptionAgent (narrator already produces a timed SRT)."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Draft the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Render one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music + ambience into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio (narrator + music + ambience), both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Using this uploaded portrait of a gentle unicorn, make a bilingual English-Russian illustrated audiobook of the folk tale where the unicorn hides from hunters in the starlit glade, with a dreamy harp-and-strings and night-glade ambient (crickets, distant owl) under the narrator.',
        "rationale": (
            "Long-form illustrated-storytelling brief — full ultra chain: image-reference upload + music + ambience + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief, both audio layers (music + ambience), and bilingual subtitle. IntakeImageAgent ingests the upload. BriefEnricherAgent folds the image visual into the brief. NarrationAgent writes the narrator script (enriched). IllustrationAgent generates reference-styled illustrations. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AmbienceAgent generates the ambient bed. AudioMixAgent combines narrator + music + ambience into one final mixed wav. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), TranscriptionAgent (narrator already produces a timed SRT)."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Compose the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Design one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music + ambience into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio (narrator + music + ambience), both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of a young shamaness, make a bilingual English-Mongolian illustrated audiobook of the folk tale where the shamaness's dream-drum heals the village's sorrows, with a tribal-drum fusion and tundra-night ambient (wind, distant wolves) under the narrator.",
        "rationale": (
            "Long-form illustrated-storytelling brief — full ultra chain: image-reference upload + music + ambience + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief, both audio layers (music + ambience), and bilingual subtitle. IntakeImageAgent ingests the upload. BriefEnricherAgent folds the image visual into the brief. NarrationAgent writes the narrator script (enriched). IllustrationAgent generates reference-styled illustrations. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AmbienceAgent generates the ambient bed. AudioMixAgent combines narrator + music + ambience into one final mixed wav. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), TranscriptionAgent (narrator already produces a timed SRT)."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Polish the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Generate one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music + ambience into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio (narrator + music + ambience), both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Using this uploaded portrait of a koi-carp, make a bilingual English-Mandarin illustrated audiobook of the folk tale where the koi climbs the waterfall to become a dragon, with a gentle guzheng and river ambient (cascading water, birds) under the narrator.',
        "rationale": (
            "Long-form illustrated-storytelling brief — full ultra chain: image-reference upload + music + ambience + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief, both audio layers (music + ambience), and bilingual subtitle. IntakeImageAgent ingests the upload. BriefEnricherAgent folds the image visual into the brief. NarrationAgent writes the narrator script (enriched). IllustrationAgent generates reference-styled illustrations. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AmbienceAgent generates the ambient bed. AudioMixAgent combines narrator + music + ambience into one final mixed wav. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), TranscriptionAgent (narrator already produces a timed SRT)."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Outline the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Plan one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music + ambience into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio (narrator + music + ambience), both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Using this uploaded portrait of a firefly child, make a bilingual English-Korean illustrated audiobook of the folk tale where the firefly gathers sunlight in winter to warm his village, with a gentle celesta-and-chimes and summer-meadow ambient (cicadas, distant thunder) under the narrator.',
        "rationale": (
            "Long-form illustrated-storytelling brief — full ultra chain: image-reference upload + music + ambience + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief, both audio layers (music + ambience), and bilingual subtitle. IntakeImageAgent ingests the upload. BriefEnricherAgent folds the image visual into the brief. NarrationAgent writes the narrator script (enriched). IllustrationAgent generates reference-styled illustrations. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AmbienceAgent generates the ambient bed. AudioMixAgent combines narrator + music + ambience into one final mixed wav. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), TranscriptionAgent (narrator already produces a timed SRT)."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Draft the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Render one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music + ambience into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio (narrator + music + ambience), both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Using this uploaded portrait of a moon-rabbit, make a bilingual English-Hindi illustrated audiobook of the folk tale where the moon-rabbit pounds stars into bread for sleeping children, with a soft music-box and moonlit-meadow ambient (owl, crickets, distant wind) under the narrator.',
        "rationale": (
            "Long-form illustrated-storytelling brief — full ultra chain: image-reference upload + music + ambience + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief, both audio layers (music + ambience), and bilingual subtitle. IntakeImageAgent ingests the upload. BriefEnricherAgent folds the image visual into the brief. NarrationAgent writes the narrator script (enriched). IllustrationAgent generates reference-styled illustrations. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AmbienceAgent generates the ambient bed. AudioMixAgent combines narrator + music + ambience into one final mixed wav. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), TranscriptionAgent (narrator already produces a timed SRT)."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Compose the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Design one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music + ambience into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio (narrator + music + ambience), both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of a lighthouse-keeper's daughter, make a bilingual English-French illustrated audiobook of the folk tale where she guides ghost ships to their final resting place, with a gentle strings-and-flute and lighthouse-island ambient (waves, seagulls, fog-horn) under the narrator.",
        "rationale": (
            "Long-form illustrated-storytelling brief — full ultra chain: image-reference upload + music + ambience + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief, both audio layers (music + ambience), and bilingual subtitle. IntakeImageAgent ingests the upload. BriefEnricherAgent folds the image visual into the brief. NarrationAgent writes the narrator script (enriched). IllustrationAgent generates reference-styled illustrations. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AmbienceAgent generates the ambient bed. AudioMixAgent combines narrator + music + ambience into one final mixed wav. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), TranscriptionAgent (narrator already produces a timed SRT)."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Polish the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Generate one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music + ambience into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio (narrator + music + ambience), both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Using this uploaded portrait of a forest-spirit child, make a bilingual English-Swedish illustrated audiobook of the folk tale where the spirit teaches children to hear trees speak, with a soft woodwind-quartet and ancient-forest ambient (wind through oaks, distant birds) under the narrator.',
        "rationale": (
            "Long-form illustrated-storytelling brief — full ultra chain: image-reference upload + music + ambience + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief, both audio layers (music + ambience), and bilingual subtitle. IntakeImageAgent ingests the upload. BriefEnricherAgent folds the image visual into the brief. NarrationAgent writes the narrator script (enriched). IllustrationAgent generates reference-styled illustrations. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AmbienceAgent generates the ambient bed. AudioMixAgent combines narrator + music + ambience into one final mixed wav. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), TranscriptionAgent (narrator already produces a timed SRT)."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Outline the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Plan one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music + ambience into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio (narrator + music + ambience), both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of a young fisherman's apprentice, make a bilingual English-Norwegian illustrated audiobook of the folk tale where the apprentice learns to listen to the sea's oldest songs, with a gentle folk-guitar and seaside-dawn ambient (waves, distant fishing boats, gulls) under the narrator.",
        "rationale": (
            "Long-form illustrated-storytelling brief — full ultra chain: image-reference upload + music + ambience + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief, both audio layers (music + ambience), and bilingual subtitle. IntakeImageAgent ingests the upload. BriefEnricherAgent folds the image visual into the brief. NarrationAgent writes the narrator script (enriched). IllustrationAgent generates reference-styled illustrations. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AmbienceAgent generates the ambient bed. AudioMixAgent combines narrator + music + ambience into one final mixed wav. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), TranscriptionAgent (narrator already produces a timed SRT)."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Draft the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Render one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music + ambience into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio (narrator + music + ambience), both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Using this uploaded portrait of a little stargazer, make a bilingual English-Arabic illustrated audiobook of the folk tale where the stargazer maps new constellations for lost sailors, with a dreamy ambient-harp and night-sky ambient (gentle wind, distant crickets) under the narrator.',
        "rationale": (
            "Long-form illustrated-storytelling brief — full ultra chain: image-reference upload + music + ambience + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief, both audio layers (music + ambience), and bilingual subtitle. IntakeImageAgent ingests the upload. BriefEnricherAgent folds the image visual into the brief. NarrationAgent writes the narrator script (enriched). IllustrationAgent generates reference-styled illustrations. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AmbienceAgent generates the ambient bed. AudioMixAgent combines narrator + music + ambience into one final mixed wav. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), TranscriptionAgent (narrator already produces a timed SRT)."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Compose the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Design one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music + ambience into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio (narrator + music + ambience), both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Using this uploaded portrait of a patient river-turtle, make a bilingual English-Thai illustrated audiobook of the folk tale where the turtle carries wishes from the village to the sea, with a gentle pan-flute and river-morning ambient (water lap, distant birds) under the narrator.',
        "rationale": (
            "Long-form illustrated-storytelling brief — full ultra chain: image-reference upload + music + ambience + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief, both audio layers (music + ambience), and bilingual subtitle. IntakeImageAgent ingests the upload. BriefEnricherAgent folds the image visual into the brief. NarrationAgent writes the narrator script (enriched). IllustrationAgent generates reference-styled illustrations. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AmbienceAgent generates the ambient bed. AudioMixAgent combines narrator + music + ambience into one final mixed wav. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), TranscriptionAgent (narrator already produces a timed SRT)."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Polish the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Generate one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music + ambience into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio (narrator + music + ambience), both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of a young poet-bard, make a bilingual English-Greek illustrated audiobook of the folk tale where the bard's songs end the forest's long sorrow, with a soft lyre-and-flute and meadow-night ambient (wind, distant night-birds) under the narrator.",
        "rationale": (
            "Long-form illustrated-storytelling brief — full ultra chain: image-reference upload + music + ambience + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief, both audio layers (music + ambience), and bilingual subtitle. IntakeImageAgent ingests the upload. BriefEnricherAgent folds the image visual into the brief. NarrationAgent writes the narrator script (enriched). IllustrationAgent generates reference-styled illustrations. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AmbienceAgent generates the ambient bed. AudioMixAgent combines narrator + music + ambience into one final mixed wav. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), TranscriptionAgent (narrator already produces a timed SRT)."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Outline the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Plan one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music + ambience into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio (narrator + music + ambience), both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of a gentle hedgehog, make a bilingual English-Finnish illustrated audiobook of the folk tale where the hedgehog collects fallen stars to restore the meadow's light, with a soft acoustic harp and meadow-summer-night ambient (crickets, soft wind) under the narrator.",
        "rationale": (
            "Long-form illustrated-storytelling brief — full ultra chain: image-reference upload + music + ambience + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief, both audio layers (music + ambience), and bilingual subtitle. IntakeImageAgent ingests the upload. BriefEnricherAgent folds the image visual into the brief. NarrationAgent writes the narrator script (enriched). IllustrationAgent generates reference-styled illustrations. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AmbienceAgent generates the ambient bed. AudioMixAgent combines narrator + music + ambience into one final mixed wav. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), TranscriptionAgent (narrator already produces a timed SRT)."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Draft the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Render one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music + ambience into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio (narrator + music + ambience), both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": "Using this uploaded portrait of a dreaming dolphin, make a bilingual English-Dutch illustrated audiobook of the folk tale where the dolphin sings lost sailors' names so their families can grieve, with a gentle underwater-harp and deep-ocean ambient (muffled waves, distant whale song) under the narrator.",
        "rationale": (
            "Long-form illustrated-storytelling brief — full ultra chain: image-reference upload + music + ambience + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief, both audio layers (music + ambience), and bilingual subtitle. IntakeImageAgent ingests the upload. BriefEnricherAgent folds the image visual into the brief. NarrationAgent writes the narrator script (enriched). IllustrationAgent generates reference-styled illustrations. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AmbienceAgent generates the ambient bed. AudioMixAgent combines narrator + music + ambience into one final mixed wav. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), TranscriptionAgent (narrator already produces a timed SRT)."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Compose the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Design one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music + ambience into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio (narrator + music + ambience), both source and translated subtitles burned in.',
        ],
    },
]
