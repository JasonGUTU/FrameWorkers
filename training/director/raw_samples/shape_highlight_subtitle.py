"""Shape: highlight_subtitle — IntakeVideo → VideoAnalysis → Highlight → Transcription → Compositor.

User uploaded a long video, wants highlights cut out AND captioned.
No BGM / Ambience / Style / Extend / Translation.
"""
from __future__ import annotations

SAMPLES: list[dict] = [
    {
        "user_goal": "Please pull just the best rally highlights from this 2-hour tennis match and add English captions from the commentator.",
        "rationale": (
            "User uploaded a 2-hour tennis match, wants highlight-reel cuts + English "
            "captions. IntakeVideoAgent ingests. VideoAnalysisAgent identifies rally climaxes. "
            "HighlightAgent cuts those segments. TranscriptionAgent transcribes the commentator "
            "on the highlight clips. CompositorAgent burns English SRT onto the highlights. "
            "Reject TranslationAgent (monolingual), MusicAgent / AmbienceAgent / AudioMixAgent "
            "(no audio overlay), StyleTransferAgent / VideoExtendAgent (no visual / length "
            "change)."
        ),
        "intents": [
            "Ingest the 2-hour tennis-match recording into the workspace.",
            "Analyze the match to locate the best rally / climactic moments.",
            "Extract the identified rallies as highlight segments.",
            "Transcribe the English commentator audio on the highlight segments into SRT.",
            "Compose the highlight reel with English captions burned onto the rally clips.",
        ],
    },
    {
        "user_goal": "From this 90-minute football match, extract the goals and add English subtitles from the announcers' calls.",
        "rationale": (
            "Football match + goals highlight + English subs from announcer. IntakeVideoAgent "
            "→ VideoAnalysisAgent (goal events) → HighlightAgent (cuts goals) → "
            "TranscriptionAgent (English announcer) → CompositorAgent (English SRT on cuts)."
        ),
        "intents": [
            "Ingest the 90-minute football-match recording into the workspace.",
            "Analyze the match to locate goal events.",
            "Extract the goals as highlight segments.",
            "Transcribe the announcer's English calls on the goal segments into SRT.",
            "Compose the goal highlight reel with English captions burned onto the cuts.",
        ],
    },
    {
        "user_goal": "Please pull the funniest moments from this 2-hour podcast episode and add English captions.",
        "rationale": (
            "Video-podcast + funniest moments highlight + English captions. IntakeVideoAgent "
            "→ VideoAnalysisAgent (laugh spikes) → HighlightAgent → TranscriptionAgent "
            "(English dialogue) → CompositorAgent (English SRT)."
        ),
        "intents": [
            "Ingest the 2-hour video-podcast recording into the workspace.",
            "Analyze the podcast to identify the funniest / biggest-laugh moments.",
            "Extract those funny moments as highlight segments.",
            "Transcribe the English podcast dialogue on those segments into SRT.",
            "Compose the highlight reel with English captions burned onto the funny-moment cuts.",
        ],
    },
    {
        "user_goal": "From this 90-minute TED-talk marathon, please extract the quotable one-liners and add English captions.",
        "rationale": (
            "TED-talk marathon + one-liner highlight + English captions. IntakeVideoAgent → "
            "VideoAnalysisAgent → HighlightAgent → TranscriptionAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 90-minute TED-talk marathon recording into the workspace.",
            "Analyze the marathon to locate the most-quotable one-liner moments.",
            "Extract the one-liner moments as highlight segments.",
            "Transcribe the English one-liners on those segments into SRT.",
            "Compose the highlight reel with English captions burned onto the one-liner cuts.",
        ],
    },
    {
        "user_goal": "Please pull the best moments from this 3-hour e-sports tournament and add English-language captions from the casters.",
        "rationale": (
            "E-sports tournament + best-moments highlight + English caster captions. "
            "IntakeVideoAgent → VideoAnalysisAgent (clutch / team-fight) → HighlightAgent → "
            "TranscriptionAgent (English casters) → CompositorAgent."
        ),
        "intents": [
            "Ingest the 3-hour e-sports tournament recording into the workspace.",
            "Analyze the tournament to locate clutch plays and team-fight moments.",
            "Extract those clutch / team-fight moments as highlight segments.",
            "Transcribe the English caster commentary on the highlight segments into SRT.",
            "Compose the highlight reel with English captions burned onto the tournament cuts.",
        ],
    },
    {
        "user_goal": "Please extract the emotional moments from this 1-hour wedding-ceremony recording and add English subtitles.",
        "rationale": (
            "Wedding ceremony + emotional-moments highlight + English subtitles. "
            "IntakeVideoAgent → VideoAnalysisAgent (vows, ring exchange, first kiss) → "
            "HighlightAgent → TranscriptionAgent (English vows) → CompositorAgent."
        ),
        "intents": [
            "Ingest the hour-long wedding-ceremony recording into the workspace.",
            "Analyze the ceremony to locate vows, ring exchange, and first-kiss moments.",
            "Extract those emotional ceremony moments as highlight segments.",
            "Transcribe the English vows on the highlight segments into SRT.",
            "Compose the highlight reel with English captions burned onto the ceremony cuts.",
        ],
    },
    {
        "user_goal": "From this 2-hour dance competition, pull the top performances and add English captions from the judges' feedback.",
        "rationale": (
            "Dance competition + top-performances highlight + English judge captions. "
            "IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → TranscriptionAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 2-hour dance-competition recording into the workspace.",
            "Analyze the competition to locate top performances and judge reactions.",
            "Extract the top performances as highlight segments.",
            "Transcribe the judges' English feedback on the highlight segments into SRT.",
            "Compose the highlight reel with English captions burned onto the performance cuts.",
        ],
    },
    {
        "user_goal": "Please pull the biggest-laugh moments from this 2-hour standup show and add English captions.",
        "rationale": (
            "Standup show + biggest-laugh highlight + English captions. IntakeVideoAgent → "
            "VideoAnalysisAgent → HighlightAgent → TranscriptionAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 2-hour standup-comedy show into the workspace.",
            "Analyze the show to locate the biggest-laugh punchline moments.",
            "Extract those punchline moments as highlight segments.",
            "Transcribe the English stand-up dialogue on the highlight segments into SRT.",
            "Compose the highlight reel with English captions burned onto the punchline cuts.",
        ],
    },
    {
        "user_goal": "From this 4-hour gaming livestream, extract the funny-reaction moments and add English captions from the streamer.",
        "rationale": (
            "Gaming livestream + funny-reaction highlight + English streamer captions. "
            "IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → TranscriptionAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 4-hour gaming-livestream recording into the workspace.",
            "Analyze the stream to locate funny-reaction / epic-fail moments.",
            "Extract those reaction moments as highlight segments.",
            "Transcribe the streamer's English commentary on the segments into SRT.",
            "Compose the highlight reel with English captions burned onto the streamer cuts.",
        ],
    },
    {
        "user_goal": "Please cut the dramatic moments from this 2-hour reality-TV episode and add English captions.",
        "rationale": (
            "Reality-TV episode + dramatic moments highlight + English captions. "
            "IntakeVideoAgent → VideoAnalysisAgent (emotional peaks) → HighlightAgent → "
            "TranscriptionAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 2-hour reality-TV episode into the workspace.",
            "Analyze the episode to locate dramatic / emotional-peak moments.",
            "Extract those dramatic moments as highlight segments.",
            "Transcribe the English cast dialogue on the segments into SRT.",
            "Compose the highlight reel with English captions burned onto the reality-TV cuts.",
        ],
    },
    {
        "user_goal": "From this 2-hour Spanish-language soccer match, pull the goals and add Spanish-only captions from the announcer.",
        "rationale": (
            "Spanish soccer match + goals highlight + Spanish (monolingual) announcer captions. "
            "IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → TranscriptionAgent "
            "(Spanish) → CompositorAgent."
        ),
        "intents": [
            "Ingest the 2-hour Spanish-language soccer match into the workspace.",
            "Analyze the match to locate goal events.",
            "Extract the goals as highlight segments.",
            "Transcribe the Spanish announcer commentary on the goal segments into SRT.",
            "Compose the goal highlight reel with Spanish captions burned onto the cuts.",
        ],
    },
    {
        "user_goal": "Please extract the best rehearsal moments from this 3-hour orchestra rehearsal and add English captions from the conductor.",
        "rationale": (
            "Orchestra rehearsal + best-moments highlight + English conductor captions. "
            "IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → TranscriptionAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 3-hour orchestra rehearsal recording into the workspace.",
            "Analyze the rehearsal to locate the strongest musical-pass moments.",
            "Extract those best-pass moments as highlight segments.",
            "Transcribe the conductor's English instructions on the segments into SRT.",
            "Compose the highlight reel with English captions burned onto the rehearsal cuts.",
        ],
    },
    {
        "user_goal": "From this 2-hour baseball game, pull the home runs and add English captions from the broadcast.",
        "rationale": (
            "Baseball game + home-runs highlight + English broadcast captions. "
            "IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → TranscriptionAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 2-hour baseball-game recording into the workspace.",
            "Analyze the game to locate home-run moments.",
            "Extract the home-runs as highlight segments.",
            "Transcribe the English broadcast commentary on the home-run segments into SRT.",
            "Compose the home-run highlight reel with English captions burned onto the cuts.",
        ],
    },
    {
        "user_goal": "Please extract the scariest scenes from this 2-hour horror-movie recording and add English captions.",
        "rationale": (
            "Horror-movie recording + scariest scenes highlight + English captions. "
            "IntakeVideoAgent → VideoAnalysisAgent (jump-scares / horror-peak) → "
            "HighlightAgent → TranscriptionAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 2-hour horror-movie recording into the workspace.",
            "Analyze the movie to locate the scariest / most-tense peak scenes.",
            "Extract those scary scenes as highlight segments.",
            "Transcribe the English movie dialogue on the segments into SRT.",
            "Compose the highlight reel with English captions burned onto the scary-scene cuts.",
        ],
    },
    {
        "user_goal": "From this 3-hour Valorant esports tournament, pull the ace rounds and add English captions from the casters.",
        "rationale": (
            "Valorant tournament + ace rounds highlight + English caster captions. "
            "IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → TranscriptionAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 3-hour Valorant tournament stream into the workspace.",
            "Analyze the tournament to locate ace rounds and 1v4 / 1v5 clutch moments.",
            "Extract the ace-round and clutch moments as highlight segments.",
            "Transcribe the English caster commentary on the segments into SRT.",
            "Compose the highlight reel with English captions burned onto the ace-round cuts.",
        ],
    },
    {
        "user_goal": "Please pull the celebrity-guest's best moments from this 1-hour talk-show episode and add English captions.",
        "rationale": (
            "Talk-show episode + celebrity-guest highlight + English captions. "
            "IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → TranscriptionAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the hour-long talk-show episode into the workspace.",
            "Analyze the episode to locate the celebrity guest's standout moments.",
            "Extract those guest moments as highlight segments.",
            "Transcribe the English guest / host dialogue on the segments into SRT.",
            "Compose the highlight reel with English captions burned onto the guest-moment cuts.",
        ],
    },
    {
        "user_goal": "From this 90-minute boxing match, extract the knockdown moments and add English captions from the broadcast.",
        "rationale": (
            "Boxing match + knockdown highlight + English broadcast captions. "
            "IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → TranscriptionAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 90-minute boxing-match recording into the workspace.",
            "Analyze the match to locate knockdown events.",
            "Extract the knockdowns as highlight segments.",
            "Transcribe the English broadcast commentary on the knockdown segments into SRT.",
            "Compose the highlight reel with English captions burned onto the knockdown cuts.",
        ],
    },
    {
        "user_goal": "Please pull the revelation moments from this 1-hour interview recording and add English captions.",
        "rationale": (
            "Interview recording + revelation highlight + English captions. IntakeVideoAgent "
            "→ VideoAnalysisAgent → HighlightAgent → TranscriptionAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the hour-long interview recording into the workspace.",
            "Analyze the interview to locate surprising / revelation moments.",
            "Extract the revelation moments as highlight segments.",
            "Transcribe the English interview dialogue on the segments into SRT.",
            "Compose the highlight reel with English captions burned onto the revelation cuts.",
        ],
    },
    {
        "user_goal": "From this 90-minute F1 race, extract the overtakes and add English captions from the commentary.",
        "rationale": (
            "F1 race + overtakes highlight + English commentary captions. IntakeVideoAgent → "
            "VideoAnalysisAgent → HighlightAgent → TranscriptionAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 90-minute F1 race recording into the workspace.",
            "Analyze the race to locate overtaking maneuvers.",
            "Extract the overtakes as highlight segments.",
            "Transcribe the English F1 commentary on the overtake segments into SRT.",
            "Compose the highlight reel with English captions burned onto the overtake cuts.",
        ],
    },
    {
        "user_goal": "Please pull the game-winning plays from this 2-hour NBA game and add English captions from the broadcast.",
        "rationale": (
            "NBA game + game-winning plays highlight + English broadcast captions. "
            "IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → TranscriptionAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 2-hour NBA-game recording into the workspace.",
            "Analyze the game to locate decisive clutch / game-winning moments.",
            "Extract the game-winning plays as highlight segments.",
            "Transcribe the English broadcast commentary on the segments into SRT.",
            "Compose the highlight reel with English captions burned onto the clutch-play cuts.",
        ],
    },
    {
        "user_goal": "From this 90-minute volleyball tournament, pull the best spikes and add English captions.",
        "rationale": (
            "Volleyball tournament + best-spikes highlight + English captions. "
            "IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → TranscriptionAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 90-minute volleyball-tournament recording into the workspace.",
            "Analyze the tournament to locate spike events.",
            "Extract the spikes as highlight segments.",
            "Transcribe the English volleyball commentary on the spike segments into SRT.",
            "Compose the highlight reel with English captions burned onto the spike cuts.",
        ],
    },
    {
        "user_goal": "Please extract the biggest-play moments from this 2-hour American football game and add English captions.",
        "rationale": (
            "American football game + biggest-plays highlight + English captions. "
            "IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → TranscriptionAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 2-hour American football-game recording into the workspace.",
            "Analyze the game to locate the biggest play moments.",
            "Extract the biggest plays as highlight segments.",
            "Transcribe the English broadcast commentary on the segments into SRT.",
            "Compose the highlight reel with English captions burned onto the biggest-play cuts.",
        ],
    },
    {
        "user_goal": "From this 2-hour hockey game, pull the goals, saves, and fights, and add English captions.",
        "rationale": (
            "Hockey game + multi-event highlight (goals / saves / fights) + English captions. "
            "IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → TranscriptionAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 2-hour hockey-game recording into the workspace.",
            "Analyze the hockey game to locate goals, big saves, and fights.",
            "Extract those hockey-highlight events as segments.",
            "Transcribe the English broadcast commentary on the segments into SRT.",
            "Compose the highlight reel with English captions burned onto the hockey cuts.",
        ],
    },
    {
        "user_goal": "Please pull the best magic-trick reveals from this 90-minute magic show and add English captions.",
        "rationale": (
            "Magic show + trick-reveals highlight + English captions. IntakeVideoAgent → "
            "VideoAnalysisAgent → HighlightAgent → TranscriptionAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 90-minute magic-show recording into the workspace.",
            "Analyze the show to locate peak trick-reveal moments.",
            "Extract the magic-trick reveals as highlight segments.",
            "Transcribe the English magician's patter on the reveal segments into SRT.",
            "Compose the highlight reel with English captions burned onto the magic-reveal cuts.",
        ],
    },
    {
        "user_goal": "From this 3-hour chess tournament stream, pull the decisive combination moments and add English captions from the commentators.",
        "rationale": (
            "Chess tournament + decisive-combinations highlight + English commentator captions. "
            "IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → TranscriptionAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 3-hour chess-tournament stream into the workspace.",
            "Analyze the tournament to locate decisive tactical-combination moments.",
            "Extract the decisive-combination moments as highlight segments.",
            "Transcribe the English chess commentary on the segments into SRT.",
            "Compose the highlight reel with English captions burned onto the chess cuts.",
        ],
    },
    {
        "user_goal": "Please extract the best tricks from this 1-hour skateboarding-competition recording and add English captions from the announcer.",
        "rationale": (
            "Skateboarding competition + best-tricks highlight + English announcer captions. "
            "IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → TranscriptionAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 1-hour skateboarding-competition recording into the workspace.",
            "Analyze the competition to locate the highest-scoring trick moments.",
            "Extract the best tricks as highlight segments.",
            "Transcribe the English announcer's calls on the segments into SRT.",
            "Compose the highlight reel with English captions burned onto the skate cuts.",
        ],
    },
    {
        "user_goal": "From this 2-hour ski-competition broadcast, pull the best runs and add English captions.",
        "rationale": (
            "Ski competition + best-runs highlight + English captions. IntakeVideoAgent → "
            "VideoAnalysisAgent → HighlightAgent → TranscriptionAgent → CompositorAgent."
        ),
        "intents": [
            "Ingest the 2-hour ski-competition broadcast into the workspace.",
            "Analyze the broadcast to locate the best ski-run moments.",
            "Extract the best runs as highlight segments.",
            "Transcribe the English ski-broadcast commentary on the segments into SRT.",
            "Compose the highlight reel with English captions burned onto the ski cuts.",
        ],
    },
    {
        "user_goal": "Please pull the best goal-saves from this 90-minute goalkeeper-compilation and add English captions from the commentary.",
        "rationale": (
            "Goalkeeper compilation + best-saves highlight + English commentary captions. "
            "IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → TranscriptionAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 90-minute goalkeeper-compilation recording into the workspace.",
            "Analyze the compilation to locate the best goal-save moments.",
            "Extract the saves as highlight segments.",
            "Transcribe the English commentary on the save segments into SRT.",
            "Compose the highlight reel with English captions burned onto the save cuts.",
        ],
    },
    {
        "user_goal": "From this 4-hour live concert recording, extract the headline songs and add English captions of the lyrics.",
        "rationale": (
            "Live concert + headline-songs highlight + English lyrics captions. "
            "IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → TranscriptionAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 4-hour live-concert recording into the workspace.",
            "Analyze the concert to locate headline-song performances.",
            "Extract the headline-song performances as highlight segments.",
            "Transcribe the English vocal lyrics on the song segments into SRT.",
            "Compose the highlight reel with English lyrics burned onto the song cuts.",
        ],
    },
    {
        "user_goal": "Please pull the acrobatic highlights from this 2-hour circus show and add English captions from the ringmaster.",
        "rationale": (
            "Circus show + acrobatic highlight + English ringmaster captions. "
            "IntakeVideoAgent → VideoAnalysisAgent → HighlightAgent → TranscriptionAgent → "
            "CompositorAgent."
        ),
        "intents": [
            "Ingest the 2-hour circus-show recording into the workspace.",
            "Analyze the show to locate signature acrobatic moments.",
            "Extract the acrobatic moments as highlight segments.",
            "Transcribe the English ringmaster's announcements on the segments into SRT.",
            "Compose the highlight reel with English captions burned onto the circus cuts.",
        ],
    },
]
