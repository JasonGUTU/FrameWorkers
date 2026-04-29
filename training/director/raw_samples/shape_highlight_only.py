"""Shape: highlight_only — IntakeVideo → VideoAnalysis → Highlight (raw cut output).

User uploaded a long video and wants ONLY the highlight-reel cuts — raw
segmented highlight output is the deliverable.  No compositor (no overlay),
no audio, no subtitle, no style change.

Reject biases:
  - CompositorAgent (highlight output IS the deliverable; nothing to overlay)
  - MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay)
  - TranscriptionAgent / TranslationAgent (no subtitle)
  - StyleTransferAgent / VideoExtendAgent (no restyle / length change)
"""
from __future__ import annotations

SAMPLES: list[dict] = [
    {
        "user_goal": "I have a 2-hour tennis match recording. Please pull out just the best rallies and match points.",
        "rationale": (
            "User uploaded a long tennis match and wants only the highlight segments (best "
            "rallies + match points) — raw segmented clips are the deliverable. IntakeVideoAgent "
            "ingests the recording. VideoAnalysisAgent parses the match to surface rally climaxes "
            "and scoring moments. HighlightAgent extracts those segments as a cut list. Reject "
            "CompositorAgent (no overlay requested — the cut segments ARE the output), "
            "TranscriptionAgent / TranslationAgent (no subtitles), MusicAgent / AmbienceAgent / "
            "AudioMixAgent (no BGM or ambient ask), StyleTransferAgent (no restyle)."
        ),
        "intents": [
            "Ingest the 2-hour tennis-match recording into the workspace.",
            "Analyze the tennis match to locate best rallies and match-point moments.",
            "Extract the identified rallies and match points as a cut list of highlight segments.",
        ],
    },
    {
        "user_goal": "Here's a 90-minute football match. Can you get me the goals and near-misses only?",
        "rationale": (
            "90-minute football recording + request for goals and near-misses highlight only. "
            "IntakeVideoAgent ingests the match. VideoAnalysisAgent identifies scoring and "
            "near-scoring moments. HighlightAgent cuts those segments out. Raw highlight "
            "cut list is the deliverable — no overlay, audio, or subtitle operations."
        ),
        "intents": [
            "Ingest the 90-minute football-match recording into the workspace.",
            "Analyze the football match to locate goal and near-miss moments.",
            "Extract the goals and near-misses as highlight segments.",
        ],
    },
    {
        "user_goal": "I have an hour-long wedding ceremony recording. Please pull out just the emotional moments — vows, ring exchange, first kiss.",
        "rationale": (
            "1-hour wedding-ceremony recording + request for emotional-moments highlight. "
            "IntakeVideoAgent ingests the ceremony. VideoAnalysisAgent identifies the vows, ring "
            "exchange, and first-kiss moments through content analysis. HighlightAgent extracts "
            "those segments. Raw highlight clips are the deliverable."
        ),
        "intents": [
            "Ingest the hour-long wedding-ceremony recording into the workspace.",
            "Analyze the ceremony to locate vows, ring-exchange, and first-kiss moments.",
            "Extract those emotional ceremony moments as highlight segments.",
        ],
    },
    {
        "user_goal": "Please make a highlight reel from this 3-hour e-sports tournament match — just the clutch plays and team fights.",
        "rationale": (
            "3-hour e-sports tournament + request for clutch plays and team-fights highlight. "
            "IntakeVideoAgent ingests the tournament footage. VideoAnalysisAgent analyses the "
            "match to surface clutch plays and multi-kill team-fights. HighlightAgent cuts those "
            "segments. Raw cut list is delivered."
        ),
        "intents": [
            "Ingest the 3-hour e-sports tournament recording into the workspace.",
            "Analyze the tournament to locate clutch plays and team-fight moments.",
            "Extract the clutch plays and team-fights as highlight segments.",
        ],
    },
    {
        "user_goal": "I have a 45-minute university lecture recording. Please extract just the key explanation moments.",
        "rationale": (
            "45-minute lecture + request for key-explanation-moment highlights. IntakeVideoAgent "
            "ingests the lecture. VideoAnalysisAgent identifies the key explanation segments by "
            "content and emphasis. HighlightAgent extracts those segments. No overlay / audio / "
            "subtitle operations requested — raw cut list is the output."
        ),
        "intents": [
            "Ingest the 45-minute university-lecture recording into the workspace.",
            "Analyze the lecture to identify the key explanation / teachable-moment segments.",
            "Extract the key explanation segments as highlights.",
        ],
    },
    {
        "user_goal": "Here's a 2-hour podcast recording. Please give me just the funniest moments.",
        "rationale": (
            "2-hour video podcast + request for funniest-moments highlight. IntakeVideoAgent "
            "ingests the podcast. VideoAnalysisAgent identifies laughter spikes / punchline "
            "moments through audio-visual cues. HighlightAgent cuts those moments. Raw cut "
            "list is delivered."
        ),
        "intents": [
            "Ingest the 2-hour video-podcast recording into the workspace.",
            "Analyze the podcast to locate the funniest / most-laughed-at moments.",
            "Extract those funny moments as highlight segments.",
        ],
    },
    {
        "user_goal": "Please pull out the best moments from this 90-minute basketball game — just dunks, three-pointers, and big defensive plays.",
        "rationale": (
            "90-minute basketball game + request for dunks / threes / defensive plays. "
            "IntakeVideoAgent ingests the game. VideoAnalysisAgent identifies those specific "
            "basketball-highlight events. HighlightAgent cuts them. Raw cut list delivered."
        ),
        "intents": [
            "Ingest the 90-minute basketball-game recording into the workspace.",
            "Analyze the basketball game to locate dunks, three-pointers, and big defensive plays.",
            "Extract those basketball highlight events as segments.",
        ],
    },
    {
        "user_goal": "I recorded a full 4-hour gaming livestream. Please extract just the funny reactions and epic fail moments.",
        "rationale": (
            "4-hour gaming livestream + request for funny reactions + epic fails highlight. "
            "IntakeVideoAgent ingests the stream. VideoAnalysisAgent identifies reaction spikes "
            "and epic-fail events by facial and audio cues. HighlightAgent extracts those "
            "segments. Raw cut list is the deliverable."
        ),
        "intents": [
            "Ingest the 4-hour gaming-livestream recording into the workspace.",
            "Analyze the livestream to identify funny-reaction and epic-fail moments.",
            "Extract the funny reactions and epic-fails as highlight segments.",
        ],
    },
    {
        "user_goal": "I have a 2-hour hockey game recording. Please just cut out the goals, saves, and fights.",
        "rationale": (
            "2-hour hockey game + request for goals / saves / fights highlight. IntakeVideoAgent "
            "ingests the game. VideoAnalysisAgent identifies scoring, big saves, and fights "
            "through content cues. HighlightAgent cuts those segments. Raw cut list delivered."
        ),
        "intents": [
            "Ingest the 2-hour hockey-game recording into the workspace.",
            "Analyze the hockey game to locate goals, big saves, and fights.",
            "Extract the hockey highlights as segments.",
        ],
    },
    {
        "user_goal": "Here's a 3-hour cooking-show marathon. Pull out just the plating reveals and taste-test reactions.",
        "rationale": (
            "3-hour cooking-show marathon + request for plating-reveals + taste-test-reactions "
            "highlight. IntakeVideoAgent ingests the marathon. VideoAnalysisAgent identifies "
            "plating reveals and reaction moments. HighlightAgent cuts those. Raw cut list is "
            "the output."
        ),
        "intents": [
            "Ingest the 3-hour cooking-show marathon recording into the workspace.",
            "Analyze the marathon to locate plating-reveal and taste-test-reaction moments.",
            "Extract the plating reveals and taste-test reactions as highlight segments.",
        ],
    },
    {
        "user_goal": "I have a 90-minute TED-talk marathon. Please give me the best one-liners and audience-applause moments.",
        "rationale": (
            "90-minute TED-talk marathon + request for one-liners + applause highlights. "
            "IntakeVideoAgent ingests the marathon. VideoAnalysisAgent identifies quoted "
            "one-liners (speech analysis) and applause spikes. HighlightAgent extracts those "
            "moments. Raw cut list delivered."
        ),
        "intents": [
            "Ingest the 90-minute TED-talk marathon recording into the workspace.",
            "Analyze the TED-talk marathon to locate quotable one-liners and applause moments.",
            "Extract those one-liners and applause beats as highlight segments.",
        ],
    },
    {
        "user_goal": "Please extract the most intense fight scenes from this 2-hour boxing match.",
        "rationale": (
            "2-hour boxing match + request for intense fight scenes only. IntakeVideoAgent "
            "ingests the match. VideoAnalysisAgent identifies high-intensity exchanges (combo "
            "flurries, knockdowns). HighlightAgent cuts those segments. Raw cut list delivered."
        ),
        "intents": [
            "Ingest the 2-hour boxing-match recording into the workspace.",
            "Analyze the boxing match to locate the most-intense exchange and knockdown moments.",
            "Extract the intense fight-scene moments as highlight segments.",
        ],
    },
    {
        "user_goal": "I have a 60-minute interview recording. Please pull out just the surprising / shocking revelation moments.",
        "rationale": (
            "60-minute interview + request for shocking revelations only. IntakeVideoAgent "
            "ingests the interview. VideoAnalysisAgent identifies moments of surprise or "
            "revelation (tonal / facial cues). HighlightAgent cuts those. Raw cut list is the "
            "output."
        ),
        "intents": [
            "Ingest the 60-minute interview recording into the workspace.",
            "Analyze the interview to locate surprising / shocking revelation moments.",
            "Extract those revelation moments as highlight segments.",
        ],
    },
    {
        "user_goal": "Please extract the best rehearsal moments from this 3-hour orchestra rehearsal footage.",
        "rationale": (
            "3-hour orchestra rehearsal + request for best rehearsal moments highlight. "
            "IntakeVideoAgent ingests the footage. VideoAnalysisAgent identifies the cleanest / "
            "most-musical rehearsal segments. HighlightAgent cuts those. Raw cut list is the "
            "deliverable."
        ),
        "intents": [
            "Ingest the 3-hour orchestra rehearsal recording into the workspace.",
            "Analyze the rehearsal to locate the strongest musical-pass moments.",
            "Extract the best rehearsal passes as highlight segments.",
        ],
    },
    {
        "user_goal": "I have a 4-hour baseball game recording. Please pull out just home runs and great plays.",
        "rationale": (
            "4-hour baseball game + request for home-runs and great-plays highlight. "
            "IntakeVideoAgent ingests the game. VideoAnalysisAgent identifies home-run swings "
            "and defensive gems. HighlightAgent cuts those segments. Raw cut list delivered."
        ),
        "intents": [
            "Ingest the 4-hour baseball-game recording into the workspace.",
            "Analyze the baseball game to locate home-runs and great defensive plays.",
            "Extract the home-runs and defensive gems as highlight segments.",
        ],
    },
    {
        "user_goal": "Please cut down this 2-hour standup-comedy show to just the biggest laugh moments.",
        "rationale": (
            "2-hour standup show + request for biggest-laugh moments. IntakeVideoAgent ingests "
            "the show. VideoAnalysisAgent identifies laugh spikes through audience audio "
            "cues. HighlightAgent cuts those punchline + laughter segments. Raw cut list "
            "delivered."
        ),
        "intents": [
            "Ingest the 2-hour standup-comedy show into the workspace.",
            "Analyze the standup show to locate the moments with the biggest audience laughs.",
            "Extract the biggest-laugh punchline moments as highlights.",
        ],
    },
    {
        "user_goal": "I have a 3-hour dance-competition recording. Please extract just the top performances and judges' strongest reactions.",
        "rationale": (
            "3-hour dance competition + request for top performances + judge reactions. "
            "IntakeVideoAgent ingests the recording. VideoAnalysisAgent identifies "
            "high-scoring-performance moments and strong judge-reaction beats. HighlightAgent "
            "cuts those. Raw cut list is the deliverable."
        ),
        "intents": [
            "Ingest the 3-hour dance-competition recording into the workspace.",
            "Analyze the competition to locate top performances and strong judge reactions.",
            "Extract the top performances and reactions as highlight segments.",
        ],
    },
    {
        "user_goal": "Please pull the best acrobatic moments from this 2-hour circus-show recording.",
        "rationale": (
            "2-hour circus show + request for best acrobatic moments. IntakeVideoAgent ingests "
            "the show. VideoAnalysisAgent identifies signature acrobatic tricks / high-difficulty "
            "movements. HighlightAgent extracts those. Raw cut list delivered."
        ),
        "intents": [
            "Ingest the 2-hour circus-show recording into the workspace.",
            "Analyze the circus show to locate signature acrobatic / high-difficulty tricks.",
            "Extract those best acrobatic moments as highlight segments.",
        ],
    },
    {
        "user_goal": "I have a 90-minute Formula 1 race recording. Please extract overtakes, crashes, and pit-stop action only.",
        "rationale": (
            "90-minute F1 race + request for overtakes / crashes / pit-stops highlight. "
            "IntakeVideoAgent ingests the race. VideoAnalysisAgent identifies overtaking "
            "maneuvers, crash events, and pit-stop actions. HighlightAgent cuts those. Raw "
            "cut list is delivered."
        ),
        "intents": [
            "Ingest the 90-minute Formula 1 race recording into the workspace.",
            "Analyze the F1 race to locate overtakes, crashes, and pit-stop events.",
            "Extract overtakes, crashes, and pit-stop moments as highlight segments.",
        ],
    },
    {
        "user_goal": "I have a 3-hour poker-tournament stream. Please pull out just the big hands and all-in moments.",
        "rationale": (
            "3-hour poker-tournament stream + request for big hands + all-ins highlight. "
            "IntakeVideoAgent ingests the stream. VideoAnalysisAgent identifies the big-hand "
            "showdowns and all-in moments. HighlightAgent cuts those. Raw cut list delivered."
        ),
        "intents": [
            "Ingest the 3-hour poker-tournament stream into the workspace.",
            "Analyze the tournament stream to locate big hands and all-in moments.",
            "Extract the big hands and all-ins as highlight segments.",
        ],
    },
    {
        "user_goal": "Please pull the best game-winning plays from this 2-hour NBA game recording.",
        "rationale": (
            "2-hour NBA game + request for game-winning plays highlight. IntakeVideoAgent "
            "ingests the game. VideoAnalysisAgent identifies the decisive clutch possessions "
            "(final-seconds shots, game-winning stops). HighlightAgent cuts those. Raw cut list "
            "delivered."
        ),
        "intents": [
            "Ingest the 2-hour NBA-game recording into the workspace.",
            "Analyze the NBA game to locate the decisive clutch / game-winning moments.",
            "Extract the game-winning plays as highlight segments.",
        ],
    },
    {
        "user_goal": "I have an hour-long talk-show episode. Please cut out only the celebrity-guest's best moments.",
        "rationale": (
            "1-hour talk show + request for celebrity-guest's best moments. IntakeVideoAgent "
            "ingests the episode. VideoAnalysisAgent identifies the guest's standout segments "
            "(stories, reactions). HighlightAgent cuts those. Raw cut list is the deliverable."
        ),
        "intents": [
            "Ingest the hour-long talk-show episode into the workspace.",
            "Analyze the talk-show episode to locate the celebrity guest's standout moments.",
            "Extract the guest's best moments as highlight segments.",
        ],
    },
    {
        "user_goal": "Please extract the scariest / most-tense scenes from this 2-hour horror-movie recording.",
        "rationale": (
            "2-hour horror-movie recording + request for scariest scenes highlight. "
            "IntakeVideoAgent ingests the movie. VideoAnalysisAgent identifies high-tension "
            "jump-scare / horror-peak moments via visual-audio cues. HighlightAgent cuts those "
            "scenes. Raw cut list delivered."
        ),
        "intents": [
            "Ingest the 2-hour horror-movie recording into the workspace.",
            "Analyze the movie to locate the scariest / most-tense peak scenes.",
            "Extract the scariest scenes as highlight segments.",
        ],
    },
    {
        "user_goal": "I recorded a 6-hour long-haul flight-deck cockpit video. Please pull just the takeoff, cruise-altitude changes, and landing.",
        "rationale": (
            "6-hour cockpit video + request for takeoff / cruise-change / landing highlight. "
            "IntakeVideoAgent ingests the full cockpit footage. VideoAnalysisAgent identifies "
            "takeoff sequence, altitude-change events, and landing approach. HighlightAgent "
            "cuts those. Raw cut list delivered."
        ),
        "intents": [
            "Ingest the 6-hour flight-deck cockpit recording into the workspace.",
            "Analyze the cockpit recording to locate takeoff, cruise-altitude changes, and landing.",
            "Extract those flight-phase events as highlight segments.",
        ],
    },
    {
        "user_goal": "Please pull the best magic-trick reveals from this 90-minute magic-show recording.",
        "rationale": (
            "90-minute magic show + request for best-trick-reveals highlight. IntakeVideoAgent "
            "ingests the show. VideoAnalysisAgent identifies the peak-reveal moments of each "
            "trick (audience gasp cues / presentational climax). HighlightAgent cuts those "
            "reveal moments. Raw cut list delivered."
        ),
        "intents": [
            "Ingest the 90-minute magic-show recording into the workspace.",
            "Analyze the magic show to locate the peak trick-reveal moments.",
            "Extract the magic-trick reveals as highlight segments.",
        ],
    },
    {
        "user_goal": "I have a 4-hour chess tournament stream. Please extract just the blunder moments and decisive combinations.",
        "rationale": (
            "4-hour chess tournament + request for blunders + decisive-combo moments. "
            "IntakeVideoAgent ingests the stream. VideoAnalysisAgent identifies blunder "
            "reactions and decisive combination announcements by commentator / on-board cues. "
            "HighlightAgent cuts those. Raw cut list delivered."
        ),
        "intents": [
            "Ingest the 4-hour chess-tournament stream into the workspace.",
            "Analyze the chess tournament to locate blunders and decisive tactical combinations.",
            "Extract those blunder and decisive-combination moments as highlight segments.",
        ],
    },
    {
        "user_goal": "Please pull the most emotional moments from this 2-hour reality-TV episode.",
        "rationale": (
            "2-hour reality-TV episode + request for most-emotional moments highlight. "
            "IntakeVideoAgent ingests the episode. VideoAnalysisAgent identifies emotional "
            "peak moments (tear-up reactions, outbursts, reconciliations). HighlightAgent cuts "
            "those. Raw cut list is the deliverable."
        ),
        "intents": [
            "Ingest the 2-hour reality-TV episode into the workspace.",
            "Analyze the episode to locate the most-emotional / tear-up / outburst moments.",
            "Extract those emotional peaks as highlight segments.",
        ],
    },
    {
        "user_goal": "I have a 3-hour esports Valorant tournament stream. Please extract just ace rounds and clutch 1v4 / 1v5 moments.",
        "rationale": (
            "3-hour Valorant tournament + request for ace rounds and 1v4 / 1v5 clutches. "
            "IntakeVideoAgent ingests the stream. VideoAnalysisAgent identifies ace and clutch "
            "events by kill-feed and commentator cues. HighlightAgent cuts those rounds. Raw "
            "cut list delivered."
        ),
        "intents": [
            "Ingest the 3-hour Valorant tournament stream into the workspace.",
            "Analyze the Valorant tournament to locate ace rounds and 1v4 / 1v5 clutch moments.",
            "Extract the ace rounds and clutch moments as highlight segments.",
        ],
    },
    {
        "user_goal": "Please pull the best save-the-day moments from this 60-minute drone-rescue documentary.",
        "rationale": (
            "60-minute drone-rescue documentary + request for save-the-day moments highlight. "
            "IntakeVideoAgent ingests the documentary. VideoAnalysisAgent identifies successful "
            "rescue climaxes. HighlightAgent cuts those moments. Raw cut list delivered."
        ),
        "intents": [
            "Ingest the 60-minute drone-rescue documentary into the workspace.",
            "Analyze the documentary to locate successful save-the-day rescue moments.",
            "Extract the rescue-success moments as highlight segments.",
        ],
    },
    {
        "user_goal": "I have a 2-hour ski-competition broadcast. Please pull the best runs and biggest crashes.",
        "rationale": (
            "2-hour ski-competition broadcast + request for best runs + biggest crashes. "
            "IntakeVideoAgent ingests the broadcast. VideoAnalysisAgent identifies high-score "
            "runs and crash events. HighlightAgent cuts those. Raw cut list delivered."
        ),
        "intents": [
            "Ingest the 2-hour ski-competition broadcast into the workspace.",
            "Analyze the ski-competition broadcast to locate best runs and biggest crashes.",
            "Extract the best runs and biggest crashes as highlight segments.",
        ],
    },
    {
        "user_goal": "Please give me the funniest moments from this 90-minute talk-show episode with multiple guests.",
        "rationale": (
            "90-minute multi-guest talk show + request for funniest moments highlight. "
            "IntakeVideoAgent ingests the episode. VideoAnalysisAgent identifies laugh spikes "
            "and punchline moments across all guest segments. HighlightAgent cuts those. Raw "
            "cut list delivered."
        ),
        "intents": [
            "Ingest the 90-minute multi-guest talk-show episode into the workspace.",
            "Analyze the episode to locate the funniest / biggest-laugh punchline moments.",
            "Extract those funny moments as highlight segments.",
        ],
    },
    {
        "user_goal": "I have a 3-hour board-game marathon stream. Please cut out only the dramatic twist moments.",
        "rationale": (
            "3-hour board-game marathon + request for dramatic twist moments highlight. "
            "IntakeVideoAgent ingests the marathon stream. VideoAnalysisAgent identifies twist "
            "beats (big reactions, upsets). HighlightAgent cuts those. Raw cut list delivered."
        ),
        "intents": [
            "Ingest the 3-hour board-game marathon stream into the workspace.",
            "Analyze the marathon to locate dramatic twist / upset moments.",
            "Extract those twist moments as highlight segments.",
        ],
    },
    {
        "user_goal": "Please cut out just the best goal-saves and penalty moments from this 90-minute goalkeeper-compilation recording.",
        "rationale": (
            "90-minute goalkeeper compilation + request for goal-saves and penalty moments. "
            "IntakeVideoAgent ingests the compilation. VideoAnalysisAgent identifies save events "
            "and penalty kick moments. HighlightAgent cuts those. Raw cut list delivered."
        ),
        "intents": [
            "Ingest the 90-minute goalkeeper-compilation recording into the workspace.",
            "Analyze the compilation to locate the best goal-saves and penalty-kick moments.",
            "Extract the goal-saves and penalty moments as highlight segments.",
        ],
    },
    {
        "user_goal": "I have a 4-hour live concert recording. Please extract just the headline songs and biggest applause moments.",
        "rationale": (
            "4-hour live concert + request for headline songs + applause moments highlight. "
            "IntakeVideoAgent ingests the recording. VideoAnalysisAgent identifies headline "
            "songs (by song-title display / solo spots) and peak applause moments. "
            "HighlightAgent cuts those. Raw cut list delivered."
        ),
        "intents": [
            "Ingest the 4-hour live-concert recording into the workspace.",
            "Analyze the concert to locate headline songs and peak applause moments.",
            "Extract the headline songs and applause peaks as highlight segments.",
        ],
    },
    {
        "user_goal": "Please pull just the best tricks from this 60-minute skateboarding competition.",
        "rationale": (
            "60-minute skateboarding competition + request for best tricks highlight. "
            "IntakeVideoAgent ingests the competition. VideoAnalysisAgent identifies "
            "highest-scoring / most-difficult tricks. HighlightAgent cuts those. Raw cut list "
            "delivered."
        ),
        "intents": [
            "Ingest the 60-minute skateboarding-competition recording into the workspace.",
            "Analyze the competition to locate the highest-scoring / most-difficult tricks.",
            "Extract the best tricks as highlight segments.",
        ],
    },
    {
        "user_goal": "I have a 3-hour game-dev livestream with a boss-fight section. Please extract just the boss-attempt moments where the streamer reacts to big hits and deaths.",
        "rationale": (
            "3-hour game-dev livestream + request for boss-attempt reactions highlight. "
            "IntakeVideoAgent ingests the stream. VideoAnalysisAgent identifies moments of "
            "big-hit reactions and death events (face-cam + in-game cues). HighlightAgent cuts "
            "those. Raw cut list delivered."
        ),
        "intents": [
            "Ingest the 3-hour game-dev livestream into the workspace.",
            "Analyze the livestream to locate boss-attempt moments with big-hit reactions and deaths.",
            "Extract those reaction-rich boss-attempt moments as highlight segments.",
        ],
    },
    {
        "user_goal": "Please pull the best dunks, alley-oops, and posterizations from this 2-hour high-school basketball recording.",
        "rationale": (
            "2-hour high-school basketball + request for dunks / alley-oops / posterizations "
            "highlight. IntakeVideoAgent ingests the game. VideoAnalysisAgent identifies those "
            "specific high-flying play types. HighlightAgent cuts those. Raw cut list delivered."
        ),
        "intents": [
            "Ingest the 2-hour high-school basketball recording into the workspace.",
            "Analyze the game to locate dunks, alley-oops, and posterization moments.",
            "Extract the dunks, alley-oops, and posterizations as highlight segments.",
        ],
    },
    {
        "user_goal": "I have a 5-hour marathon race recording. Please pull the race-leader overtakes and finish-line moments.",
        "rationale": (
            "5-hour marathon race + request for overtakes + finish-line moments highlight. "
            "IntakeVideoAgent ingests the race. VideoAnalysisAgent identifies lead-change "
            "events and finish-line crossings. HighlightAgent cuts those. Raw cut list delivered."
        ),
        "intents": [
            "Ingest the 5-hour marathon-race recording into the workspace.",
            "Analyze the marathon to locate lead-change overtakes and finish-line moments.",
            "Extract those race-leader overtakes and finish-line moments as highlight segments.",
        ],
    },
    {
        "user_goal": "Please extract the funniest pet-animal moments from this 2-hour pet-vlog compilation.",
        "rationale": (
            "2-hour pet-vlog compilation + request for funniest pet moments highlight. "
            "IntakeVideoAgent ingests the compilation. VideoAnalysisAgent identifies the "
            "funniest pet moments via motion / audio cues. HighlightAgent cuts those. Raw cut "
            "list delivered."
        ),
        "intents": [
            "Ingest the 2-hour pet-vlog compilation into the workspace.",
            "Analyze the compilation to locate the funniest pet-animal moments.",
            "Extract those funny pet moments as highlight segments.",
        ],
    },
    {
        "user_goal": "I have a 90-minute volleyball tournament recording. Please pull out spikes, blocks, and match points.",
        "rationale": (
            "90-minute volleyball tournament + request for spikes / blocks / match-points "
            "highlight. IntakeVideoAgent ingests the tournament. VideoAnalysisAgent identifies "
            "those specific volleyball play types. HighlightAgent cuts those. Raw cut list "
            "delivered."
        ),
        "intents": [
            "Ingest the 90-minute volleyball-tournament recording into the workspace.",
            "Analyze the volleyball tournament to locate spikes, blocks, and match-point moments.",
            "Extract the spikes, blocks, and match-points as highlight segments.",
        ],
    },
]
