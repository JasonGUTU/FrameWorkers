"""GRPO shape: extend_style_subtitle — IntakeVideo → VideoExtend → StyleTransfer → Transcription → Compositor.

20 samples (target_n=20). Extend + style-transfer + same-language subtitles.
"""
from __future__ import annotations


def _make(topic, target_dur, style, lang):
    return {
        "rationale": (
            f"{topic} clip + extend-to-{target_dur} + {style} style transfer + "
            f"same-language {lang} subtitles. Reject TranslationAgent, Music/Ambience/AudioMix, VideoAnalysis/Highlight."
        ),
        "intents": [
            f"Ingest the user's uploaded {topic} clip into the workspace.",
            f"Extend the {topic} clip to ~{target_dur} duration.",
            f"Apply {style} style transfer to the extended {topic} clip.",
            f"Transcribe the {lang} dialogue into timestamped subtitle segments.",
            f"Composite the final extended-and-restyled {topic} mp4 with {lang} subtitles overlaid.",
        ],
    }


SAMPLES: list[dict] = [
    {**_make("English lecture clip", "10 minutes", "Pixar-3D animation", "English"),
     "user_goal": "Extend my English lecture clip to ~10 minutes, restyle in Pixar-3D animation, and add English subtitles."},
    {**_make("Spanish cooking demo", "8 minutes", "watercolor painting", "Spanish"),
     "user_goal": "Extend my Spanish cooking demo to ~8 minutes, apply watercolor-painting style, and add Spanish subtitles."},
    {**_make("Japanese tea-ceremony tutorial", "12 minutes", "ukiyo-e woodblock", "Japanese"),
     "user_goal": "Extend my Japanese tea-ceremony tutorial to ~12 minutes, restyle in ukiyo-e woodblock, and add Japanese subtitles."},
    {**_make("French art-history lecture", "15 minutes", "oil-painting Impressionist", "French"),
     "user_goal": "Extend my French art-history lecture to ~15 minutes, apply oil-painting Impressionist style, and add French subtitles."},
    {**_make("German engineering lecture", "20 minutes", "graphic-novel halftone", "German"),
     "user_goal": "Extend my German engineering lecture to ~20 minutes, restyle in graphic-novel halftone, and add German subtitles."},
    {**_make("Italian cooking show", "10 minutes", "Renaissance-fresco", "Italian"),
     "user_goal": "Extend my Italian cooking show to ~10 minutes, apply Renaissance-fresco style, and add Italian subtitles."},
    {**_make("Russian programming tutorial", "25 minutes", "neon-cyberpunk", "Russian"),
     "user_goal": "Extend my Russian programming tutorial to ~25 minutes, restyle in neon-cyberpunk, and add Russian subtitles."},
    {**_make("Mandarin business presentation", "20 minutes", "Chinese-ink-wash", "Mandarin"),
     "user_goal": "Extend my Mandarin business presentation to ~20 minutes, apply Chinese-ink-wash style, and add Mandarin subtitles."},
    {**_make("Hindi yoga class", "30 minutes", "Pattachitra", "Hindi"),
     "user_goal": "Extend my Hindi yoga class to ~30 minutes, restyle in Pattachitra, and add Hindi subtitles."},
    {**_make("Korean fitness video", "20 minutes", "Korean-minhwa", "Korean"),
     "user_goal": "Extend my Korean fitness video to ~20 minutes, apply Korean-minhwa style, and add Korean subtitles."},
    {**_make("Cantonese cooking show", "15 minutes", "Hong-Kong-comic", "Cantonese"),
     "user_goal": "Extend my Cantonese cooking show to ~15 minutes, restyle in Hong-Kong-comic, and add Cantonese subtitles."},
    {**_make("Arabic news commentary", "10 minutes", "Arabic-miniature", "Arabic"),
     "user_goal": "Extend my Arabic news commentary to ~10 minutes, apply Arabic-miniature style, and add Arabic subtitles."},
    {**_make("Turkish recipe video", "12 minutes", "Ottoman-miniature", "Turkish"),
     "user_goal": "Extend my Turkish recipe video to ~12 minutes, restyle in Ottoman-miniature, and add Turkish subtitles."},
    {**_make("Vietnamese travel vlog", "20 minutes", "Vietnamese-folk", "Vietnamese"),
     "user_goal": "Extend my Vietnamese travel vlog to ~20 minutes, apply Vietnamese-folk style, and add Vietnamese subtitles."},
    {**_make("Thai street-food tour", "15 minutes", "Thai-mural-style", "Thai"),
     "user_goal": "Extend my Thai street-food tour to ~15 minutes, restyle in Thai-mural style, and add Thai subtitles."},
    {**_make("Polish history lecture", "30 minutes", "illuminated-manuscript", "Polish"),
     "user_goal": "Extend my Polish history lecture to ~30 minutes, apply illuminated-manuscript style, and add Polish subtitles."},
    {**_make("Portuguese language lesson", "25 minutes", "Portuguese-azulejo-tile", "Portuguese"),
     "user_goal": "Extend my Portuguese language lesson to ~25 minutes, restyle in Portuguese-azulejo-tile, and add Portuguese subtitles."},
    {**_make("Dutch programming workshop", "20 minutes", "Vermeer-painterly", "Dutch"),
     "user_goal": "Extend my Dutch programming workshop to ~20 minutes, apply Vermeer-painterly style, and add Dutch subtitles."},
    {**_make("Greek philosophy seminar", "30 minutes", "Greek-vase-painting", "Greek"),
     "user_goal": "Extend my Greek philosophy seminar to ~30 minutes, restyle in Greek-vase-painting, and add Greek subtitles."},
    {**_make("Hebrew prayer recitation", "15 minutes", "Hebrew-illuminated-manuscript", "Hebrew"),
     "user_goal": "Extend my Hebrew prayer recitation to ~15 minutes, apply Hebrew-illuminated-manuscript style, and add Hebrew subtitles."},
]
