"""Shape: story_music_ambience — Narration → Illustration → Narrator → Music → Ambience → AudioMix → Compositor.

Illustrated storytelling WITH BOTH music + ambience, NO subtitle, NO image upload.
Per-sample tailored: each rationale and each intent references the user_goal's protagonist + audio asks."""
from __future__ import annotations


SAMPLES: list[dict] = [
    {
        "user_goal": "Make an illustrated audiobook of this ocean-themed children's story, with a gentle piano lullaby playing under the narrator AND ambient wave sounds.",
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + dual audio layers (music score + environmental ambience). NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. MusicAgent composes the music score the user specified. AmbienceAgent generates the ambient bed the user specified. AudioMixAgent combines narrator + music + ambience into one final mixed wav. CompositorAgent muxes the slideshow video. Reject Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Polish the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Generate one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music score + ambient bed into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio (narrator + music + ambience).',
        ],
    },
    {
        "user_goal": 'Make an illustrated audiobook of this winter-forest bedtime tale, with a soft harp playing under the narrator AND forest-night ambient (owl, wind, snow crunch).',
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + dual audio layers (music score + environmental ambience). NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. MusicAgent composes the music score the user specified. AmbienceAgent generates the ambient bed the user specified. AudioMixAgent combines narrator + music + ambience into one final mixed wav. CompositorAgent muxes the slideshow video. Reject Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Outline the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Plan one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music score + ambient bed into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio (narrator + music + ambience).',
        ],
    },
    {
        "user_goal": 'Make an illustrated audiobook of this savanna story about a lost lion cub, with a warm kalimba playing under the narrator AND savanna ambient (distant zebras, cicadas, wind through grass).',
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + dual audio layers (music score + environmental ambience). NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. MusicAgent composes the music score the user specified. AmbienceAgent generates the ambient bed the user specified. AudioMixAgent combines narrator + music + ambience into one final mixed wav. CompositorAgent muxes the slideshow video. Reject Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Draft the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Render one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music score + ambient bed into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio (narrator + music + ambience).',
        ],
    },
    {
        "user_goal": "Make an illustrated audiobook of this rain-forest children's tale, with a gentle flute playing under the narrator AND rainforest ambient (exotic birds, distant rain, insects).",
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + dual audio layers (music score + environmental ambience). NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. MusicAgent composes the music score the user specified. AmbienceAgent generates the ambient bed the user specified. AudioMixAgent combines narrator + music + ambience into one final mixed wav. CompositorAgent muxes the slideshow video. Reject Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Compose the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Design one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music score + ambient bed into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio (narrator + music + ambience).',
        ],
    },
    {
        "user_goal": 'Make an illustrated audiobook of this desert-oasis fable, with a soft oud playing under the narrator AND desert ambient (wind, distant camel bells, palm rustle).',
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + dual audio layers (music score + environmental ambience). NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. MusicAgent composes the music score the user specified. AmbienceAgent generates the ambient bed the user specified. AudioMixAgent combines narrator + music + ambience into one final mixed wav. CompositorAgent muxes the slideshow video. Reject Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Polish the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Generate one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music score + ambient bed into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio (narrator + music + ambience).',
        ],
    },
    {
        "user_goal": 'Make an illustrated audiobook of this arctic-fox winter tale, with a gentle celesta playing under the narrator AND arctic ambient (howling wind, distant ice cracks).',
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + dual audio layers (music score + environmental ambience). NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. MusicAgent composes the music score the user specified. AmbienceAgent generates the ambient bed the user specified. AudioMixAgent combines narrator + music + ambience into one final mixed wav. CompositorAgent muxes the slideshow video. Reject Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Outline the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Plan one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music score + ambient bed into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio (narrator + music + ambience).',
        ],
    },
    {
        "user_goal": 'Make an illustrated audiobook of this mountain-monastery story for children, with a gentle Tibetan bowls playing under the narrator AND monastery ambient (wind chimes, distant chants).',
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + dual audio layers (music score + environmental ambience). NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. MusicAgent composes the music score the user specified. AmbienceAgent generates the ambient bed the user specified. AudioMixAgent combines narrator + music + ambience into one final mixed wav. CompositorAgent muxes the slideshow video. Reject Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Draft the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Render one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music score + ambient bed into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio (narrator + music + ambience).',
        ],
    },
    {
        "user_goal": "Make an illustrated audiobook of this haunted-library children's tale, with a soft harpsichord playing under the narrator AND old-library ambient (page turns, distant footsteps, ticking clock).",
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + dual audio layers (music score + environmental ambience). NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. MusicAgent composes the music score the user specified. AmbienceAgent generates the ambient bed the user specified. AudioMixAgent combines narrator + music + ambience into one final mixed wav. CompositorAgent muxes the slideshow video. Reject Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Compose the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Design one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music score + ambient bed into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio (narrator + music + ambience).',
        ],
    },
    {
        "user_goal": 'Make an illustrated audiobook of this seashore fable about a wishing starfish, with a gentle harp playing under the narrator AND seashore ambient (waves, gulls, distant foghorn).',
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + dual audio layers (music score + environmental ambience). NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. MusicAgent composes the music score the user specified. AmbienceAgent generates the ambient bed the user specified. AudioMixAgent combines narrator + music + ambience into one final mixed wav. CompositorAgent muxes the slideshow video. Reject Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Polish the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Generate one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music score + ambient bed into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio (narrator + music + ambience).',
        ],
    },
    {
        "user_goal": 'Make an illustrated audiobook of this meadow-pond picture-book tale, with a soft acoustic guitar playing under the narrator AND meadow-pond ambient (frogs, dragonflies, breeze through reeds).',
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + dual audio layers (music score + environmental ambience). NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. MusicAgent composes the music score the user specified. AmbienceAgent generates the ambient bed the user specified. AudioMixAgent combines narrator + music + ambience into one final mixed wav. CompositorAgent muxes the slideshow video. Reject Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Outline the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Plan one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music score + ambient bed into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio (narrator + music + ambience).',
        ],
    },
    {
        "user_goal": 'Make an illustrated audiobook of this bamboo-forest fable, with a gentle shakuhachi playing under the narrator AND bamboo-forest ambient (creaking stalks, distant birds, wind).',
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + dual audio layers (music score + environmental ambience). NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. MusicAgent composes the music score the user specified. AmbienceAgent generates the ambient bed the user specified. AudioMixAgent combines narrator + music + ambience into one final mixed wav. CompositorAgent muxes the slideshow video. Reject Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Draft the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Render one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music score + ambient bed into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio (narrator + music + ambience).',
        ],
    },
    {
        "user_goal": 'Make an illustrated audiobook of this moonlit-garden bedtime tale, with a dreamy celesta playing under the narrator AND moonlit-garden ambient (crickets, distant owl, fountain trickle).',
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + dual audio layers (music score + environmental ambience). NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. MusicAgent composes the music score the user specified. AmbienceAgent generates the ambient bed the user specified. AudioMixAgent combines narrator + music + ambience into one final mixed wav. CompositorAgent muxes the slideshow video. Reject Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Compose the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Design one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music score + ambient bed into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio (narrator + music + ambience).',
        ],
    },
    {
        "user_goal": 'Make an illustrated audiobook of this firelit-cabin winter tale, with a warm acoustic guitar playing under the narrator AND firelit-cabin ambient (fire crackle, wind outside, floorboard creaks).',
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + dual audio layers (music score + environmental ambience). NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. MusicAgent composes the music score the user specified. AmbienceAgent generates the ambient bed the user specified. AudioMixAgent combines narrator + music + ambience into one final mixed wav. CompositorAgent muxes the slideshow video. Reject Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Polish the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Generate one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music score + ambient bed into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio (narrator + music + ambience).',
        ],
    },
    {
        "user_goal": 'Make an illustrated audiobook of this underwater-coral-reef tale, with a dreamy ambient pad playing under the narrator AND coral-reef ambient (muffled bubbles, distant whale song).',
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + dual audio layers (music score + environmental ambience). NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. MusicAgent composes the music score the user specified. AmbienceAgent generates the ambient bed the user specified. AudioMixAgent combines narrator + music + ambience into one final mixed wav. CompositorAgent muxes the slideshow video. Reject Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Outline the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Plan one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music score + ambient bed into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio (narrator + music + ambience).',
        ],
    },
    {
        "user_goal": 'Make an illustrated audiobook of this snowy-village picture-book tale, with a gentle music-box playing under the narrator AND snowy-village ambient (distant church bells, snowfall, sleigh bells).',
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + dual audio layers (music score + environmental ambience). NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. MusicAgent composes the music score the user specified. AmbienceAgent generates the ambient bed the user specified. AudioMixAgent combines narrator + music + ambience into one final mixed wav. CompositorAgent muxes the slideshow video. Reject Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Draft the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Render one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music score + ambient bed into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio (narrator + music + ambience).',
        ],
    },
    {
        "user_goal": 'Make an illustrated audiobook of this cave-hibernation bear tale, with a soft cello playing under the narrator AND cave ambient (distant drip, wind at entrance, low rumble).',
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + dual audio layers (music score + environmental ambience). NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. MusicAgent composes the music score the user specified. AmbienceAgent generates the ambient bed the user specified. AudioMixAgent combines narrator + music + ambience into one final mixed wav. CompositorAgent muxes the slideshow video. Reject Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Compose the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Design one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music score + ambient bed into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio (narrator + music + ambience).',
        ],
    },
    {
        "user_goal": 'Make an illustrated audiobook of this night-garden bedtime tale, with a soft music-box-and-harp playing under the narrator AND night-garden ambient (crickets, soft wind, distant nightbird).',
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + dual audio layers (music score + environmental ambience). NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. MusicAgent composes the music score the user specified. AmbienceAgent generates the ambient bed the user specified. AudioMixAgent combines narrator + music + ambience into one final mixed wav. CompositorAgent muxes the slideshow video. Reject Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Polish the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Generate one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music score + ambient bed into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio (narrator + music + ambience).',
        ],
    },
    {
        "user_goal": "Make an illustrated audiobook of this summer-lake children's tale, with a warm ukulele-and-strings playing under the narrator AND summer-lake ambient (lapping water, cicadas, distant laughter).",
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + dual audio layers (music score + environmental ambience). NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. MusicAgent composes the music score the user specified. AmbienceAgent generates the ambient bed the user specified. AudioMixAgent combines narrator + music + ambience into one final mixed wav. CompositorAgent muxes the slideshow video. Reject Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Outline the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Plan one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music score + ambient bed into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio (narrator + music + ambience).',
        ],
    },
    {
        "user_goal": 'Make an illustrated audiobook of this autumn-orchard tale, with a gentle folk-guitar playing under the narrator AND orchard ambient (leaves rustling, distant tractor, apple-thud).',
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + dual audio layers (music score + environmental ambience). NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. MusicAgent composes the music score the user specified. AmbienceAgent generates the ambient bed the user specified. AudioMixAgent combines narrator + music + ambience into one final mixed wav. CompositorAgent muxes the slideshow video. Reject Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Draft the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Render one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music score + ambient bed into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio (narrator + music + ambience).',
        ],
    },
    {
        "user_goal": 'Make an illustrated audiobook of this lighthouse-island tale, with a gentle strings playing under the narrator AND lighthouse-island ambient (waves, distant gulls, foghorn).',
        "rationale": (
            "Long-form illustrated-storytelling brief — the protagonist's arc + dual audio layers (music score + environmental ambience). NarrationAgent writes the narrator script split into picture-aligned segments. IllustrationAgent generates one illustration per segment. NarratorAgent renders the script as voiceover wav. MusicAgent composes the music score the user specified. AmbienceAgent generates the ambient bed the user specified. AudioMixAgent combines narrator + music + ambience into one final mixed wav. CompositorAgent muxes the slideshow video. Reject Transcription/Translation (no subtitle / multilingual ask), VideoAnalysis/IntakeVideo/StyleTransfer/VideoExtend/Highlight (no source clip), Story/Screenplay/KeyFrame/Video (slideshow voiceover, not multi-shot film), IntakeImage/BriefEnricher (no image upload)."
        ),
        "intents": [
            "Compose the user's storytelling brief into a narrator script tracing the protagonist's arc — illustration-aligned segments with per-segment image_prompt + per-line TTS text.",
            "Design one illustration per narrator segment in picture-book style, depicting the protagonist's setting and key moments.",
            'Render the narrator script as a continuous voiceover — per-line TTS with inter-line pauses, full wav + line-level SRT + per-segment timing.',
            'Compose the music score the user requested, sized for the narrator-voiceover duration and matching the the protagonist story tone.',
            "Generate the ambient sound bed the user requested, matching the the protagonist story's environmental setting.",
            'Combine narrator wav + music score + ambient bed into one final mixed wav.',
            'Composite the final illustrated-audiobook slideshow — segment illustrations timed to the mixed audio (narrator + music + ambience).',
        ],
    },
]
