"""GRPO shape: style_extend_music — IntakeVideo → StyleTransfer → VideoExtend → Music → AudioMix → Compositor.

20 samples (target_n=20). Style-transfer THEN extend (so styling propagates to extension) + BGM.
"""
from __future__ import annotations


def _make(topic, style, target_dur, music):
    return {
        "rationale": (
            f"{topic} clip + {style} style transfer + extend-to-{target_dur} (so styled "
            f"look is preserved through the extension) + {music} BGM. Reject AmbienceAgent, "
            "Transcription/Translation, VideoAnalysis/Highlight."
        ),
        "intents": [
            f"Ingest the user's uploaded {topic} clip into the workspace.",
            f"Apply {style} style transfer to the {topic} clip.",
            f"Extend the styled {topic} clip to ~{target_dur} duration so the styled look propagates through the new footage.",
            f"Compose the {music} BGM the user requested.",
            f"Layer the {music} BGM under the styled-and-extended clip into one final mixed wav.",
            f"Composite the final styled-and-extended {topic} mp4 with mixed audio.",
        ],
    }


SAMPLES: list[dict] = [
    {**_make("vacation beach", "watercolor painting", "60 seconds", "tropical surf-rock"),
     "user_goal": "Apply watercolor-painting style to my vacation beach clip, extend it to ~60 seconds, and add tropical surf-rock BGM."},
    {**_make("birthday party", "Pixar-3D animation", "45 seconds", "upbeat indie-pop"),
     "user_goal": "Restyle my birthday-party clip in Pixar-3D, extend to ~45 seconds, and add upbeat indie-pop BGM."},
    {**_make("street-food market", "Studio-Ghibli anime", "30 seconds", "lively world-music"),
     "user_goal": "Re-render my street-food market clip in Studio-Ghibli anime style, extend to ~30 seconds, and add lively world-music BGM."},
    {**_make("graduation ceremony", "oil-painting Impressionist", "40 seconds", "uplifting orchestral"),
     "user_goal": "Apply oil-painting Impressionist style to my graduation ceremony clip, extend to ~40 seconds, and add uplifting orchestral BGM."},
    {**_make("city-tour", "ink-wash Chinese-painting", "50 seconds", "ambient guzheng"),
     "user_goal": "Restyle my city-tour clip in ink-wash Chinese-painting, extend to ~50 seconds, and add ambient-guzheng BGM."},
    {**_make("hiking trail", "Bob-Ross-style oil-painting", "30 seconds", "ambient acoustic-guitar"),
     "user_goal": "Apply Bob-Ross-style oil-painting to my hiking trail clip, extend to ~30 seconds, and add ambient acoustic-guitar BGM."},
    {**_make("dance recital", "comic-book ink-and-color", "60 seconds", "playful piano-and-strings"),
     "user_goal": "Re-render my dance recital clip in comic-book ink-and-color, extend to ~60 seconds, and add playful piano-and-strings BGM."},
    {**_make("concert footage", "neon-cyberpunk", "45 seconds", "high-energy drum-and-bass"),
     "user_goal": "Apply neon-cyberpunk style to my concert footage, extend to ~45 seconds, and add high-energy drum-and-bass BGM."},
    {**_make("wedding ceremony", "vintage-1950s Technicolor", "30 seconds", "romantic strings"),
     "user_goal": "Restyle my wedding ceremony clip in vintage-1950s Technicolor, extend to ~30 seconds, and add romantic-strings BGM."},
    {**_make("yoga session", "Japanese-ukiyo-e woodblock", "60 seconds", "meditative ambient"),
     "user_goal": "Apply Japanese-ukiyo-e woodblock style to my yoga session, extend to ~60 seconds, and add meditative ambient BGM."},
    {**_make("road-trip", "Wes-Anderson-pastel", "45 seconds", "Americana folk"),
     "user_goal": "Re-render my road-trip clip in Wes-Anderson-pastel, extend to ~45 seconds, and add Americana-folk BGM."},
    {**_make("museum tour", "Renaissance-fresco", "50 seconds", "gentle classical-piano"),
     "user_goal": "Apply Renaissance-fresco style to my museum tour, extend to ~50 seconds, and add gentle classical-piano BGM."},
    {**_make("autumn-leaves walk", "Monet-Impressionist", "40 seconds", "wistful piano-and-cello"),
     "user_goal": "Restyle my autumn-leaves walk in Monet-Impressionist, extend to ~40 seconds, and add wistful piano-and-cello BGM."},
    {**_make("ski-trip", "Andy-Warhol pop-art", "60 seconds", "epic adventure orchestral"),
     "user_goal": "Apply Andy-Warhol pop-art to my ski-trip clip, extend to ~60 seconds, and add epic-adventure orchestral BGM."},
    {**_make("snowboarding", "comic-book Frank-Miller noir", "45 seconds", "high-energy rock-guitar"),
     "user_goal": "Re-render my snowboarding video in Frank-Miller-comic-book noir, extend to ~45 seconds, and add high-energy rock-guitar BGM."},
    {**_make("aquarium visit", "stained-glass cathedral", "50 seconds", "ambient marimba"),
     "user_goal": "Apply stained-glass cathedral style to my aquarium visit, extend to ~50 seconds, and add ambient-marimba BGM."},
    {**_make("garden tour", "Beatrix-Potter watercolor", "40 seconds", "pastoral flute-and-strings"),
     "user_goal": "Restyle my garden tour clip in Beatrix-Potter watercolor, extend to ~40 seconds, and add pastoral flute-and-strings BGM."},
    {**_make("hot-air-balloon ride", "art-nouveau Mucha", "60 seconds", "soaring strings"),
     "user_goal": "Apply art-nouveau Mucha style to my hot-air-balloon ride, extend to ~60 seconds, and add soaring-strings BGM."},
    {**_make("hiking summit", "Caspar-David-Friedrich Romantic", "45 seconds", "epic horn-and-strings"),
     "user_goal": "Re-render my hiking-summit footage in Caspar-David-Friedrich Romantic style, extend to ~45 seconds, and add epic horn-and-strings BGM."},
    {**_make("urban-skyline night", "Vincent-van-Gogh post-Impressionist", "50 seconds", "synthwave 80s"),
     "user_goal": "Apply Vincent-van-Gogh post-Impressionist style to my urban-skyline night video, extend to ~50 seconds, and add synthwave 80s BGM."},
]
