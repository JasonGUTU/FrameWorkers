#!/usr/bin/env python3
"""Translate cr (10) + intake_img (10) user_goal Chinese → English.

Why: this dataset is going into a paper. The 20 cr/intake_img cases were
rewritten Chinese-short-drama-flavor earlier in this session for FrameWorkers'
domestic short-video context; for the paper we keep the same trope inventory
(cultivation / rebirth-revenge / palace intrigue / zombie / wealthy clan /
CEO chase / etc.) but express in English so the whole 30-case selection is
language-uniform with storytelling and any reader can parse.

Trigger keywords are preserved verbatim by translation:
  - Ambience: "Add ambient sounds: ..."
  - Music: "Add a ... BGM"
  - Transcription: "Add Chinese subtitles ..."
  - Translation: "Add bilingual Chinese-English subtitles ..."

Backup: per-case _meta.user_goal_zh keeps the Chinese version for audit.
"""
from __future__ import annotations
import json
from pathlib import Path

NEW_GOALS_EN: dict[str, str] = {
    # === cr Type A: 6 layers, no audio ===
    "cr_042": (
        "Make a cultivation / xianxia animated short drama — a prodigy "
        "disciple is framed by his senior brother and his cultivation core "
        "is crippled. With nothing but his family's broken sword, he "
        "refounds his foundation, slays ancient demons, and finally breaks "
        "through the nine heavenly tribulations to ascend to godhood."
    ),
    "cr_023": (
        "Make a period rebirth-revenge palace-intrigue animated short "
        "drama — the disgraced former Empress Liu Ruyan, poisoned to "
        "death in a cold palace by her own elder sister in her past life, "
        "wakes up reborn on the day before she enters the palace. This "
        "time she vows to force every betrayer in her past life to kneel "
        "before her, one by one."
    ),
    "cr_049": (
        "Make a modern-urban rebirth-revenge animated short drama — a "
        "top-tier lawyer is framed by his business partner and thrown in "
        "prison; by the time he gets out, his wife and daughter are dead. "
        "Granted a second chance, he wakes up ten years earlier on the "
        "rainy night that changed everything, determined to drag every "
        "single one of his betrayers down with him."
    ),

    # === cr Type B: 8 layers, +Ambience ===
    "cr_064": (
        "Make a zombie-apocalypse animated short drama — day seven of the "
        "outbreak, a small squad led by a former special-ops captain and a "
        "female doctor cuts through zombie-infested underground tunnels in "
        "search of the legendary vaccine lab. Add ambient sounds: zombie "
        "shrieks, distant air-raid sirens, and wind whipping through "
        "ruined corridors."
    ),
    "cr_104": (
        "Make a wuxia / xianxia revenge animated short drama — the only "
        "surviving young Daoist after his sect is massacred by the demonic "
        "cult carries his master's severed head all the way back to Mount "
        "Kunlun, vowing to perform the blood-moon vengeance rite that very "
        "night. Add ambient sounds: howling mountain wind, ringing sword "
        "strikes, and rolling distant thunder."
    ),
    "cr_016": (
        "Make a supernatural-suspense animated short drama — at midnight "
        "inside the old wing of a psychiatric hospital, the new male "
        "intern discovers that Room 304 plays a thirty-year-old recording "
        "every single night by itself. When he finally pushes that door "
        "open, he sees his ten-year-old self standing inside. Add ambient "
        "sounds: faint electrical hum, hollow corridor reverb, and distant "
        "sobbing."
    ),

    # === cr Type C: 9 layers, +Music+Ambience ===
    "cr_107": (
        "Make a period war-epic animated short drama — General Murong "
        "Rong's only son has guarded the western frontier for ten years "
        "without returning home. In his final stand he charges alone into "
        "ten thousand enemy soldiers, only to reclaim the family's "
        "ancestral green-dragon polearm from the body of his fallen "
        "father. Add ambient sounds: war horses neighing, bowstrings drawn "
        "taut, frozen wind sweeping the snow plains. Add a stirring "
        "period war-drum BGM."
    ),
    "cr_072": (
        "Make a Chinese-mythology fantasy animated short drama — at the "
        "close of the Investiture of the Gods war, the last surviving "
        "little nine-tailed fox demon is dragged up onto the Investiture "
        "Platform by Jiang Ziya. Just before her execution, she suddenly "
        "remembers a man who has been appearing in her dreams. Add "
        "ambient sounds of the nine-heaven thunder rolling, and a "
        "mournful classical-Chinese BGM."
    ),

    # === cr Type D: 8 layers, +Music ===
    "cr_059": (
        "Make a high-school revenge animated short drama — Gu Xiuning, "
        "the ice-cold transfer student who always ranks first, is "
        "discovered on his very first day to be the only survivor of an "
        "arson that struck this school ten years ago. The new homeroom "
        "teacher, Mr. Lin, turns out to be the very man who dragged him "
        "out of the flames back then. Add a restrained, suppressed piano "
        "BGM."
    ),
    "cr_030": (
        "Make a CEO-chasing-his-wife animated short drama — Su Nian, the "
        "contract-marriage wife, returns three years later with twin "
        "children to deliver divorce papers to the heir of the Huo family. "
        "The man who once treated her merely as a stand-in for someone "
        "else, kneels before her for the very first time. Add a "
        "heart-tugging string BGM."
    ),

    # === intake_img Type A: 8 layers, no audio ===
    "intake_img_019": (
        "Use this uploaded photo as the face of the rebirth-revenge "
        "female lead. Make a period rebirth-revenge palace-intrigue "
        "animated short drama — she is the former empress who was forced "
        "to drink poisoned wine. Reborn back to the day of the imperial "
        "selection, this time she will personally send every soul who "
        "once owed her a life into the underworld."
    ),
    "intake_img_018": (
        "Use this uploaded photo as the wealthy-heir male lead. Make a "
        "modern-urban wealthy-clan tortured-romance animated short "
        "drama — seven years ago he watched her jump off a yacht into the "
        "deep sea; seven years later she returns under a different name, "
        "becomes his biggest business rival, and the one shadow he can "
        "never quite catch."
    ),
    "intake_img_005": (
        "Use this uploaded photo as the look of the cultivation male "
        "lead. Make a cultivation-rebirth animated short drama — in his "
        "previous life he was the Heavenly Emperor who suppressed all "
        "under heaven, killed by the joint betrayal of nine sacred lands. "
        "He is now reborn into the body of the trash junior disciple "
        "every senior in the sect mocks; every one of those who once "
        "stepped on him has no idea they are already standing at the "
        "edge of doom."
    ),
    "intake_img_008": (
        "Use this uploaded photo as the fantasy female lead. Make a "
        "post-apocalyptic super-power animated short drama — the day the "
        "virus broke out she awakened the power to bend metal inside a "
        "subway car. Now she leads a band of survivors through the "
        "zombie-flooded city, dodging the military's super-power task "
        "force as she hunts for whoever truly released the pathogen."
    ),

    # === intake_img Type B: 10 layers, +Music ===
    "intake_img_046": (
        "Use this uploaded photo as the period female lead. Make a "
        "palace-intrigue rise-from-the-ashes animated short drama — she "
        "is the disgraced empress who climbed all the way back from the "
        "cold palace to the principal palace; the only one who still "
        "remembers her real name on this revenge road is the little "
        "eunuch who once took a knife for her. Add a sweeping "
        "classical-Chinese BGM."
    ),
    "intake_img_039": (
        "Use this uploaded photo as the high-school female lead. Make a "
        "contemporary high-school sweet-and-bitter romance animated short "
        "drama — rumor says she is the secret daughter of the largest "
        "private-academy benefactor in northern Jiangbei; on her very "
        "first day as a transfer student she clashes head-on with the "
        "school's most untouchable bully. Add a light-yet-bittersweet "
        "piano BGM."
    ),

    # === intake_img Type C: 10 layers, +Transcription+Translation ===
    "intake_img_036": (
        "Use this uploaded photo as the look of the CEO male lead. Make "
        "a modern-urban wealthy-clan tortured-romance animated short "
        "drama — three years after the car crash that erased her memory, "
        "the little contract wife Su Nian reappears in front of CEO Huo "
        "with a small boy who looks exactly like him. Add bilingual "
        "Chinese-English subtitles for overseas distribution."
    ),
    "intake_img_037": (
        "Use this uploaded photo as the fantasy female lead. Make a "
        "demon-empress rebirth animated short drama — in her previous "
        "life she was the demon empress who guarded the human realm, "
        "killed by the joint betrayal of her most trusted disciple and "
        "the heavenly court. Reborn to the day before her demonic "
        "awakening, this time she will personally drag every one of "
        "those self-righteous heavenly beings down from their pedestals. "
        "Add bilingual Chinese-English subtitles for overseas short-video "
        "distribution."
    ),

    # === intake_img Type D: 9 layers, +Transcription ===
    "intake_img_030": (
        "Use this uploaded photo as the suspense male lead. Make an "
        "urban crime-suspense animated short drama — the new deputy "
        "captain of the homicide unit takes his very first case: a "
        "serial-disposal cold case that has been silent for fifteen "
        "years. As he closes in on the truth, he finds his own father's "
        "name plainly listed among the original suspects. Add Chinese "
        "subtitles for short-video platform distribution."
    ),

    # === intake_img Type E: 11 layers, +Transcription+Music ===
    "intake_img_049": (
        "Use this uploaded photo as the wealthy-clan tortured-romance "
        "female lead. Make a modern-urban stand-in-bride wealthy-clan "
        "animated short drama — she was brought in to replace his dead "
        "first love. The day her three-year contract expires she hands "
        "him divorce papers, and the man who never once truly looked at "
        "her in those three years suddenly begins hunting for her like a "
        "madman across the whole city. Add Chinese subtitles for "
        "short-video platform distribution and a sad piano BGM."
    ),
}


