"""GRPO shape: extend_style — IntakeVideo → VideoExtend → StyleTransfer.

20 samples (target_n=20). Extend video + style-transfer (raw output).
"""
from __future__ import annotations


def _make(topic, target_dur, style):
    return {
        "rationale": (
            f"{topic} clip + extend-to-{target_dur} + {style} style transfer. Raw "
            "style-transferred extended output is the deliverable. Reject Compositor "
            "(no overlay), Music/Ambience/AudioMix, Transcription/Translation, "
            "VideoAnalysis/Highlight."
        ),
        "intents": [
            f"Ingest the user's uploaded {topic} clip into the workspace.",
            f"Extend the {topic} clip to ~{target_dur} duration.",
            f"Apply {style} style transfer to the extended {topic} clip and output the restyled extended video.",
        ],
    }


SAMPLES: list[dict] = [
    {**_make("vacation beach", "60 seconds", "watercolor painting"),
     "user_goal": "Extend my vacation beach clip to ~60 seconds and apply watercolor-painting style."},
    {**_make("birthday party", "45 seconds", "Pixar-3D animation"),
     "user_goal": "Extend my birthday-party clip to ~45 seconds and restyle it in Pixar-3D animation."},
    {**_make("street-food market", "30 seconds", "Studio-Ghibli anime"),
     "user_goal": "Extend my street-food market clip to ~30 seconds and re-render in Studio-Ghibli anime style."},
    {**_make("graduation ceremony", "40 seconds", "oil-painting Impressionist"),
     "user_goal": "Extend my graduation ceremony clip to ~40 seconds and apply oil-painting Impressionist style."},
    {**_make("city-tour", "50 seconds", "ink-wash Chinese-painting"),
     "user_goal": "Extend my city-tour clip to ~50 seconds and restyle in ink-wash Chinese-painting style."},
    {**_make("hiking trail", "30 seconds", "Bob-Ross-style oil-painting"),
     "user_goal": "Extend my hiking trail clip to ~30 seconds and apply Bob-Ross-style oil-painting."},
    {**_make("dance recital", "60 seconds", "comic-book ink-and-color"),
     "user_goal": "Extend my dance recital clip to ~60 seconds and re-render in comic-book ink-and-color style."},
    {**_make("concert footage", "45 seconds", "neon-cyberpunk"),
     "user_goal": "Extend my concert footage to ~45 seconds and apply neon-cyberpunk style."},
    {**_make("wedding ceremony", "30 seconds", "vintage-1950s Technicolor"),
     "user_goal": "Extend my wedding ceremony clip to ~30 seconds and restyle in vintage-1950s Technicolor."},
    {**_make("yoga session", "60 seconds", "Japanese-ukiyo-e woodblock"),
     "user_goal": "Extend my yoga session clip to ~60 seconds and re-render in Japanese-ukiyo-e woodblock style."},
    {**_make("road-trip", "45 seconds", "Wes-Anderson-pastel"),
     "user_goal": "Extend my road-trip clip to ~45 seconds and apply Wes-Anderson-pastel style."},
    {**_make("museum tour", "50 seconds", "Renaissance-fresco"),
     "user_goal": "Extend my museum tour clip to ~50 seconds and restyle in Renaissance-fresco style."},
    {**_make("autumn-leaves walk", "40 seconds", "Monet-Impressionist"),
     "user_goal": "Extend my autumn-leaves walk clip to ~40 seconds and apply Monet-Impressionist style."},
    {**_make("ski-trip", "60 seconds", "Andy-Warhol pop-art"),
     "user_goal": "Extend my ski-trip clip to ~60 seconds and re-render in Andy-Warhol pop-art style."},
    {**_make("snowboarding", "45 seconds", "comic-book Frank-Miller noir"),
     "user_goal": "Extend my snowboarding video to ~45 seconds and apply Frank-Miller-comic-book noir style."},
    {**_make("aquarium visit", "50 seconds", "stained-glass cathedral"),
     "user_goal": "Extend my aquarium visit clip to ~50 seconds and restyle in stained-glass cathedral style."},
    {**_make("garden tour", "40 seconds", "Beatrix-Potter watercolor"),
     "user_goal": "Extend my garden tour clip to ~40 seconds and apply Beatrix-Potter watercolor style."},
    {**_make("amusement-park ride", "30 seconds", "Saturday-morning-cartoon"),
     "user_goal": "Extend my amusement-park ride clip to ~30 seconds and re-render in Saturday-morning-cartoon style."},
    {**_make("hot-air-balloon ride", "60 seconds", "art-nouveau Mucha"),
     "user_goal": "Extend my hot-air-balloon ride clip to ~60 seconds and apply art-nouveau Mucha style."},
    {**_make("hiking summit", "45 seconds", "Caspar-David-Friedrich Romantic"),
     "user_goal": "Extend my hiking-summit footage to ~45 seconds and restyle in Caspar-David-Friedrich Romantic style."},
]
