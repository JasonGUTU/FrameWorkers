"""Shape: extend_ambience —
    IntakeVideo → VideoExtend → Ambience → AudioMix → Compositor.

User uploads a video clip + asks to extend it AND add an environmental
sound layer (rain / wind / wave / forest / thunder / crowd / city / etc.).
Symmetric to extend_music — the audio slot is filled by AmbienceAgent
(environmental sound), not MusicAgent (melodic BGM). (Path B alignment with
v3 eval — opt-in audio: chain has Ambience iff user_goal explicitly mentions
environmental sound.)
"""
from __future__ import annotations

SAMPLES: list[dict] = [
    {
        "user_goal": "Extend this scene of the female lead confessing and crying by 8 seconds, adding rain sound effects and close-ups of her trembling hands.",
        "rationale": "Confession-and-rain extension + environmental rain layer. Chain: IntakeVideo → VideoExtend → Ambience → AudioMix → Compositor → done.",
        "intents": [
            "Ingest the uploaded confession-scene clip into the workspace.",
            "Extend the clip by 8 seconds with close-ups of trembling hands.",
            "Generate rain sound effects as an environmental ambient layer.",
            "Mix the rain ambient with the extended clip's baked-in audio.",
            "Composite the final clip with the extended footage and mixed rain ambient track.",
        ],
    },
    {
        "user_goal": "Extend this rooftop sunset farewell shot by 12 seconds, layering in distant city traffic ambient sounds.",
        "rationale": "Rooftop farewell extension + city-traffic ambient layer. Chain: IntakeVideo → VideoExtend → Ambience → AudioMix → Compositor → done.",
        "intents": [
            "Ingest the rooftop farewell clip into the workspace.",
            "Extend the clip by 12 seconds with the sunset reflection lingering.",
            "Generate distant city-traffic ambient sounds (cars, distant horns, wind across rooftop).",
            "Mix the city ambient with the extended clip's baked audio.",
            "Composite the final extended shot with the city ambient overlay.",
        ],
    },
    {
        "user_goal": "Extend this haunted-corridor walk-through scene by 10 seconds, adding distant creaks, wind howl, and a faint dripping sound effect bed.",
        "rationale": "Haunted-corridor extension + multi-element ambient bed (creaks, wind, drips). Chain: IntakeVideo → VideoExtend → Ambience → AudioMix → Compositor → done.",
        "intents": [
            "Ingest the haunted-corridor clip into the workspace.",
            "Extend the corridor walk-through by 10 seconds with deeper visual perspective.",
            "Generate the layered ambient bed: distant wood creaks, wind howl through windows, faint dripping.",
            "Mix the haunted ambient bed with the extended clip's baked audio.",
            "Composite the final clip with extended footage and ambient overlay.",
        ],
    },
    {
        "user_goal": "Extend this seaside lovers' farewell shot by 15 seconds, layering in ocean wave and seagull ambient sounds.",
        "rationale": "Seaside farewell extension + ocean+seagull ambient. Chain: IntakeVideo → VideoExtend → Ambience → AudioMix → Compositor → done.",
        "intents": [
            "Ingest the seaside farewell clip into the workspace.",
            "Extend the shot by 15 seconds with the lovers' silhouettes lingering.",
            "Generate ocean-wave and distant seagull ambient sounds.",
            "Mix the seaside ambient with the extended clip's baked audio.",
            "Composite the final extended shot with the seaside ambient overlay.",
        ],
    },
    {
        "user_goal": "Extend this thunderstorm-night chase sequence by 20 seconds, adding heavy rain, thunder rolls, and rumbling wind sound effects.",
        "rationale": "Thunderstorm-night chase extension + multi-layer storm ambient. Chain: IntakeVideo → VideoExtend → Ambience → AudioMix → Compositor → done.",
        "intents": [
            "Ingest the thunderstorm chase clip into the workspace.",
            "Extend the chase by 20 seconds with additional pursuit footage.",
            "Generate thunderstorm ambient: heavy rain, distant thunder rolls, rumbling wind.",
            "Mix the storm ambient with the extended clip's baked audio.",
            "Composite the final extended chase with the storm ambient overlay.",
        ],
    },
    {
        "user_goal": "Extend this forest-trek scene by 8 seconds, adding bird-chirp and distant stream-water sound effects.",
        "rationale": "Forest-trek extension + forest-bird+stream ambient. Chain: IntakeVideo → VideoExtend → Ambience → AudioMix → Compositor → done.",
        "intents": [
            "Ingest the forest-trek clip into the workspace.",
            "Extend the trek by 8 seconds with deeper forest visual exploration.",
            "Generate bird-chirp and distant stream-water ambient sounds.",
            "Mix the forest ambient with the extended clip's baked audio.",
            "Composite the final extended trek with the forest ambient overlay.",
        ],
    },
    {
        "user_goal": "Extend this market-bargaining scene by 10 seconds, layering in crowd chatter and distant vendor calls as ambient sounds.",
        "rationale": "Market-bargaining extension + market-crowd ambient. Chain: IntakeVideo → VideoExtend → Ambience → AudioMix → Compositor → done.",
        "intents": [
            "Ingest the market-bargaining clip into the workspace.",
            "Extend the bargaining sequence by 10 seconds.",
            "Generate market-crowd ambient: chatter, distant vendor calls, footsteps on cobblestones.",
            "Mix the market ambient with the extended clip's baked audio.",
            "Composite the final extended scene with the market ambient overlay.",
        ],
    },
    {
        "user_goal": "Extend this cave-exploration scene by 12 seconds, adding water drip, distant cave echo, and faint bat-wing flutter sound effects.",
        "rationale": "Cave-exploration extension + cave ambient (drips, echoes, bats). Chain: IntakeVideo → VideoExtend → Ambience → AudioMix → Compositor → done.",
        "intents": [
            "Ingest the cave-exploration clip into the workspace.",
            "Extend the exploration by 12 seconds, deeper into the cavern.",
            "Generate cave ambient: water drips, distant echoing chambers, faint bat-wing flutter.",
            "Mix the cave ambient with the extended clip's baked audio.",
            "Composite the final extended cave scene with the ambient overlay.",
        ],
    },
    {
        "user_goal": "Extend this airport-departure goodbye scene by 10 seconds, layering in airport announcement chatter and distant jet-engine ambient sounds.",
        "rationale": "Airport-departure extension + airport ambient (announcements, jet engines). Chain: IntakeVideo → VideoExtend → Ambience → AudioMix → Compositor → done.",
        "intents": [
            "Ingest the airport-departure clip into the workspace.",
            "Extend the goodbye scene by 10 seconds with the lovers' last glance.",
            "Generate airport ambient: muffled PA announcements, distant jet engines, footsteps on tile.",
            "Mix the airport ambient with the extended clip's baked audio.",
            "Composite the final extended airport scene with the ambient overlay.",
        ],
    },
    {
        "user_goal": "Extend this rainy-night Paris café reunion scene by 8 seconds, adding café chatter, espresso machine hisses, and outside rain ambient.",
        "rationale": "Paris café reunion extension + café+rain ambient. Chain: IntakeVideo → VideoExtend → Ambience → AudioMix → Compositor → done.",
        "intents": [
            "Ingest the Paris café reunion clip into the workspace.",
            "Extend the reunion scene by 8 seconds with extended emotional reactions.",
            "Generate café-and-rain ambient: chatter, espresso machine, outside rain on glass.",
            "Mix the café ambient with the extended clip's baked audio.",
            "Composite the final extended café scene with the ambient overlay.",
        ],
    },
    {
        "user_goal": "Extend this snowy-mountain trek scene by 15 seconds, layering in howling wind and distant snow-crunch sound effects.",
        "rationale": "Snowy-mountain trek extension + wind+snow-crunch ambient. Chain: IntakeVideo → VideoExtend → Ambience → AudioMix → Compositor → done.",
        "intents": [
            "Ingest the snowy-mountain clip into the workspace.",
            "Extend the trek by 15 seconds across the icy ridge.",
            "Generate snowy-mountain ambient: howling wind, snow underfoot, distant ice creaks.",
            "Mix the mountain ambient with the extended clip's baked audio.",
            "Composite the final extended trek with the mountain ambient overlay.",
        ],
    },
    {
        "user_goal": "Extend this medieval battlefield aftermath shot by 12 seconds, adding distant crow caws, smoldering-fire crackle, and wind rolling across the field as ambient sounds.",
        "rationale": "Battlefield aftermath extension + battlefield ambient (crows, fire, wind). Chain: IntakeVideo → VideoExtend → Ambience → AudioMix → Compositor → done.",
        "intents": [
            "Ingest the battlefield aftermath clip into the workspace.",
            "Extend the aftermath shot by 12 seconds with the camera panning across the field.",
            "Generate battlefield ambient: distant crows, smoldering fire crackle, wind across the field.",
            "Mix the battlefield ambient with the extended clip's baked audio.",
            "Composite the final extended battlefield scene with the ambient overlay.",
        ],
    },
    {
        "user_goal": "Extend this office late-night break-up scene by 8 seconds, layering in distant city traffic, office HVAC hum, and faint elevator ding ambient sounds.",
        "rationale": "Office break-up extension + office+city ambient (HVAC, traffic, elevator). Chain: IntakeVideo → VideoExtend → Ambience → AudioMix → Compositor → done.",
        "intents": [
            "Ingest the office break-up clip into the workspace.",
            "Extend the break-up scene by 8 seconds with quieter aftermath.",
            "Generate office-night ambient: distant city traffic, HVAC hum, faint elevator ding.",
            "Mix the office ambient with the extended clip's baked audio.",
            "Composite the final extended office scene with the ambient overlay.",
        ],
    },
    {
        "user_goal": "Extend this temple meditation scene by 10 seconds, adding distant gong reverberation, wind through pine trees, and incense smoke crackle ambient.",
        "rationale": "Temple meditation extension + temple-natural ambient (gong, wind, crackle). Chain: IntakeVideo → VideoExtend → Ambience → AudioMix → Compositor → done.",
        "intents": [
            "Ingest the temple meditation clip into the workspace.",
            "Extend the meditation scene by 10 seconds with deeper stillness.",
            "Generate temple ambient: distant gong reverberation, wind through pines, incense smoke crackle.",
            "Mix the temple ambient with the extended clip's baked audio.",
            "Composite the final extended meditation scene with the ambient overlay.",
        ],
    },
    {
        "user_goal": "Extend this subway-platform reunion scene by 8 seconds, layering in train brake squeals, crowd footsteps, and PA announcement ambient sounds.",
        "rationale": "Subway reunion extension + subway-platform ambient. Chain: IntakeVideo → VideoExtend → Ambience → AudioMix → Compositor → done.",
        "intents": [
            "Ingest the subway-platform reunion clip into the workspace.",
            "Extend the reunion scene by 8 seconds with the lovers' embrace lingering.",
            "Generate subway ambient: train brake squeals, crowd footsteps, PA announcements.",
            "Mix the subway ambient with the extended clip's baked audio.",
            "Composite the final extended subway scene with the ambient overlay.",
        ],
    },
    {
        "user_goal": "Extend this monsoon-rooftop-tea scene by 10 seconds, adding heavy monsoon rain on the tin roof, rolling thunder, and the kettle whistling as ambient sounds.",
        "rationale": "Monsoon-rooftop extension + rain+thunder+kettle ambient. Chain: IntakeVideo → VideoExtend → Ambience → AudioMix → Compositor → done.",
        "intents": [
            "Ingest the monsoon-rooftop-tea clip into the workspace.",
            "Extend the tea scene by 10 seconds with the rain intensifying.",
            "Generate monsoon ambient: heavy rain on tin roof, distant thunder, kettle whistling.",
            "Mix the monsoon ambient with the extended clip's baked audio.",
            "Composite the final extended tea scene with the ambient overlay.",
        ],
    },
    {
        "user_goal": "Extend this fireplace winter-night confession by 12 seconds, layering in fire crackle, snow tapping the window, and old wooden floor creak ambient sounds.",
        "rationale": "Fireplace confession extension + fire+snow+floor ambient. Chain: IntakeVideo → VideoExtend → Ambience → AudioMix → Compositor → done.",
        "intents": [
            "Ingest the fireplace confession clip into the workspace.",
            "Extend the confession by 12 seconds with the silence between lines stretching.",
            "Generate fireplace ambient: fire crackle, snow on window, wooden floor creak.",
            "Mix the fireplace ambient with the extended clip's baked audio.",
            "Composite the final extended fireplace scene with the ambient overlay.",
        ],
    },
    {
        "user_goal": "Extend this rural-village-festival reveal by 10 seconds, adding festival-crowd cheers, fireworks crackle, and distant drum-circle ambient sounds.",
        "rationale": "Festival reveal extension + festival-crowd+fireworks ambient. Chain: IntakeVideo → VideoExtend → Ambience → AudioMix → Compositor → done.",
        "intents": [
            "Ingest the festival reveal clip into the workspace.",
            "Extend the reveal by 10 seconds with the crowd's reaction unfolding.",
            "Generate festival ambient: crowd cheers, fireworks crackle, distant drum-circle thuds.",
            "Mix the festival ambient with the extended clip's baked audio.",
            "Composite the final extended festival scene with the ambient overlay.",
        ],
    },
    {
        "user_goal": "Extend this cyberpunk-alleyway escape by 12 seconds, layering in neon-buzz hum, distant siren wails, and rain on metal pipes as ambient sounds.",
        "rationale": "Cyberpunk-alleyway extension + neon+siren+rain-metal ambient. Chain: IntakeVideo → VideoExtend → Ambience → AudioMix → Compositor → done.",
        "intents": [
            "Ingest the cyberpunk-alleyway clip into the workspace.",
            "Extend the escape by 12 seconds with deeper alley pursuit.",
            "Generate cyberpunk ambient: neon-buzz hum, distant sirens, rain on metal pipes.",
            "Mix the cyberpunk ambient with the extended clip's baked audio.",
            "Composite the final extended cyberpunk scene with the ambient overlay.",
        ],
    },
    {
        "user_goal": "Extend this rainforest-river boat-ride shot by 15 seconds, adding river-current splash, monkey calls in the canopy, and distant cicada hum as ambient.",
        "rationale": "Rainforest-river boat extension + jungle-river ambient (splash, monkeys, cicadas). Chain: IntakeVideo → VideoExtend → Ambience → AudioMix → Compositor → done.",
        "intents": [
            "Ingest the rainforest-river boat-ride clip into the workspace.",
            "Extend the ride by 15 seconds with the boat drifting deeper down the river.",
            "Generate rainforest ambient: river current splash, monkey calls, cicada hum.",
            "Mix the rainforest ambient with the extended clip's baked audio.",
            "Composite the final extended boat-ride with the rainforest ambient overlay.",
        ],
    },
]