def main() -> None:
    here = Path(__file__).parent.resolve()
    src = here / "selection.json"
    data = json.loads(src.read_text())

    translated = 0
    for c in data:
        if c["name"] in NEW_GOALS_EN:
            c["_meta"]["user_goal_zh"] = c["user_goal"]
            c["user_goal"] = NEW_GOALS_EN[c["name"]]
            c["_meta"]["user_goal_en_translated"] = True
            translated += 1

    src.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    md: list[str] = [
        "# 30-case selection (cr+intake_img translated to English 2026-05-09)\n\n",
        f"- {translated} cr/intake_img user_goals translated zh → en for paper\n\n",
    ]
    for cat in ["cr", "intake_img", "storytelling"]:
        cat_picks = sorted([c for c in data if c["category"] == cat],
                           key=lambda c: c["name"])
        md.append(f"## {cat} ({len(cat_picks)})\n\n")
        md.append("| name | user_goal |\n|---|---|\n")
        for c in cat_picks:
            goal = c["user_goal"][:200].replace("|", r"\|")
            if len(c["user_goal"]) > 200:
                goal += "..."
            md.append(f"| `{c['name']}` | {goal} |\n")
        md.append("\n")
    (here / "selection.md").write_text("".join(md))

    print(f"Translated {translated} user_goals zh → en")


if __name__ == "__main__":
    main()
