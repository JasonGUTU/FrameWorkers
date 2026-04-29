"""GRPO shape: style_subtitle — IntakeVideo → StyleTransfer → Transcription → Compositor.

30 samples (target_n=30). Style-transfer + same-language subtitles.
"""
from __future__ import annotations


def _make(topic, style, lang):
    return {
        "rationale": (
            f"{topic} clip + {style} style transfer + same-language {lang} subtitles. "
            "Reject TranslationAgent (no bilingual), MusicAgent / AmbienceAgent / "
            "AudioMixAgent (no audio overlay), VideoAnalysis/Highlight, VideoExtend (no length change)."
        ),
        "intents": [
            f"Ingest the user's uploaded {topic} clip into the workspace.",
            f"Apply {style} style transfer to the {topic} clip.",
            f"Transcribe the {lang} dialogue into timestamped subtitle segments.",
            f"Composite the final restyled {topic} mp4 with {lang} subtitles overlaid.",
        ],
    }


SAMPLES: list[dict] = [
    {**_make("English lecture", "Pixar-3D animation", "English"),
     "user_goal": "Restyle my English lecture in Pixar-3D animation style and add English subtitles."},
    {**_make("Spanish cooking demo", "watercolor painting", "Spanish"),
     "user_goal": "Apply watercolor-painting style to my Spanish cooking demo and add Spanish subtitles."},
    {**_make("Japanese tea-ceremony tutorial", "ukiyo-e woodblock", "Japanese"),
     "user_goal": "Restyle my Japanese tea-ceremony tutorial in ukiyo-e woodblock style and add Japanese subtitles."},
    {**_make("French art-history lecture", "oil-painting Impressionist", "French"),
     "user_goal": "Apply oil-painting Impressionist style to my French art-history lecture and add French subtitles."},
    {**_make("German engineering lecture", "graphic-novel halftone", "German"),
     "user_goal": "Restyle my German engineering lecture in graphic-novel halftone style and add German subtitles."},
    {**_make("Italian cooking show", "Renaissance-fresco", "Italian"),
     "user_goal": "Apply Renaissance-fresco style to my Italian cooking show and add Italian subtitles."},
    {**_make("Russian programming tutorial", "neon-cyberpunk", "Russian"),
     "user_goal": "Restyle my Russian programming tutorial in neon-cyberpunk style and add Russian subtitles."},
    {**_make("Mandarin business presentation", "Chinese-ink-wash", "Mandarin"),
     "user_goal": "Apply Chinese-ink-wash style to my Mandarin business presentation and add Mandarin subtitles."},
    {**_make("Hindi yoga class", "Pattachitra", "Hindi"),
     "user_goal": "Restyle my Hindi yoga class in Pattachitra style and add Hindi subtitles."},
    {**_make("Korean fitness video", "Korean-minhwa", "Korean"),
     "user_goal": "Apply Korean-minhwa style to my Korean fitness video and add Korean subtitles."},
    {**_make("Arabic news commentary", "Arabic-miniature", "Arabic"),
     "user_goal": "Restyle my Arabic news commentary in Arabic-miniature style and add Arabic subtitles."},
    {**_make("Turkish recipe video", "Ottoman-miniature", "Turkish"),
     "user_goal": "Apply Ottoman-miniature style to my Turkish recipe video and add Turkish subtitles."},
    {**_make("Vietnamese travel vlog", "Vietnamese-folk", "Vietnamese"),
     "user_goal": "Restyle my Vietnamese travel vlog in Vietnamese-folk style and add Vietnamese subtitles."},
    {**_make("Thai street-food tour", "Thai-mural-style", "Thai"),
     "user_goal": "Apply Thai-mural-style to my Thai street-food tour and add Thai subtitles."},
    {**_make("Polish history lecture", "illuminated-manuscript", "Polish"),
     "user_goal": "Restyle my Polish history lecture in illuminated-manuscript style and add Polish subtitles."},
    {**_make("Portuguese language lesson", "Portuguese-azulejo-tile", "Portuguese"),
     "user_goal": "Apply Portuguese-azulejo-tile style to my Portuguese language lesson and add Portuguese subtitles."},
    {**_make("Dutch programming workshop", "Vermeer-painterly", "Dutch"),
     "user_goal": "Restyle my Dutch programming workshop in Vermeer-painterly style and add Dutch subtitles."},
    {**_make("Swedish hiking guide", "Nordic-illustration", "Swedish"),
     "user_goal": "Apply Nordic-illustration style to my Swedish hiking guide and add Swedish subtitles."},
    {**_make("Greek philosophy seminar", "Greek-vase-painting", "Greek"),
     "user_goal": "Restyle my Greek philosophy seminar in Greek-vase-painting style and add Greek subtitles."},
    {**_make("Hebrew prayer recitation", "Hebrew-illuminated-manuscript", "Hebrew"),
     "user_goal": "Apply Hebrew-illuminated-manuscript style to my Hebrew prayer recitation and add Hebrew subtitles."},
    {**_make("Persian poetry reading", "Persian-miniature", "Persian"),
     "user_goal": "Restyle my Persian poetry reading in Persian-miniature style and add Persian subtitles."},
    {**_make("Bengali storytelling", "Pattachitra-Bengal", "Bengali"),
     "user_goal": "Apply Pattachitra-Bengal style to my Bengali storytelling video and add Bengali subtitles."},
    {**_make("Punjabi cooking demo", "Mughal-miniature", "Punjabi"),
     "user_goal": "Restyle my Punjabi cooking demo in Mughal-miniature style and add Punjabi subtitles."},
    {**_make("Tamil temple-festival commentary", "Tanjore-painting", "Tamil"),
     "user_goal": "Apply Tanjore-painting style to my Tamil temple-festival commentary and add Tamil subtitles."},
    {**_make("Indonesian street-food", "Balinese-batik", "Indonesian"),
     "user_goal": "Restyle my Indonesian street-food video in Balinese-batik style and add Indonesian subtitles."},
    {**_make("Tagalog family interview", "Filipino-watercolor", "Tagalog"),
     "user_goal": "Apply Filipino-watercolor style to my Tagalog family interview and add Tagalog subtitles."},
    {**_make("Welsh choir performance", "Celtic-knot illuminated", "Welsh"),
     "user_goal": "Restyle my Welsh choir performance in Celtic-knot illuminated style and add Welsh subtitles."},
    {**_make("Swahili documentary", "Swahili-tinga-tinga", "Swahili"),
     "user_goal": "Apply Swahili-tinga-tinga painting style to my Swahili documentary and add Swahili subtitles."},
    {**_make("Yoruba elder interview", "Yoruba-adire-cloth", "Yoruba"),
     "user_goal": "Restyle my Yoruba elder interview in Yoruba-adire-cloth style and add Yoruba subtitles."},
    {**_make("Cantonese dim-sum tutorial", "Hong-Kong-comic", "Cantonese"),
     "user_goal": "Apply Hong-Kong-comic style to my Cantonese dim-sum tutorial and add Cantonese subtitles."},
]
