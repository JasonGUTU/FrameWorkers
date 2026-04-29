"""Shape: story_music_bilingual — Narration → Illustration → Narrator → Music → AudioMix → Translation → Compositor.

Illustrated storytelling WITH music + bilingual / foreign subtitle, NO ambience, NO image upload.
Per-sample tailored: each rationale and each intent references the user_goal's protagonist + audio + subtitle asks."""
from __future__ import annotations


SAMPLES: list[dict] = [
    {
        "user_goal": 'Create an English-Chinese bilingual illustrated audiobook of this Hans Christian Andersen fairytale with a gentle harp-and-celesta BGM.',
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + music score + bilingual / foreign-language subtitle ask. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav + source-language SRT (timed). MusicAgent composes the music score the user specified. AudioMixAgent layers the music under the narrator wav. TranslationAgent translates the source SRT into the target language preserving timing. CompositorAgent muxes the slideshow with mixed audio + both subtitle tracks. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), IntakeImage/BriefEnricher (no image upload). Reject TranscriptionAgent — narrator already produces a timed SRT."
        ),
        "intents": [
            "Polish the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Generate one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": "Create an English-German bilingual illustrated audiobook of this Grimm brothers' tale about Little Red Riding Hood with a soft pizzicato-strings BGM.",
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + music score + bilingual / foreign-language subtitle ask. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav + source-language SRT (timed). MusicAgent composes the music score the user specified. AudioMixAgent layers the music under the narrator wav. TranslationAgent translates the source SRT into the target language preserving timing. CompositorAgent muxes the slideshow with mixed audio + both subtitle tracks. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), IntakeImage/BriefEnricher (no image upload). Reject TranscriptionAgent — narrator already produces a timed SRT."
        ),
        "intents": [
            "Outline the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Plan one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Create an English-Mandarin bilingual illustrated audiobook of this Chinese folktale about the jade rabbit on the moon with a gentle guzheng BGM.',
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + music score + bilingual / foreign-language subtitle ask. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav + source-language SRT (timed). MusicAgent composes the music score the user specified. AudioMixAgent layers the music under the narrator wav. TranslationAgent translates the source SRT into the target language preserving timing. CompositorAgent muxes the slideshow with mixed audio + both subtitle tracks. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), IntakeImage/BriefEnricher (no image upload). Reject TranscriptionAgent — narrator already produces a timed SRT."
        ),
        "intents": [
            "Draft the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Render one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Create an English-Japanese bilingual illustrated audiobook of this Japanese fairytale about Momotaro with a soft shakuhachi-and-koto BGM.',
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + music score + bilingual / foreign-language subtitle ask. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav + source-language SRT (timed). MusicAgent composes the music score the user specified. AudioMixAgent layers the music under the narrator wav. TranslationAgent translates the source SRT into the target language preserving timing. CompositorAgent muxes the slideshow with mixed audio + both subtitle tracks. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), IntakeImage/BriefEnricher (no image upload). Reject TranscriptionAgent — narrator already produces a timed SRT."
        ),
        "intents": [
            "Compose the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Design one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Create an English-Russian bilingual illustrated audiobook of this Russian folktale about Snegurochka the snow maiden with a dreamy celesta BGM.',
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + music score + bilingual / foreign-language subtitle ask. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav + source-language SRT (timed). MusicAgent composes the music score the user specified. AudioMixAgent layers the music under the narrator wav. TranslationAgent translates the source SRT into the target language preserving timing. CompositorAgent muxes the slideshow with mixed audio + both subtitle tracks. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), IntakeImage/BriefEnricher (no image upload). Reject TranscriptionAgent — narrator already produces a timed SRT."
        ),
        "intents": [
            "Polish the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Generate one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Create an English-Korean bilingual illustrated audiobook of this Korean folktale about the clever rabbit and the dragon king with a gentle gayageum BGM.',
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + music score + bilingual / foreign-language subtitle ask. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav + source-language SRT (timed). MusicAgent composes the music score the user specified. AudioMixAgent layers the music under the narrator wav. TranslationAgent translates the source SRT into the target language preserving timing. CompositorAgent muxes the slideshow with mixed audio + both subtitle tracks. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), IntakeImage/BriefEnricher (no image upload). Reject TranscriptionAgent — narrator already produces a timed SRT."
        ),
        "intents": [
            "Outline the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Plan one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Create an English-French bilingual illustrated audiobook of this French fable by La Fontaine about the lion and the mouse with a Parisian musette BGM.',
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + music score + bilingual / foreign-language subtitle ask. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav + source-language SRT (timed). MusicAgent composes the music score the user specified. AudioMixAgent layers the music under the narrator wav. TranslationAgent translates the source SRT into the target language preserving timing. CompositorAgent muxes the slideshow with mixed audio + both subtitle tracks. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), IntakeImage/BriefEnricher (no image upload). Reject TranscriptionAgent — narrator already produces a timed SRT."
        ),
        "intents": [
            "Draft the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Render one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": "Create an English-Italian bilingual illustrated audiobook of this Italian folktale about Pulcinella's moonlight journey with a soft mandolin BGM.",
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + music score + bilingual / foreign-language subtitle ask. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav + source-language SRT (timed). MusicAgent composes the music score the user specified. AudioMixAgent layers the music under the narrator wav. TranslationAgent translates the source SRT into the target language preserving timing. CompositorAgent muxes the slideshow with mixed audio + both subtitle tracks. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), IntakeImage/BriefEnricher (no image upload). Reject TranscriptionAgent — narrator already produces a timed SRT."
        ),
        "intents": [
            "Compose the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Design one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Create an English-Arabic bilingual illustrated audiobook of this Arabian tale from the 1001 Nights with a gentle oud-and-ney BGM.',
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + music score + bilingual / foreign-language subtitle ask. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav + source-language SRT (timed). MusicAgent composes the music score the user specified. AudioMixAgent layers the music under the narrator wav. TranslationAgent translates the source SRT into the target language preserving timing. CompositorAgent muxes the slideshow with mixed audio + both subtitle tracks. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), IntakeImage/BriefEnricher (no image upload). Reject TranscriptionAgent — narrator already produces a timed SRT."
        ),
        "intents": [
            "Polish the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Generate one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Create an English-Hindi bilingual illustrated audiobook of this Indian Panchatantra fable about the turtle and the geese with a gentle sitar-and-tanpura BGM.',
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + music score + bilingual / foreign-language subtitle ask. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav + source-language SRT (timed). MusicAgent composes the music score the user specified. AudioMixAgent layers the music under the narrator wav. TranslationAgent translates the source SRT into the target language preserving timing. CompositorAgent muxes the slideshow with mixed audio + both subtitle tracks. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), IntakeImage/BriefEnricher (no image upload). Reject TranscriptionAgent — narrator already produces a timed SRT."
        ),
        "intents": [
            "Outline the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Plan one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Create an English-Irish bilingual illustrated audiobook of this Celtic folktale about the selkie with a gentle pennywhistle-and-harp BGM.',
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + music score + bilingual / foreign-language subtitle ask. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav + source-language SRT (timed). MusicAgent composes the music score the user specified. AudioMixAgent layers the music under the narrator wav. TranslationAgent translates the source SRT into the target language preserving timing. CompositorAgent muxes the slideshow with mixed audio + both subtitle tracks. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), IntakeImage/BriefEnricher (no image upload). Reject TranscriptionAgent — narrator already produces a timed SRT."
        ),
        "intents": [
            "Draft the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Render one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Create an English-Spanish bilingual illustrated audiobook of this Spanish folktale about the silver horseshoe with a soft Spanish guitar BGM.',
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + music score + bilingual / foreign-language subtitle ask. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav + source-language SRT (timed). MusicAgent composes the music score the user specified. AudioMixAgent layers the music under the narrator wav. TranslationAgent translates the source SRT into the target language preserving timing. CompositorAgent muxes the slideshow with mixed audio + both subtitle tracks. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), IntakeImage/BriefEnricher (no image upload). Reject TranscriptionAgent — narrator already produces a timed SRT."
        ),
        "intents": [
            "Compose the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Design one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Create an English-Swedish bilingual illustrated audiobook of this Scandinavian folktale about the trolls under the bridge with a Nordic-folk nyckelharpa BGM.',
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + music score + bilingual / foreign-language subtitle ask. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav + source-language SRT (timed). MusicAgent composes the music score the user specified. AudioMixAgent layers the music under the narrator wav. TranslationAgent translates the source SRT into the target language preserving timing. CompositorAgent muxes the slideshow with mixed audio + both subtitle tracks. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), IntakeImage/BriefEnricher (no image upload). Reject TranscriptionAgent — narrator already produces a timed SRT."
        ),
        "intents": [
            "Polish the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Generate one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Create an English-Thai bilingual illustrated audiobook of this Thai folktale about the rice grandmother with a gentle khaen-and-khim BGM.',
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + music score + bilingual / foreign-language subtitle ask. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav + source-language SRT (timed). MusicAgent composes the music score the user specified. AudioMixAgent layers the music under the narrator wav. TranslationAgent translates the source SRT into the target language preserving timing. CompositorAgent muxes the slideshow with mixed audio + both subtitle tracks. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), IntakeImage/BriefEnricher (no image upload). Reject TranscriptionAgent — narrator already produces a timed SRT."
        ),
        "intents": [
            "Outline the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Plan one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Create an English-Hawaiian bilingual illustrated audiobook of this Hawaiian legend about the rainbow sister with a gentle slack-key guitar BGM.',
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + music score + bilingual / foreign-language subtitle ask. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav + source-language SRT (timed). MusicAgent composes the music score the user specified. AudioMixAgent layers the music under the narrator wav. TranslationAgent translates the source SRT into the target language preserving timing. CompositorAgent muxes the slideshow with mixed audio + both subtitle tracks. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), IntakeImage/BriefEnricher (no image upload). Reject TranscriptionAgent — narrator already produces a timed SRT."
        ),
        "intents": [
            "Draft the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Render one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Create an English-Persian bilingual illustrated audiobook of this Persian fairytale about the simurgh bird with a gentle santur-and-kamancheh BGM.',
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + music score + bilingual / foreign-language subtitle ask. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav + source-language SRT (timed). MusicAgent composes the music score the user specified. AudioMixAgent layers the music under the narrator wav. TranslationAgent translates the source SRT into the target language preserving timing. CompositorAgent muxes the slideshow with mixed audio + both subtitle tracks. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), IntakeImage/BriefEnricher (no image upload). Reject TranscriptionAgent — narrator already produces a timed SRT."
        ),
        "intents": [
            "Compose the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Design one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Create an English-Tagalog bilingual illustrated audiobook of this Filipino folktale about how the pineapple got its eyes with a gentle kulintang BGM.',
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + music score + bilingual / foreign-language subtitle ask. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav + source-language SRT (timed). MusicAgent composes the music score the user specified. AudioMixAgent layers the music under the narrator wav. TranslationAgent translates the source SRT into the target language preserving timing. CompositorAgent muxes the slideshow with mixed audio + both subtitle tracks. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), IntakeImage/BriefEnricher (no image upload). Reject TranscriptionAgent — narrator already produces a timed SRT."
        ),
        "intents": [
            "Polish the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Generate one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Create an English-Hebrew bilingual illustrated audiobook of this Hebrew folktale about the clever rabbi of Chelm with a soft klezmer clarinet BGM.',
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + music score + bilingual / foreign-language subtitle ask. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav + source-language SRT (timed). MusicAgent composes the music score the user specified. AudioMixAgent layers the music under the narrator wav. TranslationAgent translates the source SRT into the target language preserving timing. CompositorAgent muxes the slideshow with mixed audio + both subtitle tracks. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), IntakeImage/BriefEnricher (no image upload). Reject TranscriptionAgent — narrator already produces a timed SRT."
        ),
        "intents": [
            "Outline the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Plan one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Create an English-Vietnamese bilingual illustrated audiobook of this Vietnamese folktale about the golden star fruit tree with a gentle dan-bau BGM.',
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + music score + bilingual / foreign-language subtitle ask. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav + source-language SRT (timed). MusicAgent composes the music score the user specified. AudioMixAgent layers the music under the narrator wav. TranslationAgent translates the source SRT into the target language preserving timing. CompositorAgent muxes the slideshow with mixed audio + both subtitle tracks. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), IntakeImage/BriefEnricher (no image upload). Reject TranscriptionAgent — narrator already produces a timed SRT."
        ),
        "intents": [
            "Draft the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Render one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
    {
        "user_goal": 'Create an English-Samoan bilingual illustrated audiobook of this Polynesian folktale about Maui slowing the sun with a gentle Polynesian-flute BGM.',
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + music score + bilingual / foreign-language subtitle ask. NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav + source-language SRT (timed). MusicAgent composes the music score the user specified. AudioMixAgent layers the music under the narrator wav. TranslationAgent translates the source SRT into the target language preserving timing. CompositorAgent muxes the slideshow with mixed audio + both subtitle tracks. Reject AmbienceAgent (no environmental ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow, not multi-shot film), IntakeImage/BriefEnricher (no image upload). Reject TranscriptionAgent — narrator already produces a timed SRT."
        ),
        "intents": [
            "Compose the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Design one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level source-language SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            'Layer the music score under the narrator wav into one final mixed wav.',
            "Translate the narrator SRT into the user-specified target language, preserving every segment's timing intact.",
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio, both source and translated subtitles burned in.',
        ],
    },
]
