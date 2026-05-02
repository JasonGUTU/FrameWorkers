"""Phase 3 final: style +20 + extend +18 + highlight +28 (= 66 cases).

style: 3 shapes (pure 17 / +Trans 11 / +Music 10)
extend: 3 shapes (pure 13 / +Trans 11 / +Music 10)
highlight: 4 shapes (pure 13 / +Trans 11 / +Music 11 / multi-addon alt 15)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

THIS = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS))
from categorize import categorize  # noqa: E402

V4 = THIS / "eval_cases_v4_500.json"

STYLE_PURE = [["IntakeVideoAgent"], ["StyleTransferAgent"], ["done"]]
STYLE_TRANS = [["IntakeVideoAgent"], ["StyleTransferAgent"], ["TranscriptionAgent"], ["CompositorAgent"], ["done"]]
STYLE_MUSIC = [["IntakeVideoAgent"], ["StyleTransferAgent"], ["MusicAgent"], ["AudioMixAgent"], ["CompositorAgent"], ["done"]]

EXTEND_PURE = [["IntakeVideoAgent"], ["VideoExtendAgent"], ["done"]]
EXTEND_TRANS = [["IntakeVideoAgent"], ["VideoExtendAgent"], ["TranscriptionAgent"], ["CompositorAgent"], ["done"]]
EXTEND_MUSIC = [["IntakeVideoAgent"], ["VideoExtendAgent"], ["MusicAgent"], ["AudioMixAgent"], ["CompositorAgent"], ["done"]]

HL_PURE = [["IntakeVideoAgent"], ["VideoAnalysisAgent"], ["HighlightAgent"], ["done"]]
HL_TRANS = [["IntakeVideoAgent"], ["VideoAnalysisAgent"], ["HighlightAgent"], ["TranscriptionAgent"], ["CompositorAgent"], ["done"]]
HL_MUSIC = [["IntakeVideoAgent"], ["VideoAnalysisAgent"], ["HighlightAgent"], ["MusicAgent"], ["AudioMixAgent"], ["CompositorAgent"], ["done"]]
HL_ALT = [["IntakeVideoAgent"], ["VideoAnalysisAgent"], ["HighlightAgent"], ["MusicAgent", "TranscriptionAgent"], ["TranscriptionAgent", "MusicAgent"], ["TranscriptionAgent", "MusicAgent"], ["AudioMixAgent"], ["CompositorAgent"], ["done"]]


BATCHES = [
    # ===== style pure +9 =====
    {"chain": STYLE_PURE, "bucket": "style", "cases": [
        ("style_019", "Take this 30-second clip of my morning commute and convert it to a watercolor animation style."),
        ("style_020", "Restyle this 2-minute home video of my kids' birthday party as a Studio Ghibli watercolor."),
        ("style_021", "Convert this 1-minute corporate office tour into a 1980s synthwave aesthetic."),
        ("style_022", "Take this 90-second clip of a city park in autumn and restyle it as a Van Gogh oil painting."),
        ("style_023", "Convert this 30-second skating clip into a 1990s graffiti street-art style."),
        ("style_024", "Take this 2-minute sunset montage and transform it into a Hokusai woodblock-print style."),
        ("style_025", "Restyle this 90-second underwater snorkeling clip as an art-deco mosaic."),
        ("style_026", "Convert this 1-minute cooking demo into a children's-book illustration style."),
        ("style_027", "Take this 2-minute kayaking video and transform it into a Pixar-animated look."),
    ]},

    # ===== style + Trans +6 =====
    {"chain": STYLE_TRANS, "bucket": "style", "cases": [
        ("style_028", "Convert this 4-minute lecture clip to a hand-drawn whiteboard style and add English subtitles."),
        ("style_029", "Take this 2-minute tour-guide narration and restyle it as a vintage travelogue, with English subtitles burned in."),
        ("style_030", "Convert this 90-second podcast video to a 1970s newspaper-comic style and add English subtitles."),
        ("style_031", "Restyle this 3-minute educational explainer into a chalkboard-line-art animation, with English subtitles."),
        ("style_032", "Convert this 4-minute interview clip into a graphic-novel style and burn in English subtitles."),
        ("style_033", "Take this 2-minute YouTube tutorial and restyle it as a Ghibli watercolor, with English subtitles for accessibility."),
    ]},

    # ===== style + Music +5 =====
    {"chain": STYLE_MUSIC, "bucket": "style", "cases": [
        ("style_034", "Convert this 90-second skateboarding clip to a 1990s graffiti aesthetic and add a hip-hop beat."),
        ("style_035", "Take this 2-minute scenic drive footage and restyle as a watercolor animation with a soft acoustic-folk score."),
        ("style_036", "Convert this 30-second dance clip into a 1980s neon synthwave look with a synthwave music track."),
        ("style_037", "Restyle this 90-second yoga session as a Japanese woodblock animation with a koto-and-shakuhachi score."),
        ("style_038", "Convert this 2-minute time-lapse of city construction into a steampunk illustration with a brass-clockwork score."),
    ]},

    # ===== extend pure +7 =====
    {"chain": EXTEND_PURE, "bucket": "extend", "cases": [
        ("extend_017", "Extend this 5-second clip of my dog catching a frisbee to 20 seconds in slow motion."),
        ("extend_018", "Take this 8-second time-lapse of dough rising and extend it to 30 seconds."),
        ("extend_019", "Extend this 6-second drone shot of a waterfall to 25 seconds."),
        ("extend_020", "Take this 10-second clip of a flame dancing in a fireplace and extend it to 40 seconds."),
        ("extend_021", "Extend this 7-second moment of my child's first steps to 25 seconds."),
        ("extend_022", "Take this 5-second wave breaking on a beach and extend it to 20 seconds in slow motion."),
        ("extend_023", "Extend this 8-second clip of a pottery wheel spinning to 30 seconds."),
    ]},

    # ===== extend + Trans +6 =====
    {"chain": EXTEND_TRANS, "bucket": "extend", "cases": [
        ("extend_024", "Take this 6-second clip of my speech opening and extend it to 25 seconds, then add English subtitles."),
        ("extend_025", "Extend this 8-second wedding-vow exchange to 30 seconds in slow-motion, and burn in English subtitles."),
        ("extend_026", "Take this 5-second podcast outro and stretch it to 20 seconds, adding English subtitles."),
        ("extend_027", "Extend this 10-second product demo to 30 seconds and add English subtitles for accessibility."),
        ("extend_028", "Take this 7-second motivational quote moment from my talk and extend it to 25 seconds with English subtitles."),
        ("extend_029", "Extend this 6-second cooking-show plating moment to 22 seconds and add English subtitles."),
    ]},

    # ===== extend + Music +5 =====
    {"chain": EXTEND_MUSIC, "bucket": "extend", "cases": [
        ("extend_030", "Take this 5-second clip of my dog leaping and extend it to 20 seconds in slow motion, then add a triumphant orchestral score."),
        ("extend_031", "Extend this 8-second time-lapse of fog rolling over a hill to 30 seconds and add a melancholic piano score."),
        ("extend_032", "Take this 6-second clip of pottery hands shaping clay and extend it to 25 seconds with a meditative ambient score."),
        ("extend_033", "Extend this 7-second clip of a child's first steps to 25 seconds and add a warm acoustic-guitar score."),
        ("extend_034", "Take this 10-second drone shot of a snowy mountain pass and extend it to 35 seconds with a sweeping cinematic score."),
    ]},

    # ===== highlight pure +7 =====
    {"chain": HL_PURE, "bucket": "highlight", "cases": [
        ("highlight_023", "I've uploaded a 30-minute company all-hands meeting. Cut me the highlight reel of the most engaging moments."),
        ("highlight_024", "Here's a 90-minute basketball scrimmage from my kid's team. Pull out the highlight reel of the best plays."),
        ("highlight_025", "I have a 2-hour wedding video. Cut me a highlight reel of the most emotional moments."),
        ("highlight_026", "Take this 45-minute keynote and pull out the highlight clips of the most quotable moments."),
        ("highlight_027", "Here's a 60-minute talent-show recording. Cut a highlight reel of the standout performances."),
        ("highlight_028", "I've uploaded an hour-long debate. Pull out the highlight clips of the most heated exchanges."),
        ("highlight_029", "Take this 90-minute family-vacation footage and produce a highlight reel of the best moments."),
    ]},

    # ===== highlight + Trans +6 =====
    {"chain": HL_TRANS, "bucket": "highlight", "cases": [
        ("highlight_030", "Here's a 60-minute podcast interview. Cut me a 5-minute highlight reel and burn in English subtitles."),
        ("highlight_031", "I've uploaded an hour of my graduation ceremony. Pull a highlight reel of the speeches with English subtitles."),
        ("highlight_032", "Take this 90-minute startup pitch event and produce a highlight reel of the best pitches with English subtitles."),
        ("highlight_033", "Here's a 2-hour municipal-council meeting. Cut a highlight reel of the heated debates with English subtitles."),
        ("highlight_034", "I have a 45-minute documentary interview. Pull a highlight reel with English subtitles."),
        ("highlight_035", "Take this 60-minute town-hall recording and cut a highlight reel of audience questions with English subtitles."),
    ]},

    # ===== highlight + Music +8 =====
    {"chain": HL_MUSIC, "bucket": "highlight", "cases": [
        ("highlight_036", "Cut me the highlight reel from this 90-minute soccer match and add an upbeat anthem score."),
        ("highlight_037", "I've uploaded a 2-hour skateboarding session. Pull a highlight reel and add a hip-hop beat."),
        ("highlight_038", "Take this 60-minute concert recording and cut me a highlight reel with a soft instrumental score over the in-between moments."),
        ("highlight_039", "Here's a 45-minute parkour session. Cut a highlight reel and layer in an electronic-rock score."),
        ("highlight_040", "I've uploaded a 90-minute family video from a Christmas morning. Pull a highlight reel with a warm holiday-piano score."),
        ("highlight_041", "Take this 60-minute corporate retreat footage and cut a highlight reel with an upbeat indie-pop score."),
        ("highlight_042", "Here's a 2-hour mountain-bike ride GoPro recording. Pull a highlight reel and add an adventurous orchestral score."),
        ("highlight_043", "I've recorded a 45-minute cooking competition between friends. Cut a highlight reel with a playful jazz-piano score."),
    ]},

    # ===== highlight multi-addon alt +7 =====
    {"chain": HL_ALT, "bucket": "highlight", "cases": [
        ("highlight_044", "Take this 2-hour TEDx event. Cut a highlight reel with English subtitles and a soft inspirational background score."),
        ("highlight_045", "Here's a 90-minute fashion-show recording. Cut a highlight reel with English subtitles and an upbeat electronic track."),
        ("highlight_046", "I've uploaded a 60-minute yoga workshop. Pull a highlight reel of the best poses, with English subtitles for the instructor's commentary, plus a meditative ambient track."),
        ("highlight_047", "Take this 45-minute cooking-show pilot. Cut a highlight reel with English subtitles and a playful jazz-piano score."),
        ("highlight_048", "Here's a 2-hour drone-racing championship. Cut a highlight reel with English subtitles and a high-energy electronic track."),
        ("highlight_049", "I've recorded a 90-minute live-music open mic. Pull a highlight reel with English subtitles for the comedy bits and a folk-acoustic score under the music."),
        ("highlight_050", "Take this 60-minute community-theater rehearsal. Cut a highlight reel with English subtitles and an upbeat showtune score."),
    ]},
]


def main() -> None:
    existing = json.loads(V4.read_text(encoding="utf-8"))
    existing_names = {c["name"] for c in existing}

    new_entries: list[dict] = []
    for batch in BATCHES:
        chain = batch["chain"]
        bucket_expected = batch["bucket"]
        bucket = categorize(chain)
        if bucket != bucket_expected:
            raise SystemExit(f"chain mismatch: expected {bucket_expected}, got {bucket} for {chain}")
        for name, goal in batch["cases"]:
            if name in existing_names:
                raise SystemExit(f"duplicate: {name}")
            new_entries.append({
                "name": name,
                "category": bucket_expected,
                "user_goal": goal,
                "expected_chain": chain,
            })

    print(f"prepared {len(new_entries)} new cases")

    merged = existing + new_entries
    V4.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"appended -> {V4}")
    print(f"total cases now: {len(merged)}")

    from collections import Counter
    from categorize import BUCKET_ORDER
    buckets = Counter(c["category"] for c in merged)
    for b in BUCKET_ORDER:
        print(f"  {b:<14} {buckets.get(b, 0)}")


if __name__ == "__main__":
    main()
