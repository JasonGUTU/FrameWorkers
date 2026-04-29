"""GRPO shape: vid_music — IntakeVideo → Music → AudioMix → Compositor.

30 samples (target_n=30). Add BGM to uploaded video.
"""
from __future__ import annotations


def _make(topic, music):
    return {
        "rationale": (
            f"{topic} clip + {music} BGM overlay. Reject AmbienceAgent (no atmospheric "
            "ask), Transcription/Translation (no subtitles), VideoAnalysis/Highlight "
            "(no analysis or trim), StyleTransfer/VideoExtend (no restyle / length change)."
        ),
        "intents": [
            f"Ingest the user's uploaded {topic} clip into the workspace.",
            f"Compose the {music} BGM the user requested.",
            f"Layer the {music} BGM under the clip's baked audio into one final mixed wav.",
            f"Composite the final {topic} mp4 with mixed audio.",
        ],
    }


SAMPLES: list[dict] = [
    {**_make("vacation beach", "tropical surf-rock"),
     "user_goal": "Add tropical surf-rock BGM to my vacation beach clip."},
    {**_make("birthday party", "upbeat indie-pop"),
     "user_goal": "Add upbeat indie-pop BGM to my birthday-party video."},
    {**_make("street-food market", "lively world-music"),
     "user_goal": "Layer lively world-music BGM over my street-food market clip."},
    {**_make("graduation ceremony", "uplifting orchestral"),
     "user_goal": "Add uplifting orchestral BGM to my graduation ceremony video."},
    {**_make("hiking trail", "ambient acoustic-guitar"),
     "user_goal": "Layer ambient acoustic-guitar BGM over my hiking trail clip."},
    {**_make("dance recital", "playful piano-and-strings"),
     "user_goal": "Add playful piano-and-strings BGM to my dance recital video."},
    {**_make("concert footage", "high-energy drum-and-bass"),
     "user_goal": "Layer high-energy drum-and-bass BGM over my concert footage."},
    {**_make("wedding ceremony", "romantic strings"),
     "user_goal": "Add romantic-strings BGM to my wedding ceremony video."},
    {**_make("cooking demo", "cheerful ukulele"),
     "user_goal": "Layer cheerful ukulele BGM over my cooking demo clip."},
    {**_make("yoga session", "meditative ambient"),
     "user_goal": "Add meditative ambient BGM to my yoga session video."},
    {**_make("road-trip", "Americana folk"),
     "user_goal": "Layer Americana-folk BGM over my road-trip footage."},
    {**_make("baby's first steps", "tender lullaby"),
     "user_goal": "Add tender lullaby BGM to my baby's-first-steps clip."},
    {**_make("museum tour", "gentle classical-piano"),
     "user_goal": "Layer gentle classical-piano BGM over my museum tour clip."},
    {**_make("gym workout", "intense electronic-beats"),
     "user_goal": "Add intense electronic-beats BGM to my gym workout video."},
    {**_make("autumn-leaves walk", "wistful piano-and-cello"),
     "user_goal": "Layer wistful piano-and-cello BGM over my autumn-leaves walk video."},
    {**_make("ski-trip", "epic adventure orchestral"),
     "user_goal": "Add epic-adventure orchestral BGM to my ski-trip clip."},
    {**_make("coastal drone footage", "cinematic post-rock"),
     "user_goal": "Layer cinematic post-rock BGM over my coastal drone footage."},
    {**_make("backyard barbecue", "summer reggae"),
     "user_goal": "Add summer-reggae BGM to my backyard barbecue video."},
    {**_make("Christmas-morning", "festive piano-and-bells"),
     "user_goal": "Layer festive piano-and-bells BGM over my Christmas-morning clip."},
    {**_make("snowboarding", "high-energy rock-guitar"),
     "user_goal": "Add high-energy rock-guitar BGM to my snowboarding video."},
    {**_make("aquarium visit", "ambient marimba"),
     "user_goal": "Layer ambient-marimba BGM over my aquarium visit clip."},
    {**_make("garden tour", "pastoral flute-and-strings"),
     "user_goal": "Add pastoral flute-and-strings BGM to my garden tour video."},
    {**_make("amusement-park ride", "playful circus"),
     "user_goal": "Layer playful-circus BGM over my amusement-park ride clip."},
    {**_make("first-day-of-school", "warm orchestral"),
     "user_goal": "Add warm-orchestral BGM to my first-day-of-school video."},
    {**_make("ice-rink skating", "dreamy waltz"),
     "user_goal": "Layer dreamy-waltz BGM over my ice-rink skating clip."},
    {**_make("hot-air-balloon ride", "soaring strings"),
     "user_goal": "Add soaring-strings BGM to my hot-air-balloon ride video."},
    {**_make("hiking summit", "epic horn-and-strings"),
     "user_goal": "Layer epic horn-and-strings BGM over my hiking summit footage."},
    {**_make("city-tour", "jazzy walking-bass"),
     "user_goal": "Add jazzy walking-bass BGM to my city tour video."},
    {**_make("flower-show", "delicate harp-and-flute"),
     "user_goal": "Layer delicate harp-and-flute BGM over my flower-show clip."},
    {**_make("kayaking trip", "adventure folk-rock"),
     "user_goal": "Add adventure folk-rock BGM to my kayaking trip video."},
]
