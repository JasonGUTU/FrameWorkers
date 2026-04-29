"""Shape: extend_style — IntakeVideo → VideoExtend → StyleTransfer (raw styled-extended output).

User uploaded a short video, wants it extended AND restyled.  Order
matters: extend first (so the extended clip inherits consistent baseline
frames), then StyleTransfer re-renders the whole longer clip.  Raw
styled-extended clip is the deliverable — no audio overlay, no subtitle,
no compositor pass.

Reject biases:
  - CompositorAgent (nothing to overlay on raw styled extended output)
  - MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay)
  - TranscriptionAgent / TranslationAgent (no subtitle)
  - VideoAnalysisAgent / HighlightAgent (no trimming)
"""
from __future__ import annotations

SAMPLES: list[dict] = [
    {
        "user_goal": "I have a short 5-second skateboard clip. Please extend it to about 15 seconds AND restyle the whole thing into a Japanese ukiyo-e woodblock look.",
        "rationale": (
            "User uploaded a 5-second skate clip, asks to extend to ~15 seconds AND apply a "
            "ukiyo-e woodblock style. IntakeVideoAgent ingests the clip. VideoExtendAgent "
            "generates the additional 10 seconds of motion first. StyleTransferAgent then "
            "re-renders the full 15-second extended clip in ukiyo-e style (applied once over "
            "the final extended length). Raw styled-extended clip is the deliverable. Reject "
            "CompositorAgent (nothing to overlay), MusicAgent / AmbienceAgent / AudioMixAgent "
            "(no audio overlay), TranscriptionAgent / TranslationAgent (no subtitle), "
            "VideoAnalysisAgent / HighlightAgent (no trim)."
        ),
        "intents": [
            "Ingest the 5-second skateboard clip into the workspace.",
            "Extend the skate clip from 5 to ~15 seconds preserving the trick motion.",
            "Restyle the full extended 15-second clip into a Japanese ukiyo-e woodblock aesthetic.",
        ],
    },
    {
        "user_goal": "Please extend this 6-second forest-walk footage to around 20 seconds and turn the whole thing into a Studio Ghibli watercolor style.",
        "rationale": (
            "Forest-walk clip + extend-to-20s + Ghibli watercolor style transfer. "
            "IntakeVideoAgent ingests the clip. VideoExtendAgent extends to ~20s preserving "
            "walk trajectory. StyleTransferAgent re-renders the full extended clip in Ghibli "
            "watercolor aesthetic. Raw styled-extended clip is the output."
        ),
        "intents": [
            "Ingest the 6-second forest-walk clip into the workspace.",
            "Extend the forest-walk footage to ~20 seconds preserving the walk trajectory.",
            "Restyle the full extended forest-walk clip into a Studio Ghibli watercolor aesthetic.",
        ],
    },
    {
        "user_goal": "Take this 4-second clip of a waterfall and extend it to 15 seconds, then restyle as a Chinese ink-wash painting.",
        "rationale": (
            "4-second waterfall clip + extend-to-15s + Chinese ink-wash style transfer. "
            "IntakeVideoAgent ingests the clip. VideoExtendAgent produces continuation frames "
            "to reach 15s. StyleTransferAgent re-renders the full extended waterfall in "
            "ink-wash aesthetic."
        ),
        "intents": [
            "Ingest the 4-second waterfall clip into the workspace.",
            "Extend the waterfall footage to ~15 seconds preserving the continuous flow.",
            "Restyle the full extended waterfall clip into a Chinese ink-wash painting aesthetic.",
        ],
    },
    {
        "user_goal": "Please extend this short 8-second cityscape clip to 25 seconds AND make it look like Blade Runner 2049's neon-noir style.",
        "rationale": (
            "Cityscape clip + extend-to-25s + Blade Runner 2049 neon-noir style. "
            "IntakeVideoAgent ingests the clip. VideoExtendAgent continues the cityscape motion "
            "to 25s. StyleTransferAgent re-renders the extended clip in the amber/teal neon-"
            "noir palette characteristic of BR2049."
        ),
        "intents": [
            "Ingest the 8-second cityscape clip into the workspace.",
            "Extend the cityscape footage to ~25 seconds preserving motion and time-of-day.",
            "Restyle the full extended cityscape clip into a Blade Runner 2049 neon-noir aesthetic.",
        ],
    },
    {
        "user_goal": "Extend this 5-second dance clip to about 15 seconds and make the whole piece look like a pastel watercolor animation.",
        "rationale": (
            "Dance clip + extend-to-15s + pastel watercolor animation style. IntakeVideoAgent "
            "ingests the clip. VideoExtendAgent extends the choreography motion. "
            "StyleTransferAgent re-renders the full extended dance in pastel watercolor "
            "animation aesthetic."
        ),
        "intents": [
            "Ingest the 5-second dance clip into the workspace.",
            "Extend the dance clip to ~15 seconds preserving the choreography motion.",
            "Restyle the full extended dance into a pastel watercolor animation aesthetic.",
        ],
    },
    {
        "user_goal": "Take this short 6-second shot of a bird in flight, extend to 20 seconds, and restyle as a Japanese woodblock nature print.",
        "rationale": (
            "Bird-in-flight clip + extend-to-20s + Japanese woodblock nature-print style. "
            "IntakeVideoAgent ingests the clip. VideoExtendAgent continues the flight arc. "
            "StyleTransferAgent re-renders the extended flight in a woodblock nature-print "
            "aesthetic."
        ),
        "intents": [
            "Ingest the 6-second bird-in-flight clip into the workspace.",
            "Extend the bird-in-flight clip to ~20 seconds continuing the flight arc.",
            "Restyle the full extended bird-flight clip into a Japanese woodblock nature-print aesthetic.",
        ],
    },
    {
        "user_goal": "Please extend this 7-second aerial beach-shot to 25 seconds and then give the whole thing a Van Gogh impasto oil-painting look.",
        "rationale": (
            "Aerial beach clip + extend-to-25s + Van Gogh impasto oil-paint style. "
            "IntakeVideoAgent ingests the clip. VideoExtendAgent continues the aerial sweep. "
            "StyleTransferAgent re-renders the full extended beach aerial in Van Gogh impasto "
            "aesthetic."
        ),
        "intents": [
            "Ingest the 7-second aerial beach-shot clip into the workspace.",
            "Extend the aerial beach footage to ~25 seconds continuing the flight path.",
            "Restyle the full extended aerial clip into a Van Gogh impasto oil-painting aesthetic.",
        ],
    },
    {
        "user_goal": "Extend this 4-second candle-flame clip to 12 seconds and turn the whole thing into a chiaroscuro Caravaggio-style painting look.",
        "rationale": (
            "Candle-flame clip + extend-to-12s + Caravaggio chiaroscuro style. IntakeVideoAgent "
            "ingests the clip. VideoExtendAgent extends the flame motion. StyleTransferAgent "
            "re-renders the full extended clip in Caravaggio's dramatic light-and-shadow "
            "aesthetic."
        ),
        "intents": [
            "Ingest the 4-second candle-flame clip into the workspace.",
            "Extend the candle-flame footage to ~12 seconds preserving the flicker cadence.",
            "Restyle the full extended candle clip into a Caravaggio chiaroscuro aesthetic.",
        ],
    },
    {
        "user_goal": "Please extend this 5-second horse-gallop clip to 18 seconds AND restyle as a Degas pastel painting.",
        "rationale": (
            "Horse-gallop clip + extend-to-18s + Degas pastel painting style. IntakeVideoAgent "
            "ingests the clip. VideoExtendAgent continues the gallop motion. "
            "StyleTransferAgent re-renders the extended clip in Degas's pastel equine-painting "
            "aesthetic."
        ),
        "intents": [
            "Ingest the 5-second horse-gallop clip into the workspace.",
            "Extend the horse-gallop footage to ~18 seconds continuing the gallop motion.",
            "Restyle the full extended gallop clip into a Degas pastel-painting aesthetic.",
        ],
    },
    {
        "user_goal": "Take this 6-second drone shot of a coastline, extend to 20 seconds, and give the full extended clip a Turner watercolor seascape look.",
        "rationale": (
            "Drone coastline + extend-to-20s + Turner watercolor seascape style. "
            "IntakeVideoAgent ingests the clip. VideoExtendAgent extends the drone sweep. "
            "StyleTransferAgent re-renders the extended coastline in Turner's atmospheric "
            "watercolor seascape aesthetic."
        ),
        "intents": [
            "Ingest the 6-second drone coastline clip into the workspace.",
            "Extend the drone coastline footage to ~20 seconds continuing the flight path.",
            "Restyle the full extended coastline clip into a Turner watercolor seascape aesthetic.",
        ],
    },
    {
        "user_goal": "Please extend this 5-second fireworks clip to 15 seconds and restyle it as a traditional Chinese New Year paper-cut art style.",
        "rationale": (
            "Fireworks clip + extend-to-15s + Chinese New Year paper-cut art style. "
            "IntakeVideoAgent ingests the clip. VideoExtendAgent produces more firework burst "
            "sequences. StyleTransferAgent re-renders the extended clip in traditional "
            "paper-cut aesthetic with bold red accents."
        ),
        "intents": [
            "Ingest the 5-second fireworks clip into the workspace.",
            "Extend the fireworks footage to ~15 seconds with additional burst sequences.",
            "Restyle the full extended fireworks clip into a Chinese New Year paper-cut aesthetic.",
        ],
    },
    {
        "user_goal": "Extend this short 4-second clip of a ballerina spinning to 12 seconds, then restyle as a Matisse cutout-collage.",
        "rationale": (
            "Ballerina-spinning clip + extend-to-12s + Matisse cutout-collage style. "
            "IntakeVideoAgent ingests the clip. VideoExtendAgent extends the spin for the "
            "additional seconds. StyleTransferAgent re-renders the full extended spin in "
            "Matisse cutout-collage aesthetic with flat bold colors."
        ),
        "intents": [
            "Ingest the 4-second ballerina-spinning clip into the workspace.",
            "Extend the ballerina-spin footage to ~12 seconds preserving the rotation.",
            "Restyle the full extended spin clip into a Matisse cutout-collage aesthetic.",
        ],
    },
    {
        "user_goal": "Please take this 7-second aerial clip of a forest canopy and extend to 25 seconds, then style it as a Monet impressionist painting.",
        "rationale": (
            "Forest-canopy aerial + extend-to-25s + Monet impressionist style. "
            "IntakeVideoAgent ingests the clip. VideoExtendAgent extends the aerial sweep "
            "over the canopy. StyleTransferAgent re-renders the extended aerial in Monet's "
            "impressionist soft-brush palette."
        ),
        "intents": [
            "Ingest the 7-second aerial forest-canopy clip into the workspace.",
            "Extend the aerial forest-canopy footage to ~25 seconds continuing the flight path.",
            "Restyle the full extended aerial clip into a Monet impressionist aesthetic.",
        ],
    },
    {
        "user_goal": "Extend this 6-second shot of autumn leaves falling to 20 seconds, then restyle as a watercolor children's-book illustration.",
        "rationale": (
            "Autumn-leaves-falling clip + extend-to-20s + children's-book watercolor style. "
            "IntakeVideoAgent ingests the clip. VideoExtendAgent continues the leaf-fall "
            "motion. StyleTransferAgent re-renders the extended clip in a children's-book "
            "watercolor illustration style."
        ),
        "intents": [
            "Ingest the 6-second autumn-leaves-falling clip into the workspace.",
            "Extend the autumn-leaves-falling footage to ~20 seconds with more leaves drifting down.",
            "Restyle the full extended leaves clip into a children's-book watercolor illustration.",
        ],
    },
    {
        "user_goal": "Take this 5-second clip of a blooming flower, extend to 15 seconds (fully open on camera), and restyle as a Georgia O'Keeffe close-up painting.",
        "rationale": (
            "Blooming-flower clip + extend-to-15s (full bloom) + Georgia O'Keeffe close-up "
            "painting style. IntakeVideoAgent ingests the clip. VideoExtendAgent continues "
            "the bloom through full opening. StyleTransferAgent re-renders the extended "
            "clip in O'Keeffe's large-scale close-up floral aesthetic."
        ),
        "intents": [
            "Ingest the 5-second blooming-flower clip into the workspace.",
            "Extend the blooming footage to ~15 seconds so the flower fully opens on camera.",
            "Restyle the full extended bloom clip into a Georgia O'Keeffe close-up floral aesthetic.",
        ],
    },
    {
        "user_goal": "Please extend this 4-second clip of a snowfall on city streets to 18 seconds, then restyle as a 1940s noir black-and-white look.",
        "rationale": (
            "Snowfall-on-street clip + extend-to-18s + 1940s film-noir B&W style. "
            "IntakeVideoAgent ingests the clip. VideoExtendAgent continues the snowfall. "
            "StyleTransferAgent re-renders the extended clip in 1940s noir high-contrast "
            "monochrome aesthetic."
        ),
        "intents": [
            "Ingest the 4-second snowfall-on-city-street clip into the workspace.",
            "Extend the snowfall-on-street footage to ~18 seconds preserving snow motion.",
            "Restyle the full extended snowfall clip into a 1940s film-noir B&W aesthetic.",
        ],
    },
    {
        "user_goal": "Extend this 5-second underwater-reef clip to 20 seconds AND restyle the full thing as a neon bioluminescence-glow abstract.",
        "rationale": (
            "Underwater-reef clip + extend-to-20s + neon bioluminescence-glow abstract style. "
            "IntakeVideoAgent ingests the clip. VideoExtendAgent produces more reef-swim "
            "footage. StyleTransferAgent re-renders the extended clip in a neon-glow "
            "bioluminescent abstract aesthetic."
        ),
        "intents": [
            "Ingest the 5-second underwater-reef clip into the workspace.",
            "Extend the reef footage to ~20 seconds with coherent fish / coral motion.",
            "Restyle the full extended reef clip into a neon bioluminescence-glow abstract aesthetic.",
        ],
    },
    {
        "user_goal": "Please extend this 6-second rain-on-street clip to 22 seconds, then apply a 1960s French New Wave black-and-white style.",
        "rationale": (
            "Rain-on-street clip + extend-to-22s + 1960s French New Wave B&W style. "
            "IntakeVideoAgent ingests the clip. VideoExtendAgent continues the rainfall. "
            "StyleTransferAgent re-renders the extended clip in French New Wave monochrome "
            "aesthetic with characteristic grain and framing."
        ),
        "intents": [
            "Ingest the 6-second rain-on-street clip into the workspace.",
            "Extend the rain-on-street footage to ~22 seconds preserving the rainfall cadence.",
            "Restyle the full extended rain clip into a 1960s French New Wave B&W aesthetic.",
        ],
    },
    {
        "user_goal": "Take this 5-second clip of a snake slithering and extend to 15 seconds, then restyle in a Henri Rousseau jungle-painting aesthetic.",
        "rationale": (
            "Snake-slithering clip + extend-to-15s + Henri Rousseau jungle-painting style. "
            "IntakeVideoAgent ingests the clip. VideoExtendAgent continues the slithering "
            "motion. StyleTransferAgent re-renders the extended clip in Rousseau's jungle-"
            "painting naive-art aesthetic."
        ),
        "intents": [
            "Ingest the 5-second snake-slithering clip into the workspace.",
            "Extend the snake-slithering footage to ~15 seconds continuing the motion.",
            "Restyle the full extended snake clip into a Henri Rousseau jungle-painting aesthetic.",
        ],
    },
    {
        "user_goal": "Please extend this 5-second shot of a desert sandstorm to 18 seconds and then restyle it as an apocalyptic sepia-tone oil painting.",
        "rationale": (
            "Desert-sandstorm clip + extend-to-18s + apocalyptic sepia-tone oil-painting style. "
            "IntakeVideoAgent ingests the clip. VideoExtendAgent extends the sandstorm motion. "
            "StyleTransferAgent re-renders the extended clip in apocalyptic sepia oil-painting "
            "aesthetic."
        ),
        "intents": [
            "Ingest the 5-second desert-sandstorm clip into the workspace.",
            "Extend the sandstorm footage to ~18 seconds preserving wind-driven motion.",
            "Restyle the full extended sandstorm clip into an apocalyptic sepia-tone oil-painting aesthetic.",
        ],
    },
]
