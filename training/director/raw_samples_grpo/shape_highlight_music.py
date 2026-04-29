"""GRPO shape: highlight_music — IntakeVideo → VideoAnalysis → Highlight → Music → AudioMix → Compositor.

20 samples (target_n=20). Highlight reel with BGM overlay.
"""
from __future__ import annotations


def _make(topic, focus, music):
    return {
        "rationale": (
            f"{topic} + {focus} highlight + {music} BGM. Reject AmbienceAgent, "
            "Transcription/Translation, StyleTransfer/VideoExtend."
        ),
        "intents": [
            f"Ingest the user's uploaded {topic} recording into the workspace.",
            f"Analyze the {topic} to locate {focus} moments.",
            f"Extract the {focus} as highlight segments.",
            f"Compose the {music} BGM the user requested.",
            f"Layer the {music} BGM under the highlight segments into one final mixed wav.",
            f"Composite the final highlight reel mp4 with mixed audio.",
        ],
    }


SAMPLES: list[dict] = [
    {**_make("3-hour NBA game", "dunk-and-block", "high-energy hip-hop"),
     "user_goal": "Make a highlight reel of dunks and blocks from my 3-hour NBA game with high-energy hip-hop BGM."},
    {**_make("4-hour cooking competition", "judging-moment", "playful piano-and-strings"),
     "user_goal": "Cut a highlight reel of judging moments from my 4-hour cooking competition with playful piano-and-strings BGM."},
    {**_make("2-hour fashion-week runway", "finale-walk", "high-fashion electronic"),
     "user_goal": "Make a highlight reel of finale walks from my 2-hour fashion-week runway with high-fashion electronic BGM."},
    {**_make("6-hour academic conference", "keynote-highlight", "uplifting orchestral"),
     "user_goal": "Cut a highlight reel of keynote highlights from my 6-hour academic conference with uplifting orchestral BGM."},
    {**_make("8-hour gaming tournament", "boss-kill-and-final-round", "epic gaming-orchestral"),
     "user_goal": "Make a highlight reel of boss kills and final rounds from my 8-hour gaming tournament with epic gaming-orchestral BGM."},
    {**_make("5-hour music festival main-stage", "headlining-act", "festival-rock-anthem"),
     "user_goal": "Cut a highlight reel of headlining acts from my 5-hour music festival main-stage with festival-rock-anthem BGM."},
    {**_make("90-minute soccer match", "goal-and-save", "stadium anthem"),
     "user_goal": "Make a highlight reel of goals and saves from my 90-minute soccer match with stadium-anthem BGM."},
    {**_make("3-hour volleyball championship", "kill-and-block", "energetic electronic-rock"),
     "user_goal": "Cut a highlight reel of kills and blocks from my 3-hour volleyball championship with energetic electronic-rock BGM."},
    {**_make("7-hour cricket Test match", "boundary-and-wicket", "Indian-orchestral celebratory"),
     "user_goal": "Make a highlight reel of boundaries and wickets from my 7-hour cricket Test match with Indian-orchestral celebratory BGM."},
    {**_make("4-hour baseball game", "home-run-and-strikeout", "stadium organ"),
     "user_goal": "Cut a highlight reel of home runs and strikeouts from my 4-hour baseball game with stadium-organ BGM."},
    {**_make("2.5-hour ice hockey final", "goal-and-goalie-save", "hard-rock-anthem"),
     "user_goal": "Make a highlight reel of goals and goalie saves from my 2.5-hour ice hockey final with hard-rock-anthem BGM."},
    {**_make("4-hour F1 race weekend", "overtake-and-pit-stop", "orchestral-electronic"),
     "user_goal": "Cut a highlight reel of overtakes and pit stops from my 4-hour F1 race weekend with orchestral-electronic BGM."},
    {**_make("90-minute MotoGP grand prix", "overtake-and-rider-save", "racing-electronic"),
     "user_goal": "Make a highlight reel of overtakes and rider saves from my 90-minute MotoGP grand prix with racing-electronic BGM."},
    {**_make("6-hour Olympic gymnastics broadcast", "perfect-score-routine", "Olympic-fanfare"),
     "user_goal": "Cut a highlight reel of perfect-score routines from my 6-hour Olympic gymnastics broadcast with Olympic-fanfare BGM."},
    {**_make("5-hour swimming championship", "gold-medal-heat", "uplifting orchestral"),
     "user_goal": "Make a highlight reel of gold-medal heats from my 5-hour swimming championship with uplifting orchestral BGM."},
    {**_make("4-hour tennis grand slam final", "break-point-and-match-point", "tense-strings"),
     "user_goal": "Cut a highlight reel of break-points and match-points from my 4-hour tennis grand slam final with tense-strings BGM."},
    {**_make("5-hour golf major", "birdie-and-eagle", "soft-acoustic"),
     "user_goal": "Make a highlight reel of birdies and eagles from my 5-hour golf major with soft-acoustic BGM."},
    {**_make("90-minute boxing title fight", "knockdown", "powerful-percussion"),
     "user_goal": "Cut a highlight reel of knockdowns from my 90-minute boxing title fight with powerful-percussion BGM."},
    {**_make("3-hour MMA championship", "knockout-and-submission", "intense-electronic"),
     "user_goal": "Make a highlight reel of knockouts and submissions from my 3-hour MMA championship with intense-electronic BGM."},
    {**_make("4-hour surfing competition", "top-wave", "tropical-rock"),
     "user_goal": "Cut a highlight reel of top waves from my 4-hour surfing competition with tropical-rock BGM."},
]
