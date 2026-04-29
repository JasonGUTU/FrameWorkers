"""GRPO shape: highlight_only — IntakeVideo → VideoAnalysis → Highlight.

40 samples (target_n=40, no long_story_n). Pure highlight-extraction
from uploaded long video. Topics span sports / entertainment /
conference / performance domains. Rationale style mirrors SFT: medium
flow narrative + explicit reject list.
"""
from __future__ import annotations

SAMPLES: list[dict] = [
    {
        "user_goal": "I have a 3-hour NBA game recording. Please pull out just the dunks, blocks, and game-tying shots.",
        "rationale": (
            "3-hour NBA game + dunks / blocks / game-tying-shots highlight only. "
            "IntakeVideoAgent ingests the game recording; VideoAnalysisAgent surfaces the "
            "dunk, block, and game-tying-shot moments; HighlightAgent extracts those "
            "segments as a cut list. Raw highlight clips ARE the deliverable. Reject "
            "CompositorAgent (no overlay), TranscriptionAgent / TranslationAgent (no "
            "subtitles), MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay), "
            "StyleTransferAgent / VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 3-hour NBA game recording into the workspace.",
            "Analyze the NBA game to locate dunks, blocks, and game-tying-shot moments.",
            "Extract the dunks, blocks, and game-tying shots as a highlight-segment cut list.",
        ],
    },
    {
        "user_goal": "Please extract only the elimination rounds and judge tasting moments from this 4-hour cooking competition recording.",
        "rationale": (
            "4-hour cooking competition + elimination-rounds and judge-tasting highlight "
            "only. IntakeVideoAgent loads the long recording; VideoAnalysisAgent identifies "
            "elimination announcements and judge-tasting reactions; HighlightAgent cuts "
            "those moments out as a segmented cut list. Reject CompositorAgent (raw cuts "
            "ARE the deliverable, no overlay), TranscriptionAgent / TranslationAgent (no "
            "subtitles), MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay), "
            "StyleTransferAgent / VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 4-hour cooking-competition recording into the workspace.",
            "Analyze the cooking competition to locate elimination rounds and judge-tasting moments.",
            "Extract the elimination rounds and judge-tasting moments as highlight segments.",
        ],
    },
    {
        "user_goal": "I have a 2-hour fashion-week runway show recording. Can you pull only the finale walk and designer takes-a-bow segments?",
        "rationale": (
            "2-hour fashion-week runway show + finale-walk and designer-bow highlight "
            "only. IntakeVideoAgent ingests the show; VideoAnalysisAgent locates the "
            "finale-walk and designer-bow moments; HighlightAgent extracts those segments. "
            "Raw highlight clips are the deliverable. Reject CompositorAgent (no overlay), "
            "TranscriptionAgent / TranslationAgent (no subtitles), MusicAgent / "
            "AmbienceAgent / AudioMixAgent (no audio overlay), StyleTransferAgent / "
            "VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 2-hour fashion-week runway show recording into the workspace.",
            "Analyze the runway show to locate the finale walk and designer-bow moments.",
            "Extract the finale walk and designer-bow moments as highlight segments.",
        ],
    },
    {
        "user_goal": "Please pull just the keynote-question moments out of this 6-hour academic conference recording — speakers were asked questions after their talks, I want only those Q&A exchanges.",
        "rationale": (
            "6-hour academic conference + post-talk Q&A-exchange highlight only. "
            "IntakeVideoAgent ingests the conference recording; VideoAnalysisAgent "
            "identifies the post-talk Q&A exchanges between speakers and audience; "
            "HighlightAgent extracts those exchanges as cut segments. Raw segmented Q&A "
            "cuts are the final deliverable. Reject CompositorAgent (no overlay), "
            "TranscriptionAgent / TranslationAgent (no subtitle ask), MusicAgent / "
            "AmbienceAgent / AudioMixAgent (no BGM / ambient / mix asked), "
            "StyleTransferAgent / VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 6-hour academic-conference recording into the workspace.",
            "Analyze the conference recording to locate post-talk Q&A exchanges.",
            "Extract the keynote-question Q&A exchanges as highlight segments.",
        ],
    },
    {
        "user_goal": "Got an 8-hour video-game tournament stream archive — please cut out only the boss-kill and final-round moments.",
        "rationale": (
            "8-hour video-game tournament archive + boss-kill / final-round highlight "
            "only. IntakeVideoAgent ingests the long stream; VideoAnalysisAgent locates "
            "the boss-kill moments and final-round footage; HighlightAgent extracts those "
            "segments. Raw cut list is the deliverable. Reject CompositorAgent (no "
            "overlay), TranscriptionAgent / TranslationAgent (no subtitles), MusicAgent / "
            "AmbienceAgent / AudioMixAgent (no audio overlay), StyleTransferAgent / "
            "VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 8-hour video-game tournament stream archive into the workspace.",
            "Analyze the tournament stream to locate boss-kill and final-round moments.",
            "Extract the boss-kill and final-round moments as highlight segments.",
        ],
    },
    {
        "user_goal": "Pull just the headlining-act moments and crowd singalong segments from this 5-hour music festival main-stage recording.",
        "rationale": (
            "5-hour music festival main-stage + headlining-act and crowd-singalong "
            "highlight only. IntakeVideoAgent ingests the stage recording; "
            "VideoAnalysisAgent identifies the headlining-act performance segments and "
            "crowd-singalong moments; HighlightAgent cuts those out. Raw cut clips are "
            "the deliverable. Reject CompositorAgent (no overlay), MusicAgent / "
            "AmbienceAgent / AudioMixAgent (no audio overlay needed — original festival "
            "audio is preserved by the highlight cuts themselves), TranscriptionAgent / "
            "TranslationAgent (no subtitle ask), StyleTransferAgent / VideoExtendAgent "
            "(no restyle / length change)."
        ),
        "intents": [
            "Ingest the 5-hour music-festival main-stage recording into the workspace.",
            "Analyze the festival recording to locate headlining-act performances and crowd-singalong moments.",
            "Extract the headlining-act and crowd-singalong moments as highlight segments.",
        ],
    },
    {
        "user_goal": "I have a 2-hour soccer tournament recording. Please pull just the goals and great saves.",
        "rationale": (
            "2-hour soccer tournament + goals and great-saves highlight only. "
            "IntakeVideoAgent loads the tournament; VideoAnalysisAgent surfaces the goal "
            "and goalkeeper-save moments; HighlightAgent extracts those segments as a "
            "cut list. Raw highlight clips ARE the deliverable. Reject CompositorAgent "
            "(no overlay), TranscriptionAgent / TranslationAgent (no subtitles), "
            "MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay), "
            "StyleTransferAgent / VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 2-hour soccer tournament recording into the workspace.",
            "Analyze the soccer tournament to locate goals and great-saves moments.",
            "Extract the goals and great saves as a highlight-segment cut list.",
        ],
    },
    {
        "user_goal": "Please cut just the tries and big tackles from this 90-minute rugby final recording.",
        "rationale": (
            "90-minute rugby final + tries and big-tackles highlight only. "
            "IntakeVideoAgent ingests the final; VideoAnalysisAgent identifies the try-"
            "scoring and key-tackle moments; HighlightAgent cuts those out. Raw "
            "highlight clips are the deliverable. Reject CompositorAgent (no overlay), "
            "TranscriptionAgent / TranslationAgent (no subtitles), MusicAgent / "
            "AmbienceAgent / AudioMixAgent (no audio overlay), StyleTransferAgent / "
            "VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 90-minute rugby final recording into the workspace.",
            "Analyze the rugby final to locate tries and big-tackle moments.",
            "Extract the tries and big tackles as highlight segments.",
        ],
    },
    {
        "user_goal": "Got a 3-hour volleyball championship recording. Please pull only the kills and blocks.",
        "rationale": (
            "3-hour volleyball championship + kills and blocks highlight only. "
            "IntakeVideoAgent loads the championship; VideoAnalysisAgent surfaces the "
            "spike-kill and block moments; HighlightAgent extracts those segments. Raw "
            "cut list is the deliverable. Reject CompositorAgent (no overlay), "
            "TranscriptionAgent / TranslationAgent (no subtitles), MusicAgent / "
            "AmbienceAgent / AudioMixAgent (no audio overlay), StyleTransferAgent / "
            "VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 3-hour volleyball championship recording into the workspace.",
            "Analyze the volleyball championship to locate kill and block moments.",
            "Extract the kills and blocks as highlight segments.",
        ],
    },
    {
        "user_goal": "Please extract only the boundaries and wickets from this 7-hour cricket Test match recording.",
        "rationale": (
            "7-hour cricket Test match + boundaries and wickets highlight only. "
            "IntakeVideoAgent ingests the long Test match recording; VideoAnalysisAgent "
            "identifies the boundary-shot and wicket-fall moments; HighlightAgent cuts "
            "those moments out as a segmented cut list. Reject CompositorAgent (no "
            "overlay), TranscriptionAgent / TranslationAgent (no subtitles), MusicAgent "
            "/ AmbienceAgent / AudioMixAgent (no audio overlay), StyleTransferAgent / "
            "VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 7-hour cricket Test match recording into the workspace.",
            "Analyze the cricket Test match to locate boundaries and wicket-fall moments.",
            "Extract the boundaries and wickets as highlight segments.",
        ],
    },
    {
        "user_goal": "I have a 4-hour baseball game recording — please pull just the home runs and strikeouts.",
        "rationale": (
            "4-hour baseball game + home-runs and strikeouts highlight only. "
            "IntakeVideoAgent loads the game; VideoAnalysisAgent surfaces the home-run "
            "and strikeout moments; HighlightAgent extracts those segments. Raw "
            "highlight clips are the deliverable. Reject CompositorAgent (no overlay), "
            "TranscriptionAgent / TranslationAgent (no subtitles), MusicAgent / "
            "AmbienceAgent / AudioMixAgent (no audio overlay), StyleTransferAgent / "
            "VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 4-hour baseball game recording into the workspace.",
            "Analyze the baseball game to locate home-run and strikeout moments.",
            "Extract the home runs and strikeouts as highlight segments.",
        ],
    },
    {
        "user_goal": "Got a 2.5-hour ice hockey final recording. Please pull just the goals and the goalie's biggest saves.",
        "rationale": (
            "2.5-hour ice hockey final + goals and goalie-saves highlight only. "
            "IntakeVideoAgent ingests the final; VideoAnalysisAgent identifies the goal "
            "and goalie-save moments; HighlightAgent cuts those segments out. Raw "
            "highlight clips are the deliverable. Reject CompositorAgent (no overlay), "
            "TranscriptionAgent / TranslationAgent (no subtitles), MusicAgent / "
            "AmbienceAgent / AudioMixAgent (no audio overlay), StyleTransferAgent / "
            "VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 2.5-hour ice hockey final recording into the workspace.",
            "Analyze the ice hockey final to locate goal and goalie-save moments.",
            "Extract the goals and biggest goalie saves as highlight segments.",
        ],
    },
    {
        "user_goal": "Please extract just the overtakes and pit stops from this 4-hour F1 race weekend recording.",
        "rationale": (
            "4-hour F1 race weekend + overtakes and pit-stops highlight only. "
            "IntakeVideoAgent loads the race weekend; VideoAnalysisAgent identifies the "
            "overtaking and pit-stop moments; HighlightAgent extracts those segments. "
            "Raw cut list is the deliverable. Reject CompositorAgent (no overlay), "
            "TranscriptionAgent / TranslationAgent (no subtitles), MusicAgent / "
            "AmbienceAgent / AudioMixAgent (no audio overlay), StyleTransferAgent / "
            "VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 4-hour F1 race weekend recording into the workspace.",
            "Analyze the F1 race weekend to locate overtake and pit-stop moments.",
            "Extract the overtakes and pit stops as highlight segments.",
        ],
    },
    {
        "user_goal": "Got a 90-minute MotoGP grand prix recording. Please pull only the overtakes and the riders' big saves.",
        "rationale": (
            "90-minute MotoGP grand prix + overtakes and big-saves highlight only. "
            "IntakeVideoAgent ingests the grand prix; VideoAnalysisAgent locates the "
            "overtaking maneuvers and rider-save moments; HighlightAgent cuts those "
            "moments out. Raw highlight clips are the deliverable. Reject "
            "CompositorAgent (no overlay), TranscriptionAgent / TranslationAgent (no "
            "subtitles), MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay), "
            "StyleTransferAgent / VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 90-minute MotoGP grand prix recording into the workspace.",
            "Analyze the MotoGP grand prix to locate overtake and rider-save moments.",
            "Extract the overtakes and big saves as highlight segments.",
        ],
    },
    {
        "user_goal": "Please cut just the perfect-score routines from this 6-hour Olympic gymnastics recording.",
        "rationale": (
            "6-hour Olympic gymnastics broadcast + perfect-score-routines highlight "
            "only. IntakeVideoAgent loads the long broadcast; VideoAnalysisAgent "
            "identifies the perfect-score routine performances; HighlightAgent extracts "
            "those segments. Raw highlight clips are the deliverable. Reject "
            "CompositorAgent (no overlay), TranscriptionAgent / TranslationAgent (no "
            "subtitles), MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay), "
            "StyleTransferAgent / VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 6-hour Olympic gymnastics broadcast into the workspace.",
            "Analyze the gymnastics broadcast to locate perfect-score routine moments.",
            "Extract the perfect-score routines as highlight segments.",
        ],
    },
    {
        "user_goal": "Got a 5-hour swimming championship broadcast. Please extract just the gold-medal heats.",
        "rationale": (
            "5-hour swimming championship broadcast + gold-medal-heats highlight only. "
            "IntakeVideoAgent ingests the broadcast; VideoAnalysisAgent identifies the "
            "gold-medal heat performances; HighlightAgent cuts those moments out. Raw "
            "cut list is the deliverable. Reject CompositorAgent (no overlay), "
            "TranscriptionAgent / TranslationAgent (no subtitles), MusicAgent / "
            "AmbienceAgent / AudioMixAgent (no audio overlay), StyleTransferAgent / "
            "VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 5-hour swimming championship broadcast into the workspace.",
            "Analyze the swimming championship to locate gold-medal heat moments.",
            "Extract the gold-medal heats as highlight segments.",
        ],
    },
    {
        "user_goal": "Please pull just the break-points and match-points from this 4-hour tennis grand slam final recording.",
        "rationale": (
            "4-hour tennis grand slam final + break-points and match-points highlight "
            "only. IntakeVideoAgent loads the final; VideoAnalysisAgent surfaces the "
            "break-point and match-point moments; HighlightAgent extracts those "
            "segments. Raw highlight clips are the deliverable. Reject CompositorAgent "
            "(no overlay), TranscriptionAgent / TranslationAgent (no subtitles), "
            "MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay), "
            "StyleTransferAgent / VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 4-hour tennis grand slam final recording into the workspace.",
            "Analyze the tennis final to locate break-point and match-point moments.",
            "Extract the break-points and match-points as highlight segments.",
        ],
    },
    {
        "user_goal": "Got a 5-hour golf major tournament broadcast. Please pull only the birdies and eagles.",
        "rationale": (
            "5-hour golf major tournament broadcast + birdies and eagles highlight only. "
            "IntakeVideoAgent ingests the broadcast; VideoAnalysisAgent identifies the "
            "birdie and eagle moments across the field; HighlightAgent cuts those "
            "segments out. Raw cut list is the deliverable. Reject CompositorAgent (no "
            "overlay), TranscriptionAgent / TranslationAgent (no subtitles), MusicAgent "
            "/ AmbienceAgent / AudioMixAgent (no audio overlay), StyleTransferAgent / "
            "VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 5-hour golf major tournament broadcast into the workspace.",
            "Analyze the golf tournament broadcast to locate birdie and eagle moments.",
            "Extract the birdies and eagles as highlight segments.",
        ],
    },
    {
        "user_goal": "Please extract just the knockdown moments from this 90-minute boxing heavyweight title fight recording.",
        "rationale": (
            "90-minute boxing heavyweight title fight + knockdown highlight only. "
            "IntakeVideoAgent loads the fight; VideoAnalysisAgent identifies the "
            "knockdown moments; HighlightAgent extracts those segments. Raw highlight "
            "clips are the deliverable. Reject CompositorAgent (no overlay), "
            "TranscriptionAgent / TranslationAgent (no subtitles), MusicAgent / "
            "AmbienceAgent / AudioMixAgent (no audio overlay), StyleTransferAgent / "
            "VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 90-minute boxing heavyweight title fight recording into the workspace.",
            "Analyze the boxing fight to locate knockdown moments.",
            "Extract the knockdowns as highlight segments.",
        ],
    },
    {
        "user_goal": "Got a 3-hour MMA championship event recording. Please pull only the knockouts and submissions.",
        "rationale": (
            "3-hour MMA championship event + knockouts and submissions highlight only. "
            "IntakeVideoAgent ingests the event; VideoAnalysisAgent identifies the "
            "knockout and submission-finish moments; HighlightAgent extracts those "
            "segments. Raw cut list is the deliverable. Reject CompositorAgent (no "
            "overlay), TranscriptionAgent / TranslationAgent (no subtitles), MusicAgent "
            "/ AmbienceAgent / AudioMixAgent (no audio overlay), StyleTransferAgent / "
            "VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 3-hour MMA championship event recording into the workspace.",
            "Analyze the MMA event to locate knockout and submission moments.",
            "Extract the knockouts and submissions as highlight segments.",
        ],
    },
    {
        "user_goal": "Please cut just the top waves from this 4-hour surfing competition broadcast.",
        "rationale": (
            "4-hour surfing competition broadcast + top-waves highlight only. "
            "IntakeVideoAgent loads the broadcast; VideoAnalysisAgent identifies the "
            "best-scoring wave rides; HighlightAgent extracts those segments. Raw "
            "highlight clips are the deliverable. Reject CompositorAgent (no overlay), "
            "TranscriptionAgent / TranslationAgent (no subtitles), MusicAgent / "
            "AmbienceAgent / AudioMixAgent (no audio overlay), StyleTransferAgent / "
            "VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 4-hour surfing competition broadcast into the workspace.",
            "Analyze the surfing broadcast to locate top-scoring wave rides.",
            "Extract the top waves as highlight segments.",
        ],
    },
    {
        "user_goal": "Got a 3-hour ski jumping world cup broadcast. Please extract just the gold-medal jumps.",
        "rationale": (
            "3-hour ski jumping world cup broadcast + gold-medal-jumps highlight only. "
            "IntakeVideoAgent ingests the broadcast; VideoAnalysisAgent identifies the "
            "gold-medal jump performances; HighlightAgent cuts those moments out. Raw "
            "highlight clips are the deliverable. Reject CompositorAgent (no overlay), "
            "TranscriptionAgent / TranslationAgent (no subtitles), MusicAgent / "
            "AmbienceAgent / AudioMixAgent (no audio overlay), StyleTransferAgent / "
            "VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 3-hour ski jumping world cup broadcast into the workspace.",
            "Analyze the ski jumping broadcast to locate gold-medal jump moments.",
            "Extract the gold-medal jumps as highlight segments.",
        ],
    },
    {
        "user_goal": "Please pull only the perfect-spin sequences from this 4-hour figure skating championship broadcast.",
        "rationale": (
            "4-hour figure skating championship broadcast + perfect-spin-sequences "
            "highlight only. IntakeVideoAgent loads the broadcast; VideoAnalysisAgent "
            "identifies the perfect-spin sequence performances; HighlightAgent cuts "
            "those segments out. Raw cut list is the deliverable. Reject "
            "CompositorAgent (no overlay), TranscriptionAgent / TranslationAgent (no "
            "subtitles), MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay), "
            "StyleTransferAgent / VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 4-hour figure skating championship broadcast into the workspace.",
            "Analyze the figure skating broadcast to locate perfect-spin sequence moments.",
            "Extract the perfect-spin sequences as highlight segments.",
        ],
    },
    {
        "user_goal": "Got a 6-hour amateur baking competition stream. Please extract just the judging moments.",
        "rationale": (
            "6-hour amateur baking competition + judging-moments highlight only. "
            "IntakeVideoAgent ingests the long stream; VideoAnalysisAgent identifies "
            "the judges' tasting and verdict moments; HighlightAgent cuts those "
            "segments out. Raw highlight clips are the deliverable. Reject "
            "CompositorAgent (no overlay), TranscriptionAgent / TranslationAgent (no "
            "subtitles), MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay), "
            "StyleTransferAgent / VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 6-hour amateur baking competition stream into the workspace.",
            "Analyze the baking competition to locate judges' tasting and verdict moments.",
            "Extract the judging moments as highlight segments.",
        ],
    },
    {
        "user_goal": "Please cut only the final-dish-reveal moments from this 5-hour cooking show season finale.",
        "rationale": (
            "5-hour cooking show season finale + final-dish-reveal highlight only. "
            "IntakeVideoAgent loads the season finale; VideoAnalysisAgent identifies "
            "the final-dish reveal moments; HighlightAgent extracts those segments. "
            "Raw cut list is the deliverable. Reject CompositorAgent (no overlay), "
            "TranscriptionAgent / TranslationAgent (no subtitles), MusicAgent / "
            "AmbienceAgent / AudioMixAgent (no audio overlay), StyleTransferAgent / "
            "VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 5-hour cooking show season finale recording into the workspace.",
            "Analyze the cooking finale to locate final-dish reveal moments.",
            "Extract the final-dish reveals as highlight segments.",
        ],
    },
    {
        "user_goal": "Got a 4-hour dance reality show recording. Please pull just the top-scoring routines.",
        "rationale": (
            "4-hour dance reality show + top-scoring-routines highlight only. "
            "IntakeVideoAgent ingests the show; VideoAnalysisAgent identifies the "
            "top-scoring routine performances; HighlightAgent cuts those segments out. "
            "Raw highlight clips are the deliverable. Reject CompositorAgent (no "
            "overlay), TranscriptionAgent / TranslationAgent (no subtitles), MusicAgent "
            "/ AmbienceAgent / AudioMixAgent (no audio overlay), StyleTransferAgent / "
            "VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 4-hour dance reality show recording into the workspace.",
            "Analyze the dance reality show to locate top-scoring routine moments.",
            "Extract the top-scoring routines as highlight segments.",
        ],
    },
    {
        "user_goal": "Please extract just the winning performances from this 3-hour talent show finale recording.",
        "rationale": (
            "3-hour talent show finale + winning-performances highlight only. "
            "IntakeVideoAgent loads the finale; VideoAnalysisAgent identifies the "
            "winning-act performances; HighlightAgent extracts those segments. Raw "
            "highlight clips are the deliverable. Reject CompositorAgent (no overlay), "
            "TranscriptionAgent / TranslationAgent (no subtitles), MusicAgent / "
            "AmbienceAgent / AudioMixAgent (no audio overlay), StyleTransferAgent / "
            "VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 3-hour talent show finale recording into the workspace.",
            "Analyze the talent show finale to locate winning-act performance moments.",
            "Extract the winning performances as highlight segments.",
        ],
    },
    {
        "user_goal": "Got a 2-hour drag race show recording — please pull only the runway-look moments.",
        "rationale": (
            "2-hour drag race show + runway-look highlight only. IntakeVideoAgent "
            "ingests the show; VideoAnalysisAgent identifies the runway-look "
            "presentations; HighlightAgent cuts those moments out. Raw cut list is the "
            "deliverable. Reject CompositorAgent (no overlay), TranscriptionAgent / "
            "TranslationAgent (no subtitles), MusicAgent / AmbienceAgent / "
            "AudioMixAgent (no audio overlay), StyleTransferAgent / VideoExtendAgent "
            "(no restyle / length change)."
        ),
        "intents": [
            "Ingest the 2-hour drag race show recording into the workspace.",
            "Analyze the drag race show to locate runway-look presentation moments.",
            "Extract the runway looks as highlight segments.",
        ],
    },
    {
        "user_goal": "Please extract just the winning-speech moments from this 3-hour drama awards ceremony recording.",
        "rationale": (
            "3-hour drama awards ceremony + winning-speech highlight only. "
            "IntakeVideoAgent loads the ceremony; VideoAnalysisAgent identifies the "
            "winning-speech moments; HighlightAgent extracts those segments. Raw "
            "highlight clips are the deliverable. Reject CompositorAgent (no overlay), "
            "TranscriptionAgent / TranslationAgent (no subtitles), MusicAgent / "
            "AmbienceAgent / AudioMixAgent (no audio overlay), StyleTransferAgent / "
            "VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 3-hour drama awards ceremony recording into the workspace.",
            "Analyze the awards ceremony to locate winning-speech moments.",
            "Extract the winning speeches as highlight segments.",
        ],
    },
    {
        "user_goal": "Got a 3-hour comedy roast night recording. Please pull just the best zingers.",
        "rationale": (
            "3-hour comedy roast night + best-zingers highlight only. IntakeVideoAgent "
            "ingests the roast night; VideoAnalysisAgent identifies the best-laugh-"
            "response zinger moments; HighlightAgent cuts those segments out. Raw "
            "highlight clips are the deliverable. Reject CompositorAgent (no overlay), "
            "TranscriptionAgent / TranslationAgent (no subtitles), MusicAgent / "
            "AmbienceAgent / AudioMixAgent (no audio overlay), StyleTransferAgent / "
            "VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 3-hour comedy roast night recording into the workspace.",
            "Analyze the roast night to locate best-laugh-response zinger moments.",
            "Extract the best zingers as highlight segments.",
        ],
    },
    {
        "user_goal": "Please cut just the top illusions from this 2-hour magic show recording.",
        "rationale": (
            "2-hour magic show + top-illusions highlight only. IntakeVideoAgent loads "
            "the show; VideoAnalysisAgent identifies the most impressive illusion "
            "performances; HighlightAgent extracts those segments. Raw cut list is the "
            "deliverable. Reject CompositorAgent (no overlay), TranscriptionAgent / "
            "TranslationAgent (no subtitles), MusicAgent / AmbienceAgent / "
            "AudioMixAgent (no audio overlay), StyleTransferAgent / VideoExtendAgent "
            "(no restyle / length change)."
        ),
        "intents": [
            "Ingest the 2-hour magic show recording into the workspace.",
            "Analyze the magic show to locate the most impressive illusion moments.",
            "Extract the top illusions as highlight segments.",
        ],
    },
    {
        "user_goal": "Got a 6-hour scientific symposium recording. Please pull just the keynote-highlight moments.",
        "rationale": (
            "6-hour scientific symposium + keynote-highlight moments only. "
            "IntakeVideoAgent ingests the symposium; VideoAnalysisAgent identifies the "
            "keynote highlight passages — major findings, audience-reaction-worthy "
            "moments; HighlightAgent cuts those segments out. Raw cut list is the "
            "deliverable. Reject CompositorAgent (no overlay), TranscriptionAgent / "
            "TranslationAgent (no subtitles), MusicAgent / AmbienceAgent / "
            "AudioMixAgent (no audio overlay), StyleTransferAgent / VideoExtendAgent "
            "(no restyle / length change)."
        ),
        "intents": [
            "Ingest the 6-hour scientific symposium recording into the workspace.",
            "Analyze the symposium to locate keynote-highlight moments.",
            "Extract the keynote highlights as highlight segments.",
        ],
    },
    {
        "user_goal": "Please extract just the product-reveal moments from this 4-hour tech conference keynote recording.",
        "rationale": (
            "4-hour tech conference keynote + product-reveal highlight only. "
            "IntakeVideoAgent loads the keynote; VideoAnalysisAgent identifies the "
            "product-reveal demonstration moments; HighlightAgent extracts those "
            "segments. Raw highlight clips are the deliverable. Reject CompositorAgent "
            "(no overlay), TranscriptionAgent / TranslationAgent (no subtitles), "
            "MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay), "
            "StyleTransferAgent / VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 4-hour tech conference keynote recording into the workspace.",
            "Analyze the tech keynote to locate product-reveal demonstration moments.",
            "Extract the product reveals as highlight segments.",
        ],
    },
    {
        "user_goal": "Got an 8-hour TED-talk all-day event recording. Please cut only the top talks.",
        "rationale": (
            "8-hour TED-talk all-day event + top-talks highlight only. IntakeVideoAgent "
            "ingests the day-long event; VideoAnalysisAgent identifies the highest-"
            "engagement talk segments based on audience reaction and content density; "
            "HighlightAgent cuts those out. Raw highlight clips are the deliverable. "
            "Reject CompositorAgent (no overlay), TranscriptionAgent / TranslationAgent "
            "(no subtitles), MusicAgent / AmbienceAgent / AudioMixAgent (no audio "
            "overlay), StyleTransferAgent / VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 8-hour TED-talk all-day event recording into the workspace.",
            "Analyze the TED event to locate the highest-engagement talk segments.",
            "Extract the top talks as highlight segments.",
        ],
    },
    {
        "user_goal": "Please extract just the sharpest exchanges from this 3-hour political debate recording.",
        "rationale": (
            "3-hour political debate + sharpest-exchanges highlight only. "
            "IntakeVideoAgent loads the debate; VideoAnalysisAgent identifies the "
            "sharpest cross-examination exchanges; HighlightAgent cuts those segments "
            "out. Raw cut list is the deliverable. Reject CompositorAgent (no "
            "overlay), TranscriptionAgent / TranslationAgent (no subtitles), MusicAgent "
            "/ AmbienceAgent / AudioMixAgent (no audio overlay), StyleTransferAgent / "
            "VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 3-hour political debate recording into the workspace.",
            "Analyze the political debate to locate the sharpest cross-examination exchanges.",
            "Extract the sharpest exchanges as highlight segments.",
        ],
    },
    {
        "user_goal": "Got a 3-hour concert tour archive from one venue. Please pull just the encore moments.",
        "rationale": (
            "3-hour concert tour archive (one venue) + encore-moments highlight only. "
            "IntakeVideoAgent ingests the archive; VideoAnalysisAgent identifies the "
            "encore-performance moments; HighlightAgent extracts those segments. Raw "
            "cut list is the deliverable. Reject CompositorAgent (no overlay), "
            "MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay needed — "
            "concert audio is preserved by the highlight cuts themselves), "
            "TranscriptionAgent / TranslationAgent (no subtitles), StyleTransferAgent "
            "/ VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 3-hour concert tour archive into the workspace.",
            "Analyze the concert archive to locate encore-performance moments.",
            "Extract the encore moments as highlight segments.",
        ],
    },
    {
        "user_goal": "Please cut just the solo-passage moments from this 2-hour orchestral symphony recording.",
        "rationale": (
            "2-hour orchestral symphony + solo-passages highlight only. "
            "IntakeVideoAgent loads the symphony recording; VideoAnalysisAgent "
            "identifies the soloist-feature passages within the symphony; "
            "HighlightAgent extracts those segments. Raw highlight clips are the "
            "deliverable. Reject CompositorAgent (no overlay), MusicAgent / "
            "AmbienceAgent / AudioMixAgent (no audio overlay needed — orchestra audio "
            "is preserved), TranscriptionAgent / TranslationAgent (no subtitles), "
            "StyleTransferAgent / VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 2-hour orchestral symphony recording into the workspace.",
            "Analyze the symphony to locate soloist-feature passages.",
            "Extract the solo passages as highlight segments.",
        ],
    },
    {
        "user_goal": "Got a 3-hour opera production recording. Please pull just the climactic arias.",
        "rationale": (
            "3-hour opera production + climactic-arias highlight only. "
            "IntakeVideoAgent ingests the production; VideoAnalysisAgent identifies the "
            "climactic-aria performances; HighlightAgent cuts those segments out. Raw "
            "cut list is the deliverable. Reject CompositorAgent (no overlay), "
            "MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay needed — "
            "opera audio is preserved), TranscriptionAgent / TranslationAgent (no "
            "subtitles), StyleTransferAgent / VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 3-hour opera production recording into the workspace.",
            "Analyze the opera production to locate climactic-aria moments.",
            "Extract the climactic arias as highlight segments.",
        ],
    },
    {
        "user_goal": "Please extract just the pas-de-deux moments from this 2.5-hour ballet performance recording.",
        "rationale": (
            "2.5-hour ballet performance + pas-de-deux highlight only. "
            "IntakeVideoAgent loads the ballet; VideoAnalysisAgent identifies the "
            "pas-de-deux duet moments; HighlightAgent extracts those segments. Raw "
            "highlight clips are the deliverable. Reject CompositorAgent (no overlay), "
            "MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay), "
            "TranscriptionAgent / TranslationAgent (no subtitles), StyleTransferAgent "
            "/ VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 2.5-hour ballet performance recording into the workspace.",
            "Analyze the ballet performance to locate pas-de-deux duet moments.",
            "Extract the pas-de-deux as highlight segments.",
        ],
    },
    {
        "user_goal": "Got a 6-hour theme-park ride compilation footage from a vlogger. Please pull just the drop moments from each ride.",
        "rationale": (
            "6-hour theme-park ride compilation + drop-moments highlight only. "
            "IntakeVideoAgent ingests the long footage; VideoAnalysisAgent identifies "
            "the drop / climax moments across the various rides; HighlightAgent "
            "extracts those segments. Raw cut list is the deliverable. Reject "
            "CompositorAgent (no overlay), TranscriptionAgent / TranslationAgent (no "
            "subtitles), MusicAgent / AmbienceAgent / AudioMixAgent (no audio overlay), "
            "StyleTransferAgent / VideoExtendAgent (no restyle / length change)."
        ),
        "intents": [
            "Ingest the 6-hour theme-park ride compilation footage into the workspace.",
            "Analyze the theme-park footage to locate drop / climax moments across rides.",
            "Extract the drop moments as highlight segments.",
        ],
    },
]
