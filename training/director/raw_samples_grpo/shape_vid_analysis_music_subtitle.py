"""GRPO shape: vid_analysis_music_subtitle — IntakeVideo → VideoAnalysis → Transcription → Music → AudioMix → Compositor.

20 samples (target_n=20). Uploaded video: analyze, subtitle, swap BGM.
"""
from __future__ import annotations


def _make(topic, lang, music):
    return {
        "rationale": (
            f"{topic} clip + analyze + same-language {lang} subtitles + {music} BGM swap. "
            "Reject AmbienceAgent, TranslationAgent, StyleTransfer/VideoExtend/Highlight, "
            "Story/Screenplay/KeyFrame/Video (no creative authoring requested), "
            "Narration/Illustration/Narrator."
        ),
        "intents": [
            f"Ingest the user's uploaded {topic} clip into the workspace.",
            f"Analyze the {topic} for content structure and beats.",
            f"Transcribe the {lang} dialogue into timestamped subtitle segments.",
            f"Compose the {music} BGM the user requested.",
            f"Layer the {music} BGM under the original audio into one final mixed wav.",
            f"Composite the final {topic} mp4 with {lang} subtitles overlaid and mixed audio.",
        ],
    }


SAMPLES: list[dict] = [
    {**_make("English documentary clip", "English", "ambient documentary-strings"),
     "user_goal": "Analyze my English documentary clip, add English subtitles, and swap in ambient documentary-strings BGM."},
    {**_make("Spanish news segment", "Spanish", "tense news-orchestral"),
     "user_goal": "Analyze my Spanish news segment, add Spanish subtitles, and swap in tense news-orchestral BGM."},
    {**_make("Japanese variety show", "Japanese", "playful J-pop"),
     "user_goal": "Analyze my Japanese variety show, add Japanese subtitles, and swap in playful J-pop BGM."},
    {**_make("French art-history lecture", "French", "Parisian-cafe-strings"),
     "user_goal": "Analyze my French art-history lecture, add French subtitles, and swap in Parisian-cafe-strings BGM."},
    {**_make("German political talk", "German", "tense documentary-orchestral"),
     "user_goal": "Analyze my German political talk, add German subtitles, and swap in tense documentary-orchestral BGM."},
    {**_make("Italian cooking show", "Italian", "Italian-mandolin"),
     "user_goal": "Analyze my Italian cooking show, add Italian subtitles, and swap in Italian-mandolin BGM."},
    {**_make("Russian space-program documentary", "Russian", "Soviet-orchestral"),
     "user_goal": "Analyze my Russian space-program documentary, add Russian subtitles, and swap in Soviet-orchestral BGM."},
    {**_make("Mandarin business presentation", "Mandarin", "modern-Chinese-instrumental"),
     "user_goal": "Analyze my Mandarin business presentation, add Mandarin subtitles, and swap in modern-Chinese-instrumental BGM."},
    {**_make("Hindi yoga class", "Hindi", "Indian sitar-and-tabla"),
     "user_goal": "Analyze my Hindi yoga class, add Hindi subtitles, and swap in Indian sitar-and-tabla BGM."},
    {**_make("Korean variety show", "Korean", "K-pop instrumental"),
     "user_goal": "Analyze my Korean variety show, add Korean subtitles, and swap in K-pop instrumental BGM."},
    {**_make("Cantonese drama clip", "Cantonese", "Cantopop strings"),
     "user_goal": "Analyze my Cantonese drama clip, add Cantonese subtitles, and swap in Cantopop-strings BGM."},
    {**_make("Arabic news commentary", "Arabic", "tense oud-and-percussion"),
     "user_goal": "Analyze my Arabic news commentary, add Arabic subtitles, and swap in tense oud-and-percussion BGM."},
    {**_make("Turkish recipe video", "Turkish", "Turkish-folk-strings"),
     "user_goal": "Analyze my Turkish recipe video, add Turkish subtitles, and swap in Turkish-folk-strings BGM."},
    {**_make("Vietnamese travel vlog", "Vietnamese", "Vietnamese đàn tranh"),
     "user_goal": "Analyze my Vietnamese travel vlog, add Vietnamese subtitles, and swap in Vietnamese đàn tranh BGM."},
    {**_make("Thai street-food tour", "Thai", "Thai-folk-percussion"),
     "user_goal": "Analyze my Thai street-food tour, add Thai subtitles, and swap in Thai-folk-percussion BGM."},
    {**_make("Polish history lecture", "Polish", "Polish-cello-and-piano"),
     "user_goal": "Analyze my Polish history lecture, add Polish subtitles, and swap in Polish-cello-and-piano BGM."},
    {**_make("Portuguese art-museum tour", "Portuguese", "fado-guitar"),
     "user_goal": "Analyze my Portuguese art-museum tour, add Portuguese subtitles, and swap in fado-guitar BGM."},
    {**_make("Dutch programming workshop", "Dutch", "Dutch-baroque harpsichord"),
     "user_goal": "Analyze my Dutch programming workshop, add Dutch subtitles, and swap in Dutch-baroque harpsichord BGM."},
    {**_make("Greek philosophy seminar", "Greek", "Greek bouzouki-and-strings"),
     "user_goal": "Analyze my Greek philosophy seminar, add Greek subtitles, and swap in Greek bouzouki-and-strings BGM."},
    {**_make("Hebrew rabbinical talk", "Hebrew", "Israeli-folk strings"),
     "user_goal": "Analyze my Hebrew rabbinical talk, add Hebrew subtitles, and swap in Israeli-folk-strings BGM."},
]
