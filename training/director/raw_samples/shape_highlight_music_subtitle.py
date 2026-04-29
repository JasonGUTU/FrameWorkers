"""Shape: highlight_music_subtitle —
    IntakeVideo → VideoAnalysis → Highlight → Music → Transcription → AudioMix → Compositor.

Long video → highlight cut → BGM overlay + monolingual subtitle burn-in.
NOTE: eval GT has 8 slots with 3× {Music|Transcription} — only 2 distinct
agents available in that set.  Training canonical is the logical 7-step.
"""
from __future__ import annotations

SAMPLES: list[dict] = [
    {
        "user_goal": "Analyze this mini-drama, cut the climactic twist moments, add English subtitles, and add a tense-suspenseful BGM.",
        "rationale": (
            "User uploaded mini-drama, asks for climactic-twist highlights + English subtitles "
            "+ tense BGM. IntakeVideoAgent → VideoAnalysisAgent (twist moments) → "
            "HighlightAgent (cuts twists) → MusicAgent (tense suspense) → TranscriptionAgent "
            "(English) → AudioMixAgent (BGM + dialogue) → CompositorAgent (SRT + audio)."
        ),
        "intents": [
            "Ingest the mini-drama recording into the workspace.",
            "Analyze the drama to locate climactic twist moments.",
            "Extract the twist moments as highlight segments.",
            "Compose a tense-suspenseful BGM fitting the twist highlight reel.",
            "Transcribe the English dialogue on the twist segments into SRT.",
            "Mix the suspenseful BGM with the highlight reel's baked audio.",
            "Compose the highlight reel with English captions and mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "From this 90-minute soccer match, pull the goals, add English subtitles from the announcer, and add an anthemic rock BGM.",
        "rationale": (
            "Soccer match + goals highlight + English announcer subs + anthemic rock BGM. "
            "IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → MusicAgent (anthemic "
            "rock) → TranscriptionAgent (English) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 90-minute soccer-match recording into the workspace.",
            "Analyze the match to locate goal events.",
            "Extract the goals as highlight segments.",
            "Compose an anthemic rock BGM fitting the goal highlight reel.",
            "Transcribe the English announcer commentary on the goal segments into SRT.",
            "Mix the rock BGM with the highlight reel's baked audio.",
            "Compose the goal highlight reel with English captions and mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Pull the funniest moments from this 2-hour podcast, add English captions, and add a playful jazz BGM.",
        "rationale": (
            "Video-podcast + funniest moments + English captions + playful jazz BGM. "
            "IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → MusicAgent (playful "
            "jazz) → TranscriptionAgent (English) → AudioMixAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 2-hour video-podcast recording into the workspace.",
            "Analyze the podcast to locate the funniest / biggest-laugh moments.",
            "Extract those funny moments as highlight segments.",
            "Compose a playful jazz BGM fitting the comedy highlight reel.",
            "Transcribe the English podcast dialogue on the segments into SRT.",
            "Mix the jazz BGM with the highlight reel's baked audio.",
            "Compose the reel with English captions and mixed jazz BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "From this 2-hour basketball game, pull the best dunks, add English captions, and add an energetic hip-hop BGM.",
        "rationale": (
            "Basketball game + dunks highlight + English captions + energetic hip-hop BGM."
        ),
        "intents": [
            "Ingest the 2-hour basketball-game recording into the workspace.",
            "Analyze the game to locate dunk events.",
            "Extract the dunks as highlight segments.",
            "Compose an energetic hip-hop BGM fitting the dunk highlight reel.",
            "Transcribe the English broadcast commentary on the dunk segments into SRT.",
            "Mix the hip-hop BGM with the highlight reel's baked audio.",
            "Compose the reel with English captions and mixed hip-hop BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Please pull the quotable one-liners from this 90-minute TED-talk marathon, add English captions, and add a subtle inspirational BGM.",
        "rationale": (
            "TED-talk marathon + one-liners + English captions + subtle inspirational BGM."
        ),
        "intents": [
            "Ingest the 90-minute TED-talk marathon recording into the workspace.",
            "Analyze the marathon to locate the most-quotable one-liner moments.",
            "Extract the one-liners as highlight segments.",
            "Compose a subtle inspirational BGM fitting the TED-talk reel.",
            "Transcribe the English one-liners on the segments into SRT.",
            "Mix the inspirational BGM with the highlight reel's baked audio.",
            "Compose the reel with English captions and mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Extract the clutch plays from this 3-hour e-sports tournament, add English captions from the casters, and add an epic trailer-style BGM.",
        "rationale": (
            "E-sports tournament + clutch plays + English caster captions + epic trailer BGM."
        ),
        "intents": [
            "Ingest the 3-hour e-sports tournament recording into the workspace.",
            "Analyze the tournament to locate clutch plays and team-fight moments.",
            "Extract those clutch moments as highlight segments.",
            "Compose an epic trailer-style BGM fitting the e-sports reel.",
            "Transcribe the English caster commentary on the segments into SRT.",
            "Mix the trailer BGM with the highlight reel's baked audio.",
            "Compose the reel with English captions and mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "From this 2-hour hockey game, pull the goals and fights, add English captions, and add a hard-rock BGM.",
        "rationale": (
            "Hockey game + goals/fights + English captions + hard-rock BGM."
        ),
        "intents": [
            "Ingest the 2-hour hockey-game recording into the workspace.",
            "Analyze the hockey game to locate goals and fight events.",
            "Extract the goals and fights as highlight segments.",
            "Compose a hard-rock BGM fitting the hockey highlight reel.",
            "Transcribe the English broadcast commentary on the segments into SRT.",
            "Mix the rock BGM with the highlight reel's baked audio.",
            "Compose the reel with English captions and mixed rock BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Pull the emotional moments from this 1-hour wedding-ceremony recording, add English captions, and add a soft string-quartet BGM.",
        "rationale": (
            "Wedding ceremony + emotional moments + English captions + soft string-quartet BGM."
        ),
        "intents": [
            "Ingest the hour-long wedding-ceremony recording into the workspace.",
            "Analyze the ceremony to locate vows, ring exchange, and first-kiss moments.",
            "Extract those emotional moments as highlight segments.",
            "Compose a soft string-quartet BGM fitting the wedding mood.",
            "Transcribe the English vows on the segments into SRT.",
            "Mix the quartet BGM with the highlight reel's baked audio.",
            "Compose the reel with English captions and mixed quartet BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "From this 2-hour dance competition, pull the top performances, add English captions, and add an energetic EDM BGM.",
        "rationale": (
            "Dance competition + top performances + English captions + energetic EDM BGM."
        ),
        "intents": [
            "Ingest the 2-hour dance-competition recording into the workspace.",
            "Analyze the competition to locate top-performance moments.",
            "Extract the top performances as highlight segments.",
            "Compose an energetic EDM BGM fitting the dance reel.",
            "Transcribe the English judges' feedback on the segments into SRT.",
            "Mix the EDM BGM with the highlight reel's baked audio.",
            "Compose the reel with English captions and mixed EDM BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Please extract the biggest laughs from this 2-hour standup show, add English captions, and add a lighthearted piano BGM.",
        "rationale": (
            "Standup show + biggest laughs + English captions + lighthearted piano BGM."
        ),
        "intents": [
            "Ingest the 2-hour standup-comedy show into the workspace.",
            "Analyze the show to locate the biggest-laugh punchline moments.",
            "Extract the punchline moments as highlight segments.",
            "Compose a lighthearted piano BGM fitting the comedy reel.",
            "Transcribe the English standup dialogue on the segments into SRT.",
            "Mix the piano BGM with the highlight reel's baked audio.",
            "Compose the reel with English captions and mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "From this 4-hour gaming livestream, pull the funny reactions, add English captions from the streamer, and add a quirky chiptune BGM.",
        "rationale": (
            "Gaming livestream + funny reactions + English captions + quirky chiptune BGM."
        ),
        "intents": [
            "Ingest the 4-hour gaming-livestream recording into the workspace.",
            "Analyze the stream to locate funny-reaction moments.",
            "Extract those reaction moments as highlight segments.",
            "Compose a quirky chiptune BGM fitting the gaming reel.",
            "Transcribe the streamer's English commentary on the segments into SRT.",
            "Mix the chiptune BGM with the highlight reel's baked audio.",
            "Compose the reel with English captions and mixed chiptune BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Pull the dramatic moments from this 2-hour reality-TV episode, add English captions, and add a tension-building BGM.",
        "rationale": (
            "Reality-TV episode + dramatic moments + English captions + tension-building BGM."
        ),
        "intents": [
            "Ingest the 2-hour reality-TV episode into the workspace.",
            "Analyze the episode to locate dramatic / emotional-peak moments.",
            "Extract the dramatic moments as highlight segments.",
            "Compose a tension-building BGM fitting the reality-TV reel.",
            "Transcribe the English cast dialogue on the segments into SRT.",
            "Mix the tension BGM with the highlight reel's baked audio.",
            "Compose the reel with English captions and mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "From this 2-hour boxing match, extract the knockdowns, add English captions from the broadcast, and add an intense metal BGM.",
        "rationale": (
            "Boxing match + knockdowns + English captions + intense metal BGM."
        ),
        "intents": [
            "Ingest the 2-hour boxing-match recording into the workspace.",
            "Analyze the match to locate knockdown events.",
            "Extract the knockdowns as highlight segments.",
            "Compose an intense metal BGM fitting the knockdown reel.",
            "Transcribe the English broadcast commentary on the segments into SRT.",
            "Mix the metal BGM with the highlight reel's baked audio.",
            "Compose the reel with English captions and mixed metal BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Please pull the revelation moments from this 1-hour interview, add English captions, and add an investigative-style ambient BGM.",
        "rationale": (
            "Interview + revelation moments + English captions + investigative ambient BGM."
        ),
        "intents": [
            "Ingest the hour-long interview recording into the workspace.",
            "Analyze the interview to locate surprising / revelation moments.",
            "Extract those revelation moments as highlight segments.",
            "Compose an investigative-style ambient BGM fitting the interview reveals.",
            "Transcribe the English interview dialogue on the segments into SRT.",
            "Mix the ambient BGM with the highlight reel's baked audio.",
            "Compose the reel with English captions and mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "From this 90-minute F1 race, extract the overtakes, add English captions from the commentary, and add an adrenaline electronic-rock BGM.",
        "rationale": (
            "F1 race + overtakes + English captions + adrenaline electronic-rock BGM."
        ),
        "intents": [
            "Ingest the 90-minute F1 race recording into the workspace.",
            "Analyze the race to locate overtaking maneuvers.",
            "Extract the overtakes as highlight segments.",
            "Compose an adrenaline electronic-rock BGM fitting the F1 reel.",
            "Transcribe the English F1 commentary on the segments into SRT.",
            "Mix the rock BGM with the highlight reel's baked audio.",
            "Compose the reel with English captions and mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Pull the game-winning plays from this 2-hour NBA game, add English captions, and add a heroic orchestral BGM.",
        "rationale": (
            "NBA game + game-winning plays + English captions + heroic orchestral BGM."
        ),
        "intents": [
            "Ingest the 2-hour NBA-game recording into the workspace.",
            "Analyze the game to locate decisive clutch / game-winning moments.",
            "Extract the game-winning plays as highlight segments.",
            "Compose a heroic orchestral BGM fitting the game-winning reel.",
            "Transcribe the English broadcast commentary on the segments into SRT.",
            "Mix the orchestral BGM with the highlight reel's baked audio.",
            "Compose the reel with English captions and mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "From this 90-minute volleyball tournament, pull the best spikes, add English captions, and add an energetic techno BGM.",
        "rationale": (
            "Volleyball tournament + best spikes + English captions + energetic techno BGM."
        ),
        "intents": [
            "Ingest the 90-minute volleyball-tournament recording into the workspace.",
            "Analyze the tournament to locate the best-spike moments.",
            "Extract the spikes as highlight segments.",
            "Compose an energetic techno BGM fitting the volleyball reel.",
            "Transcribe the English volleyball commentary on the segments into SRT.",
            "Mix the techno BGM with the highlight reel's baked audio.",
            "Compose the reel with English captions and mixed techno BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Please pull the biggest plays from this 2-hour American football game, add English captions, and add an anthemic rock BGM.",
        "rationale": (
            "American football game + biggest plays + English captions + anthemic rock BGM."
        ),
        "intents": [
            "Ingest the 2-hour American football-game recording into the workspace.",
            "Analyze the game to locate the biggest-play moments.",
            "Extract the biggest plays as highlight segments.",
            "Compose an anthemic rock BGM fitting the football reel.",
            "Transcribe the English broadcast commentary on the segments into SRT.",
            "Mix the rock BGM with the highlight reel's baked audio.",
            "Compose the reel with English captions and mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "From this 2-hour baseball game, pull the home runs, add English captions, and add a cheerful honky-tonk BGM.",
        "rationale": (
            "Baseball game + home runs + English captions + cheerful honky-tonk BGM."
        ),
        "intents": [
            "Ingest the 2-hour baseball-game recording into the workspace.",
            "Analyze the game to locate home-run moments.",
            "Extract the home-runs as highlight segments.",
            "Compose a cheerful honky-tonk BGM fitting the baseball reel.",
            "Transcribe the English broadcast commentary on the home-run segments into SRT.",
            "Mix the honky-tonk BGM with the highlight reel's baked audio.",
            "Compose the reel with English captions and mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Extract the scariest scenes from this 2-hour horror-movie recording, add English captions, and add a spine-tingling ambient BGM.",
        "rationale": (
            "Horror movie + scariest scenes + English captions + spine-tingling ambient BGM."
        ),
        "intents": [
            "Ingest the 2-hour horror-movie recording into the workspace.",
            "Analyze the movie to locate the scariest / most-tense peak scenes.",
            "Extract those scary scenes as highlight segments.",
            "Compose a spine-tingling ambient BGM fitting the horror reel.",
            "Transcribe the English movie dialogue on the segments into SRT.",
            "Mix the ambient BGM with the highlight reel's baked audio.",
            "Compose the reel with English captions and mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "From this 3-hour Valorant tournament, pull the ace rounds, add English captions from the casters, and add an epic trailer BGM.",
        "rationale": (
            "Valorant tournament + ace rounds + English caster captions + epic trailer BGM."
        ),
        "intents": [
            "Ingest the 3-hour Valorant tournament stream into the workspace.",
            "Analyze the tournament to locate ace rounds and 1v4 / 1v5 clutch moments.",
            "Extract the ace-round moments as highlight segments.",
            "Compose an epic trailer BGM fitting the Valorant reel.",
            "Transcribe the English caster commentary on the segments into SRT.",
            "Mix the trailer BGM with the highlight reel's baked audio.",
            "Compose the reel with English captions and mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Pull the celebrity-guest's best moments from this 1-hour talk show, add English captions, and add a jazzy lounge BGM.",
        "rationale": (
            "Talk show + guest best moments + English captions + jazzy lounge BGM."
        ),
        "intents": [
            "Ingest the hour-long talk-show episode into the workspace.",
            "Analyze the episode to locate the celebrity guest's standout moments.",
            "Extract those guest moments as highlight segments.",
            "Compose a jazzy lounge BGM fitting the talk-show vibe.",
            "Transcribe the English guest / host dialogue on the segments into SRT.",
            "Mix the lounge BGM with the highlight reel's baked audio.",
            "Compose the reel with English captions and mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "From this 90-minute ski-competition broadcast, pull the best runs, add English captions from the broadcast, and add an adventurous orchestral BGM.",
        "rationale": (
            "Ski competition + best runs + English broadcast captions + adventurous orchestral "
            "BGM."
        ),
        "intents": [
            "Ingest the 90-minute ski-competition broadcast into the workspace.",
            "Analyze the broadcast to locate the best ski-run moments.",
            "Extract the best runs as highlight segments.",
            "Compose an adventurous orchestral BGM fitting the ski reel.",
            "Transcribe the English ski-broadcast commentary on the segments into SRT.",
            "Mix the orchestral BGM with the highlight reel's baked audio.",
            "Compose the reel with English captions and mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Pull the magic-trick reveals from this 90-minute magic show, add English captions, and add a whimsical orchestral BGM.",
        "rationale": (
            "Magic show + reveals + English captions + whimsical orchestral BGM."
        ),
        "intents": [
            "Ingest the 90-minute magic-show recording into the workspace.",
            "Analyze the show to locate peak trick-reveal moments.",
            "Extract the trick-reveals as highlight segments.",
            "Compose a whimsical orchestral BGM fitting the magic reel.",
            "Transcribe the English magician's patter on the segments into SRT.",
            "Mix the orchestral BGM with the highlight reel's baked audio.",
            "Compose the reel with English captions and mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "From this 3-hour chess tournament, pull the decisive combinations, add English captions from the commentators, and add a tension-building electronic BGM.",
        "rationale": (
            "Chess tournament + decisive combinations + English captions + tension-building "
            "electronic BGM."
        ),
        "intents": [
            "Ingest the 3-hour chess-tournament stream into the workspace.",
            "Analyze the tournament to locate decisive tactical-combination moments.",
            "Extract the decisive combinations as highlight segments.",
            "Compose a tension-building electronic BGM fitting the chess reel.",
            "Transcribe the English chess commentary on the segments into SRT.",
            "Mix the electronic BGM with the highlight reel's baked audio.",
            "Compose the reel with English captions and mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Please pull the best tricks from this 1-hour skateboarding contest, add English captions from the announcer, and add a punk-rock BGM.",
        "rationale": (
            "Skateboarding contest + best tricks + English announcer captions + punk-rock BGM."
        ),
        "intents": [
            "Ingest the 1-hour skateboarding-contest recording into the workspace.",
            "Analyze the contest to locate the highest-scoring trick moments.",
            "Extract the best tricks as highlight segments.",
            "Compose a punk-rock BGM fitting the skate reel.",
            "Transcribe the English announcer's calls on the segments into SRT.",
            "Mix the punk BGM with the highlight reel's baked audio.",
            "Compose the reel with English captions and mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "From this 2-hour MMA event, pull the knockouts, add English captions from the broadcast, and add an intense metal BGM.",
        "rationale": (
            "MMA event + knockouts + English captions + intense metal BGM."
        ),
        "intents": [
            "Ingest the 2-hour MMA event recording into the workspace.",
            "Analyze the event to locate knockout moments.",
            "Extract the knockouts as highlight segments.",
            "Compose an intense metal BGM fitting the MMA reel.",
            "Transcribe the English broadcast commentary on the segments into SRT.",
            "Mix the metal BGM with the highlight reel's baked audio.",
            "Compose the reel with English captions and mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Pull the best goal-saves from this 90-minute goalkeeper compilation, add English captions, and add a heroic orchestral BGM.",
        "rationale": (
            "Goalkeeper compilation + saves + English captions + heroic orchestral BGM."
        ),
        "intents": [
            "Ingest the 90-minute goalkeeper-compilation recording into the workspace.",
            "Analyze the compilation to locate the best goal-save moments.",
            "Extract the saves as highlight segments.",
            "Compose a heroic orchestral BGM fitting the goalkeeper reel.",
            "Transcribe the English commentary on the save segments into SRT.",
            "Mix the orchestral BGM with the highlight reel's baked audio.",
            "Compose the reel with English captions and mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Extract the best surfing tricks from this 2-hour surf competition, add English captions from the broadcast, and add a laid-back reggae BGM.",
        "rationale": (
            "Surf competition + best tricks + English captions + laid-back reggae BGM."
        ),
        "intents": [
            "Ingest the 2-hour surf-competition recording into the workspace.",
            "Analyze the competition to locate the best surf-trick moments.",
            "Extract the best tricks as highlight segments.",
            "Compose a laid-back reggae BGM fitting the surf reel.",
            "Transcribe the English surf commentary on the segments into SRT.",
            "Mix the reggae BGM with the highlight reel's baked audio.",
            "Compose the reel with English captions and mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "From this 2-hour ski-jumping competition, pull the best jumps, add English captions, and add an epic cinematic BGM.",
        "rationale": (
            "Ski-jumping competition + best jumps + English captions + epic cinematic BGM."
        ),
        "intents": [
            "Ingest the 2-hour ski-jumping competition recording into the workspace.",
            "Analyze the competition to locate the best ski-jump moments.",
            "Extract the best jumps as highlight segments.",
            "Compose an epic cinematic BGM fitting the ski-jump reel.",
            "Transcribe the English ski commentary on the segments into SRT.",
            "Mix the cinematic BGM with the highlight reel's baked audio.",
            "Compose the reel with English captions and mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "From this 3-hour rally-racing broadcast, pull the overtakes and crashes, add English captions, and add a driving electronic BGM.",
        "rationale": (
            "Rally racing + overtakes/crashes + English captions + driving electronic BGM."
        ),
        "intents": [
            "Ingest the 3-hour rally-racing broadcast into the workspace.",
            "Analyze the broadcast to locate overtake and crash events.",
            "Extract the overtakes and crashes as highlight segments.",
            "Compose a driving electronic BGM fitting the rally reel.",
            "Transcribe the English rally commentary on the segments into SRT.",
            "Mix the electronic BGM with the highlight reel's baked audio.",
            "Compose the reel with English captions and mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Pull the best acrobatic moments from this 2-hour circus show, add English captions, and add a whimsical carousel-organ BGM.",
        "rationale": (
            "Circus show + acrobatic moments + English captions + whimsical carousel-organ BGM."
        ),
        "intents": [
            "Ingest the 2-hour circus-show recording into the workspace.",
            "Analyze the show to locate signature acrobatic moments.",
            "Extract the best acrobatic moments as highlight segments.",
            "Compose a whimsical carousel-organ BGM fitting the circus reel.",
            "Transcribe the English ringmaster announcements on the segments into SRT.",
            "Mix the carousel BGM with the highlight reel's baked audio.",
            "Compose the reel with English captions and mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Extract the best snowboard tricks from this 2-hour snowboarding event, add English captions, and add an energetic indie-rock BGM.",
        "rationale": (
            "Snowboarding event + best tricks + English captions + energetic indie-rock BGM."
        ),
        "intents": [
            "Ingest the 2-hour snowboarding-event recording into the workspace.",
            "Analyze the event to locate the best snowboard-trick moments.",
            "Extract the best snowboard tricks as highlight segments.",
            "Compose an energetic indie-rock BGM fitting the snowboard reel.",
            "Transcribe the English snowboard commentary on the segments into SRT.",
            "Mix the indie-rock BGM with the highlight reel's baked audio.",
            "Compose the reel with English captions and mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "From this 2-hour Formula E electric-racing broadcast, pull the overtakes, add English captions, and add a futuristic synthwave BGM.",
        "rationale": (
            "Formula E + overtakes + English captions + futuristic synthwave BGM."
        ),
        "intents": [
            "Ingest the 2-hour Formula E broadcast into the workspace.",
            "Analyze the broadcast to locate overtake events.",
            "Extract the overtakes as highlight segments.",
            "Compose a futuristic synthwave BGM fitting the Formula E reel.",
            "Transcribe the English Formula E commentary on the segments into SRT.",
            "Mix the synthwave BGM with the highlight reel's baked audio.",
            "Compose the reel with English captions and mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "From this 2-hour triathlon broadcast, pull the leader changes, add English captions, and add a motivational electronic BGM.",
        "rationale": (
            "Triathlon broadcast + leader changes + English captions + motivational electronic "
            "BGM."
        ),
        "intents": [
            "Ingest the 2-hour triathlon broadcast into the workspace.",
            "Analyze the broadcast to locate leader-change moments.",
            "Extract the leader changes as highlight segments.",
            "Compose a motivational electronic BGM fitting the triathlon reel.",
            "Transcribe the English triathlon commentary on the segments into SRT.",
            "Mix the electronic BGM with the highlight reel's baked audio.",
            "Compose the reel with English captions and mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Pull the key points from this 1-hour conference keynote, add English captions, and add a subtle inspirational BGM.",
        "rationale": (
            "Conference keynote + key points + English captions + subtle inspirational BGM."
        ),
        "intents": [
            "Ingest the 1-hour conference keynote into the workspace.",
            "Analyze the keynote to locate key-point / quotable moments.",
            "Extract the key-point moments as highlight segments.",
            "Compose a subtle inspirational BGM fitting the keynote reel.",
            "Transcribe the English keynote speech on the segments into SRT.",
            "Mix the inspirational BGM with the highlight reel's baked audio.",
            "Compose the reel with English captions and mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "From this 3-hour ASMR livestream, pull the most-relaxing moments, add English captions from the streamer, and add a gentle ambient BGM.",
        "rationale": (
            "ASMR livestream + most-relaxing moments + English captions + gentle ambient BGM."
        ),
        "intents": [
            "Ingest the 3-hour ASMR livestream into the workspace.",
            "Analyze the stream to locate the most-relaxing / peak-ASMR moments.",
            "Extract the relaxing moments as highlight segments.",
            "Compose a gentle ambient BGM fitting the ASMR reel.",
            "Transcribe the streamer's English narration on the segments into SRT.",
            "Mix the ambient BGM with the highlight reel's baked audio.",
            "Compose the reel with English captions and mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Extract the best karaoke-performance moments from this 2-hour karaoke-night recording, add English captions, and add a sparkling disco BGM.",
        "rationale": (
            "Karaoke night + best performances + English captions + sparkling disco BGM."
        ),
        "intents": [
            "Ingest the 2-hour karaoke-night recording into the workspace.",
            "Analyze the recording to locate the best karaoke-performance moments.",
            "Extract those performances as highlight segments.",
            "Compose a sparkling disco BGM fitting the karaoke reel.",
            "Transcribe the English vocal lyrics / MC chatter on the segments into SRT.",
            "Mix the disco BGM with the highlight reel's baked audio.",
            "Compose the reel with English captions and mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "Pull the best debate clashes from this 2-hour political debate, add English captions, and add a subtle tension BGM.",
        "rationale": (
            "Political debate + best clashes + English captions + subtle tension BGM."
        ),
        "intents": [
            "Ingest the 2-hour political-debate recording into the workspace.",
            "Analyze the debate to locate the best / most-heated clash moments.",
            "Extract the clash moments as highlight segments.",
            "Compose a subtle tension BGM fitting the debate reel.",
            "Transcribe the English debate dialogue on the segments into SRT.",
            "Mix the tension BGM with the highlight reel's baked audio.",
            "Compose the reel with English captions and mixed BGM overlaid on the cuts.",
        ],
    },
    {
        "user_goal": "From this 1-hour cooking-competition finale, pull the plating reveals, add English captions from the judges, and add a dramatic orchestral BGM.",
        "rationale": (
            "Cooking-competition finale + plating reveals + English judge captions + dramatic "
            "orchestral BGM."
        ),
        "intents": [
            "Ingest the hour-long cooking-competition finale into the workspace.",
            "Analyze the finale to locate plating-reveal moments.",
            "Extract the plating reveals as highlight segments.",
            "Compose a dramatic orchestral BGM fitting the finale reveals.",
            "Transcribe the English judges' feedback on the reveal segments into SRT.",
            "Mix the orchestral BGM with the highlight reel's baked audio.",
            "Compose the reel with English captions and mixed BGM overlaid on the cuts.",
        ],
    },
]
