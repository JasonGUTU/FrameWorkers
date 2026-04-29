"""Shape: vid_music_ambience — IntakeVideo → Music → Ambience → AudioMix → Compositor.

User uploaded video, wants BOTH BGM AND ambient atmosphere overlaid.

Reject: Transcription / Translation (no subtitle), StyleTransferAgent
(no restyle), VideoExtendAgent (no extend), VideoAnalysisAgent /
HighlightAgent (no trim).
"""
from __future__ import annotations

SAMPLES: list[dict] = [
    {
        "user_goal": "Please add some cinematic orchestral BGM AND forest ambient sounds to this hiking-in-forest video.",
        "rationale": (
            "User uploaded a hiking-in-forest video and asks for BOTH cinematic orchestral BGM "
            "AND forest ambient sounds. IntakeVideoAgent ingests. MusicAgent composes the "
            "orchestral cue. AmbienceAgent generates a forest ambient bed (wind through trees, "
            "distant birds). AudioMixAgent layers BGM + ambience + baked audio. CompositorAgent "
            "muxes the mixed track onto the hike video. Reject Transcription / Translation (no "
            "subtitle), StyleTransferAgent (no restyle), VideoExtendAgent (no extend), "
            "VideoAnalysisAgent / HighlightAgent (no trim)."
        ),
        "intents": [
            "Ingest the hiking-in-forest video into the workspace.",
            "Compose a cinematic orchestral BGM cue fitting the forest-hike pacing.",
            "Generate a forest ambient bed (wind, leaves, distant birds) to underlay the video.",
            "Mix the orchestral BGM, forest ambient bed, and the hike video's baked audio.",
            "Compose the hike video with the mixed music + ambience overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Add dramatic battle music AND ocean-wind ambient sounds to this pirate-ship deck video.",
        "rationale": (
            "Pirate-ship deck video + dramatic battle BGM + ocean-wind ambient. "
            "IntakeVideoAgent ingests the clip. MusicAgent composes the dramatic battle cue. "
            "AmbienceAgent generates ocean-wind (wind, sail creaks, sea). AudioMixAgent layers "
            "the BGM + ambient + baked audio. CompositorAgent muxes the result."
        ),
        "intents": [
            "Ingest the pirate-ship deck video into the workspace.",
            "Compose a dramatic battle BGM fitting the pirate-deck action.",
            "Generate an ocean-wind ambient bed (wind, sail creaks, sea sounds) for the pirate scene.",
            "Mix the battle BGM, ocean-wind ambience, and the deck video's baked audio.",
            "Compose the pirate-ship video with the mixed music + ambience overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Please add gentle piano BGM AND rainy-café ambient sounds to this coffee-shop timelapse.",
        "rationale": (
            "Coffee-shop timelapse + gentle piano BGM + rainy-café ambient. IntakeVideoAgent "
            "→ MusicAgent (gentle piano) → AmbienceAgent (rainy café: rain, muted chatter, "
            "coffee-cup clinks) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the coffee-shop timelapse video into the workspace.",
            "Compose a gentle piano BGM cue fitting the coffee-shop calm pacing.",
            "Generate a rainy-café ambient bed (rain, muted chatter, cup clinks) for the scene.",
            "Mix the piano BGM, rainy-café ambience, and the timelapse's baked audio.",
            "Compose the timelapse with the mixed music + ambience overlaid on the coffee-shop footage.",
        ],
    },
    {
        "user_goal": "Add epic orchestral BGM AND battlefield ambient (distant thunder, sword clashes) to this medieval-reenactment video.",
        "rationale": (
            "Medieval reenactment + epic orchestral BGM + battlefield ambient. "
            "IntakeVideoAgent → MusicAgent (epic orchestral) → AmbienceAgent (battlefield: "
            "thunder, sword clashes, distant cries) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the medieval-reenactment video into the workspace.",
            "Compose an epic orchestral BGM fitting the medieval-battle atmosphere.",
            "Generate a battlefield ambient bed (distant thunder, sword clashes, cries) for the reenactment.",
            "Mix the orchestral BGM, battlefield ambience, and the video's baked audio.",
            "Compose the reenactment with the mixed music + ambience overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Please add mellow bossa-nova BGM AND beach ambient sounds (waves, gulls) to this beach-walk vlog.",
        "rationale": (
            "Beach-walk vlog + mellow bossa-nova BGM + beach ambient. IntakeVideoAgent → "
            "MusicAgent (mellow bossa-nova) → AmbienceAgent (beach: waves, gulls, distant "
            "surf) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the beach-walk vlog into the workspace.",
            "Compose a mellow bossa-nova BGM fitting the beach-walk vibe.",
            "Generate a beach ambient bed (waves, gulls, distant surf) for the vlog.",
            "Mix the bossa BGM, beach ambience, and the vlog's baked audio.",
            "Compose the vlog with the mixed music + ambience overlaid on the beach footage.",
        ],
    },
    {
        "user_goal": "Add a haunting cello BGM AND cemetery-wind ambient sounds to this old-cemetery walkthrough video.",
        "rationale": (
            "Old-cemetery walkthrough + haunting cello BGM + cemetery-wind ambient. "
            "IntakeVideoAgent → MusicAgent (haunting cello) → AmbienceAgent (cemetery wind, "
            "distant crows) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the old-cemetery walkthrough video into the workspace.",
            "Compose a haunting cello BGM fitting the cemetery mood.",
            "Generate a cemetery-wind ambient bed (wind through gravestones, distant crows).",
            "Mix the cello BGM, cemetery ambience, and the walkthrough's baked audio.",
            "Compose the walkthrough with the mixed music + ambience overlaid on the cemetery footage.",
        ],
    },
    {
        "user_goal": "Please add cheerful marching-band BGM AND carnival crowd ambient sounds to this parade footage.",
        "rationale": (
            "Parade footage + cheerful marching-band BGM + carnival crowd ambient. "
            "IntakeVideoAgent → MusicAgent (cheerful marching band) → AmbienceAgent (carnival "
            "crowd: cheers, distant laughter, popping balloons) → AudioMixAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the parade footage into the workspace.",
            "Compose a cheerful marching-band BGM fitting the parade energy.",
            "Generate a carnival-crowd ambient bed (cheers, distant laughter, balloon pops).",
            "Mix the marching BGM, crowd ambience, and the parade's baked audio.",
            "Compose the parade video with the mixed music + ambience overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Add a meditative shakuhachi BGM AND temple ambient sounds (distant bells, wind chimes) to this Japanese-temple tour.",
        "rationale": (
            "Japanese-temple tour + meditative shakuhachi BGM + temple ambient. "
            "IntakeVideoAgent → MusicAgent (meditative shakuhachi) → AmbienceAgent (temple: "
            "distant bells, wind chimes, muted footsteps) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the Japanese-temple tour video into the workspace.",
            "Compose a meditative shakuhachi BGM fitting the temple's reverent mood.",
            "Generate a temple ambient bed (distant bells, wind chimes, hushed footsteps).",
            "Mix the shakuhachi BGM, temple ambience, and the tour's baked audio.",
            "Compose the tour with the mixed music + ambience overlaid on the temple footage.",
        ],
    },
    {
        "user_goal": "Please add ambient-industrial BGM AND factory-floor ambient sounds to this abandoned-factory exploration video.",
        "rationale": (
            "Abandoned-factory exploration + ambient-industrial BGM (music genre) + factory "
            "ambient. IntakeVideoAgent → MusicAgent (ambient-industrial) → AmbienceAgent "
            "(factory: distant metal clangs, echoing drips, wind through gaps) → AudioMixAgent "
            "→ CompositorAgent."
        ),
        "intents": [
            "Ingest the abandoned-factory exploration video into the workspace.",
            "Compose an ambient-industrial BGM fitting the abandoned factory atmosphere.",
            "Generate a factory ambient bed (distant metal clangs, echoing drips, wind through gaps).",
            "Mix the industrial BGM, factory ambience, and the exploration's baked audio.",
            "Compose the exploration with the mixed music + ambience overlaid on the factory footage.",
        ],
    },
    {
        "user_goal": "Add a sweeping string BGM AND mountain-wind ambient sounds to this drone alpine-peak footage.",
        "rationale": (
            "Drone alpine-peak footage + sweeping string BGM + mountain-wind ambient. "
            "IntakeVideoAgent → MusicAgent (sweeping strings) → AmbienceAgent (mountain wind, "
            "distant avalanche rumbles) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the drone alpine-peak footage into the workspace.",
            "Compose a sweeping-strings BGM fitting the alpine grandeur.",
            "Generate a mountain-wind ambient bed (high-altitude wind, distant avalanche rumbles).",
            "Mix the strings BGM, mountain ambience, and the drone's baked audio.",
            "Compose the drone clip with the mixed music + ambience overlaid on the alpine footage.",
        ],
    },
    {
        "user_goal": "Please add an uplifting gospel-choir BGM AND reverent church ambient sounds to this cathedral-interior video.",
        "rationale": (
            "Cathedral-interior video + uplifting gospel-choir BGM + reverent church ambient. "
            "IntakeVideoAgent → MusicAgent (gospel choir) → AmbienceAgent (church: distant "
            "echoes, shuffling footsteps, candle crackles) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the cathedral-interior video into the workspace.",
            "Compose an uplifting gospel-choir BGM fitting the cathedral's reverence.",
            "Generate a church ambient bed (distant echoes, shuffling steps, candle crackles).",
            "Mix the gospel BGM, church ambience, and the cathedral video's baked audio.",
            "Compose the cathedral video with the mixed music + ambience overlaid on the interior footage.",
        ],
    },
    {
        "user_goal": "Add some epic taiko-drum BGM AND thunderstorm ambient (distant thunder, heavy rain) to this stormy samurai-sparring clip.",
        "rationale": (
            "Samurai-sparring clip + epic taiko-drum BGM + thunderstorm ambient. "
            "IntakeVideoAgent → MusicAgent (epic taiko) → AmbienceAgent (thunderstorm: "
            "distant thunder, heavy rain) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the samurai-sparring clip into the workspace.",
            "Compose an epic taiko-drum BGM fitting the sparring intensity.",
            "Generate a thunderstorm ambient bed (distant thunder, heavy rain).",
            "Mix the taiko BGM, thunderstorm ambience, and the sparring clip's baked audio.",
            "Compose the sparring clip with the mixed music + ambience overlaid on the storm footage.",
        ],
    },
    {
        "user_goal": "Please add a breezy ukulele BGM AND tropical-rainforest ambient (exotic birds, insects, distant waterfall) to this jungle-trek vlog.",
        "rationale": (
            "Jungle-trek vlog + breezy ukulele BGM + tropical-rainforest ambient. "
            "IntakeVideoAgent → MusicAgent (breezy ukulele) → AmbienceAgent (rainforest: "
            "exotic birds, insects, distant waterfall) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the jungle-trek vlog into the workspace.",
            "Compose a breezy ukulele BGM fitting the jungle-trek vibe.",
            "Generate a tropical-rainforest ambient bed (exotic birds, insects, waterfall).",
            "Mix the ukulele BGM, rainforest ambience, and the trek's baked audio.",
            "Compose the vlog with the mixed music + ambience overlaid on the jungle-trek footage.",
        ],
    },
    {
        "user_goal": "Add a cozy folk-guitar BGM AND crackling-fireplace ambient to this winter-cabin-interior video.",
        "rationale": (
            "Winter-cabin-interior video + cozy folk-guitar BGM + crackling-fireplace ambient. "
            "IntakeVideoAgent → MusicAgent (cozy folk guitar) → AmbienceAgent (crackling "
            "fireplace, wind outside) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the winter-cabin-interior video into the workspace.",
            "Compose a cozy folk-guitar BGM fitting the winter-cabin warmth.",
            "Generate a crackling-fireplace ambient bed (fire crackles, wind outside).",
            "Mix the folk BGM, fireplace ambience, and the cabin video's baked audio.",
            "Compose the video with the mixed music + ambience overlaid on the cabin-interior footage.",
        ],
    },
    {
        "user_goal": "Please add dark ambient-electronic BGM AND eerie abandoned-hospital ambient (distant footsteps, flickering lights, dripping pipes) to this urbex exploration clip.",
        "rationale": (
            "Urbex abandoned-hospital exploration + dark ambient-electronic BGM + eerie "
            "hospital ambient. IntakeVideoAgent → MusicAgent (dark ambient-electronic) → "
            "AmbienceAgent (abandoned hospital: footsteps, flicker-light buzz, drips) → "
            "AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the abandoned-hospital exploration clip into the workspace.",
            "Compose a dark ambient-electronic BGM fitting the eerie abandoned hospital.",
            "Generate an eerie hospital ambient bed (distant footsteps, light buzz, dripping pipes).",
            "Mix the ambient-electronic BGM, hospital ambience, and the exploration's baked audio.",
            "Compose the exploration with the mixed music + ambience overlaid on the urbex footage.",
        ],
    },
    {
        "user_goal": "Add a mellow jazz-piano BGM AND rainy-night city-street ambient to this noir-mood walk.",
        "rationale": (
            "Noir-mood walk + mellow jazz-piano BGM + rainy-night city ambient. "
            "IntakeVideoAgent → MusicAgent (mellow jazz piano) → AmbienceAgent (rainy night "
            "city: rain, distant traffic, occasional footsteps) → AudioMixAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the noir-mood walk video into the workspace.",
            "Compose a mellow jazz-piano BGM fitting the noir-walk atmosphere.",
            "Generate a rainy-night city ambient bed (rain, distant traffic, footsteps).",
            "Mix the jazz BGM, city ambience, and the walk's baked audio.",
            "Compose the walk video with the mixed music + ambience overlaid on the noir footage.",
        ],
    },
    {
        "user_goal": "Please add a peaceful bamboo-flute BGM AND bamboo-forest ambient sounds to this bamboo-grove drone footage.",
        "rationale": (
            "Bamboo-grove drone + peaceful bamboo-flute BGM + bamboo-forest ambient. "
            "IntakeVideoAgent → MusicAgent (peaceful bamboo flute) → AmbienceAgent (bamboo "
            "forest: creaking stalks, rustling leaves, distant birds) → AudioMixAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the bamboo-grove drone footage into the workspace.",
            "Compose a peaceful bamboo-flute BGM fitting the bamboo-forest calm.",
            "Generate a bamboo-forest ambient bed (creaking stalks, rustling leaves, distant birds).",
            "Mix the flute BGM, bamboo ambience, and the drone clip's baked audio.",
            "Compose the drone clip with the mixed music + ambience overlaid on the bamboo footage.",
        ],
    },
    {
        "user_goal": "Add gentle lullaby BGM AND nighttime-bedroom ambient (soft crickets, distant owl) to this baby-sleeping video.",
        "rationale": (
            "Baby-sleeping video + gentle lullaby BGM + nighttime-bedroom ambient. "
            "IntakeVideoAgent → MusicAgent (gentle lullaby) → AmbienceAgent (crickets, "
            "distant owl, low hum) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the baby-sleeping video into the workspace.",
            "Compose a gentle lullaby BGM fitting the baby-sleep mood.",
            "Generate a nighttime-bedroom ambient bed (soft crickets, distant owl, low hum).",
            "Mix the lullaby BGM, nighttime ambience, and the baby video's baked audio.",
            "Compose the video with the mixed music + ambience overlaid on the baby-sleeping footage.",
        ],
    },
    {
        "user_goal": "Please add a dramatic film-score BGM AND howling-arctic-wind ambient to this polar-expedition documentary clip.",
        "rationale": (
            "Polar-expedition doc + dramatic film-score BGM + howling-arctic-wind ambient. "
            "IntakeVideoAgent → MusicAgent (dramatic film score) → AmbienceAgent (arctic "
            "wind: howling, distant ice cracks) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the polar-expedition documentary clip into the workspace.",
            "Compose a dramatic film-score BGM fitting the polar expedition's scale.",
            "Generate an arctic-wind ambient bed (howling wind, distant ice cracks).",
            "Mix the film-score BGM, arctic ambience, and the documentary's baked audio.",
            "Compose the documentary with the mixed music + ambience overlaid on the polar footage.",
        ],
    },
    {
        "user_goal": "Add a quirky chiptune BGM AND retro-arcade ambient (pinging coins, distant button clicks, crowd chatter) to this 1980s-arcade nostalgia video.",
        "rationale": (
            "1980s-arcade nostalgia video + quirky chiptune BGM + retro-arcade ambient. "
            "IntakeVideoAgent → MusicAgent (quirky chiptune) → AmbienceAgent (arcade: coin "
            "pings, button clicks, crowd chatter) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 1980s-arcade nostalgia video into the workspace.",
            "Compose a quirky chiptune BGM fitting the arcade nostalgia.",
            "Generate a retro-arcade ambient bed (coin pings, button clicks, crowd chatter).",
            "Mix the chiptune BGM, arcade ambience, and the nostalgia video's baked audio.",
            "Compose the video with the mixed music + ambience overlaid on the arcade footage.",
        ],
    },
    {
        "user_goal": "Please add a sweeping film BGM AND African-savanna ambient (distant lions, birds, grass in wind) to this safari-drone clip.",
        "rationale": (
            "Safari-drone clip + sweeping film BGM + African-savanna ambient. "
            "IntakeVideoAgent → MusicAgent (sweeping film score) → AmbienceAgent (savanna: "
            "distant lions, birds, grass-in-wind) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the safari-drone clip into the workspace.",
            "Compose a sweeping-film BGM fitting the safari-drone grandeur.",
            "Generate an African-savanna ambient bed (distant lions, birds, grass in wind).",
            "Mix the film BGM, savanna ambience, and the drone clip's baked audio.",
            "Compose the safari clip with the mixed music + ambience overlaid on the drone footage.",
        ],
    },
    {
        "user_goal": "Add a melancholic piano BGM AND gentle-rainy-window ambient to this rainy-day-at-home video.",
        "rationale": (
            "Rainy-day-at-home video + melancholic piano BGM + gentle-rain ambient. "
            "IntakeVideoAgent → MusicAgent (melancholic piano) → AmbienceAgent (gentle rain "
            "on window, distant thunder) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the rainy-day-at-home video into the workspace.",
            "Compose a melancholic piano BGM fitting the rainy-day mood.",
            "Generate a gentle rainy-window ambient bed (rain on glass, distant thunder).",
            "Mix the piano BGM, rainy ambience, and the home video's baked audio.",
            "Compose the video with the mixed music + ambience overlaid on the rainy-day footage.",
        ],
    },
    {
        "user_goal": "Please add an ominous brass-drone BGM AND underwater-cave ambient (dripping water, distant echoes) to this cave-diving clip.",
        "rationale": (
            "Cave-diving clip + ominous brass-drone BGM + underwater-cave ambient. "
            "IntakeVideoAgent → MusicAgent (ominous brass drone) → AmbienceAgent (underwater "
            "cave: drips, echoes, muffled bubbles) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the cave-diving clip into the workspace.",
            "Compose an ominous brass-drone BGM fitting the cave-diving tension.",
            "Generate an underwater-cave ambient bed (drips, echoes, muffled bubbles).",
            "Mix the brass BGM, cave ambience, and the diving clip's baked audio.",
            "Compose the clip with the mixed music + ambience overlaid on the cave-diving footage.",
        ],
    },
    {
        "user_goal": "Add a cheerful polka BGM AND Bavarian-biergarten ambient (crowd cheer, mug clinks, distant yodel) to this Oktoberfest clip.",
        "rationale": (
            "Oktoberfest clip + cheerful polka BGM + Bavarian-biergarten ambient. "
            "IntakeVideoAgent → MusicAgent (cheerful polka) → AmbienceAgent (biergarten: "
            "crowd cheers, mug clinks, distant yodel) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the Oktoberfest clip into the workspace.",
            "Compose a cheerful polka BGM fitting the Oktoberfest atmosphere.",
            "Generate a Bavarian-biergarten ambient bed (crowd cheers, mug clinks, distant yodel).",
            "Mix the polka BGM, biergarten ambience, and the Oktoberfest clip's baked audio.",
            "Compose the clip with the mixed music + ambience overlaid on the Oktoberfest footage.",
        ],
    },
    {
        "user_goal": "Please add a heartwarming Disney-style BGM AND springtime-meadow ambient (bees, distant birds, gentle breeze) to this family-picnic video.",
        "rationale": (
            "Family-picnic video + heartwarming Disney BGM + springtime-meadow ambient. "
            "IntakeVideoAgent → MusicAgent (heartwarming Disney orchestral) → AmbienceAgent "
            "(meadow: bees, distant birds, gentle breeze) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the family-picnic video into the workspace.",
            "Compose a heartwarming Disney-style orchestral BGM fitting the family-picnic vibe.",
            "Generate a springtime-meadow ambient bed (bees, distant birds, gentle breeze).",
            "Mix the Disney BGM, meadow ambience, and the picnic video's baked audio.",
            "Compose the video with the mixed music + ambience overlaid on the picnic footage.",
        ],
    },
    {
        "user_goal": "Add a tense thriller BGM AND dark-alley ambient (distant footsteps, dripping pipes, occasional cat) to this noir-style short clip.",
        "rationale": (
            "Noir-style short + tense thriller BGM + dark-alley ambient. IntakeVideoAgent → "
            "MusicAgent (tense thriller) → AmbienceAgent (dark alley: distant footsteps, "
            "dripping pipes, cat) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the noir-style short clip into the workspace.",
            "Compose a tense thriller BGM fitting the noir-alley tension.",
            "Generate a dark-alley ambient bed (distant footsteps, dripping pipes, cat).",
            "Mix the thriller BGM, alley ambience, and the clip's baked audio.",
            "Compose the clip with the mixed music + ambience overlaid on the noir footage.",
        ],
    },
    {
        "user_goal": "Please add a playful carnival-organ BGM AND amusement-park ambient (crowd chatter, roller-coaster whoosh, distant announcer) to this theme-park video.",
        "rationale": (
            "Theme-park video + playful carnival-organ BGM + amusement-park ambient. "
            "IntakeVideoAgent → MusicAgent (playful carnival organ) → AmbienceAgent "
            "(amusement park: crowd chatter, coaster whoosh, announcer) → AudioMixAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the theme-park video into the workspace.",
            "Compose a playful carnival-organ BGM fitting the theme-park energy.",
            "Generate an amusement-park ambient bed (crowd chatter, coaster whoosh, announcer).",
            "Mix the carnival BGM, park ambience, and the video's baked audio.",
            "Compose the video with the mixed music + ambience overlaid on the theme-park footage.",
        ],
    },
    {
        "user_goal": "Add a dramatic cinematic BGM AND spaceship-bridge ambient (computer hums, distant alarms, radio chatter) to this sci-fi-fanfilm clip.",
        "rationale": (
            "Sci-fi fanfilm clip + dramatic cinematic BGM + spaceship-bridge ambient. "
            "IntakeVideoAgent → MusicAgent (dramatic cinematic) → AmbienceAgent (spaceship "
            "bridge: computer hums, distant alarms, radio chatter) → AudioMixAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the sci-fi fanfilm clip into the workspace.",
            "Compose a dramatic cinematic BGM fitting the sci-fi-bridge scene.",
            "Generate a spaceship-bridge ambient bed (computer hums, distant alarms, radio chatter).",
            "Mix the cinematic BGM, spaceship ambience, and the clip's baked audio.",
            "Compose the fanfilm clip with the mixed music + ambience overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Please add a solemn organ BGM AND reverent-cathedral ambient (distant choir, footsteps on marble, candle flicker) to this historical-church-tour video.",
        "rationale": (
            "Historical-church-tour + solemn organ BGM + reverent-cathedral ambient. "
            "IntakeVideoAgent → MusicAgent (solemn organ) → AmbienceAgent (cathedral: "
            "distant choir, marble footsteps, candle flicker) → AudioMixAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the historical-church-tour video into the workspace.",
            "Compose a solemn organ BGM fitting the cathedral's reverence.",
            "Generate a reverent-cathedral ambient bed (distant choir, marble footsteps, candle flicker).",
            "Mix the organ BGM, cathedral ambience, and the tour's baked audio.",
            "Compose the tour with the mixed music + ambience overlaid on the church footage.",
        ],
    },
    {
        "user_goal": "Add a melancholic violin BGM AND wheat-field-at-sunset ambient (cicadas, distant wind, grass rustle) to this sunset-farm walk.",
        "rationale": (
            "Sunset-farm walk + melancholic violin BGM + wheat-field-at-sunset ambient. "
            "IntakeVideoAgent → MusicAgent (melancholic violin) → AmbienceAgent (wheat field "
            "sunset: cicadas, wind, grass rustle) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the sunset-farm walk video into the workspace.",
            "Compose a melancholic violin BGM fitting the sunset-farm mood.",
            "Generate a wheat-field-at-sunset ambient bed (cicadas, distant wind, grass rustle).",
            "Mix the violin BGM, wheat-field ambience, and the walk's baked audio.",
            "Compose the walk video with the mixed music + ambience overlaid on the sunset-farm footage.",
        ],
    },
]
