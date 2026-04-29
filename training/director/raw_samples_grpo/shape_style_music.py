"""GRPO shape: style_music — IntakeVideo → StyleTransfer → Music → AudioMix → Compositor.

30 samples (target_n=30). Style-transfer + BGM swap.
"""
from __future__ import annotations


def _make(topic, style, music):
    return {
        "rationale": (
            f"{topic} clip + {style} style transfer + {music} BGM. Reject AmbienceAgent, "
            "Transcription/Translation, VideoAnalysis/Highlight, VideoExtend."
        ),
        "intents": [
            f"Ingest the user's uploaded {topic} clip into the workspace.",
            f"Apply {style} style transfer to the {topic} clip.",
            f"Compose the {music} BGM the user requested.",
            f"Layer the {music} BGM under the restyled clip's audio into one final mixed wav.",
            f"Composite the final restyled {topic} mp4 with mixed audio.",
        ],
    }


SAMPLES: list[dict] = [
    {**_make("vacation beach", "watercolor painting", "tropical surf-rock"),
     "user_goal": "Apply watercolor-painting style to my vacation beach clip and add tropical surf-rock BGM."},
    {**_make("birthday party", "Pixar-3D animation", "upbeat indie-pop"),
     "user_goal": "Restyle my birthday-party video in Pixar-3D animation style with upbeat indie-pop BGM."},
    {**_make("street-food market", "Studio-Ghibli anime", "lively world-music"),
     "user_goal": "Re-render my street-food market video in Studio-Ghibli anime style with lively world-music BGM."},
    {**_make("graduation ceremony", "oil-painting Impressionist", "uplifting orchestral"),
     "user_goal": "Apply oil-painting Impressionist style to my graduation ceremony clip with uplifting orchestral BGM."},
    {**_make("hiking trail", "Bob-Ross-style oil-painting", "ambient acoustic-guitar"),
     "user_goal": "Restyle my hiking trail clip in Bob-Ross-style oil-painting with ambient acoustic-guitar BGM."},
    {**_make("dance recital", "comic-book ink-and-color", "playful piano-and-strings"),
     "user_goal": "Re-render my dance recital video in comic-book ink-and-color style with playful piano-and-strings BGM."},
    {**_make("concert footage", "neon-cyberpunk", "high-energy drum-and-bass"),
     "user_goal": "Apply neon-cyberpunk style to my concert footage with high-energy drum-and-bass BGM."},
    {**_make("wedding ceremony", "vintage-1950s Technicolor", "romantic strings"),
     "user_goal": "Restyle my wedding ceremony video in vintage-1950s Technicolor style with romantic-strings BGM."},
    {**_make("cooking demo", "Studio-Ghibli watercolor", "cheerful ukulele"),
     "user_goal": "Re-render my cooking demo in Studio-Ghibli watercolor style with cheerful ukulele BGM."},
    {**_make("yoga session", "Japanese-ukiyo-e woodblock", "meditative ambient"),
     "user_goal": "Apply Japanese-ukiyo-e woodblock style to my yoga session with meditative ambient BGM."},
    {**_make("road-trip", "Wes-Anderson-pastel", "Americana folk"),
     "user_goal": "Restyle my road-trip video in Wes-Anderson-pastel style with Americana-folk BGM."},
    {**_make("museum tour", "Renaissance-fresco", "gentle classical-piano"),
     "user_goal": "Apply Renaissance-fresco style to my museum tour clip with gentle classical-piano BGM."},
    {**_make("gym workout", "graphic-novel halftone", "intense electronic-beats"),
     "user_goal": "Re-render my gym workout video in graphic-novel halftone style with intense electronic-beats BGM."},
    {**_make("autumn-leaves walk", "Monet-Impressionist", "wistful piano-and-cello"),
     "user_goal": "Apply Monet-Impressionist style to my autumn-leaves walk video with wistful piano-and-cello BGM."},
    {**_make("ski-trip", "Andy-Warhol pop-art", "epic adventure orchestral"),
     "user_goal": "Restyle my ski-trip clip in Andy-Warhol pop-art style with epic-adventure orchestral BGM."},
    {**_make("coastal drone footage", "Salvador-Dalí surrealist", "cinematic post-rock"),
     "user_goal": "Apply Salvador-Dalí surrealist style to my coastal drone footage with cinematic post-rock BGM."},
    {**_make("backyard barbecue", "Norman-Rockwell-Americana", "summer reggae"),
     "user_goal": "Re-render my backyard barbecue video in Norman-Rockwell-Americana style with summer-reggae BGM."},
    {**_make("fishing trip", "Hokusai-wave woodblock", "ambient guitar-and-pad"),
     "user_goal": "Apply Hokusai-wave woodblock style to my fishing trip clip with ambient guitar-and-pad BGM."},
    {**_make("Christmas-morning", "Hallmark-card watercolor", "festive piano-and-bells"),
     "user_goal": "Restyle my Christmas-morning clip in Hallmark-card watercolor style with festive piano-and-bells BGM."},
    {**_make("snowboarding", "comic-book Frank-Miller noir", "high-energy rock-guitar"),
     "user_goal": "Apply Frank-Miller-comic-book noir style to my snowboarding video with high-energy rock-guitar BGM."},
    {**_make("aquarium visit", "stained-glass cathedral", "ambient marimba"),
     "user_goal": "Re-render my aquarium visit clip in stained-glass cathedral style with ambient-marimba BGM."},
    {**_make("garden tour", "Beatrix-Potter watercolor", "pastoral flute-and-strings"),
     "user_goal": "Apply Beatrix-Potter watercolor style to my garden tour video with pastoral flute-and-strings BGM."},
    {**_make("amusement-park ride", "Saturday-morning-cartoon", "playful circus"),
     "user_goal": "Restyle my amusement-park ride clip in Saturday-morning-cartoon style with playful-circus BGM."},
    {**_make("ice-rink skating", "vintage-Disney 1940s", "dreamy waltz"),
     "user_goal": "Apply vintage-Disney 1940s style to my ice-rink skating clip with dreamy-waltz BGM."},
    {**_make("hot-air-balloon ride", "art-nouveau Mucha", "soaring strings"),
     "user_goal": "Re-render my hot-air-balloon ride clip in art-nouveau Mucha style with soaring-strings BGM."},
    {**_make("hiking summit", "Caspar-David-Friedrich Romantic", "epic horn-and-strings"),
     "user_goal": "Apply Caspar-David-Friedrich Romantic style to my hiking summit footage with epic horn-and-strings BGM."},
    {**_make("urban-skyline night", "Vincent-van-Gogh post-Impressionist", "synthwave 80s"),
     "user_goal": "Restyle my urban-skyline night video in Vincent-van-Gogh post-Impressionist style with synthwave 80s BGM."},
    {**_make("flower-show", "art-deco poster", "delicate harp-and-flute"),
     "user_goal": "Apply art-deco poster style to my flower-show video with delicate harp-and-flute BGM."},
    {**_make("kayaking trip", "Jean-Honoré-Fragonard Rococo", "adventure folk-rock"),
     "user_goal": "Re-render my kayaking trip clip in Rococo Fragonard style with adventure folk-rock BGM."},
    {**_make("airport-tarmac", "1980s-VHS retro", "ambient guitar-and-pad"),
     "user_goal": "Apply 1980s-VHS retro style to my airport-tarmac footage with ambient guitar-and-pad BGM."},
]
