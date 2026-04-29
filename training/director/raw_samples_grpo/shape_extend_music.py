"""GRPO shape: extend_music — IntakeVideo → VideoExtend → Music → AudioMix → Compositor.

30 samples (target_n=30). Extend video + add BGM.
"""
from __future__ import annotations


def _make(topic, target_dur, music):
    return {
        "rationale": (
            f"{topic} clip + extend-to-{target_dur} + {music} BGM. Reject AmbienceAgent "
            "(only music asked), Transcription/Translation, VideoAnalysis/Highlight, "
            "StyleTransferAgent (no restyle)."
        ),
        "intents": [
            f"Ingest the user's uploaded {topic} clip into the workspace.",
            f"Extend the {topic} clip to ~{target_dur} duration.",
            f"Compose the {music} BGM the user requested.",
            f"Layer the {music} BGM under the extended clip's audio into one final mixed wav.",
            f"Composite the final extended {topic} mp4 with mixed audio.",
        ],
    }


SAMPLES: list[dict] = [
    {**_make("vacation beach", "60 seconds", "tropical surf-rock"),
     "user_goal": "Extend my vacation beach clip to ~60 seconds and add tropical surf-rock BGM."},
    {**_make("forest-fog scenery", "45 seconds", "ambient acoustic-guitar"),
     "user_goal": "Extend my forest-fog scenery clip to ~45 seconds and add ambient acoustic-guitar BGM."},
    {**_make("city night-drive", "30 seconds", "synthwave 80s"),
     "user_goal": "Extend my city night-drive clip to ~30 seconds and add synthwave 80s BGM."},
    {**_make("autumn-park walk", "40 seconds", "wistful piano"),
     "user_goal": "Extend my autumn-park walk clip to ~40 seconds and add wistful piano BGM."},
    {**_make("rainy-day cafe", "50 seconds", "soft jazz-piano"),
     "user_goal": "Extend my rainy-day cafe clip to ~50 seconds and add soft jazz-piano BGM."},
    {**_make("snowy mountain", "30 seconds", "epic horn-and-strings"),
     "user_goal": "Extend my snowy-mountain clip to ~30 seconds and add epic horn-and-strings BGM."},
    {**_make("desert sunrise", "60 seconds", "ambient guitar-and-pad"),
     "user_goal": "Extend my desert-sunrise clip to ~60 seconds and add ambient guitar-and-pad BGM."},
    {**_make("kayak river-trip", "45 seconds", "adventure folk-rock"),
     "user_goal": "Extend my kayak river-trip clip to ~45 seconds and add adventure folk-rock BGM."},
    {**_make("urban-street market", "30 seconds", "lively world-music"),
     "user_goal": "Extend my urban-street market clip to ~30 seconds and add lively world-music BGM."},
    {**_make("countryside-farm tour", "40 seconds", "pastoral flute-and-strings"),
     "user_goal": "Extend my countryside-farm tour clip to ~40 seconds and add pastoral flute-and-strings BGM."},
    {**_make("aquarium visit", "50 seconds", "ambient marimba"),
     "user_goal": "Extend my aquarium visit clip to ~50 seconds and add ambient-marimba BGM."},
    {**_make("Tokyo neon-street", "30 seconds", "Tokyo synth-pop"),
     "user_goal": "Extend my Tokyo neon-street clip to ~30 seconds and add Tokyo synth-pop BGM."},
    {**_make("Provence-village walk", "45 seconds", "French accordion"),
     "user_goal": "Extend my Provence-village walk clip to ~45 seconds and add French-accordion BGM."},
    {**_make("Andean-mountain trek", "60 seconds", "Andean pan-flute"),
     "user_goal": "Extend my Andean-mountain trek clip to ~60 seconds and add Andean pan-flute BGM."},
    {**_make("Saharan-desert caravan", "45 seconds", "North-African oud"),
     "user_goal": "Extend my Saharan-desert caravan clip to ~45 seconds and add North-African oud BGM."},
    {**_make("Highland-Scotland walk", "30 seconds", "Celtic-bagpipes-and-fiddle"),
     "user_goal": "Extend my Highland-Scotland walk clip to ~30 seconds and add Celtic-bagpipes-and-fiddle BGM."},
    {**_make("Hawaiian-beach sunset", "40 seconds", "Hawaiian ukulele"),
     "user_goal": "Extend my Hawaiian-beach sunset clip to ~40 seconds and add Hawaiian-ukulele BGM."},
    {**_make("Korean-temple visit", "50 seconds", "Korean gayageum"),
     "user_goal": "Extend my Korean-temple visit clip to ~50 seconds and add Korean gayageum BGM."},
    {**_make("Indian-village festival", "30 seconds", "Indian sitar-and-tabla"),
     "user_goal": "Extend my Indian-village festival clip to ~30 seconds and add Indian sitar-and-tabla BGM."},
    {**_make("Tibetan-monastery walk", "45 seconds", "Tibetan singing-bowl"),
     "user_goal": "Extend my Tibetan-monastery walk clip to ~45 seconds and add Tibetan singing-bowl BGM."},
    {**_make("Bali rice-terrace", "60 seconds", "gamelan"),
     "user_goal": "Extend my Bali rice-terrace clip to ~60 seconds and add gamelan BGM."},
    {**_make("Greek-island harbor", "40 seconds", "bouzouki"),
     "user_goal": "Extend my Greek-island harbor clip to ~40 seconds and add bouzouki BGM."},
    {**_make("Norwegian-fjord cruise", "45 seconds", "Nordic-strings"),
     "user_goal": "Extend my Norwegian-fjord cruise clip to ~45 seconds and add Nordic-strings BGM."},
    {**_make("Brazilian-beach festival", "30 seconds", "Brazilian samba"),
     "user_goal": "Extend my Brazilian-beach festival clip to ~30 seconds and add Brazilian samba BGM."},
    {**_make("Russian-winter walk", "50 seconds", "Russian-balalaika"),
     "user_goal": "Extend my Russian-winter walk clip to ~50 seconds and add Russian-balalaika BGM."},
    {**_make("Japanese-onsen", "60 seconds", "Japanese shakuhachi-flute"),
     "user_goal": "Extend my Japanese-onsen clip to ~60 seconds and add Japanese shakuhachi-flute BGM."},
    {**_make("Egyptian-pyramid tour", "45 seconds", "Egyptian oud-and-percussion"),
     "user_goal": "Extend my Egyptian-pyramid tour clip to ~45 seconds and add Egyptian oud-and-percussion BGM."},
    {**_make("Mexican-festival parade", "30 seconds", "Mexican mariachi"),
     "user_goal": "Extend my Mexican-festival parade clip to ~30 seconds and add Mexican-mariachi BGM."},
    {**_make("Argentine-tango milonga", "45 seconds", "Argentine bandoneón"),
     "user_goal": "Extend my Argentine-tango milonga clip to ~45 seconds and add Argentine bandoneón BGM."},
    {**_make("Vietnamese-Hanoi alley", "40 seconds", "Vietnamese đàn tranh"),
     "user_goal": "Extend my Vietnamese-Hanoi alley clip to ~40 seconds and add Vietnamese đàn tranh BGM."},
]
