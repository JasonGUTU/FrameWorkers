"""GRPO shape: extend_subtitle — IntakeVideo → VideoExtend → Transcription → Compositor.

30 samples (target_n=30). Extend video + add subtitles.
"""
from __future__ import annotations


def _make(topic, target_dur, lang):
    return {
        "rationale": (
            f"{topic} clip + extend-to-{target_dur} + same-language {lang} subtitles. "
            "Reject TranslationAgent (no bilingual ask), MusicAgent / AmbienceAgent / "
            "AudioMixAgent (no audio overlay), VideoAnalysis/Highlight, StyleTransfer."
        ),
        "intents": [
            f"Ingest the user's uploaded {topic} clip into the workspace.",
            f"Extend the {topic} clip to ~{target_dur} duration.",
            f"Transcribe the {lang} dialogue into timestamped subtitle segments.",
            f"Composite the final extended {topic} mp4 with {lang} subtitles overlaid.",
        ],
    }


SAMPLES: list[dict] = [
    {**_make("English lecture clip", "10 minutes", "English"),
     "user_goal": "Extend my English lecture clip to ~10 minutes and add English subtitles."},
    {**_make("Spanish cooking demo", "8 minutes", "Spanish"),
     "user_goal": "Extend my Spanish cooking demo to ~8 minutes and add Spanish subtitles."},
    {**_make("Japanese tea-ceremony tutorial", "12 minutes", "Japanese"),
     "user_goal": "Extend my Japanese tea-ceremony tutorial to ~12 minutes and add Japanese subtitles."},
    {**_make("French language lesson", "15 minutes", "French"),
     "user_goal": "Extend my French language lesson to ~15 minutes and add French subtitles."},
    {**_make("German engineering lecture", "20 minutes", "German"),
     "user_goal": "Extend my German engineering lecture to ~20 minutes and add German subtitles."},
    {**_make("Italian recipe video", "10 minutes", "Italian"),
     "user_goal": "Extend my Italian recipe video to ~10 minutes and add Italian subtitles."},
    {**_make("Russian programming tutorial", "25 minutes", "Russian"),
     "user_goal": "Extend my Russian programming tutorial to ~25 minutes and add Russian subtitles."},
    {**_make("Mandarin business presentation", "20 minutes", "Mandarin"),
     "user_goal": "Extend my Mandarin business presentation to ~20 minutes and add Mandarin subtitles."},
    {**_make("Hindi yoga class", "30 minutes", "Hindi"),
     "user_goal": "Extend my Hindi yoga class to ~30 minutes and add Hindi subtitles."},
    {**_make("Korean fitness video", "20 minutes", "Korean"),
     "user_goal": "Extend my Korean fitness video to ~20 minutes and add Korean subtitles."},
    {**_make("Cantonese cooking show", "15 minutes", "Cantonese"),
     "user_goal": "Extend my Cantonese cooking show to ~15 minutes and add Cantonese subtitles."},
    {**_make("Arabic news commentary", "10 minutes", "Arabic"),
     "user_goal": "Extend my Arabic news commentary to ~10 minutes and add Arabic subtitles."},
    {**_make("Turkish recipe video", "12 minutes", "Turkish"),
     "user_goal": "Extend my Turkish recipe video to ~12 minutes and add Turkish subtitles."},
    {**_make("Vietnamese travel vlog", "20 minutes", "Vietnamese"),
     "user_goal": "Extend my Vietnamese travel vlog to ~20 minutes and add Vietnamese subtitles."},
    {**_make("Thai street-food tour", "15 minutes", "Thai"),
     "user_goal": "Extend my Thai street-food tour to ~15 minutes and add Thai subtitles."},
    {**_make("Polish history lecture", "30 minutes", "Polish"),
     "user_goal": "Extend my Polish history lecture to ~30 minutes and add Polish subtitles."},
    {**_make("Portuguese language lesson", "25 minutes", "Portuguese"),
     "user_goal": "Extend my Portuguese language lesson to ~25 minutes and add Portuguese subtitles."},
    {**_make("Dutch programming workshop", "20 minutes", "Dutch"),
     "user_goal": "Extend my Dutch programming workshop to ~20 minutes and add Dutch subtitles."},
    {**_make("Swedish hiking guide", "15 minutes", "Swedish"),
     "user_goal": "Extend my Swedish hiking guide to ~15 minutes and add Swedish subtitles."},
    {**_make("Greek philosophy seminar", "30 minutes", "Greek"),
     "user_goal": "Extend my Greek philosophy seminar to ~30 minutes and add Greek subtitles."},
    {**_make("Hebrew prayer recitation", "15 minutes", "Hebrew"),
     "user_goal": "Extend my Hebrew prayer recitation to ~15 minutes and add Hebrew subtitles."},
    {**_make("Persian poetry reading", "20 minutes", "Persian"),
     "user_goal": "Extend my Persian poetry reading to ~20 minutes and add Persian subtitles."},
    {**_make("Bengali storytelling", "25 minutes", "Bengali"),
     "user_goal": "Extend my Bengali storytelling video to ~25 minutes and add Bengali subtitles."},
    {**_make("Punjabi cooking demo", "15 minutes", "Punjabi"),
     "user_goal": "Extend my Punjabi cooking demo to ~15 minutes and add Punjabi subtitles."},
    {**_make("Tamil temple-festival commentary", "20 minutes", "Tamil"),
     "user_goal": "Extend my Tamil temple-festival commentary to ~20 minutes and add Tamil subtitles."},
    {**_make("Indonesian street-food", "12 minutes", "Indonesian"),
     "user_goal": "Extend my Indonesian street-food video to ~12 minutes and add Indonesian subtitles."},
    {**_make("Tagalog family interview", "30 minutes", "Tagalog"),
     "user_goal": "Extend my Tagalog family interview to ~30 minutes and add Tagalog subtitles."},
    {**_make("Welsh choir performance", "15 minutes", "Welsh"),
     "user_goal": "Extend my Welsh choir performance to ~15 minutes and add Welsh subtitles."},
    {**_make("Swahili documentary", "25 minutes", "Swahili"),
     "user_goal": "Extend my Swahili documentary to ~25 minutes and add Swahili subtitles."},
    {**_make("Yoruba elder interview", "30 minutes", "Yoruba"),
     "user_goal": "Extend my Yoruba elder interview to ~30 minutes and add Yoruba subtitles."},
]
