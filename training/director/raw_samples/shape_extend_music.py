"""Shape: extend_music — IntakeVideo → VideoExtend → Music → AudioMix → Compositor.

User uploaded short video, wants it extended AND has BGM added.

Reject: AmbienceAgent (music only), Transcription / Translation
(no subtitle), Style (no restyle), Analysis / Highlight (no trim).
"""
from __future__ import annotations

SAMPLES: list[dict] = [
    {
        "user_goal": "Please extend this 6-second surfing clip to 20 seconds and add some upbeat summer-reggae BGM.",
        "rationale": (
            "User uploaded a 6-second surfing clip and asks to extend to ~20 seconds AND add "
            "upbeat summer-reggae BGM. IntakeVideoAgent ingests. VideoExtendAgent extends the "
            "clip to 20 seconds first — so the BGM spans the correct length. MusicAgent "
            "composes the summer-reggae cue. AudioMixAgent mixes the BGM with the extended "
            "clip's baked audio. CompositorAgent muxes the mixed audio onto the extended "
            "footage. Reject AmbienceAgent (music only asked), Transcription / Translation "
            "(no subtitles), StyleTransferAgent (no restyle), VideoAnalysisAgent / "
            "HighlightAgent (no trimming)."
        ),
        "intents": [
            "Ingest the 6-second surfing clip into the workspace.",
            "Extend the surfing clip to ~20 seconds continuing the wave-riding motion.",
            "Compose an upbeat summer-reggae BGM cue covering the extended ~20-second length.",
            "Mix the reggae BGM with the extended surfing clip's baked audio.",
            "Compose the extended surfing clip with the mixed reggae BGM overlaid on the footage.",
        ],
    },
    {
        "user_goal": "I have a 5-second drone shot of mountain peaks. Please extend to 18 seconds and add an epic orchestral score.",
        "rationale": (
            "Mountain-peaks drone clip + extend + epic orchestral BGM. IntakeVideoAgent → "
            "VideoExtendAgent (~18s) → MusicAgent (epic orchestral) → AudioMixAgent → "
            "CompositorAgent. The extend-first ordering ensures the orchestral cue is composed "
            "for the full ~18s duration."
        ),
        "intents": [
            "Ingest the 5-second mountain-peaks drone clip into the workspace.",
            "Extend the drone clip to ~18 seconds continuing the flight path over the peaks.",
            "Compose an epic orchestral BGM covering the extended ~18-second length.",
            "Mix the orchestral BGM with the extended drone clip's wind / baked audio.",
            "Compose the extended drone clip with the mixed orchestral BGM overlaid on the mountain footage.",
        ],
    },
    {
        "user_goal": "Extend this 4-second skate-trick clip to 15 seconds and put some punk-rock BGM under it.",
        "rationale": (
            "Skate-trick clip + extend + punk-rock BGM. IntakeVideoAgent → VideoExtendAgent "
            "(~15s) → MusicAgent (punk-rock) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 4-second skate-trick clip into the workspace.",
            "Extend the skate clip to ~15 seconds preserving the trick motion and follow-through.",
            "Compose a punk-rock BGM cue covering the extended ~15-second length.",
            "Mix the punk-rock BGM with the extended skate clip's baked audio.",
            "Compose the extended skate clip with the mixed punk-rock BGM overlaid on the trick footage.",
        ],
    },
    {
        "user_goal": "Please extend this 7-second wedding-first-dance clip to 25 seconds and add a romantic string-quartet BGM.",
        "rationale": (
            "Wedding-first-dance clip + extend + romantic string-quartet BGM. "
            "IntakeVideoAgent → VideoExtendAgent (~25s) → MusicAgent (romantic string quartet) "
            "→ AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 7-second wedding-first-dance clip into the workspace.",
            "Extend the first-dance clip to ~25 seconds continuing the couple's dance motion.",
            "Compose a romantic string-quartet BGM covering the extended ~25-second length.",
            "Mix the string-quartet BGM with the extended first-dance clip's baked audio.",
            "Compose the extended first-dance clip with the mixed string-quartet BGM overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Extend this 5-second sunrise-timelapse to 20 seconds and add an uplifting ambient-cinematic BGM.",
        "rationale": (
            "Sunrise-timelapse + extend + uplifting ambient-cinematic BGM (music genre, not "
            "environmental sound). IntakeVideoAgent → VideoExtendAgent (~20s) → MusicAgent "
            "(ambient-cinematic) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 5-second sunrise-timelapse into the workspace.",
            "Extend the sunrise-timelapse to ~20 seconds continuing the color shift.",
            "Compose an uplifting ambient-cinematic BGM cue covering the extended ~20-second length.",
            "Mix the ambient-cinematic BGM with the extended timelapse's baked audio.",
            "Compose the extended timelapse with the mixed BGM overlaid on the sunrise footage.",
        ],
    },
    {
        "user_goal": "Please extend this 4-second horse-gallop clip to 15 seconds and add a Western-style harmonica-and-guitar BGM.",
        "rationale": (
            "Horse-gallop clip + extend + Western-style harmonica-guitar BGM. IntakeVideoAgent "
            "→ VideoExtendAgent (~15s) → MusicAgent (Western harmonica-guitar) → AudioMixAgent "
            "→ CompositorAgent."
        ),
        "intents": [
            "Ingest the 4-second horse-gallop clip into the workspace.",
            "Extend the gallop clip to ~15 seconds continuing the horse's motion.",
            "Compose a Western-style harmonica-and-guitar BGM covering the extended length.",
            "Mix the Western BGM with the extended gallop clip's baked audio.",
            "Compose the extended clip with the mixed Western BGM overlaid on the gallop footage.",
        ],
    },
    {
        "user_goal": "Extend this 6-second snowfall-in-forest clip to 20 seconds and add a cozy piano-ballad BGM.",
        "rationale": (
            "Snowfall-in-forest clip + extend + cozy piano-ballad BGM. IntakeVideoAgent → "
            "VideoExtendAgent (~20s) → MusicAgent (cozy piano ballad) → AudioMixAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 6-second snowfall-in-forest clip into the workspace.",
            "Extend the snowfall clip to ~20 seconds preserving the forest setting.",
            "Compose a cozy piano-ballad BGM covering the extended ~20-second length.",
            "Mix the piano BGM with the extended snowfall clip's ambient audio.",
            "Compose the extended clip with the mixed piano BGM overlaid on the snow-forest footage.",
        ],
    },
    {
        "user_goal": "Please extend this 5-second city-night-traffic clip to 18 seconds and add a synthwave-retro BGM.",
        "rationale": (
            "City-night-traffic clip + extend + synthwave-retro BGM. IntakeVideoAgent → "
            "VideoExtendAgent (~18s) → MusicAgent (synthwave) → AudioMixAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 5-second city-night-traffic clip into the workspace.",
            "Extend the city-night clip to ~18 seconds continuing the traffic flow.",
            "Compose a synthwave-retro BGM covering the extended ~18-second length.",
            "Mix the synthwave BGM with the extended city-night clip's baked audio.",
            "Compose the extended clip with the mixed synthwave BGM overlaid on the traffic footage.",
        ],
    },
    {
        "user_goal": "Extend this 7-second pottery-wheel clip to 22 seconds and add meditative Japanese-shakuhachi BGM.",
        "rationale": (
            "Pottery-wheel clip + extend + Japanese-shakuhachi meditative BGM. IntakeVideoAgent "
            "→ VideoExtendAgent (~22s) → MusicAgent (shakuhachi) → AudioMixAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 7-second pottery-wheel clip into the workspace.",
            "Extend the pottery-wheel clip to ~22 seconds continuing the shaping motion.",
            "Compose a meditative Japanese-shakuhachi BGM covering the extended length.",
            "Mix the shakuhachi BGM with the extended pottery clip's baked audio.",
            "Compose the extended clip with the mixed shakuhachi BGM overlaid on the pottery footage.",
        ],
    },
    {
        "user_goal": "Please extend this 4-second dance-clip to 12 seconds and put some lo-fi hip-hop BGM under it.",
        "rationale": (
            "Dance clip + extend + lo-fi hip-hop BGM. IntakeVideoAgent → VideoExtendAgent "
            "(~12s) → MusicAgent (lo-fi hip-hop) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 4-second dance clip into the workspace.",
            "Extend the dance clip to ~12 seconds continuing the choreography.",
            "Compose a lo-fi hip-hop BGM covering the extended ~12-second length.",
            "Mix the lo-fi BGM with the extended dance clip's baked audio.",
            "Compose the extended clip with the mixed lo-fi BGM overlaid on the dance footage.",
        ],
    },
    {
        "user_goal": "Extend this 6-second kids-playground clip to 20 seconds and add a cheerful ukulele-whistle BGM.",
        "rationale": (
            "Kids-playground clip + extend + cheerful ukulele-whistle BGM. IntakeVideoAgent → "
            "VideoExtendAgent (~20s) → MusicAgent (cheerful ukulele-whistle) → AudioMixAgent "
            "→ CompositorAgent."
        ),
        "intents": [
            "Ingest the 6-second kids-playground clip into the workspace.",
            "Extend the playground clip to ~20 seconds continuing the kids' play motion.",
            "Compose a cheerful ukulele-whistle BGM covering the extended ~20-second length.",
            "Mix the ukulele BGM with the extended playground clip's baked audio.",
            "Compose the extended clip with the mixed cheerful BGM overlaid on the playground footage.",
        ],
    },
    {
        "user_goal": "Please extend this 5-second firework-display clip to 18 seconds and add a dramatic Chinese-drum BGM.",
        "rationale": (
            "Fireworks clip + extend + Chinese-drum dramatic BGM. IntakeVideoAgent → "
            "VideoExtendAgent (~18s) → MusicAgent (Chinese drums) → AudioMixAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 5-second firework-display clip into the workspace.",
            "Extend the fireworks clip to ~18 seconds with additional burst sequences.",
            "Compose a dramatic Chinese-drum BGM covering the extended ~18-second length.",
            "Mix the Chinese-drum BGM with the extended fireworks clip's baked audio.",
            "Compose the extended clip with the mixed drum BGM overlaid on the fireworks footage.",
        ],
    },
    {
        "user_goal": "Extend this 4-second koi-pond clip to 15 seconds and add a gentle guzheng BGM.",
        "rationale": (
            "Koi-pond clip + extend + guzheng gentle BGM. IntakeVideoAgent → VideoExtendAgent "
            "(~15s) → MusicAgent (guzheng) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 4-second koi-pond clip into the workspace.",
            "Extend the koi-pond clip to ~15 seconds continuing the fish motion.",
            "Compose a gentle guzheng BGM covering the extended ~15-second length.",
            "Mix the guzheng BGM with the extended koi-pond clip's baked audio.",
            "Compose the extended clip with the mixed guzheng BGM overlaid on the koi-pond footage.",
        ],
    },
    {
        "user_goal": "Please extend this 6-second campfire-night clip to 20 seconds and add folk-acoustic-guitar BGM.",
        "rationale": (
            "Campfire-night clip + extend + folk-acoustic-guitar BGM. IntakeVideoAgent → "
            "VideoExtendAgent (~20s) → MusicAgent (folk acoustic guitar) → AudioMixAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 6-second campfire-night clip into the workspace.",
            "Extend the campfire clip to ~20 seconds preserving the flame motion.",
            "Compose a folk-acoustic-guitar BGM covering the extended length.",
            "Mix the folk-guitar BGM with the extended campfire clip's ambient audio.",
            "Compose the extended clip with the mixed folk BGM overlaid on the campfire footage.",
        ],
    },
    {
        "user_goal": "Extend this 5-second ferris-wheel clip to 18 seconds and add a carnival-style accordion BGM.",
        "rationale": (
            "Ferris-wheel clip + extend + carnival-accordion BGM. IntakeVideoAgent → "
            "VideoExtendAgent (~18s) → MusicAgent (carnival accordion) → AudioMixAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 5-second ferris-wheel clip into the workspace.",
            "Extend the ferris-wheel clip to ~18 seconds continuing the rotation.",
            "Compose a carnival-accordion BGM covering the extended ~18-second length.",
            "Mix the accordion BGM with the extended ferris-wheel clip's ambient audio.",
            "Compose the extended clip with the mixed carnival BGM overlaid on the ferris-wheel footage.",
        ],
    },
    {
        "user_goal": "Please extend this 7-second beach-walk clip to 22 seconds and add a mellow bossa-nova BGM.",
        "rationale": (
            "Beach-walk clip + extend + mellow bossa-nova BGM. IntakeVideoAgent → "
            "VideoExtendAgent (~22s) → MusicAgent (bossa-nova) → AudioMixAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 7-second beach-walk clip into the workspace.",
            "Extend the beach-walk clip to ~22 seconds continuing the walking motion.",
            "Compose a mellow bossa-nova BGM covering the extended ~22-second length.",
            "Mix the bossa-nova BGM with the extended beach-walk clip's ambient audio.",
            "Compose the extended clip with the mixed bossa BGM overlaid on the beach-walk footage.",
        ],
    },
    {
        "user_goal": "Extend this 4-second candle-flame clip to 12 seconds and add a haunting cello-solo BGM.",
        "rationale": (
            "Candle-flame clip + extend + haunting cello solo BGM. IntakeVideoAgent → "
            "VideoExtendAgent (~12s) → MusicAgent (haunting cello) → AudioMixAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 4-second candle-flame clip into the workspace.",
            "Extend the candle-flame clip to ~12 seconds preserving the flicker cadence.",
            "Compose a haunting cello-solo BGM covering the extended ~12-second length.",
            "Mix the cello BGM with the extended candle clip's baked audio.",
            "Compose the extended clip with the mixed cello BGM overlaid on the candle footage.",
        ],
    },
    {
        "user_goal": "Please extend this 6-second dog-running clip to 20 seconds and add cheerful Disney-style BGM.",
        "rationale": (
            "Dog-running clip + extend + cheerful Disney-style BGM. IntakeVideoAgent → "
            "VideoExtendAgent (~20s) → MusicAgent (Disney-style cheerful) → AudioMixAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 6-second dog-running clip into the workspace.",
            "Extend the dog-running clip to ~20 seconds continuing the motion.",
            "Compose a cheerful Disney-style BGM covering the extended ~20-second length.",
            "Mix the Disney BGM with the extended dog clip's baked audio.",
            "Compose the extended clip with the mixed Disney BGM overlaid on the dog-running footage.",
        ],
    },
    {
        "user_goal": "Extend this 5-second balloon-inflation clip to 15 seconds and add a playful xylophone-percussion BGM.",
        "rationale": (
            "Balloon-inflation clip + extend + playful xylophone-percussion BGM. "
            "IntakeVideoAgent → VideoExtendAgent (~15s) → MusicAgent (playful xylophone) → "
            "AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 5-second balloon-inflation clip into the workspace.",
            "Extend the balloon clip to ~15 seconds so the balloon fully inflates.",
            "Compose a playful xylophone-percussion BGM covering the extended length.",
            "Mix the xylophone BGM with the extended balloon clip's baked audio.",
            "Compose the extended clip with the mixed xylophone BGM overlaid on the balloon footage.",
        ],
    },
    {
        "user_goal": "Please extend this 7-second waterfall clip to 22 seconds and add a meditative tibetan-bowl BGM.",
        "rationale": (
            "Waterfall clip + extend + meditative tibetan-bowl BGM. IntakeVideoAgent → "
            "VideoExtendAgent (~22s) → MusicAgent (tibetan singing bowl) → AudioMixAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 7-second waterfall clip into the workspace.",
            "Extend the waterfall clip to ~22 seconds preserving continuous water flow.",
            "Compose a meditative tibetan-bowl BGM covering the extended ~22-second length.",
            "Mix the tibetan-bowl BGM with the extended waterfall clip's ambient audio.",
            "Compose the extended clip with the mixed tibetan BGM overlaid on the waterfall footage.",
        ],
    },
    {
        "user_goal": "Extend this 4-second autumn-forest-walk clip to 12 seconds and add a celtic-harp BGM.",
        "rationale": (
            "Autumn-forest-walk clip + extend + celtic-harp BGM. IntakeVideoAgent → "
            "VideoExtendAgent (~12s) → MusicAgent (celtic harp) → AudioMixAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 4-second autumn-forest-walk clip into the workspace.",
            "Extend the walk clip to ~12 seconds continuing the forest walk.",
            "Compose a celtic-harp BGM covering the extended ~12-second length.",
            "Mix the harp BGM with the extended walk clip's ambient audio.",
            "Compose the extended clip with the mixed harp BGM overlaid on the autumn-forest footage.",
        ],
    },
    {
        "user_goal": "Please extend this 5-second aerial-lighthouse clip to 18 seconds and add a grand brass-fanfare BGM.",
        "rationale": (
            "Aerial-lighthouse clip + extend + grand brass-fanfare BGM. IntakeVideoAgent → "
            "VideoExtendAgent (~18s) → MusicAgent (grand brass fanfare) → AudioMixAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 5-second aerial-lighthouse clip into the workspace.",
            "Extend the aerial clip to ~18 seconds continuing the flight path.",
            "Compose a grand brass-fanfare BGM covering the extended ~18-second length.",
            "Mix the brass BGM with the extended aerial clip's wind / baked audio.",
            "Compose the extended clip with the mixed brass BGM overlaid on the lighthouse footage.",
        ],
    },
    {
        "user_goal": "Extend this 6-second tea-pour clip to 20 seconds and add a gentle Japanese-koto BGM.",
        "rationale": (
            "Tea-pour clip + extend + gentle Japanese-koto BGM. IntakeVideoAgent → "
            "VideoExtendAgent (~20s) → MusicAgent (gentle koto) → AudioMixAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 6-second tea-pour clip into the workspace.",
            "Extend the tea-pour clip to ~20 seconds continuing the pour motion.",
            "Compose a gentle Japanese-koto BGM covering the extended ~20-second length.",
            "Mix the koto BGM with the extended tea-pour clip's ambient audio.",
            "Compose the extended clip with the mixed koto BGM overlaid on the tea-pour footage.",
        ],
    },
    {
        "user_goal": "Please extend this 4-second cherry-blossom clip to 12 seconds and add a gentle shakuhachi-and-flute BGM.",
        "rationale": (
            "Cherry-blossom clip + extend + shakuhachi-flute gentle BGM. IntakeVideoAgent → "
            "VideoExtendAgent (~12s) → MusicAgent (shakuhachi and flute) → AudioMixAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 4-second cherry-blossom clip into the workspace.",
            "Extend the cherry-blossom clip to ~12 seconds preserving petal motion.",
            "Compose a gentle shakuhachi-and-flute BGM covering the extended length.",
            "Mix the BGM with the extended cherry-blossom clip's ambient audio.",
            "Compose the extended clip with the mixed flute BGM overlaid on the blossom footage.",
        ],
    },
    {
        "user_goal": "Extend this 7-second cathedral-interior walk to 22 seconds and add a grand pipe-organ BGM.",
        "rationale": (
            "Cathedral-interior walk + extend + grand pipe-organ BGM. IntakeVideoAgent → "
            "VideoExtendAgent (~22s) → MusicAgent (grand pipe organ) → AudioMixAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 7-second cathedral-interior walk into the workspace.",
            "Extend the walk to ~22 seconds continuing the motion through the cathedral.",
            "Compose a grand pipe-organ BGM covering the extended ~22-second length.",
            "Mix the pipe-organ BGM with the extended walk's baked audio.",
            "Compose the extended clip with the mixed organ BGM overlaid on the cathedral footage.",
        ],
    },
    {
        "user_goal": "Please extend this 5-second martial-arts spar clip to 18 seconds and add an epic taiko-drum BGM.",
        "rationale": (
            "Martial-arts spar clip + extend + epic taiko-drum BGM. IntakeVideoAgent → "
            "VideoExtendAgent (~18s) → MusicAgent (epic taiko) → AudioMixAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 5-second martial-arts spar clip into the workspace.",
            "Extend the spar clip to ~18 seconds continuing the exchange.",
            "Compose an epic taiko-drum BGM covering the extended ~18-second length.",
            "Mix the taiko BGM with the extended spar clip's baked audio.",
            "Compose the extended clip with the mixed taiko BGM overlaid on the spar footage.",
        ],
    },
    {
        "user_goal": "Extend this 4-second autumn-maple-falling clip to 12 seconds and add a gentle clarinet-solo BGM.",
        "rationale": (
            "Autumn-maple-falling clip + extend + gentle clarinet-solo BGM. IntakeVideoAgent → "
            "VideoExtendAgent (~12s) → MusicAgent (gentle clarinet solo) → AudioMixAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 4-second autumn-maple-falling clip into the workspace.",
            "Extend the maple-falling clip to ~12 seconds with more leaves drifting down.",
            "Compose a gentle clarinet-solo BGM covering the extended ~12-second length.",
            "Mix the clarinet BGM with the extended maple clip's ambient audio.",
            "Compose the extended clip with the mixed clarinet BGM overlaid on the maple footage.",
        ],
    },
    {
        "user_goal": "Please extend this 6-second ballerina-spin clip to 20 seconds and add a sweeping string-orchestra BGM.",
        "rationale": (
            "Ballerina-spin clip + extend + sweeping string-orchestra BGM. IntakeVideoAgent → "
            "VideoExtendAgent (~20s) → MusicAgent (sweeping string orchestra) → AudioMixAgent "
            "→ CompositorAgent."
        ),
        "intents": [
            "Ingest the 6-second ballerina-spin clip into the workspace.",
            "Extend the ballerina-spin clip to ~20 seconds preserving the rotation.",
            "Compose a sweeping string-orchestra BGM covering the extended ~20-second length.",
            "Mix the orchestral BGM with the extended spin clip's baked audio.",
            "Compose the extended clip with the mixed orchestral BGM overlaid on the ballerina footage.",
        ],
    },
    {
        "user_goal": "Extend this 5-second river-flow clip to 18 seconds and add a peaceful bamboo-flute BGM.",
        "rationale": (
            "River-flow clip + extend + peaceful bamboo-flute BGM. IntakeVideoAgent → "
            "VideoExtendAgent (~18s) → MusicAgent (peaceful bamboo flute) → AudioMixAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 5-second river-flow clip into the workspace.",
            "Extend the river clip to ~18 seconds preserving continuous water motion.",
            "Compose a peaceful bamboo-flute BGM covering the extended ~18-second length.",
            "Mix the flute BGM with the extended river clip's ambient audio.",
            "Compose the extended clip with the mixed flute BGM overlaid on the river footage.",
        ],
    },
    {
        "user_goal": "Please extend this 7-second lava-flow clip to 22 seconds and add an ominous low-drone-brass BGM.",
        "rationale": (
            "Lava-flow clip + extend + ominous low-drone-brass BGM. IntakeVideoAgent → "
            "VideoExtendAgent (~22s) → MusicAgent (ominous drone brass) → AudioMixAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 7-second lava-flow clip into the workspace.",
            "Extend the lava-flow clip to ~22 seconds preserving flow dynamics.",
            "Compose an ominous low-drone-brass BGM covering the extended ~22-second length.",
            "Mix the drone BGM with the extended lava clip's baked audio.",
            "Compose the extended clip with the mixed ominous BGM overlaid on the lava footage.",
        ],
    },
]
