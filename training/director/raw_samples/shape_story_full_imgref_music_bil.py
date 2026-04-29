"""Shape: story_full_imgref_music_bil — IntakeImage → BriefEnricher → Narration → Illustration → Narrator → Music → AudioMix → Translation → Compositor.

Illustrated storytelling WITH image reference upload + music + bilingual subtitle, NO ambience.
Per-sample tailored: each rationale and each intent references the user_goal's protagonist + image / audio / subtitle asks."""
from __future__ import annotations


SAMPLES: list[dict] = [
    {
        "user_goal": 'Using the uploaded character portrait of a fox protagonist, produce an English-Mandarin bilingual illustrated audiobook of a folk tale where the fox outsmarts the tiger at the ancient river, narrated in English with a gentle koto-and-flute background score.',
        "rationale": (
            "Long-form illustrated-storytelling brief with reference image upload + music + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief. IntakeImageAgent ingests the user's uploaded image as a caption-rich workspace artifact. BriefEnricherAgent folds the image's visual description into the user's text brief. NarrationAgent writes the narrator script (using the enriched brief). IllustrationAgent generates illustrations matching the reference style. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AudioMixAgent layers music under narrator. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film). TranscriptionAgent rejected — narrator already produces a timed SRT."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Polish the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Generate one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Using the uploaded character portrait of a shepherdess, produce an English-Spanish bilingual illustrated audiobook of a folk tale where the shepherdess guides her flock through the dreaming valley, narrated in English with a Celtic harp background score.',
        "rationale": (
            "Long-form illustrated-storytelling brief with reference image upload + music + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief. IntakeImageAgent ingests the user's uploaded image as a caption-rich workspace artifact. BriefEnricherAgent folds the image's visual description into the user's text brief. NarrationAgent writes the narrator script (using the enriched brief). IllustrationAgent generates illustrations matching the reference style. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AudioMixAgent layers music under narrator. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film). TranscriptionAgent rejected — narrator already produces a timed SRT."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Outline the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Plan one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": "Using the uploaded character portrait of a paper-boat builder, produce an English-French bilingual illustrated audiobook of a folk tale where the child's paper boats sail to the island of forgotten wishes, narrated in English with a soft piano background score.",
        "rationale": (
            "Long-form illustrated-storytelling brief with reference image upload + music + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief. IntakeImageAgent ingests the user's uploaded image as a caption-rich workspace artifact. BriefEnricherAgent folds the image's visual description into the user's text brief. NarrationAgent writes the narrator script (using the enriched brief). IllustrationAgent generates illustrations matching the reference style. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AudioMixAgent layers music under narrator. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film). TranscriptionAgent rejected — narrator already produces a timed SRT."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Draft the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Render one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Using the uploaded character portrait of a desert fox, produce an English-Arabic bilingual illustrated audiobook of a folk tale where the desert fox finds the last oasis of the singing sands, narrated in English with a ney-and-oud background score.',
        "rationale": (
            "Long-form illustrated-storytelling brief with reference image upload + music + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief. IntakeImageAgent ingests the user's uploaded image as a caption-rich workspace artifact. BriefEnricherAgent folds the image's visual description into the user's text brief. NarrationAgent writes the narrator script (using the enriched brief). IllustrationAgent generates illustrations matching the reference style. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AudioMixAgent layers music under narrator. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film). TranscriptionAgent rejected — narrator already produces a timed SRT."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Compose the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Design one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Using the uploaded character portrait of a mountain-goat kid, produce an English-German bilingual illustrated audiobook of a folk tale where the goat-kid saves her herd from the ice-giant, narrated in English with a Alpine zither background score.',
        "rationale": (
            "Long-form illustrated-storytelling brief with reference image upload + music + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief. IntakeImageAgent ingests the user's uploaded image as a caption-rich workspace artifact. BriefEnricherAgent folds the image's visual description into the user's text brief. NarrationAgent writes the narrator script (using the enriched brief). IllustrationAgent generates illustrations matching the reference style. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AudioMixAgent layers music under narrator. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film). TranscriptionAgent rejected — narrator already produces a timed SRT."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Polish the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Generate one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Using the uploaded character portrait of a woodland unicorn, produce an English-Russian bilingual illustrated audiobook of a folk tale where the unicorn hides from greedy hunters in the starlit glade, narrated in English with a dreamy harp-and-strings background score.',
        "rationale": (
            "Long-form illustrated-storytelling brief with reference image upload + music + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief. IntakeImageAgent ingests the user's uploaded image as a caption-rich workspace artifact. BriefEnricherAgent folds the image's visual description into the user's text brief. NarrationAgent writes the narrator script (using the enriched brief). IllustrationAgent generates illustrations matching the reference style. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AudioMixAgent layers music under narrator. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film). TranscriptionAgent rejected — narrator already produces a timed SRT."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Outline the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Plan one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": "Using the uploaded character portrait of a forest dragon-child, produce an English-Italian bilingual illustrated audiobook of a folk tale where the young dragon befriends the blacksmith's daughter, narrated in English with a gentle choir-and-harp background score.",
        "rationale": (
            "Long-form illustrated-storytelling brief with reference image upload + music + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief. IntakeImageAgent ingests the user's uploaded image as a caption-rich workspace artifact. BriefEnricherAgent folds the image's visual description into the user's text brief. NarrationAgent writes the narrator script (using the enriched brief). IllustrationAgent generates illustrations matching the reference style. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AudioMixAgent layers music under narrator. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film). TranscriptionAgent rejected — narrator already produces a timed SRT."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Draft the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Render one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Using the uploaded character portrait of a clever squirrel, produce an English-Portuguese bilingual illustrated audiobook of a folk tale where the squirrel delivers acorns to every forest-dweller before winter, narrated in English with a whimsical mandolin background score.',
        "rationale": (
            "Long-form illustrated-storytelling brief with reference image upload + music + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief. IntakeImageAgent ingests the user's uploaded image as a caption-rich workspace artifact. BriefEnricherAgent folds the image's visual description into the user's text brief. NarrationAgent writes the narrator script (using the enriched brief). IllustrationAgent generates illustrations matching the reference style. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AudioMixAgent layers music under narrator. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film). TranscriptionAgent rejected — narrator already produces a timed SRT."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Compose the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Design one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Using the uploaded character portrait of a star-cat, produce an English-Korean bilingual illustrated audiobook of a folk tale where the star-cat walks between dreams carrying lost children home, narrated in English with a soft celesta-and-chimes background score.',
        "rationale": (
            "Long-form illustrated-storytelling brief with reference image upload + music + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief. IntakeImageAgent ingests the user's uploaded image as a caption-rich workspace artifact. BriefEnricherAgent folds the image's visual description into the user's text brief. NarrationAgent writes the narrator script (using the enriched brief). IllustrationAgent generates illustrations matching the reference style. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AudioMixAgent layers music under narrator. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film). TranscriptionAgent rejected — narrator already produces a timed SRT."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Polish the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Generate one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Using the uploaded character portrait of a sea-horse, produce an English-Japanese bilingual illustrated audiobook of a folk tale where the sea-horse finds a pearl of truth hidden on the seabed, narrated in English with a gentle underwater harp background score.',
        "rationale": (
            "Long-form illustrated-storytelling brief with reference image upload + music + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief. IntakeImageAgent ingests the user's uploaded image as a caption-rich workspace artifact. BriefEnricherAgent folds the image's visual description into the user's text brief. NarrationAgent writes the narrator script (using the enriched brief). IllustrationAgent generates illustrations matching the reference style. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AudioMixAgent layers music under narrator. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film). TranscriptionAgent rejected — narrator already produces a timed SRT."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Outline the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Plan one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": "Using the uploaded character portrait of a wandering bard, produce an English-Irish bilingual illustrated audiobook of a folk tale where the bard's flute tames even the wild wolves of the moor, narrated in English with a soft pennywhistle-and-bodhran background score.",
        "rationale": (
            "Long-form illustrated-storytelling brief with reference image upload + music + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief. IntakeImageAgent ingests the user's uploaded image as a caption-rich workspace artifact. BriefEnricherAgent folds the image's visual description into the user's text brief. NarrationAgent writes the narrator script (using the enriched brief). IllustrationAgent generates illustrations matching the reference style. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AudioMixAgent layers music under narrator. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film). TranscriptionAgent rejected — narrator already produces a timed SRT."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Draft the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Render one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Using the uploaded character portrait of a golden deer, produce an English-Greek bilingual illustrated audiobook of a folk tale where the deer guides a grieving prince through the silver forest, narrated in English with a tender strings-and-flute background score.',
        "rationale": (
            "Long-form illustrated-storytelling brief with reference image upload + music + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief. IntakeImageAgent ingests the user's uploaded image as a caption-rich workspace artifact. BriefEnricherAgent folds the image's visual description into the user's text brief. NarrationAgent writes the narrator script (using the enriched brief). IllustrationAgent generates illustrations matching the reference style. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AudioMixAgent layers music under narrator. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film). TranscriptionAgent rejected — narrator already produces a timed SRT."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Compose the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Design one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": "Using the uploaded character portrait of a child of the north wind, produce an English-Finnish bilingual illustrated audiobook of a folk tale where the child brings winter's kindness to the frozen village, narrated in English with a soft choir-and-bells background score.",
        "rationale": (
            "Long-form illustrated-storytelling brief with reference image upload + music + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief. IntakeImageAgent ingests the user's uploaded image as a caption-rich workspace artifact. BriefEnricherAgent folds the image's visual description into the user's text brief. NarrationAgent writes the narrator script (using the enriched brief). IllustrationAgent generates illustrations matching the reference style. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AudioMixAgent layers music under narrator. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film). TranscriptionAgent rejected — narrator already produces a timed SRT."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Polish the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Generate one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": "Using the uploaded character portrait of an inky octopus, produce an English-Turkish bilingual illustrated audiobook of a folk tale where the octopus draws a mural of the ocean's secret memories, narrated in English with a gentle waterphone-and-piano background score.",
        "rationale": (
            "Long-form illustrated-storytelling brief with reference image upload + music + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief. IntakeImageAgent ingests the user's uploaded image as a caption-rich workspace artifact. BriefEnricherAgent folds the image's visual description into the user's text brief. NarrationAgent writes the narrator script (using the enriched brief). IllustrationAgent generates illustrations matching the reference style. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AudioMixAgent layers music under narrator. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film). TranscriptionAgent rejected — narrator already produces a timed SRT."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Outline the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Plan one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Using the uploaded character portrait of a silver fish, produce an English-Vietnamese bilingual illustrated audiobook of a folk tale where the silver fish swims upstream to carry a wish to the mountain god, narrated in English with a soft guzheng-and-flute background score.',
        "rationale": (
            "Long-form illustrated-storytelling brief with reference image upload + music + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief. IntakeImageAgent ingests the user's uploaded image as a caption-rich workspace artifact. BriefEnricherAgent folds the image's visual description into the user's text brief. NarrationAgent writes the narrator script (using the enriched brief). IllustrationAgent generates illustrations matching the reference style. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AudioMixAgent layers music under narrator. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film). TranscriptionAgent rejected — narrator already produces a timed SRT."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Draft the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Render one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Using the uploaded character portrait of a little snow-crane, produce an English-Chinese bilingual illustrated audiobook of a folk tale where the crane teaches frozen children how to find warmth in winter, narrated in English with a gentle koto background score.',
        "rationale": (
            "Long-form illustrated-storytelling brief with reference image upload + music + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief. IntakeImageAgent ingests the user's uploaded image as a caption-rich workspace artifact. BriefEnricherAgent folds the image's visual description into the user's text brief. NarrationAgent writes the narrator script (using the enriched brief). IllustrationAgent generates illustrations matching the reference style. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AudioMixAgent layers music under narrator. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film). TranscriptionAgent rejected — narrator already produces a timed SRT."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Compose the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Design one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Using the uploaded character portrait of a cosmic whale, produce an English-Dutch bilingual illustrated audiobook of a folk tale where the whale carries forgotten constellations back to the night sky, narrated in English with a dreamy ambient-synths background score.',
        "rationale": (
            "Long-form illustrated-storytelling brief with reference image upload + music + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief. IntakeImageAgent ingests the user's uploaded image as a caption-rich workspace artifact. BriefEnricherAgent folds the image's visual description into the user's text brief. NarrationAgent writes the narrator script (using the enriched brief). IllustrationAgent generates illustrations matching the reference style. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AudioMixAgent layers music under narrator. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film). TranscriptionAgent rejected — narrator already produces a timed SRT."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Polish the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Generate one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": "Using the uploaded character portrait of a bumblebee child, produce an English-Swedish bilingual illustrated audiobook of a folk tale where the bee-child gathers sunlight to light her village's winter lanterns, narrated in English with a gentle Celtic harp background score.",
        "rationale": (
            "Long-form illustrated-storytelling brief with reference image upload + music + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief. IntakeImageAgent ingests the user's uploaded image as a caption-rich workspace artifact. BriefEnricherAgent folds the image's visual description into the user's text brief. NarrationAgent writes the narrator script (using the enriched brief). IllustrationAgent generates illustrations matching the reference style. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AudioMixAgent layers music under narrator. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film). TranscriptionAgent rejected — narrator already produces a timed SRT."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Outline the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Plan one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Using the uploaded character portrait of a moon-rabbit, produce an English-Hindi bilingual illustrated audiobook of a folk tale where the moon-rabbit pounds stars into soft bread for sleeping children, narrated in English with a delicate celesta background score.',
        "rationale": (
            "Long-form illustrated-storytelling brief with reference image upload + music + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief. IntakeImageAgent ingests the user's uploaded image as a caption-rich workspace artifact. BriefEnricherAgent folds the image's visual description into the user's text brief. NarrationAgent writes the narrator script (using the enriched brief). IllustrationAgent generates illustrations matching the reference style. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AudioMixAgent layers music under narrator. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film). TranscriptionAgent rejected — narrator already produces a timed SRT."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Draft the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Render one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Using the uploaded character portrait of a storm-petrel, produce an English-Thai bilingual illustrated audiobook of a folk tale where the petrel guides lost souls across the stormy sea to shore, narrated in English with a haunting cello-and-choir background score.',
        "rationale": (
            "Long-form illustrated-storytelling brief with reference image upload + music + bilingual subtitle. the protagonist's arc with user-uploaded reference image folded into the brief. IntakeImageAgent ingests the user's uploaded image as a caption-rich workspace artifact. BriefEnricherAgent folds the image's visual description into the user's text brief. NarrationAgent writes the narrator script (using the enriched brief). IllustrationAgent generates illustrations matching the reference style. NarratorAgent renders the voiceover + source-language SRT. MusicAgent composes the music score. AudioMixAgent layers music under narrator. TranslationAgent translates the SRT. CompositorAgent muxes the slideshow with mixed audio + bilingual subtitles. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film). TranscriptionAgent rejected — narrator already produces a timed SRT."
        ),
        "intents": [
            "Ingest the user's uploaded reference image into the workspace as a caption-rich character / location / style reference artifact.",
            "Fold the image's visual description into the user's text brief, producing one unified enriched brief.",
            "Compose the enriched brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with image_prompt referencing the uploaded reference style.",
            "Design one illustration per narrator segment in the reference-image style, preserving the the protagonist story's visual identity across segments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — reference-styled illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
]
