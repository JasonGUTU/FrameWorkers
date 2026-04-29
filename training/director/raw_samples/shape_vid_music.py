"""Shape: vid_music — IntakeVideo → Music → AudioMix → Compositor.

User uploaded a video and asks for background music overlaid on it —
no ambient sound, no subtitle, no style change, no highlight extraction.

Reject biases:
  - AmbienceAgent (user asked for music, not ambient atmosphere)
  - TranscriptionAgent / TranslationAgent (no subtitle)
  - VideoAnalysisAgent / HighlightAgent (no trimming)
  - StyleTransferAgent / VideoExtendAgent (no visual / length change)
"""
from __future__ import annotations

SAMPLES: list[dict] = [
    {
        "user_goal": "Please add some cinematic orchestral background music to this short travel montage I made.",
        "rationale": (
            "User uploaded a travel montage and asks for cinematic orchestral background music "
            "on top of it. IntakeVideoAgent ingests the montage. MusicAgent composes the "
            "orchestral cue. AudioMixAgent mixes the new music track with the montage's baked "
            "audio. CompositorAgent muxes the mixed audio back onto the video. Reject "
            "AmbienceAgent (user asked for music, not ambient), TranscriptionAgent / "
            "TranslationAgent (no subtitles), VideoAnalysisAgent / HighlightAgent (no "
            "trimming), StyleTransferAgent / VideoExtendAgent (no visual or length change)."
        ),
        "intents": [
            "Ingest the uploaded travel-montage video into the workspace as the source clip.",
            "Compose a cinematic orchestral BGM cue fitting the travel-montage pacing.",
            "Mix the new orchestral BGM with the montage's original baked audio.",
            "Compose the final montage with the mixed BGM overlaid on the travel footage.",
        ],
    },
    {
        "user_goal": "Add some upbeat indie-pop background music to this birthday-party video.",
        "rationale": (
            "Birthday-party video + request for upbeat indie-pop BGM. IntakeVideoAgent loads "
            "the party video. MusicAgent composes the indie-pop cue. AudioMixAgent mixes it "
            "with the party's original audio. CompositorAgent muxes the mixed audio back. No "
            "ambient, subtitle, trim, or style change requested."
        ),
        "intents": [
            "Ingest the birthday-party video into the workspace.",
            "Compose an upbeat indie-pop BGM cue fitting the party's energy.",
            "Mix the indie-pop BGM with the party video's original audio track.",
            "Compose the party video with the mixed music overlaid onto the footage.",
        ],
    },
    {
        "user_goal": "Please put some lo-fi hip-hop beats under this coffee-shop timelapse video.",
        "rationale": (
            "Coffee-shop timelapse + request for lo-fi hip-hop BGM. IntakeVideoAgent ingests "
            "the timelapse. MusicAgent composes a lo-fi hip-hop loop. AudioMixAgent blends it "
            "with any existing audio. CompositorAgent muxes the final audio. No ambient, "
            "subtitle, trimming, or restyle asked."
        ),
        "intents": [
            "Ingest the coffee-shop timelapse video into the workspace.",
            "Compose a lo-fi hip-hop BGM loop fitting the chill coffee-shop vibe.",
            "Mix the lo-fi BGM with the timelapse's original audio track.",
            "Compose the timelapse with the mixed lo-fi BGM overlaid on the coffee-shop footage.",
        ],
    },
    {
        "user_goal": "Add a gentle jazz piano background track to this slow-motion cooking-demo clip.",
        "rationale": (
            "Slow-mo cooking demo + request for gentle jazz-piano BGM. IntakeVideoAgent ingests "
            "the demo clip. MusicAgent composes the jazz-piano cue. AudioMixAgent mixes the "
            "jazz with the cooking demo's baked audio. CompositorAgent muxes the result."
        ),
        "intents": [
            "Ingest the slow-motion cooking-demo clip into the workspace.",
            "Compose a gentle jazz-piano BGM that matches the slow-motion pacing.",
            "Mix the jazz-piano BGM with the cooking demo's baked audio.",
            "Compose the cooking demo with the mixed jazz BGM overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Please put some dramatic film-score-style music under this slow-motion skate-trick clip.",
        "rationale": (
            "Slow-mo skate trick + request for dramatic film-score BGM. IntakeVideoAgent "
            "ingests the trick clip. MusicAgent composes a dramatic cinematic cue matching "
            "the slow-motion climax. AudioMixAgent mixes it with the clip's audio. "
            "CompositorAgent muxes the audio track."
        ),
        "intents": [
            "Ingest the slow-motion skate-trick clip into the workspace.",
            "Compose a dramatic film-score BGM with a climax that matches the slow-motion trick.",
            "Mix the dramatic BGM with the skate clip's baked audio.",
            "Compose the skate clip with the mixed dramatic BGM overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Add some energetic EDM drop music to this gym-workout highlights clip.",
        "rationale": (
            "Gym-workout highlights + request for energetic EDM drop BGM. IntakeVideoAgent "
            "loads the clip. MusicAgent composes an EDM cue with a drop aligned to the "
            "workout intensity. AudioMixAgent mixes the EDM with the clip's original audio. "
            "CompositorAgent muxes the final audio track."
        ),
        "intents": [
            "Ingest the gym-workout highlights clip into the workspace.",
            "Compose an energetic EDM BGM with a drop that matches the workout peak.",
            "Mix the EDM BGM with the workout clip's original audio.",
            "Compose the workout clip with the mixed EDM BGM overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Please add gentle acoustic guitar BGM to this couple-engagement-shoot video.",
        "rationale": (
            "Couple engagement-shoot video + request for gentle acoustic-guitar BGM. "
            "IntakeVideoAgent ingests the shoot. MusicAgent composes the acoustic-guitar cue. "
            "AudioMixAgent mixes the acoustic BGM with the shoot's ambient audio. "
            "CompositorAgent muxes the result onto the video."
        ),
        "intents": [
            "Ingest the couple engagement-shoot video into the workspace.",
            "Compose a gentle acoustic-guitar BGM fitting the romantic engagement mood.",
            "Mix the acoustic-guitar BGM with the shoot's ambient audio.",
            "Compose the engagement shoot with the mixed acoustic BGM overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Add a melancholic piano ballad as background music to this rainy-window timelapse.",
        "rationale": (
            "Rainy-window timelapse + request for melancholic piano-ballad BGM. "
            "IntakeVideoAgent ingests the timelapse. MusicAgent composes the piano ballad. "
            "AudioMixAgent mixes the BGM with the rainy-window audio. CompositorAgent muxes "
            "the final audio."
        ),
        "intents": [
            "Ingest the rainy-window timelapse video into the workspace.",
            "Compose a melancholic piano-ballad BGM fitting the rainy-window mood.",
            "Mix the piano ballad with the timelapse's ambient rainy audio.",
            "Compose the timelapse with the mixed piano BGM overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Put some uplifting gospel-choir music under this church-community-service video.",
        "rationale": (
            "Church-community-service footage + request for uplifting gospel-choir BGM. "
            "IntakeVideoAgent loads the video. MusicAgent composes a gospel-choir cue with "
            "uplifting harmonies. AudioMixAgent blends the BGM with the service's ambient "
            "audio. CompositorAgent muxes the result."
        ),
        "intents": [
            "Ingest the church-community-service video into the workspace.",
            "Compose an uplifting gospel-choir BGM fitting the community-service tone.",
            "Mix the gospel BGM with the service's ambient audio.",
            "Compose the service video with the mixed gospel BGM overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Please add some retro-wave synth music to this cruising-at-night video.",
        "rationale": (
            "Cruising-at-night video + request for retro-wave synth BGM. IntakeVideoAgent "
            "ingests the clip. MusicAgent composes a retro-wave synth cue. AudioMixAgent mixes "
            "it with the cruising footage's audio. CompositorAgent muxes the final audio."
        ),
        "intents": [
            "Ingest the cruising-at-night video into the workspace.",
            "Compose a retro-wave synth BGM fitting the night-cruise aesthetic.",
            "Mix the retro-wave BGM with the cruising video's ambient audio.",
            "Compose the cruising video with the mixed synth BGM overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Add some traditional Chinese guzheng background music to this tea-ceremony recording.",
        "rationale": (
            "Tea-ceremony recording + request for traditional guzheng BGM. IntakeVideoAgent "
            "ingests the ceremony. MusicAgent composes a traditional guzheng cue. "
            "AudioMixAgent mixes it with the ceremony's ambient audio. CompositorAgent muxes "
            "the audio."
        ),
        "intents": [
            "Ingest the tea-ceremony recording into the workspace.",
            "Compose a traditional Chinese guzheng BGM fitting the tea-ceremony atmosphere.",
            "Mix the guzheng BGM with the tea-ceremony ambient audio.",
            "Compose the ceremony with the mixed guzheng BGM overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Please put some soft ambient electronica under this night-city-skyline timelapse.",
        "rationale": (
            "Night-city-skyline timelapse + request for soft ambient-electronica BGM. "
            "IntakeVideoAgent ingests the timelapse. MusicAgent composes the ambient-electronica "
            "cue. AudioMixAgent mixes it with the timelapse's audio. CompositorAgent muxes "
            "the final audio. Note: user said 'ambient electronica' as a music genre, not "
            "ambient environmental sound — so this stays MusicAgent, not AmbienceAgent."
        ),
        "intents": [
            "Ingest the night-city-skyline timelapse into the workspace.",
            "Compose a soft ambient-electronica BGM fitting the night-cityscape mood.",
            "Mix the ambient-electronica BGM with the timelapse's audio.",
            "Compose the timelapse with the mixed electronica BGM overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Add a dramatic Hans-Zimmer-style cinematic score to this drone mountain-fly-over clip.",
        "rationale": (
            "Drone mountain fly-over + request for Hans-Zimmer-style dramatic cinematic score. "
            "IntakeVideoAgent ingests the clip. MusicAgent composes the cinematic score with "
            "Zimmer-style brass and percussion swells. AudioMixAgent mixes it with the drone "
            "audio. CompositorAgent muxes the final audio."
        ),
        "intents": [
            "Ingest the drone mountain fly-over clip into the workspace.",
            "Compose a Hans-Zimmer-style dramatic cinematic BGM with brass swells and percussion.",
            "Mix the cinematic BGM with the drone clip's wind / baked audio.",
            "Compose the drone clip with the mixed cinematic BGM overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Please add calm spa-music-style BGM to this yoga-session recording.",
        "rationale": (
            "Yoga-session recording + request for calm spa-style BGM. IntakeVideoAgent ingests "
            "the session. MusicAgent composes the calm spa-style cue. AudioMixAgent mixes it "
            "with the yoga ambient audio. CompositorAgent muxes the result."
        ),
        "intents": [
            "Ingest the yoga-session recording into the workspace.",
            "Compose a calm spa-style BGM fitting the yoga-session pace.",
            "Mix the spa BGM with the yoga session's ambient audio.",
            "Compose the yoga session with the mixed spa BGM overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Put some Celtic-fiddle folk music under this Irish-countryside hiking vlog.",
        "rationale": (
            "Irish-countryside hiking vlog + request for Celtic-fiddle folk BGM. "
            "IntakeVideoAgent ingests the vlog. MusicAgent composes a Celtic-fiddle folk cue. "
            "AudioMixAgent mixes it with the vlog's ambient audio. CompositorAgent muxes the "
            "final audio."
        ),
        "intents": [
            "Ingest the Irish-countryside hiking vlog into the workspace.",
            "Compose a Celtic-fiddle folk BGM fitting the Irish-countryside vibe.",
            "Mix the Celtic folk BGM with the hiking vlog's ambient audio.",
            "Compose the vlog with the mixed Celtic BGM overlaid on the hiking footage.",
        ],
    },
    {
        "user_goal": "Please add mellow bossa-nova music as background to this beach-bar-at-sunset clip.",
        "rationale": (
            "Beach-bar-at-sunset clip + request for mellow bossa-nova BGM. IntakeVideoAgent "
            "ingests the clip. MusicAgent composes a mellow bossa-nova cue. AudioMixAgent mixes "
            "it with the beach-bar ambient audio. CompositorAgent muxes the result."
        ),
        "intents": [
            "Ingest the beach-bar-at-sunset clip into the workspace.",
            "Compose a mellow bossa-nova BGM fitting the sunset-bar atmosphere.",
            "Mix the bossa-nova BGM with the beach-bar ambient audio.",
            "Compose the beach-bar clip with the mixed bossa BGM overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Add some reggae dub BGM to this Caribbean-beach vlog footage.",
        "rationale": (
            "Caribbean-beach vlog + request for reggae-dub BGM. IntakeVideoAgent ingests the "
            "vlog. MusicAgent composes a reggae-dub cue. AudioMixAgent mixes it with the vlog "
            "audio. CompositorAgent muxes the final audio."
        ),
        "intents": [
            "Ingest the Caribbean-beach vlog into the workspace.",
            "Compose a reggae-dub BGM fitting the Caribbean-beach vibe.",
            "Mix the reggae BGM with the vlog's ambient audio.",
            "Compose the vlog with the mixed reggae BGM overlaid on the beach footage.",
        ],
    },
    {
        "user_goal": "Please put some Baroque-style harpsichord music under this antique-book-store walking-tour clip.",
        "rationale": (
            "Antique-book-store walking-tour + request for Baroque-style harpsichord BGM. "
            "IntakeVideoAgent ingests the tour. MusicAgent composes a Baroque harpsichord cue. "
            "AudioMixAgent mixes it with the tour's ambient audio. CompositorAgent muxes the "
            "result."
        ),
        "intents": [
            "Ingest the antique-book-store walking-tour clip into the workspace.",
            "Compose a Baroque-style harpsichord BGM fitting the antique-book-store atmosphere.",
            "Mix the harpsichord BGM with the walking-tour ambient audio.",
            "Compose the tour clip with the mixed Baroque BGM overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Add some dark brooding ambient-industrial music as background to this urban-decay exploration video.",
        "rationale": (
            "Urban-decay exploration video + request for dark ambient-industrial BGM. Note: "
            "ambient-industrial here is a music genre (MusicAgent), not environmental sound. "
            "IntakeVideoAgent ingests the video. MusicAgent composes the dark ambient-industrial "
            "cue. AudioMixAgent mixes it with the exploration video's audio. CompositorAgent "
            "muxes the final track."
        ),
        "intents": [
            "Ingest the urban-decay exploration video into the workspace.",
            "Compose a dark ambient-industrial BGM matching the eerie urban-decay atmosphere.",
            "Mix the ambient-industrial BGM with the exploration video's baked audio.",
            "Compose the exploration video with the mixed industrial BGM overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Please add some gentle koto-and-shakuhachi Japanese traditional music to this Kyoto-temple tour video.",
        "rationale": (
            "Kyoto-temple tour + request for gentle koto-and-shakuhachi traditional BGM. "
            "IntakeVideoAgent loads the tour. MusicAgent composes the traditional koto-and-"
            "shakuhachi cue. AudioMixAgent mixes it with the temple tour's ambient audio. "
            "CompositorAgent muxes the result."
        ),
        "intents": [
            "Ingest the Kyoto-temple tour video into the workspace.",
            "Compose a gentle traditional-Japanese koto-and-shakuhachi BGM fitting the temple tour.",
            "Mix the traditional BGM with the tour's ambient audio.",
            "Compose the tour video with the mixed traditional BGM overlaid on the temple footage.",
        ],
    },
    {
        "user_goal": "Add some grand pipe-organ-style music to this cathedral-walkthrough video.",
        "rationale": (
            "Cathedral walkthrough + request for grand pipe-organ BGM. IntakeVideoAgent ingests "
            "the walkthrough. MusicAgent composes a grand pipe-organ cue. AudioMixAgent mixes "
            "it with the walkthrough's baked ambient audio. CompositorAgent muxes the result."
        ),
        "intents": [
            "Ingest the cathedral-walkthrough video into the workspace.",
            "Compose a grand pipe-organ BGM fitting the cathedral's majestic interior.",
            "Mix the pipe-organ BGM with the walkthrough's ambient audio.",
            "Compose the walkthrough with the mixed organ BGM overlaid on the cathedral footage.",
        ],
    },
    {
        "user_goal": "Please put some epic taiko-drum battle music under this martial-arts-demonstration video.",
        "rationale": (
            "Martial-arts demonstration + request for epic taiko-drum battle BGM. "
            "IntakeVideoAgent ingests the demo. MusicAgent composes the taiko-drum cue. "
            "AudioMixAgent mixes it with the demo's baked audio. CompositorAgent muxes the "
            "result."
        ),
        "intents": [
            "Ingest the martial-arts-demonstration video into the workspace.",
            "Compose an epic taiko-drum battle BGM fitting the demonstration's intensity.",
            "Mix the taiko BGM with the demo's baked audio.",
            "Compose the demo video with the mixed taiko BGM overlaid on the martial-arts footage.",
        ],
    },
    {
        "user_goal": "Add a cheerful ukulele-and-whistle BGM to this puppy-park-playtime video.",
        "rationale": (
            "Puppy-park-playtime video + request for cheerful ukulele-and-whistle BGM. "
            "IntakeVideoAgent ingests the video. MusicAgent composes the cheerful ukulele cue. "
            "AudioMixAgent mixes it with the puppy-park baked audio. CompositorAgent muxes the "
            "result."
        ),
        "intents": [
            "Ingest the puppy-park-playtime video into the workspace.",
            "Compose a cheerful ukulele-and-whistle BGM fitting the puppy playtime vibe.",
            "Mix the ukulele BGM with the puppy-park baked audio.",
            "Compose the video with the mixed cheerful BGM overlaid on the puppy-park footage.",
        ],
    },
    {
        "user_goal": "Please add Spanish-flamenco guitar music as background to this matador-practice clip.",
        "rationale": (
            "Matador-practice clip + request for Spanish-flamenco guitar BGM. IntakeVideoAgent "
            "ingests the practice clip. MusicAgent composes a flamenco guitar cue. "
            "AudioMixAgent mixes it with the clip's baked audio. CompositorAgent muxes the "
            "result."
        ),
        "intents": [
            "Ingest the matador-practice clip into the workspace.",
            "Compose a Spanish-flamenco guitar BGM fitting the matador-practice rhythm.",
            "Mix the flamenco BGM with the practice clip's baked audio.",
            "Compose the practice clip with the mixed flamenco BGM overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Add some Appalachian banjo folk music to this Smoky-Mountains fall-foliage timelapse.",
        "rationale": (
            "Smoky-Mountains fall-foliage timelapse + request for Appalachian banjo folk BGM. "
            "IntakeVideoAgent loads the timelapse. MusicAgent composes an Appalachian banjo "
            "folk cue. AudioMixAgent mixes it with the timelapse's ambient audio. "
            "CompositorAgent muxes the final audio."
        ),
        "intents": [
            "Ingest the Smoky-Mountains fall-foliage timelapse into the workspace.",
            "Compose an Appalachian banjo folk BGM fitting the mountain-foliage vibe.",
            "Mix the banjo folk BGM with the timelapse's ambient audio.",
            "Compose the timelapse with the mixed banjo BGM overlaid on the foliage footage.",
        ],
    },
    {
        "user_goal": "Please put some haunting cello solo music under this abandoned-mansion exploration video.",
        "rationale": (
            "Abandoned-mansion exploration + request for haunting cello solo BGM. "
            "IntakeVideoAgent ingests the video. MusicAgent composes the haunting cello solo. "
            "AudioMixAgent mixes it with the exploration video's baked audio. CompositorAgent "
            "muxes the result."
        ),
        "intents": [
            "Ingest the abandoned-mansion exploration video into the workspace.",
            "Compose a haunting cello-solo BGM fitting the abandoned-mansion atmosphere.",
            "Mix the cello BGM with the exploration video's baked audio.",
            "Compose the video with the mixed cello BGM overlaid on the mansion footage.",
        ],
    },
    {
        "user_goal": "Add a breezy steel-drum Caribbean-sound BGM to this beach-volleyball tournament clip.",
        "rationale": (
            "Beach-volleyball tournament + request for breezy steel-drum Caribbean BGM. "
            "IntakeVideoAgent ingests the clip. MusicAgent composes the Caribbean steel-drum "
            "cue. AudioMixAgent mixes it with the tournament's baked audio. CompositorAgent "
            "muxes the result."
        ),
        "intents": [
            "Ingest the beach-volleyball tournament clip into the workspace.",
            "Compose a breezy steel-drum Caribbean BGM fitting the beach-volleyball vibe.",
            "Mix the steel-drum BGM with the tournament clip's baked audio.",
            "Compose the tournament clip with the mixed Caribbean BGM overlaid on the footage.",
        ],
    },
    {
        "user_goal": "Please add some heartwarming Disney-style orchestral music to this family-reunion video.",
        "rationale": (
            "Family-reunion video + request for heartwarming Disney-style orchestral BGM. "
            "IntakeVideoAgent ingests the reunion video. MusicAgent composes the Disney-style "
            "orchestral cue. AudioMixAgent mixes it with the reunion audio. CompositorAgent "
            "muxes the result."
        ),
        "intents": [
            "Ingest the family-reunion video into the workspace.",
            "Compose a heartwarming Disney-style orchestral BGM fitting the family-reunion mood.",
            "Mix the orchestral BGM with the reunion video's baked audio.",
            "Compose the reunion video with the mixed Disney-style BGM overlaid on the family footage.",
        ],
    },
    {
        "user_goal": "Add a funky 1970s-disco BGM to this rollerskating-rink video.",
        "rationale": (
            "Rollerskating-rink video + request for funky 1970s-disco BGM. IntakeVideoAgent "
            "ingests the rink video. MusicAgent composes a funky 1970s-disco cue. AudioMixAgent "
            "mixes it with the rink's baked audio. CompositorAgent muxes the result."
        ),
        "intents": [
            "Ingest the rollerskating-rink video into the workspace.",
            "Compose a funky 1970s-disco BGM fitting the rollerskating-rink atmosphere.",
            "Mix the disco BGM with the rink video's baked audio.",
            "Compose the rink video with the mixed disco BGM overlaid on the skating footage.",
        ],
    },
    {
        "user_goal": "Please put some dramatic Middle-Eastern oud-and-ney music under this desert-caravan drone footage.",
        "rationale": (
            "Desert-caravan drone footage + request for dramatic Middle-Eastern oud-and-ney BGM. "
            "IntakeVideoAgent ingests the drone footage. MusicAgent composes the oud-and-ney "
            "dramatic cue. AudioMixAgent mixes it with the drone clip's audio. CompositorAgent "
            "muxes the result."
        ),
        "intents": [
            "Ingest the desert-caravan drone footage into the workspace.",
            "Compose a dramatic Middle-Eastern oud-and-ney BGM fitting the desert-caravan scale.",
            "Mix the Middle-Eastern BGM with the drone clip's baked audio.",
            "Compose the drone footage with the mixed oud-and-ney BGM overlaid on the caravan scene.",
        ],
    },
]
