"""GRPO shape: vid_music_ambience — IntakeVideo → Music → Ambience → AudioMix → Compositor.

30 samples (target_n=30). Add both BGM and ambient atmosphere to uploaded video.
"""
from __future__ import annotations


def _make(topic, music, ambience):
    return {
        "rationale": (
            f"{topic} clip + {music} BGM + {ambience} ambient bed. Reject "
            "Transcription/Translation, VideoAnalysis/Highlight, StyleTransfer/VideoExtend."
        ),
        "intents": [
            f"Ingest the user's uploaded {topic} clip into the workspace.",
            f"Compose the {music} BGM the user requested.",
            f"Generate the {ambience} ambient atmosphere as the audio bed.",
            f"Layer the {music} BGM and {ambience} ambient bed under the clip's baked audio into one final mixed wav.",
            f"Composite the final {topic} mp4 with mixed audio.",
        ],
    }


SAMPLES: list[dict] = [
    {**_make("vacation beach", "tropical surf-rock", "ocean-waves-and-distant-gull"),
     "user_goal": "Add tropical surf-rock BGM and an ocean-waves-and-distant-gull ambient bed to my vacation beach clip."},
    {**_make("forest hike", "ambient acoustic-guitar", "forest-bird-and-leaf-rustle"),
     "user_goal": "Layer ambient acoustic-guitar BGM and a forest-bird-and-leaf-rustle ambient bed over my forest hike clip."},
    {**_make("city night-drive", "synthwave 80s", "city-traffic-and-distant-siren"),
     "user_goal": "Add synthwave 80s BGM and a city-traffic-and-distant-siren ambient bed to my city night-drive video."},
    {**_make("autumn-park walk", "wistful piano-and-cello", "autumn-leaf-rustle-and-distant-bird"),
     "user_goal": "Layer wistful piano-and-cello BGM and an autumn-leaf-rustle-and-distant-bird ambient bed over my autumn-park walk clip."},
    {**_make("rainy-day cafe", "soft jazz-piano", "rain-on-window-and-distant-coffee-shop"),
     "user_goal": "Add soft jazz-piano BGM and a rain-on-window-and-distant-coffee-shop ambient bed to my rainy-day cafe clip."},
    {**_make("snowy mountain", "epic horn-and-strings", "wind-and-distant-avalanche"),
     "user_goal": "Layer epic horn-and-strings BGM and a wind-and-distant-avalanche ambient bed over my snowy mountain clip."},
    {**_make("desert sunrise", "ambient guitar-and-pad", "desert-wind-and-distant-wildlife"),
     "user_goal": "Add ambient guitar-and-pad BGM and a desert-wind-and-distant-wildlife ambient bed to my desert sunrise clip."},
    {**_make("kayak river-trip", "adventure folk-rock", "river-water-and-distant-bird"),
     "user_goal": "Layer adventure folk-rock BGM and a river-water-and-distant-bird ambient bed over my kayak river-trip footage."},
    {**_make("urban-street market", "lively world-music", "street-market-crowd"),
     "user_goal": "Add lively world-music BGM and a street-market-crowd ambient bed to my urban-street market clip."},
    {**_make("countryside-farm tour", "pastoral flute-and-strings", "farmyard-and-distant-tractor"),
     "user_goal": "Layer pastoral flute-and-strings BGM and a farmyard-and-distant-tractor ambient bed over my countryside-farm tour clip."},
    {**_make("aquarium visit", "ambient marimba", "underwater-and-distant-bubble"),
     "user_goal": "Add ambient-marimba BGM and an underwater-and-distant-bubble ambient bed to my aquarium visit clip."},
    {**_make("Tokyo neon-street", "Tokyo synth-pop", "Tokyo-rain-and-distant-train"),
     "user_goal": "Layer Tokyo synth-pop BGM and a Tokyo-rain-and-distant-train ambient bed over my Tokyo neon-street clip."},
    {**_make("Provence-village walk", "French accordion", "Provence-village-and-cicada"),
     "user_goal": "Add French-accordion BGM and a Provence-village-and-cicada ambient bed to my Provence-village walk clip."},
    {**_make("Andean-mountain trek", "Andean pan-flute", "Andean-mountain-wind"),
     "user_goal": "Layer Andean pan-flute BGM and an Andean-mountain-wind ambient bed over my Andean-mountain trek clip."},
    {**_make("Saharan-desert caravan", "North-African oud", "Saharan-wind-and-distant-camel"),
     "user_goal": "Add North-African oud BGM and a Saharan-wind-and-distant-camel ambient bed to my Saharan-desert caravan clip."},
    {**_make("Highland-Scotland walk", "Celtic-bagpipes-and-fiddle", "Highland-wind-and-distant-bird"),
     "user_goal": "Layer Celtic-bagpipes-and-fiddle BGM and a Highland-wind-and-distant-bird ambient bed over my Highland-Scotland walk clip."},
    {**_make("Hawaiian-beach sunset", "Hawaiian ukulele", "Pacific-wave-and-distant-bird"),
     "user_goal": "Add Hawaiian-ukulele BGM and a Pacific-wave-and-distant-bird ambient bed to my Hawaiian-beach sunset clip."},
    {**_make("Korean-temple visit", "Korean gayageum", "temple-bell-and-distant-monk-chant"),
     "user_goal": "Layer Korean gayageum BGM and a temple-bell-and-distant-monk-chant ambient bed over my Korean-temple visit clip."},
    {**_make("Indian-village festival", "Indian sitar-and-tabla", "festival-crowd-and-distant-temple-bell"),
     "user_goal": "Add Indian sitar-and-tabla BGM and a festival-crowd-and-distant-temple-bell ambient bed to my Indian-village festival clip."},
    {**_make("Tibetan-monastery walk", "Tibetan singing-bowl", "monastery-bell-and-mountain-wind"),
     "user_goal": "Layer Tibetan singing-bowl BGM and a monastery-bell-and-mountain-wind ambient bed over my Tibetan-monastery walk clip."},
    {**_make("Bali rice-terrace", "gamelan", "rice-terrace-water-and-frog"),
     "user_goal": "Add gamelan BGM and a rice-terrace-water-and-frog ambient bed to my Bali rice-terrace clip."},
    {**_make("Greek-island harbor", "bouzouki", "harbor-and-distant-cicada"),
     "user_goal": "Layer bouzouki BGM and a harbor-and-distant-cicada ambient bed over my Greek-island harbor clip."},
    {**_make("Norwegian-fjord cruise", "Nordic-strings", "fjord-water-and-distant-bird"),
     "user_goal": "Add Nordic-strings BGM and a fjord-water-and-distant-bird ambient bed to my Norwegian-fjord cruise clip."},
    {**_make("Brazilian-beach festival", "Brazilian samba", "beach-crowd-and-distant-drum"),
     "user_goal": "Layer Brazilian samba BGM and a beach-crowd-and-distant-drum ambient bed over my Brazilian-beach festival clip."},
    {**_make("Russian-winter walk", "Russian-balalaika", "snow-crunch-and-distant-bell"),
     "user_goal": "Add Russian-balalaika BGM and a snow-crunch-and-distant-bell ambient bed to my Russian-winter walk clip."},
    {**_make("Japanese-onsen", "Japanese shakuhachi-flute", "onsen-steam-and-distant-bell"),
     "user_goal": "Layer Japanese shakuhachi-flute BGM and an onsen-steam-and-distant-bell ambient bed over my Japanese-onsen clip."},
    {**_make("Egyptian-pyramid tour", "Egyptian oud-and-percussion", "desert-wind-and-distant-call-to-prayer"),
     "user_goal": "Add Egyptian oud-and-percussion BGM and a desert-wind-and-distant-call-to-prayer ambient bed to my Egyptian-pyramid tour clip."},
    {**_make("Mexican-festival parade", "Mexican mariachi", "festival-crowd-and-distant-fireworks"),
     "user_goal": "Layer Mexican-mariachi BGM and a festival-crowd-and-distant-fireworks ambient bed over my Mexican-festival parade clip."},
    {**_make("Argentine-tango milonga", "Argentine bandoneón", "milonga-crowd-and-distant-traffic"),
     "user_goal": "Add Argentine bandoneón BGM and a milonga-crowd-and-distant-traffic ambient bed to my Argentine-tango milonga clip."},
    {**_make("Vietnamese-Hanoi alley", "Vietnamese đàn tranh", "Hanoi-alley-and-distant-motorbike"),
     "user_goal": "Layer Vietnamese đàn tranh BGM and a Hanoi-alley-and-distant-motorbike ambient bed over my Vietnamese-Hanoi alley clip."},
]
