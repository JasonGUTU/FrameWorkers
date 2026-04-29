"""Shape: highlight_music — IntakeVideo → VideoAnalysis → Highlight → Music → AudioMix → Compositor.

Long video + highlight-cut + BGM overlay on the cut reel.
"""
from __future__ import annotations

SAMPLES: list[dict] = [
    {
        "user_goal": "From this 2-hour basketball game, pull the best dunks and add some energetic hip-hop BGM.",
        "rationale": (
            "Basketball game + dunks highlight + energetic hip-hop BGM. IntakeVideoAgent "
            "ingests. VideoAnalysisAgent identifies dunks. HighlightAgent extracts the dunks. "
            "MusicAgent composes the hip-hop cue. AudioMixAgent mixes BGM with the highlight "
            "audio. CompositorAgent muxes onto the reel. Reject Ambience (music only), "
            "Transcription / Translation (no subtitle), Style / Extend (no visual / length "
            "change)."
        ),
        "intents": [
            "Ingest the 2-hour basketball-game recording into the workspace.",
            "Analyze the game to locate dunk events.",
            "Extract the dunks as highlight segments.",
            "Compose an energetic hip-hop BGM cue fitting the dunk highlight reel.",
            "Mix the hip-hop BGM with the highlight reel's baked audio.",
            "Compose the dunk highlight reel with the mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Pull the best goals from this 90-minute soccer match and add some epic orchestral BGM.",
        "rationale": (
            "Soccer match + goals highlight + epic orchestral BGM. IntakeVideoAgent → "
            "VideoAnalysisAgent (goals) → HighlightAgent → MusicAgent (epic orchestral) → "
            "AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 90-minute soccer-match recording into the workspace.",
            "Analyze the match to locate goal events.",
            "Extract the goals as highlight segments.",
            "Compose an epic orchestral BGM cue fitting the goal highlight reel.",
            "Mix the orchestral BGM with the highlight reel's baked audio.",
            "Compose the goal highlight reel with the mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Please pull the funniest moments from this 2-hour standup show and add some lighthearted jazz BGM.",
        "rationale": (
            "Standup show + funniest-moments highlight + lighthearted jazz BGM. "
            "IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → MusicAgent (lighthearted "
            "jazz) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 2-hour standup-comedy show into the workspace.",
            "Analyze the show to locate the biggest-laugh punchline moments.",
            "Extract those punchline moments as highlight segments.",
            "Compose a lighthearted jazz BGM fitting the comedy highlight reel.",
            "Mix the jazz BGM with the highlight reel's baked audio.",
            "Compose the comedy highlight reel with the mixed jazz BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Extract the fight scenes from this 2-hour boxing match and add some dramatic hard-rock BGM.",
        "rationale": (
            "Boxing match + fight-scenes highlight + dramatic hard-rock BGM. IntakeVideoAgent "
            "→ VideoAnalysisAgent → HighlightAgent → MusicAgent (dramatic hard-rock) → "
            "AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 2-hour boxing-match recording into the workspace.",
            "Analyze the match to locate intense fight-exchange moments.",
            "Extract the intense exchanges as highlight segments.",
            "Compose a dramatic hard-rock BGM cue fitting the fight-scene intensity.",
            "Mix the hard-rock BGM with the fight reel's baked audio.",
            "Compose the fight highlight reel with the mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "From this 4-hour e-sports tournament, pull the clutch plays and add some epic trailer-style BGM.",
        "rationale": (
            "E-sports tournament + clutch-plays highlight + epic trailer-style BGM. "
            "IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → MusicAgent (epic "
            "trailer) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 4-hour e-sports tournament recording into the workspace.",
            "Analyze the tournament to locate clutch plays and team-fight moments.",
            "Extract those clutch moments as highlight segments.",
            "Compose an epic trailer-style BGM fitting the e-sports clutch reel.",
            "Mix the trailer BGM with the highlight reel's baked audio.",
            "Compose the e-sports highlight reel with the mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Pull the home-runs from this 2-hour baseball game and add a cheerful honky-tonk piano BGM.",
        "rationale": (
            "Baseball game + home-runs highlight + cheerful honky-tonk piano BGM. "
            "IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → MusicAgent (honky-tonk "
            "piano) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 2-hour baseball-game recording into the workspace.",
            "Analyze the game to locate home-run moments.",
            "Extract the home-runs as highlight segments.",
            "Compose a cheerful honky-tonk piano BGM fitting the baseball highlight reel.",
            "Mix the piano BGM with the highlight reel's baked audio.",
            "Compose the home-run highlight reel with the mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Please pull the winning runs from this 90-minute F1 race and add some adrenaline electronic-rock BGM.",
        "rationale": (
            "F1 race + overtake / winning-moments highlight + adrenaline electronic-rock BGM. "
            "IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → MusicAgent (adrenaline "
            "electronic-rock) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 90-minute F1 race recording into the workspace.",
            "Analyze the race to locate overtaking and winning-maneuver moments.",
            "Extract the overtakes and winning maneuvers as highlight segments.",
            "Compose an adrenaline electronic-rock BGM fitting the F1 highlight reel.",
            "Mix the electronic-rock BGM with the highlight reel's baked audio.",
            "Compose the F1 highlight reel with the mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Extract the best tricks from this 1-hour skateboarding contest and add some punk-rock BGM.",
        "rationale": (
            "Skateboarding contest + best-tricks highlight + punk-rock BGM. IntakeVideoAgent "
            "→ VideoAnalysisAgent → HighlightAgent → MusicAgent (punk rock) → AudioMixAgent "
            "→ CompositorAgent."
        ),
        "intents": [
            "Ingest the 1-hour skateboarding-contest recording into the workspace.",
            "Analyze the contest to locate the highest-scoring trick moments.",
            "Extract the best tricks as highlight segments.",
            "Compose a punk-rock BGM fitting the skate highlight reel.",
            "Mix the punk BGM with the highlight reel's baked audio.",
            "Compose the skate highlight reel with the mixed punk BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "From this 3-hour dance competition, pull the top performances and add an energetic EDM BGM.",
        "rationale": (
            "Dance competition + top-performances highlight + energetic EDM BGM. "
            "IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → MusicAgent (energetic "
            "EDM) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 3-hour dance-competition recording into the workspace.",
            "Analyze the competition to locate top-performance moments.",
            "Extract the top performances as highlight segments.",
            "Compose an energetic EDM BGM fitting the dance highlight reel.",
            "Mix the EDM BGM with the highlight reel's baked audio.",
            "Compose the dance highlight reel with the mixed EDM BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Please pull the magic-trick reveals from this 90-minute magic show and add a whimsical orchestral BGM.",
        "rationale": (
            "Magic show + reveals highlight + whimsical orchestral BGM. IntakeVideoAgent → "
            "VideoAnalysisAgent → HighlightAgent → MusicAgent (whimsical orchestral) → "
            "AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 90-minute magic-show recording into the workspace.",
            "Analyze the show to locate peak trick-reveal moments.",
            "Extract the trick-reveals as highlight segments.",
            "Compose a whimsical orchestral BGM fitting the magic highlight reel.",
            "Mix the orchestral BGM with the highlight reel's baked audio.",
            "Compose the magic highlight reel with the mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Pull the biggest saves from this 90-minute goalkeeper-compilation and add a heroic orchestral BGM.",
        "rationale": (
            "Goalkeeper compilation + biggest-saves highlight + heroic orchestral BGM. "
            "IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → MusicAgent (heroic "
            "orchestral) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 90-minute goalkeeper-compilation recording into the workspace.",
            "Analyze the compilation to locate the biggest goal-save moments.",
            "Extract the saves as highlight segments.",
            "Compose a heroic orchestral BGM fitting the goalkeeper-save highlight reel.",
            "Mix the orchestral BGM with the highlight reel's baked audio.",
            "Compose the save highlight reel with the mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Extract the best surfing tricks from this 2-hour surf competition and add a laid-back reggae BGM.",
        "rationale": (
            "Surf competition + best-tricks highlight + laid-back reggae BGM. IntakeVideoAgent "
            "→ VideoAnalysisAgent → HighlightAgent → MusicAgent (laid-back reggae) → "
            "AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 2-hour surf-competition recording into the workspace.",
            "Analyze the competition to locate the best surf-trick moments.",
            "Extract the best surfing tricks as highlight segments.",
            "Compose a laid-back reggae BGM fitting the surf highlight reel.",
            "Mix the reggae BGM with the highlight reel's baked audio.",
            "Compose the surf highlight reel with the mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "From this 2-hour MMA event, pull the knockouts and add some intense metal BGM.",
        "rationale": (
            "MMA event + knockouts highlight + intense metal BGM. IntakeVideoAgent → "
            "VideoAnalysisAgent → HighlightAgent → MusicAgent (intense metal) → AudioMixAgent "
            "→ CompositorAgent."
        ),
        "intents": [
            "Ingest the 2-hour MMA event recording into the workspace.",
            "Analyze the event to locate knockout moments.",
            "Extract the knockouts as highlight segments.",
            "Compose an intense metal BGM fitting the MMA knockout highlight reel.",
            "Mix the metal BGM with the highlight reel's baked audio.",
            "Compose the MMA knockout highlight reel with the mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Please pull the best ski-jumps from this 2-hour ski-jumping competition and add some epic cinematic BGM.",
        "rationale": (
            "Ski-jumping competition + best-jumps highlight + epic cinematic BGM. "
            "IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → MusicAgent (epic "
            "cinematic) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 2-hour ski-jumping competition recording into the workspace.",
            "Analyze the competition to locate the best ski-jump moments.",
            "Extract the best ski-jumps as highlight segments.",
            "Compose an epic cinematic BGM fitting the ski-jump highlight reel.",
            "Mix the cinematic BGM with the highlight reel's baked audio.",
            "Compose the ski-jump highlight reel with the mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "From this 3-hour rally-racing broadcast, pull the overtakes and crashes, and add a driving electronic BGM.",
        "rationale": (
            "Rally racing broadcast + overtakes-and-crashes highlight + driving electronic BGM. "
            "IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → MusicAgent (driving "
            "electronic) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 3-hour rally-racing broadcast into the workspace.",
            "Analyze the broadcast to locate overtake and crash events.",
            "Extract the overtakes and crashes as highlight segments.",
            "Compose a driving electronic BGM fitting the rally highlight reel.",
            "Mix the electronic BGM with the highlight reel's baked audio.",
            "Compose the rally highlight reel with the mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Pull the best acrobatic moments from this 2-hour circus show and add a whimsical carousel-organ BGM.",
        "rationale": (
            "Circus show + acrobatic highlight + whimsical carousel-organ BGM. "
            "IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → MusicAgent (whimsical "
            "carousel organ) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 2-hour circus-show recording into the workspace.",
            "Analyze the show to locate signature acrobatic moments.",
            "Extract the best acrobatic moments as highlight segments.",
            "Compose a whimsical carousel-organ BGM fitting the circus highlight reel.",
            "Mix the carousel BGM with the highlight reel's baked audio.",
            "Compose the circus highlight reel with the mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "From this 3-hour chess tournament, pull the decisive combination moments and add a tension-building electronic BGM.",
        "rationale": (
            "Chess tournament + decisive-combinations highlight + tension-building electronic "
            "BGM. IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → MusicAgent "
            "(tension-building electronic) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 3-hour chess-tournament stream into the workspace.",
            "Analyze the tournament to locate decisive tactical-combination moments.",
            "Extract the decisive-combination moments as highlight segments.",
            "Compose a tension-building electronic BGM fitting the chess highlight reel.",
            "Mix the electronic BGM with the highlight reel's baked audio.",
            "Compose the chess highlight reel with the mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Please pull the spike moments from this 90-minute volleyball tournament and add an energetic techno BGM.",
        "rationale": (
            "Volleyball tournament + spikes highlight + energetic techno BGM. "
            "IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → MusicAgent (energetic "
            "techno) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 90-minute volleyball-tournament recording into the workspace.",
            "Analyze the tournament to locate the best volleyball-spike events.",
            "Extract the spikes as highlight segments.",
            "Compose an energetic techno BGM fitting the volleyball-spike highlight reel.",
            "Mix the techno BGM with the highlight reel's baked audio.",
            "Compose the volleyball highlight reel with the mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Extract the best-trick moments from this 2-hour snowboarding event and add an energetic indie-rock BGM.",
        "rationale": (
            "Snowboarding event + best-tricks highlight + energetic indie-rock BGM. "
            "IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → MusicAgent (energetic "
            "indie-rock) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 2-hour snowboarding-event recording into the workspace.",
            "Analyze the event to locate the best snowboard-trick moments.",
            "Extract the best snowboard tricks as highlight segments.",
            "Compose an energetic indie-rock BGM fitting the snowboard highlight reel.",
            "Mix the indie-rock BGM with the highlight reel's baked audio.",
            "Compose the snowboard highlight reel with the mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "From this 2-hour Formula E electric-racing broadcast, pull the overtakes and add a futuristic synthwave BGM.",
        "rationale": (
            "Formula E race + overtakes highlight + futuristic synthwave BGM. IntakeVideoAgent "
            "→ VideoAnalysisAgent → HighlightAgent → MusicAgent (futuristic synthwave) → "
            "AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 2-hour Formula E broadcast into the workspace.",
            "Analyze the broadcast to locate overtake events.",
            "Extract the overtakes as highlight segments.",
            "Compose a futuristic synthwave BGM fitting the Formula E highlight reel.",
            "Mix the synthwave BGM with the highlight reel's baked audio.",
            "Compose the Formula E highlight reel with the mixed BGM overlaid on the cuts.",
        ],
    },
]
