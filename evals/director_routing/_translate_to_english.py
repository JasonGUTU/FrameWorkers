"""One-off: translate 77 CN user_goals in eval_cases.json → English.

Also updates eval_cases.review_log.json's original_user_goal and the
input column of eval_cases.md. Deletes itself after the user OKs the diff.
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).parent

# name → English user_goal. Convention: cultivation-fantasy / animated drama /
# martial-arts / mini-drama / costume-drama / palace-intrigue / CEO romance /
# rebirth / live-in son-in-law / Chinese-English bilingual / Chinese subtitles.
# 竖屏 (case sub_vid_02) removed from goal entirely (no vertical-screen wording).
TRANS = {
    "cr_01":  "Make a cultivation-fantasy animated drama about a washed-up young man who awakens an ancient bloodline and rises through the ranks of his sect",
    "cr_03":  "Make a supernatural-thriller mini-drama where the female lead moves into a haunted house and finds a videotape left by the previous tenant that reveals an unsolved murder",
    "cr_04":  "Make a 3-minute rebirth-revenge animated drama where the female lead is framed by her best friend and falls to her death, then is reborn three years earlier to strike back",
    "cr_06":  "Make a sweet costume-drama mini-drama where the female lead transmigrates into the chancellor's legitimate daughter and moves from mutual loathing to mutual redemption with a cold-faced prince",
    "cr_08":  "Make a sci-fi animated drama about the last awakened AI falling in love with the only human engineer left",
    "cr_09":  "Make an urban romance mini-drama where the female lead runs into her ex-boyfriend — missing for five years — in a rainy-night Paris café",
    "cr_11":  "Make a palace-intrigue costume-drama mini-drama where a real and a fake princess swap places, exploit each other, and ultimately team up to expose the empress's ambitions",
    "cr_12":  "Make a martial-arts animated drama about a young swordsman who, to avenge his sect, ventures alone into the demonic cult's seven-layered killing formation",
    "cr_13":  "Make an urban underdog-comeback mini-drama where the live-in son-in-law thrown out of the rich family is secretly the heir of a top conglomerate",
    "cr_14":  "Make an epic-battle scene for a fantasy animated drama: seven ancient divine beasts gather to face a demon god returning to the mortal realm",
    "cr_15":  "Make a suspense-twist mini-drama where a therapist realizes her new patient is the man who murdered her sister years ago",
    "intake_img_01": "Using this uploaded image as the story's protagonist, produce an inspirational cultivation-fantasy animated drama",
    "intake_img_02": "Using this uploaded photo as the city backdrop, make a 3-minute urban-suspense mini-drama with an oppressive atmosphere",
    "intake_img_04": "Set in the seaside town from this uploaded photo, make a tragic costume-drama mini-drama: the female lead dies under the sea to save the male lead",
    "sub_01": "Make a Chinese-subtitled campus sweet-romance mini-drama: the top-student class president and a transferred-in delinquent girl redeem each other",
    "sub_02": "Make a subtitled costume-drama culinary animated drama where the female lead, a junior imperial-kitchen maid, rises through her cooking skills",
    "sub_04": "Make a subtitled children's cultivation-fantasy animated drama whose protagonist is a seven-year-old divine-beast boy fighting to protect a deep-sea forbidden zone",
    "sub_05": "Make a subtitled sci-fi mini-drama where the male lead, a top tech-reviewer blogger, suddenly discovers he is actually an AI",
    "sub_vid_01": "Add Chinese subtitles to this interview-style mini-drama",
    "sub_vid_02": "Add Chinese subtitles to this speech mini-drama",
    "sub_vid_05": "Batch-generate Chinese burned-in subtitles for this 30-episode cultivation-fantasy animated drama",
    "bilingual_01": "Make a Chinese-English bilingual costume-drama animated drama about a nine-generation tea-ceremony lineage reconnected with a modern female lead through reincarnation",
    "bilingual_02": "Make a Chinese-Japanese bilingual CEO-romance mini-drama where the male lead is a Japan-returned, hidden-identity conglomerate heir",
    "bilingual_04": "Make a Chinese-Spanish bilingual cultivation-fantasy animated drama, targeting Latin American market release",
    "bilingual_05": "Make a Chinese-English bilingual urban mini-drama where the female lead, a Chinese-American prodigy doctor, gets pulled into a family-inheritance battle",
    "style_01": "Convert this mini-drama clip to a Studio Ghibli animated-drama style",
    "style_02": "Make this mini-drama clip look like a cyberpunk animated drama with neon and rainy-night atmosphere",
    "style_04": "Convert this live-action mini-drama entirely to a Japanese anime style, preserving plot and camera work",
    "style_05": "Convert this costume-drama mini-drama to a Chinese ink-wash animated-drama style",
    "extend_01": "Extend this CEO-romance confrontation scene to 15 seconds, adding the male lead's inner monologue and slow-motion close-ups",
    "extend_04": "Extend this tragic costume-drama farewell scene to 20 seconds, adding snow-scene cutaways and flashbacks of the female lead recalling her past life",
    "extend_05": "Extend this scene of the female lead confessing and crying by 8 seconds, adding rain sound effects and close-ups of her trembling hands",
    "highlight_01": "Cut the most thrilling twist moments from this mini-drama episode into promotional material",
    "highlight_03": "Extract the sweetest lead-couple interactions from this mini-drama into a promo short",
    "highlight_04": "Cut the palace-intrigue iconic scenes from this costume-drama animated drama into a 30-second viral promo",
    "highlight_05": "Cut a compilation of face-slapping payback moments from this rebirth mini-drama episode",
    "complex_01": "Analyze this hit mini-drama, then write a new story in the same genre and produce it as a new animated drama",
    "complex_02": "First extend this mini-drama clip, then style-transfer it into a Japanese anime look",
    "complex_03": "Extend this mini-drama episode, then style-transfer it into an animated-drama look, and add Chinese subtitles",
    "complex_04": "Analyze the pacing of this 12-episode mini-drama, cut the best twist moments, add background music, and composite the final",
    "complex_06": "Analyze this mini-drama's emotional arc, then add subtitles and background music to it",
    "complex_08": "Translate this English interview video to Chinese and add Chinese subtitles",
    "complex_10": "Analyze this mini-drama, cut the climactic twist moments, add Chinese subtitles and background music, and output the final promo",
    "complex_11": "Transcribe this mini-drama EP01's Chinese dub, translate it to Japanese, generate Japanese subtitles, and burn them onto the video",
    "complex_13": "First analyze this hit mini-drama, then write a sequel story based on the analysis, and produce it as a new subtitled animated drama",
    "complex_15": "Cut the lead-couple highlight interactions from this urban sweet-romance mini-drama, add romantic background music and Chinese subtitles",
    "complex_19": "Using this uploaded animated-drama character image, make a Chinese-English bilingual CEO-romance mini-drama trailer",
    "complex_20": "Extract the key dialogue from this mini-drama's meeting scenes, transcribe and translate them to English, and output a subtitled highlight edit",
    "complex_21": "First style-transfer to an ink-wash animated-drama look, then extend the key scene, finally add traditional-style background music",
    "complex_23": "Using this uploaded female-lead character portrait as the protagonist, make a 3-minute cyberpunk sci-fi dystopian mini-drama: she leads an underground hacker coalition raiding a clone corporation and finally discovers she is also a clone. Extend the climactic identity-reveal confrontation scene by 10 seconds, adding slow-motion close-ups and shots of her trembling hands.",
    "complex_24": "Add a sad piano background score to this mini-drama clip",
    "complex_25": "Add rain ambience and a piano background score to this rainy-night scene",
    "complex_26": "Convert this clip to an animated-drama look and add Chinese subtitles",
    "complex_27": "Convert this costume-drama mini-drama clip to an ink-wash style and add a traditional-style background score",
    "complex_28": "Extend this confrontation scene by 10 seconds and add Chinese subtitles",
    "complex_29": "Extend this fight scene by 8 seconds and add a tense, intense background score",
    "complex_30": "Cut the highlight moments from this mini-drama and add Chinese subtitles to produce a promo",
    "complex_31": "Add an upbeat electronic ambient background score to this urban-nightscape vlog clip",
    "complex_33": "Add ocean-wave ambience and a lyrical piano background score to this seaside farewell scene",
    "complex_34": "Add thunder-and-wind ambience and an epic percussion background score to this cultivation-fantasy final-battle clip",
    "complex_35": "Convert this urban-romance clip to a cyberpunk look and add a synth-driven electronic score",
    "complex_37": "Convert this workplace-confrontation scene to a Japanese anime look and add Chinese subtitles",
    "complex_39": "Extend this CEO-romance confession scene by 12 seconds and add a romantic piano background score",
    "complex_41": "Extend this rebirth-awakening scene by 10 seconds and add Chinese subtitles",
    "complex_43": "Cut the palace-intrigue showdown iconic scenes from this mini-drama into a promo reel and add Chinese subtitles",
    "complex_45": "Extend this tragic costume-drama scene by 10 seconds and convert the whole thing to an ink-wash animated-drama look",
    "complex_46": "Extend this martial-arts fight scene by 8 seconds, convert it to an animated-drama look, and add Chinese subtitles",
    "complex_47": "First convert this urban car-chase scene to a cyberpunk look, then extend the climax by 12 seconds, finally add a synth-driven score",
    "complex_49": "Translate this Japanese-language interview mini-drama into Chinese subtitles and burn them onto the video",
    "complex_50": "Extract the highlight dialogue from this English-language business-warfare mini-drama, translate it to Chinese, and add subtitles",
    "complex_51": "Analyze this CEO-romance mini-drama's pacing, then add Chinese subtitles and a background score",
    "complex_52": "Cut the climactic scenes from this costume-drama mini-drama into a trailer, with Chinese subtitles and an epic score",
    "complex_53": "Cut the face-slapping iconic scenes from this urban rebirth mini-drama, add rousing music and Chinese subtitles",
    "complex_54": "Analyze the tropes of this hit sci-fi mini-drama and rewrite a new story in the same style as a new animated drama",
    "complex_55": "Write a sequel based on the plotline of this palace-intrigue mini-drama and produce it as a new Chinese-subtitled animated drama",
    "complex_57": "Using these uploaded costume-drama character images as the protagonists, make a Chinese-English bilingual palace-intrigue mini-drama promo",
    "complex_59": "Using this uploaded female-swordsman character portrait as the protagonist, make a martial-arts mini-drama; extend the sect-massacre opening scene by 15 seconds with slow-motion",
    # --- normalize originally-EN goals that still used phonetic transliterations or the 竖屏 word ---
    "cr_05":         "Create a post-apocalyptic animated drama where the last survivors discover a hidden sanctuary guarded by an awakened AI",
    "cr_07":         "I want a romance mini-drama where a young woman wins a dating-app lottery and ends up fake-married to a reclusive tech mogul",
    "intake_img_03": "Use the character in this uploaded image as the hero of a one-minute cultivation-fantasy animated-drama trailer",
    "complex_56":    "Study this cultivation-fantasy drama's character arcs and generate a prequel animated drama with Chinese subtitles",
}

# Flip Chinese ↔ English in goals, because FrameWorker's default source/output
# is English. Chain stays unchanged (TranslationAgent is boolean; direction
# doesn't affect the agent set). Covers 35 cases across three groups:
#   A: explicit source-lang swap (Eng→Chi ↔ Chi→Eng)
#   B: bilingual pair re-ordered (Chi-X / X-Chi → Eng-X / X-Eng)
#   C: "Chinese subtitles" → "English subtitles" on mono-language tasks
FLIP_LANG = {
    # Group A — explicit source-language swap
    "complex_08": "Translate this Chinese interview video to English and add English subtitles",
    "complex_11": "Transcribe this mini-drama EP01's English dub, translate it to Japanese, generate Japanese subtitles, and burn them onto the video",
    "complex_18": "Analyze this English mini-drama season, extract the high-tension climax moments, and add Chinese subtitles plus emotional background score",
    "complex_20": "Extract the key dialogue from this mini-drama's meeting scenes, transcribe and translate them to Chinese, and output a subtitled highlight edit",
    "complex_49": "Translate this Japanese-language interview mini-drama into English subtitles and burn them onto the video",
    "complex_50": "Extract the highlight dialogue from this Chinese-language business-warfare mini-drama, translate it to English, and add subtitles",
    "sub_vid_03": "Generate Chinese subtitles for this English mini-drama episode",
    # Group B — bilingual pair re-ordered English-first
    "bilingual_01": "Make an English-Chinese bilingual costume-drama animated drama about a nine-generation tea-ceremony lineage reconnected with a modern female lead through reincarnation",
    "bilingual_02": "Make an English-Japanese bilingual CEO-romance mini-drama where the male lead is a Japan-returned, hidden-identity conglomerate heir",
    "bilingual_03": "Create a mini-drama with English and Chinese subtitles about a martial-arts prodigy seeking revenge across ancient and modern timelines",
    "bilingual_04": "Make an English-Spanish bilingual cultivation-fantasy animated drama, targeting Latin American market release",
    "bilingual_05": "Make an English-Chinese bilingual urban mini-drama where the female lead, a Chinese-American prodigy doctor, gets pulled into a family-inheritance battle",
    "complex_19":   "Using this uploaded animated-drama character image, make an English-Chinese bilingual CEO-romance mini-drama trailer",
    "complex_57":   "Using these uploaded costume-drama character images as the protagonists, make an English-Chinese bilingual palace-intrigue mini-drama promo",
    "complex_58":   "Use these uploaded cyberpunk character portraits to produce a bilingual (English/Chinese) sci-fi mini-drama trailer",
    # Group C — Chinese subtitles → English subtitles (default-lang single-lang tasks)
    "sub_01":       "Make an English-subtitled campus sweet-romance mini-drama: the top-student class president and a transferred-in delinquent girl redeem each other",
    "sub_vid_01":   "Add English subtitles to this interview-style mini-drama",
    "sub_vid_02":   "Add English subtitles to this speech mini-drama",
    "sub_vid_05":   "Batch-generate English burned-in subtitles for this 30-episode cultivation-fantasy animated drama",
    "complex_03":   "Extend this mini-drama episode, then style-transfer it into an animated-drama look, and add English subtitles",
    "complex_10":   "Analyze this mini-drama, cut the climactic twist moments, add English subtitles and background music, and output the final promo",
    "complex_15":   "Cut the lead-couple highlight interactions from this urban sweet-romance mini-drama, add romantic background music and English subtitles",
    "complex_26":   "Convert this clip to an animated-drama look and add English subtitles",
    "complex_28":   "Extend this confrontation scene by 10 seconds and add English subtitles",
    "complex_30":   "Cut the highlight moments from this mini-drama and add English subtitles to produce a promo",
    "complex_37":   "Convert this workplace-confrontation scene to a Japanese anime look and add English subtitles",
    "complex_41":   "Extend this rebirth-awakening scene by 10 seconds and add English subtitles",
    "complex_43":   "Cut the palace-intrigue showdown iconic scenes from this mini-drama into a promo reel and add English subtitles",
    "complex_44":   "Cut the top tear-jerker moments from this romance drama into a 30-second promo with English subtitles",
    "complex_46":   "Extend this martial-arts fight scene by 8 seconds, convert it to an animated-drama look, and add English subtitles",
    "complex_51":   "Analyze this CEO-romance mini-drama's pacing, then add English subtitles and a background score",
    "complex_52":   "Cut the climactic scenes from this costume-drama mini-drama into a trailer, with English subtitles and an epic score",
    "complex_53":   "Cut the face-slapping iconic scenes from this urban rebirth mini-drama, add rousing music and English subtitles",
    "complex_55":   "Write a sequel based on the plotline of this palace-intrigue mini-drama and produce it as a new English-subtitled animated drama",
    "complex_56":   "Study this cultivation-fantasy drama's character arcs and generate a prequel animated drama with English subtitles",
}
assert len(FLIP_LANG) == 35, f"FLIP_LANG has {len(FLIP_LANG)} entries, expected 35"
TRANS.update(FLIP_LANG)  # 5 new names added, 30 existing values overridden → 86 total

assert len(TRANS) == 86, f"TRANS has {len(TRANS)} entries, expected 86"


def main():
    # 1) eval_cases.json
    ev_path = ROOT / "eval_cases.json"
    cases = json.loads(ev_path.read_text(encoding="utf-8"))
    n_hit = 0
    for c in cases:
        if c["name"] in TRANS:
            c["user_goal"] = TRANS[c["name"]]
            n_hit += 1
    ev_path.write_text(json.dumps(cases, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"eval_cases.json: updated {n_hit}/{len(cases)} entries")

    # 2) eval_cases.review_log.json
    rl_path = ROOT / "eval_cases.review_log.json"
    rl = json.loads(rl_path.read_text(encoding="utf-8"))
    n_hit_rl = 0
    for e in rl:
        if e["name"] in TRANS:
            e["original_user_goal"] = TRANS[e["name"]]
            for k in [k for k in list(e.keys()) if k.startswith("edited_")]:
                del e[k]
            n_hit_rl += 1
    rl_path.write_text(json.dumps(rl, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"eval_cases.review_log.json: updated {n_hit_rl}/{len(rl)} entries")

    # 3) eval_cases.md — replace input column where row has `name`
    md_path = ROOT / "eval_cases.md"
    md = md_path.read_text(encoding="utf-8")
    n_hit_md = 0
    for name, eng in TRANS.items():
        # row pattern: | N | `name` | GOAL | CHAIN |
        pat = re.compile(
            r"(\|\s*\d+\s*\|\s*`" + re.escape(name) + r"`\s*\|\s*)[^|]*(\s*\|)"
        )
        new_md, n = pat.subn(lambda m: m.group(1) + eng + " " + m.group(2).lstrip(), md)
        if n == 0:
            print(f"  WARN: md no row for {name}")
        else:
            md = new_md
            n_hit_md += 1
    md_path.write_text(md, encoding="utf-8")
    print(f"eval_cases.md: updated {n_hit_md}/{len(TRANS)} rows")


if __name__ == "__main__":
    main()
